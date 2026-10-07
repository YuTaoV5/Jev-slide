"""Compare server decision prompt IDs to locally rendered chat IDs."""
import argparse
import hashlib
import json
from pathlib import Path

from compare_systemone_chat import chat_payload, post


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    row = json.loads(args.input.open(encoding="utf-8").readline())
    chat, _ = chat_payload(row, "chat_1token", matched=True)
    question = row["questions"]["action"]
    result, _ = post("/v1/decisions", {
        "input": row["state"],
        "questions": [{"id": "action", "type": "choice", "question": question["instructions"],
                       "options": [{"name": k, "description": v} for k, v in question["criteria"].items()]}],
        "return_prompt_token_ids": True, "chat_template_kwargs": {"enable_thinking": False},
    })
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(args.model_path, local_files_only=True)
    encoded = tokenizer.apply_chat_template(chat["messages"], tokenize=True,
                                            add_generation_prompt=True, enable_thinking=False)
    ids = encoded if isinstance(encoded, list) else encoded["input_ids"]
    if ids and isinstance(ids[0], list):
        ids = ids[0]
    server_ids = result["answers"]["action"]["prompt_token_ids"]
    audit = {"example_id": row["id"], "token_ids_equal": ids == server_ids,
             "tokens": len(ids), "sha256": hashlib.sha256(json.dumps(ids).encode()).hexdigest(),
             "prompt_format_version": result["prompt_format_version"],
             "note": "System One and decisions share the installed _encode_question renderer; local chat IDs match served decision IDs"}
    args.output.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    if ids != server_ids:
        raise ValueError("Decision and chat prompt IDs differ")
    print(json.dumps(audit), flush=True)


if __name__ == "__main__":
    main()
