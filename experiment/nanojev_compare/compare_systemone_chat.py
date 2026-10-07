"""Paired offline latency/action benchmark: same model, System One vs chat.

Runs on the server with NanoJev public held-out data. No raw states or secrets
are written to the output. This measures decisions on fixed states, not rollout.
"""
import argparse
import collections
import json
import re
import statistics
import time
import urllib.request
from pathlib import Path

from run_paired import select_rows


URL = "http://127.0.0.1:30000"
MODEL = "Qwen3.8-27B"
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def post(path, payload):
    req = urllib.request.Request(URL + path, data=json.dumps(payload, ensure_ascii=False).encode(), headers={"Content-Type": "application/json"})
    start = time.perf_counter()
    with urllib.request.urlopen(req, timeout=120) as response:
        value = json.load(response)
    return value, time.perf_counter() - start


def chat_payload(row, mode, matched=False):
    question = row["questions"]["action"]
    options = list(question["criteria"].items())
    if matched:
        # Reuse the exact renderer in the installed SGLang version. System One
        # delegates to this same renderer; both use one user message and disable
        # thinking. This isolates the API path from wording changes.
        from sglang.srt.entrypoints.openai.serving_decisions import QuestionView, _render_question, default_labels
        view = QuestionView(kind="choice", question=question["instructions"],
                            names=[x[0] for x in options], details=[x[1] for x in options])
        text = _render_question(text=row["state"], view=view, labels=default_labels(view))
    else:
        text = "State:\n" + row["state"] + "\nQuestion: " + question["instructions"] + "\nOptions:\n"
        text += "\n".join(f"{LETTERS[i]}. {name}: {description}" for i, (name, description) in enumerate(options))
        text += "\nAnswer with exactly one option letter and nothing else."
    return {
        "model": MODEL, "messages": [{"role": "user", "content": text}],
        "temperature": 0, "max_tokens": 1 if mode == "chat_1token" else 32,
        "chat_template_kwargs": {"enable_thinking": False},
    }, dict(zip(LETTERS, (name for name, _ in options)))


def run_arm(row, arm, matched=False):
    if arm == "systemone":
        response, elapsed = post("/v1/systemone", {"model": MODEL, "state": row["state"], "questions": row["questions"]})
        answer = response["answers"]["action"]
        return {"action": answer["choice"], "latency_s": elapsed,
                "input_tokens": response.get("usage", {}).get("input_tokens"),
                "output_tokens": response.get("usage", {}).get("output_tokens"),
                "label_mass": answer.get("x_label_mass"), "probs": answer["probabilities"]}
    payload, label_map = chat_payload(row, arm, matched=matched)
    response, elapsed = post("/v1/chat/completions", payload)
    raw = response["choices"][0]["message"]["content"] or ""
    match = re.fullmatch(r"\s*([A-Z])\s*[.。]?\s*", raw)
    action = label_map.get(match.group(1)) if match else None
    usage = response.get("usage", {})
    return {"action": action, "raw": raw[:120], "latency_s": elapsed,
            "input_tokens": usage.get("prompt_tokens"), "output_tokens": usage.get("completion_tokens"),
            "finish_reason": response["choices"][0].get("finish_reason")}


def summary(records):
    out = {"n": len(records)}
    for arm in ("systemone", "chat_1token", "chat_32tokens"):
        values = [r[arm]["latency_s"] for r in records]
        out[arm] = {"latency_median_s": statistics.median(values), "latency_mean_s": statistics.mean(values),
                    "latency_p90_s": sorted(values)[max(0, int(0.9 * len(values)) - 1)],
                    "invalid": sum(r[arm]["action"] is None for r in records),
                    "input_tokens_mean": statistics.mean(r[arm]["input_tokens"] for r in records),
                    "output_tokens_mean": statistics.mean(r[arm]["output_tokens"] for r in records)}
        gold = [r for r in records if r["gold"] is not None]
        teacher = [r for r in records if r["teacher_top1"] is not None]
        out[arm]["expert_match"] = sum(r[arm]["action"] == r["gold"] for r in gold) / len(gold) if gold else None
        out[arm]["teacher_top1_match"] = sum(r[arm]["action"] == r["teacher_top1"] for r in teacher) / len(teacher) if teacher else None
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--per-task", type=int, default=30)
    parser.add_argument("--matched-prompt", action="store_true")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    rows = []
    for split in ("test", "ood"):
        selected, _ = select_rows(args.data / f"{split}.jsonl", args.per_task)
        rows.extend(selected)
    arms = ("systemone", "chat_1token", "chat_32tokens")
    # Warm up both API paths on the first real shape; exclude warmup latency.
    for arm in arms:
        run_arm(rows[0], arm, matched=args.matched_prompt)
    records = []
    output = args.output / "systemone_chat_predictions.jsonl"
    with output.open("w", encoding="utf-8") as stream:
        for index, row in enumerate(rows):
            teacher = row.get("teacher", {}).get("native_probs", {}).get("action")
            record = {"id": row["id"], "split": row["split"], "task": row["metadata"]["task"],
                      "episode_id": row["metadata"].get("episode_id"),
                      "gold": row.get("gold", {}).get("action"),
                      "teacher_top1": max(teacher, key=teacher.get) if teacher else None}
            # Rotate order to reduce systematic cache and drift bias.
            for arm in arms[index % 3:] + arms[:index % 3]:
                record[arm] = run_arm(row, arm, matched=args.matched_prompt)
            records.append(record)
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
            stream.flush()
            if (index + 1) % 10 == 0:
                print("DONE", index + 1, "/", len(rows), flush=True)
    groups = collections.defaultdict(list)
    for record in records:
        groups[record["split"] + "/" + record["task"]].append(record)
    report = {"model": MODEL, "selection": "SHA256(id), first record in up to 30 distinct episodes per split/task",
              "request_order": "rotating 3 arms", "matched_prompt": args.matched_prompt,
              "n": len(records), "overall": summary(records),
              "by_split_task": {k: summary(v) for k, v in sorted(groups.items())}}
    (args.output / "systemone_chat_summary.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print("COMPLETE", json.dumps(report["overall"]), flush=True)


if __name__ == "__main__":
    main()
