#!/usr/bin/env python3
"""Tier-3 classifier: TF-IDF + Logistic Regression, trained and evaluated honestly.

Train/test protocol (strict separation):
  - Training data: xTRam1/safe-guard-prompt-injection TRAIN split only
  - In-distribution eval: xTRam1/safe-guard-prompt-injection TEST split (held out)
  - Cross-dataset eval:   deepset/prompt-injections (ALL rows, never seen during training)

The cross-dataset number is the honest generalization estimate.

Saves artifact to benchmark/artifacts/tfidf_lr_classifier.joblib

Usage:
    python benchmark/train_classifier.py
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

BENCHMARK_DIR = Path(__file__).parent
ARTIFACTS_DIR = BENCHMARK_DIR / "artifacts"

SNAPSHOT_DEEPSET = BENCHMARK_DIR / "data" / "deepset_prompt_injections.jsonl"
SNAPSHOT_XTRAM1_TRAIN = BENCHMARK_DIR / "data" / "xtram1_injection_train.jsonl"
SNAPSHOT_XTRAM1_TEST = BENCHMARK_DIR / "data" / "xtram1_injection_test.jsonl"


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _load_jsonl(path: Path) -> tuple[list[str], list[int]]:
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    return [r["text"] for r in rows], [r["label"] for r in rows]


def compute_metrics(predictions: list[int], labels: list[int]) -> dict:
    tp = fp = tn = fn = 0
    for pred, label in zip(predictions, labels):
        if pred and label == 1:
            tp += 1
        elif pred and label == 0:
            fp += 1
        elif not pred and label == 0:
            tn += 1
        else:
            fn += 1

    n = tp + fp + tn + fn
    n_pos = tp + fn
    n_neg = fp + tn

    recall = tp / n_pos if n_pos > 0 else float("nan")
    precision = tp / (tp + fp) if (tp + fp) > 0 else float("nan")
    fpr = fp / n_neg if n_neg > 0 else float("nan")
    f1_denom = precision + recall
    f1 = 2 * precision * recall / f1_denom if (not math.isnan(f1_denom) and f1_denom > 0) else float("nan")

    return {
        "N": n, "N_pos": n_pos, "N_neg": n_neg,
        "TP": tp, "FP": fp, "TN": tn, "FN": fn,
        "recall": recall, "precision": precision, "FPR": fpr, "F1": f1,
    }


def pct(v: float) -> str:
    return "N/A" if math.isnan(v) else f"{v*100:.1f}%"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    # Check imports
    try:
        import joblib
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import Pipeline
        from sklearn.metrics import classification_report
    except ImportError as e:
        print(f"ERROR: missing dependency: {e}", file=sys.stderr)
        print("Run: pip install scikit-learn joblib", file=sys.stderr)
        return 1

    # Check snapshots
    missing = [p for p in [SNAPSHOT_DEEPSET, SNAPSHOT_XTRAM1_TRAIN, SNAPSHOT_XTRAM1_TEST]
               if not p.exists()]
    if missing:
        print("ERROR: missing snapshots:", *[str(p) for p in missing], file=sys.stderr)
        print("Run: python benchmark/fetch_data.py && python benchmark/fetch_second_dataset.py",
              file=sys.stderr)
        return 1

    print("Loading data...")
    train_texts, train_labels = _load_jsonl(SNAPSHOT_XTRAM1_TRAIN)
    test_texts, test_labels = _load_jsonl(SNAPSHOT_XTRAM1_TEST)
    deepset_texts, deepset_labels = _load_jsonl(SNAPSHOT_DEEPSET)

    print(f"  xTRam1 train: {len(train_texts)} rows ({sum(train_labels)} pos)")
    print(f"  xTRam1 test:  {len(test_texts)} rows ({sum(test_labels)} pos)")
    print(f"  deepset:      {len(deepset_texts)} rows ({sum(deepset_labels)} pos)")

    # Build and train pipeline
    print("\nTraining TF-IDF + Logistic Regression on xTRam1 train split...")
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 3),
            max_features=50_000,
            sublinear_tf=True,
            strip_accents="unicode",
            analyzer="word",
            min_df=2,
        )),
        ("clf", LogisticRegression(
            C=1.0,
            max_iter=1000,
            class_weight="balanced",
            solver="lbfgs",
            random_state=42,
        )),
    ])
    pipeline.fit(train_texts, train_labels)
    print("  Training complete.")

    # In-distribution evaluation (xTRam1 test split)
    print("\nEvaluating on xTRam1 test split (in-distribution)...")
    test_preds = list(pipeline.predict(test_texts))
    m_indist = compute_metrics(test_preds, test_labels)

    # Cross-dataset evaluation (deepset, never seen during training)
    print("Evaluating on deepset (cross-dataset, zero-shot generalization)...")
    deepset_preds = list(pipeline.predict(deepset_texts))
    m_cross = compute_metrics(deepset_preds, deepset_labels)

    # Print results
    col_w = 22
    tier_names = ["xTRam1 test (in-dist)", "deepset (cross-dataset)"]
    metrics_list = [m_indist, m_cross]

    header = f"{'Metric':<14}" + "".join(f"{n:>{col_w}}" for n in tier_names)
    sep = "-" * len(header)
    print(f"\n=== Tier 3: TF-IDF + Logistic Regression ===")
    print("  Trained on: xTRam1 train split only")
    print(sep)
    print(header)
    print(sep)
    for key in ("N", "N_pos", "N_neg", "TP", "FP", "TN", "FN"):
        row = f"  {key:<12}" + "".join(f"{m[key]:>{col_w}}" for m in metrics_list)
        print(row)
    for key, label in [("recall", "Recall"), ("precision", "Precision"), ("FPR", "FPR"), ("F1", "F1")]:
        row = f"  {label:<12}" + "".join(f"{pct(m[key]):>{col_w}}" for m in metrics_list)
        print(row)
    print(sep)

    generalization_drop = m_indist["recall"] - m_cross["recall"]
    print(f"\nGeneralization gap (recall): in-dist {pct(m_indist['recall'])} -> "
          f"cross-dataset {pct(m_cross['recall'])} ({generalization_drop*100:+.1f}pp)")

    # Save artifact
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    artifact_path = ARTIFACTS_DIR / "tfidf_lr_classifier.joblib"
    joblib.dump(pipeline, artifact_path)
    print(f"\nSaved classifier artifact to {artifact_path}")

    # Save metrics for MODEL_RESULTS.md
    tier3_metrics = {
        "indist_xtram1_test": m_indist,
        "cross_deepset": m_cross,
        "trained_on": "xTRam1 train split",
        "model": "TF-IDF(1-3gram, 50k) + LogisticRegression(C=1, balanced)",
    }
    (ARTIFACTS_DIR / "tier3_metrics.json").write_text(
        json.dumps(tier3_metrics, indent=2), encoding="utf-8"
    )
    print(f"Saved tier-3 metrics to {ARTIFACTS_DIR / 'tier3_metrics.json'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
