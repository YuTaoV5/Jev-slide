"""Execute paired, fresh navigation episodes with System One and chat.

Uses the unchanged NanoJev unified environment and its public observation
renderer. Each arm resets the exact same case and seed; later observations may
diverge as a consequence of its own actions. No teacher or oracle is queried.
"""
import argparse
import collections
import hashlib
import json
import sys
import time
from pathlib import Path

from compare_systemone_chat import run_arm


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def episode(case, arm, LocalEnvironments, policy_request):
    envs = LocalEnvironments()
    steps = []
    started = time.perf_counter()
    try:
        current = envs.reset([case])[case["id"]]
        initial_hash = digest(current["observation"])
        while not current["info"]["terminated"]:
            observation = current["observation"]
            request = policy_request(observation, case["id"])
            candidates = observation["candidates"]
            if len(candidates) == 1:
                response = {"action": next(iter(candidates)), "latency_s": 0.0, "forced": True}
            else:
                response = run_arm(request, arm, matched=True)
                response["forced"] = False
            if response["action"] not in candidates:
                return {"case": case, "arm": arm, "success": False, "complete": False,
                        "initial_observation_sha256": initial_hash,
                        "error": "invalid_model_action", "response": response, "steps": steps}
            transition = envs.step({case["id"]: response["action"]})[case["id"]]
            steps.append({"observation_sha256": digest(observation),
                          "physical_step_before": observation["step"],
                          "candidates": list(candidates), "response": response,
                          "reward": transition["reward"],
                          "physical_steps_this_action": transition["info"]["physical_steps_this_action"]})
            if transition["truncated"]:
                raise RuntimeError("Unexpected external truncation")
            current = transition
        return {"case": case, "arm": arm, "success": current["info"]["success"],
                "complete": True, "initial_observation_sha256": initial_hash,
                "elapsed_s": time.perf_counter() - started,
                "final_info": current["info"], "steps": steps}
    finally:
        envs.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit-per-variant", type=int, default=1)
    parser.add_argument("--variants", default="maze8,maze16,snake8,snake12")
    parser.add_argument("--arms", default="systemone,chat_1token")
    args = parser.parse_args()
    sys.path.insert(0, str(args.source / "scripts"))
    from unified_game_pipeline import LocalEnvironments, policy_request, read_rows
    cases = read_rows(args.cases)
    variants = set(args.variants.split(","))
    groups = collections.defaultdict(list)
    for case in cases:
        if case["split"] in ("test", "ood") and case["variant"] in variants:
            groups[(case["split"], case["variant"])].append(case)
    selected = []
    for key, group in sorted(groups.items()):
        group.sort(key=lambda x: digest(x["id"]))
        selected.extend(group[:args.limit_per_variant] if args.limit_per_variant else group)
    arms = args.arms.split(",")
    args.output.mkdir(parents=True, exist_ok=True)
    target = args.output / "episodes.jsonl"
    if target.exists():
        raise ValueError("Use a fresh output directory")
    manifest = {"selected_cases": selected, "cases_sha256": hashlib.sha256(args.cases.read_bytes()).hexdigest(),
                "arms": arms, "prompt": "same installed System One renderer, thinking disabled",
                "controller": "greedy; singletons executed by code for every arm",
                "budget": "identical physical action deadline from unchanged case specification",
                "source_sha256": {name: hashlib.sha256((args.source / "scripts" / name).read_bytes()).hexdigest()
                                  for name in ("unified_game_pipeline.py", "unified_grid_envs.py", "scaled_maze.py", "snake_game.py")},
                "finished": False}
    manifest_path = args.output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    episodes = []
    with target.open("w", encoding="utf-8") as stream:
        for index, case in enumerate(selected):
            for arm in arms[index % len(arms):] + arms[:index % len(arms)]:
                result = episode(case, arm, LocalEnvironments, policy_request)
                episodes.append(result)
                stream.write(json.dumps(result, ensure_ascii=False) + "\n")
                stream.flush()
                print("EPISODE", case["id"], arm, "success", result["success"], "steps", len(result["steps"]), flush=True)
    by_case = collections.defaultdict(list)
    for result in episodes:
        by_case[result["case"]["id"]].append(result)
    for values in by_case.values():
        if len({x["initial_observation_sha256"] for x in values}) != 1:
            raise ValueError("Paired arms have different initial observations")
    summary = {}
    for arm in arms:
        values = [x for x in episodes if x["arm"] == arm]
        summary[arm] = {"episodes": len(values), "successes": sum(x["success"] for x in values),
                        "complete": sum(x["complete"] for x in values),
                        "physical_steps": sum(x.get("final_info", {}).get("episode_metrics", {}).get("physical_steps", 0) for x in values),
                        "model_calls": sum(not s["response"]["forced"] for x in values for s in x["steps"]),
                        "model_latency_s": sum(s["response"]["latency_s"] for x in values for s in x["steps"])}
    manifest.update(finished=True, summary=summary)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print("COMPLETE", json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
