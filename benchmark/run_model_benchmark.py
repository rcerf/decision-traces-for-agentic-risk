#!/usr/bin/env python3
"""Full-tier injection detection benchmark: keyword / regex / open-model.

Evaluates three tiers on two datasets:
  Dataset A: deepset/prompt-injections (662 rows, merged train+test)
  Dataset B: xTRam1/safe-guard-prompt-injection test split (2060 rows)

Tiers:
  0  Keyword baseline  — literal substring "ignore previous instructions"
  1  Regex sentinel    — six-pattern deterministic detector (this repo)
  2  ProtectAI model   — protectai/deberta-v3-base-prompt-injection-v2

Computes TP/FP/TN/FN, recall, precision, FPR, F1, N per cell.
Writes benchmark/MODEL_RESULTS.md (partial — train_classifier.py fills Tier 3).

Usage:
    python benchmark/run_model_benchmark.py
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_DIR = Path(__file__).parent
SENTINEL_PATH = REPO_ROOT / "studies" / "anima-risk-sentinel" / "src" / "risk_sentinel.py"

SNAPSHOT_A = BENCHMARK_DIR / "data" / "deepset_prompt_injections.jsonl"
SNAPSHOT_B_TEST = BENCHMARK_DIR / "data" / "xtram1_injection_test.jsonl"

ARTIFACTS_DIR = BENCHMARK_DIR / "artifacts"


# ---------------------------------------------------------------------------
# Sentinel loader
# ---------------------------------------------------------------------------

def _load_sentinel():
    spec = importlib.util.spec_from_file_location("risk_sentinel", SENTINEL_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["risk_sentinel"] = mod
    spec.loader.exec_module(mod)
    return mod


def sentinel_pred(sentinel, text: str) -> bool:
    return bool(sentinel.matches_any(sentinel.normalize(text), sentinel.PROMPT_INJECTION_PATTERNS))


def keyword_pred(text: str) -> bool:
    return "ignore previous instructions" in text.lower()


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def compute_metrics(predictions: list[bool], labels: list[int]) -> dict:
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

    def wilson_ci(p: float, n_trials: int) -> tuple[float, float]:
        if n_trials == 0 or math.isnan(p):
            return float("nan"), float("nan")
        z = 1.96
        denom = 1 + z**2 / n_trials
        centre = (p + z**2 / (2 * n_trials)) / denom
        margin = z * math.sqrt(p * (1 - p) / n_trials + z**2 / (4 * n_trials**2)) / denom
        return max(0.0, centre - margin), min(1.0, centre + margin)

    recall_lo, recall_hi = wilson_ci(recall, n_pos)
    fpr_lo, fpr_hi = wilson_ci(fpr, n_neg)

    return {
        "N": n, "N_pos": n_pos, "N_neg": n_neg,
        "TP": tp, "FP": fp, "TN": tn, "FN": fn,
        "recall": recall, "precision": precision, "FPR": fpr, "F1": f1,
        "recall_95ci": (recall_lo, recall_hi),
        "FPR_95ci": (fpr_lo, fpr_hi),
    }


def pct(v: float) -> str:
    return "N/A" if math.isnan(v) else f"{v*100:.1f}%"


def ci_str(lo: float, hi: float) -> str:
    return "N/A" if math.isnan(lo) else f"[{lo*100:.1f}%–{hi*100:.1f}%]"


# ---------------------------------------------------------------------------
# Load datasets
# ---------------------------------------------------------------------------

def _load_jsonl(path: Path) -> tuple[list[str], list[int]]:
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    return [r["text"] for r in rows], [r["label"] for r in rows]


# ---------------------------------------------------------------------------
# Print table
# ---------------------------------------------------------------------------

TIER_NAMES = ["Keyword", "Regex", "ProtectAI-DeBERTa"]


def print_table(dataset_name: str, metrics_list: list[dict]) -> None:
    col_w = 22
    header = f"{'Metric':<16}" + "".join(f"{n:>{col_w}}" for n in TIER_NAMES)
    sep = "-" * len(header)
    print(f"\n=== {dataset_name} ===")
    print(sep)
    print(header)
    print(sep)
    for key in ("N", "N_pos", "N_neg", "TP", "FP", "TN", "FN"):
        row = f"  {key:<14}" + "".join(f"{m[key]:>{col_w}}" for m in metrics_list)
        print(row)
    for key, label in [("recall", "Recall"), ("precision", "Precision"), ("FPR", "FPR"), ("F1", "F1")]:
        row = f"  {label:<14}" + "".join(f"{pct(m[key]):>{col_w}}" for m in metrics_list)
        print(row)
    recall_row = f"  {'Recall 95% CI':<14}" + "".join(
        f"{ci_str(*m['recall_95ci']):>{col_w}}" for m in metrics_list
    )
    print(recall_row)
    print(sep)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    # Check snapshots exist
    missing = [p for p in [SNAPSHOT_A, SNAPSHOT_B_TEST] if not p.exists()]
    if missing:
        print("ERROR: missing snapshots:", *missing, file=sys.stderr)
        print("Run: python benchmark/fetch_data.py && python benchmark/fetch_second_dataset.py",
              file=sys.stderr)
        return 1

    print("Loading datasets...")
    texts_a, labels_a = _load_jsonl(SNAPSHOT_A)
    texts_b, labels_b = _load_jsonl(SNAPSHOT_B_TEST)
    print(f"  Dataset A (deepset): {len(texts_a)} rows")
    print(f"  Dataset B (xTRam1 test): {len(texts_b)} rows")

    print("\nLoading regex sentinel...")
    sentinel = _load_sentinel()

    print("Running keyword and regex tiers on Dataset A...")
    kw_preds_a = [keyword_pred(t) for t in texts_a]
    rx_preds_a = [sentinel_pred(sentinel, t) for t in texts_a]

    print("Running keyword and regex tiers on Dataset B...")
    kw_preds_b = [keyword_pred(t) for t in texts_b]
    rx_preds_b = [sentinel_pred(sentinel, t) for t in texts_b]

    print("\nLoading ProtectAI DeBERTa model (CPU, may take ~30s)...")
    # Import locally so the file can be imported without torch
    sys.path.insert(0, str(BENCHMARK_DIR))
    from model_sentinel import ModelSentinel
    model = ModelSentinel(device=-1)

    print("Running model tier on Dataset A...")
    model_results_a = model.predict_batch(texts_a, batch_size=16)
    ml_preds_a = [r["is_injection"] for r in model_results_a]

    print("Running model tier on Dataset B...")
    model_results_b = model.predict_batch(texts_b, batch_size=16)
    ml_preds_b = [r["is_injection"] for r in model_results_b]

    # Compute metrics
    m_kw_a = compute_metrics(kw_preds_a, labels_a)
    m_rx_a = compute_metrics(rx_preds_a, labels_a)
    m_ml_a = compute_metrics(ml_preds_a, labels_a)

    m_kw_b = compute_metrics(kw_preds_b, labels_b)
    m_rx_b = compute_metrics(rx_preds_b, labels_b)
    m_ml_b = compute_metrics(ml_preds_b, labels_b)

    # Print tables
    print_table("Dataset A — deepset/prompt-injections (N=662, train+test merged)", [m_kw_a, m_rx_a, m_ml_a])
    print_table("Dataset B — xTRam1/safe-guard-prompt-injection test split (N=2060)", [m_kw_b, m_rx_b, m_ml_b])

    # Save raw metrics for MODEL_RESULTS.md
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    metrics_payload = {
        "deepset": {"keyword": m_kw_a, "regex": m_rx_a, "protectai": m_ml_a},
        "xtram1_test": {"keyword": m_kw_b, "regex": m_rx_b, "protectai": m_ml_b},
    }
    (ARTIFACTS_DIR / "tier_metrics.json").write_text(
        json.dumps(metrics_payload, indent=2), encoding="utf-8"
    )
    print(f"\nSaved raw metrics to {ARTIFACTS_DIR / 'tier_metrics.json'}")

    # Note contamination observation
    recall_gap = m_ml_a["recall"] - m_ml_b["recall"]
    print(f"\nContamination signal: ProtectAI recall on deepset={pct(m_ml_a['recall'])}, "
          f"xTRam1={pct(m_ml_b['recall'])}, gap={recall_gap*100:+.1f}pp")
    print("(A large positive gap is evidence that deepset was in the model's training data.)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
