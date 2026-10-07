"""Run a reproducible, episode-stratified NanoJev/System One comparison.

Execute on the deployment host with the uploaded NanoJev repository and assets.
No credentials, weights, or raw state texts are written to the results.
"""
import argparse
import collections
import hashlib
import json
import math
import statistics
import sys
import time
import urllib.request
from pathlib import Path


def select_rows(path, per_task):
    rows = [json.loads(line) for line in path.open(encoding="utf-8")]
    by_task = collections.defaultdict(list)
    for row in rows:
        by_task[row["metadata"]["task"]].append(row)
    chosen = []
    for task, group in sorted(by_task.items()):
        # Distinct episodes reduce within-trajectory dependence. Hash ordering
        # fixes the sample before either model is queried.
        group.sort(key=lambda x: hashlib.sha256(x["id"].encode()).hexdigest())
        seen = set()
        for row in group:
            episode = row["metadata"].get("episode_id", row["id"])
            if episode in seen:
                continue
            seen.add(episode)
            chosen.append(row)
            if sum(r["metadata"]["task"] == task for r in chosen) >= per_task:
                break
    return chosen, {task: len(group) for task, group in by_task.items()}


def systemone(row, model):
    payload = {"model": model, "state": row["state"], "questions": row["questions"]}
    request = urllib.request.Request(
        "http://127.0.0.1:30000/v1/systemone",
        data=json.dumps(payload, ensure_ascii=False).encode(),
        headers={"Content-Type": "application/json"},
    )
    start = time.perf_counter()
    with urllib.request.urlopen(request, timeout=120) as response:
        result = json.load(response)
    return result, time.perf_counter() - start


def argmax(probs):
    return max(probs, key=probs.get)


def metrics(records):
    out = {"n": len(records)}
    for key in ("nano_latency_s", "sglang_latency_s"):
        values = [r[key] for r in records]
        out[key + "_median"] = statistics.median(values) if values else None
        out[key + "_mean"] = statistics.mean(values) if values else None
    out["model_top1_agreement"] = statistics.mean(r["nano_top1"] == r["sglang_top1"] for r in records) if records else None
    for prefix in ("nano", "sglang"):
        gold = [r for r in records if r.get("gold") is not None]
        out[prefix + "_expert_argmax_match"] = statistics.mean(r[prefix + "_top1"] == r["gold"] for r in gold) if gold else None
        teacher = [r for r in records if r.get("teacher_probs")]
        out[prefix + "_jev_teacher_top1_match"] = statistics.mean(r[prefix + "_top1"] == argmax(r["teacher_probs"]) for r in teacher) if teacher else None
        out[prefix + "_jev_teacher_cross_entropy"] = statistics.mean(-sum(p * math.log(max(r[prefix + "_probs"].get(k, 0), 1e-12)) for k, p in r["teacher_probs"].items()) for r in teacher) if teacher else None
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--data", type=Path, required=True)
    p.add_argument("--checkpoint", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--per-task", type=int, default=30)
    p.add_argument("--model", default="Qwen3.8-27B")
    args = p.parse_args()
    sys.path.insert(0, str(args.source / "scripts"))
    from predict_toy_decisions import DecisionPredictor
    import torch
    import transformers

    args.output.mkdir(parents=True, exist_ok=True)
    selected = []
    populations = {}
    for split in ("test", "ood"):
        rows, counts = select_rows(args.data / (split + ".jsonl"), args.per_task)
        selected.extend(rows)
        populations[split] = counts
    print("SELECTED", len(selected), populations, flush=True)
    t0 = time.perf_counter()
    nano = DecisionPredictor(args.checkpoint, disable_native_triton=True)
    load_s = time.perf_counter() - t0
    print("NANO_LOAD_S", load_s, flush=True)
    all_records = []
    out_path = args.output / "paired_predictions.jsonl"
    with out_path.open("w", encoding="utf-8") as stream:
        for i, row in enumerate(selected, 1):
            payload = {"states": [{"id": row["id"], "state": row["state"], "questions": row["questions"]}]}
            t0 = time.perf_counter()
            ny = nano.predict(payload)
            nt = time.perf_counter() - t0
            sy, st = systemone(row, args.model)
            np = ny["states"][0]["answers"]["action"]["probabilities"]
            sp = sy["answers"]["action"]["probabilities"]
            criteria = row["questions"]["action"]["criteria"]
            if set(np) != set(criteria) or set(sp) != set(criteria):
                raise ValueError("candidate mismatch: " + row["id"])
            teacher = row.get("teacher", {}).get("native_probs", {}).get("action")
            record = {
                "id": row["id"], "split": row["split"], "task": row["metadata"]["task"],
                "episode_id": row["metadata"].get("episode_id"),
                "gold": row.get("gold", {}).get("action"),
                "gold_label_kind": row.get("gold_label_kind", {}).get("action"),
                "teacher_probs": teacher,
                "nano_probs": np, "nano_top1": argmax(np), "nano_latency_s": nt,
                "sglang_probs": sp, "sglang_top1": argmax(sp), "sglang_latency_s": st,
                "sglang_x_label_mass": sy["answers"]["action"].get("x_label_mass"),
                "sglang_input_tokens": sy.get("usage", {}).get("input_tokens"),
            }
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
            stream.flush()
            all_records.append(record)
            if i % 10 == 0:
                print("DONE", i, "of", len(selected), flush=True)
    groups = collections.defaultdict(list)
    for record in all_records:
        groups[record["split"] + "/" + record["task"]].append(record)
    summary = {
        "method": "SHA256(id) order, first 30 distinct episodes per task and split; same raw state and question objects; NanoJev temperature 1, BF16 autocast, float32 weights; SGLang System One API",
        "populations": populations,
        "sample_size": len(all_records),
        "nano_load_s": load_s,
        "versions": {"torch": torch.__version__, "transformers": transformers.__version__},
        "overall": metrics(all_records),
        "by_split_task": {key: metrics(value) for key, value in sorted(groups.items())},
    }
    (args.output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("COMPLETE", json.dumps(summary["overall"]), flush=True)


if __name__ == "__main__":
    main()
