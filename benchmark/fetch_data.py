#!/usr/bin/env python3
"""Download the deepset/prompt-injections dataset and write a labeled JSONL snapshot.

The snapshot makes the benchmark reproducible offline without re-downloading.
Both train and test splits are merged so the benchmark runs over all 662 rows.

Usage:
    python benchmark/fetch_data.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

OUTPUT = Path(__file__).parent / "data" / "deepset_prompt_injections.jsonl"


def main() -> int:
    try:
        from datasets import load_dataset  # type: ignore[import-not-found]
    except ImportError:
        print(
            "ERROR: 'datasets' library not installed. Run: pip install datasets",
            file=sys.stderr,
        )
        return 1

    print("Downloading deepset/prompt-injections from Hugging Face Hub...")
    try:
        train = load_dataset("deepset/prompt-injections", split="train")
        test = load_dataset("deepset/prompt-injections", split="test")
    except Exception as exc:
        print(f"ERROR: download failed: {exc}", file=sys.stderr)
        return 1

    rows_train = [{"text": row["text"], "label": row["label"], "split": "train"} for row in train]
    rows_test = [{"text": row["text"], "label": row["label"], "split": "test"} for row in test]
    rows = rows_train + rows_test

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")

    n_pos = sum(1 for r in rows if r["label"] == 1)
    n_neg = sum(1 for r in rows if r["label"] == 0)
    print(
        f"Wrote {len(rows)} rows to {OUTPUT}\n"
        f"  positives (injection): {n_pos}\n"
        f"  negatives (benign):    {n_neg}\n"
        f"  source: https://huggingface.co/datasets/deepset/prompt-injections"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
