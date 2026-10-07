"""Fetch only the pinned NanoJev checkpoint and held-out question files."""

import hashlib
import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


BASE = Path("/root/gpufree-data/nanojev_compare")
MANIFEST = BASE / "source/NanoJev-main/results/huggingface_unified_public_release.json"
RELEASE = json.loads(MANIFEST.read_text())
MODEL_FILES = {"best.safetensors", "config.json", "backbone_config/config.json"}
MODEL_FILES.update(
    row["path"] for row in RELEASE["model"]["files"] if row["path"].startswith("tokenizer/")
)
DATA_FILES = {"unified/hard/test.jsonl", "unified/hard/ood.jsonl"}
JOBS = []
for kind, paths, repo, dest in [
    ("model", MODEL_FILES, "C-Tianyu/NanoJev", BASE / "models/NanoJev-unified"),
    (
        "dataset",
        DATA_FILES,
        "datasets/C-Tianyu/NanoJev-Data",
        BASE / "data/NanoJev-unified",
    ),
]:
    manifest_rows = {row["path"]: row for row in RELEASE[kind]["files"]}
    for path in sorted(paths):
        JOBS.append((manifest_rows[path], repo, dest))


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(job):
    row, repo, dest = job
    path = dest / row["path"]
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size == row["bytes"] and sha256(path) == row["sha256"]:
        return row["path"], "existing"
    partial = path.with_name(path.name + ".part")
    url = f"https://hf-mirror.com/{repo}/resolve/unified-games-v1/{row['path']}"
    for attempt in range(6):
        try:
            start = partial.stat().st_size if partial.exists() else 0
            headers = {"User-Agent": "NanoJev-reproduction/1.0"}
            if start:
                headers["Range"] = f"bytes={start}-"
            with urllib.request.urlopen(
                urllib.request.Request(url, headers=headers), timeout=90
            ) as response:
                if start and response.status != 206:
                    raise RuntimeError(f"resume status {response.status}")
                with partial.open("ab" if start else "wb") as output:
                    for chunk in iter(lambda: response.read(4 * 1024 * 1024), b""):
                        output.write(chunk)
            if partial.stat().st_size != row["bytes"]:
                raise RuntimeError("size mismatch")
            if sha256(partial) != row["sha256"]:
                raise RuntimeError("SHA256 mismatch")
            partial.replace(path)
            return row["path"], "downloaded"
        except Exception as exc:
            print("RETRY", row["path"], attempt + 1, type(exc).__name__, str(exc), flush=True)
            time.sleep(min(2**attempt, 30))
    raise RuntimeError(f"failed: {row['path']}")


if __name__ == "__main__":
    print("JOBS", [(row["path"], row["bytes"]) for row, _, _ in JOBS], flush=True)
    with ThreadPoolExecutor(max_workers=3) as pool:
        for future in as_completed([pool.submit(fetch, job) for job in JOBS]):
            print("DONE", *future.result(), flush=True)
    print("ALL_ASSETS_VERIFIED", flush=True)
