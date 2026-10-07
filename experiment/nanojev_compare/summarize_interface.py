"""Validate and summarize saved paired interface results, without model calls."""
import collections
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent / "results"


def rows(path):
    return [json.loads(line) for line in path.open(encoding="utf-8")]


def rollout_summary(directory):
    episodes = rows(directory / "episodes.jsonl")
    paired = collections.defaultdict(dict)
    for result in episodes:
        case_id = result["case"]["id"]
        if result["arm"] in paired[case_id]:
            raise ValueError("Duplicate case/arm")
        if not result["complete"]:
            raise ValueError("Incomplete episode")
        paired[case_id][result["arm"]] = result
    output = []
    for case_id, pair in paired.items():
        if set(pair) != {"systemone", "chat_1token"}:
            raise ValueError("Incomplete pair")
        a, b = pair["systemone"], pair["chat_1token"]
        initial_equal = a["initial_observation_sha256"] == b["initial_observation_sha256"]
        if not initial_equal:
            raise ValueError("Paired initial worlds differ")
        def actions(x):
            return [s["response"]["action"] for s in x["steps"]]
        output.append({"case_id": case_id, "split": a["case"]["split"], "variant": a["case"]["variant"],
                       "budget": a["case"]["spec"]["max_steps"],
                       "initial_world_equal": initial_equal, "action_trace_equal": actions(a) == actions(b),
                       **{arm: {"success": x["success"], "physical_steps": x["final_info"]["episode_metrics"]["physical_steps"],
                                 "collisions": x["final_info"]["episode_metrics"]["collisions"],
                                 "decisions": len(x["steps"]),
                                 "model_calls": sum(not s["response"]["forced"] for s in x["steps"]),
                                 "model_latency_s": sum(s["response"]["latency_s"] for s in x["steps"])}
                          for arm, x in pair.items()}})
    return {"paired_cases": len(output), "identical_action_traces": sum(x["action_trace_equal"] for x in output),
            "by_case": output}


def main():
    matched = rows(ROOT / "matched" / "systemone_chat_predictions.jsonl")
    arms = ("systemone", "chat_1token", "chat_32tokens")
    audit = {"matched_n": len(matched),
             "systemone_chat1_same_actions": sum(r["systemone"]["action"] == r["chat_1token"]["action"] for r in matched),
             "systemone_chat32_same_actions": sum(r["systemone"]["action"] == r["chat_32tokens"]["action"] for r in matched),
             "all_prompt_token_counts_equal": all(len({r[a]["input_tokens"] for a in arms}) == 1 for r in matched),
             "chat32_action_disagreements": [{"id": r["id"], "systemone": r["systemone"]["action"],
                                              "chat32": r["chat_32tokens"]["action"]} for r in matched
                                             if r["systemone"]["action"] != r["chat_32tokens"]["action"]]}
    for name in ("rollout_pilot", "rollout_repeat"):
        if (ROOT / name / "episodes.jsonl").exists():
            audit[name] = rollout_summary(ROOT / name)
    audit["artifact_sha256"] = {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in ROOT.rglob("*.jsonl") if "systemone_chat" in p.name or "episodes" in p.name
    }
    (ROOT / "interface_validation.json").write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in audit.items() if k not in ("rollout_pilot", "rollout_repeat", "artifact_sha256")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
