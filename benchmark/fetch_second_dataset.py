#!/usr/bin/env python3
"""Download xTRam1/safe-guard-prompt-injection and write a labeled JSONL snapshot.

Dataset: https://huggingface.co/datasets/xTRam1/safe-guard-prompt-injection
License: Not explicitly stated; dataset is publicly accessible and ungated.
Format: text (str) + label (int, 0=benign, 1=injection)

Splits: train (8236 rows) and test (2060 rows) are kept SEPARATE so the training
classifier in train_classifier.py can use the train split only, with the test
split held out strictly for evaluation.

Contamination note: xTRam1 is DISTINCT from deepset/prompt-injections and was NOT
used to train protectai/deberta-v3-base-prompt-injection-v2 (which the ProtectAI
team documented as trained primarily on deepset + internal data). This makes it the
better estimate of the open model's true generalization performance.

Usage:
    python benchmark/fetch_second_dataset.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

OUTPUT_TRAIN = Path(__file__).parent / "data" / "xtram1_injection_train.jsonl"
OUTPUT_TEST = Path(__file__).parent / "data" / "xtram1_injection_test.jsonl"

DATASET_URL = "https://huggingface.co/datasets/xTRam1/safe-guard-prompt-injection"


def main() -> int:
    try:
        from datasets import load_dataset  # type: ignore[import-not-found]
    except ImportError:
        print(
            "ERROR: 'datasets' library not installed. Run: pip install datasets",
            file=sys.stderr,
        )
        return 1

    print(f"Downloading xTRam1/safe-guard-prompt-injection from {DATASET_URL} ...")
    try:
        ds = load_dataset("xTRam1/safe-guard-prompt-injection")
    except Exception as exc:
        print(f"ERROR: download failed: {exc}", file=sys.stderr)
        return 1

    OUTPUT_TRAIN.parent.mkdir(parents=True, exist_ok=True)

    for split_name, output_path in [("train", OUTPUT_TRAIN), ("test", OUTPUT_TEST)]:
        split = ds[split_name]
        rows = [
            {"text": row["text"], "label": row["label"], "split": split_name}
            for row in split
        ]
        output_path.write_text(
            "\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8"
        )
        n_pos = sum(1 for r in rows if r["label"] == 1)
        n_neg = sum(1 for r in rows if r["label"] == 0)
        print(
            f"  {split_name}: {len(rows)} rows -> {output_path.name}"
            f"  (pos={n_pos}, neg={n_neg})"
        )

    print(f"\nSource: {DATASET_URL}")
    print("Train split is used for classifier training only.")
    print("Test split is held out for all evaluations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
