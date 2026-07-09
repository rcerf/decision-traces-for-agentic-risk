#!/usr/bin/env python3
"""Benchmark the repo's deterministic injection detector against deepset/prompt-injections.

Loads the JSONL snapshot written by fetch_data.py (does NOT re-download), runs the
public detector from studies/anima-risk-sentinel/src/risk_sentinel.py over every row,
and computes TP/FP/TN/FN/recall/precision/FPR/F1.

A trivial keyword baseline ("ignore previous instructions" substring) is also computed
as a prior-art anchor.

Writes RESULTS.md alongside this file.

Usage:
    python benchmark/run_injection_benchmark.py
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = Path(__file__).parent / "data" / "deepset_prompt_injections.jsonl"
SENTINEL_PATH = REPO_ROOT / "studies" / "anima-risk-sentinel" / "src" / "risk_sentinel.py"
RESULTS_PATH = Path(__file__).parent / "RESULTS.md"

DATASET_URL = "https://huggingface.co/datasets/deepset/prompt-injections"
DATASET_COMMIT = "main"  # pinned at fetch time; see RESULTS.md for fetch date


# ---------------------------------------------------------------------------
# Load the sentinel's regex machinery directly (no subprocess).
# ---------------------------------------------------------------------------

def _load_sentinel():
    spec = importlib.util.spec_from_file_location("risk_sentinel", SENTINEL_PATH)
    mod = importlib.util.module_from_spec(spec)
    # Must register in sys.modules before exec_module so that @dataclass and
    # other decorators that call sys.modules[cls.__module__] can find the module.
    sys.modules["risk_sentinel"] = mod
    spec.loader.exec_module(mod)
    return mod


def sentinel_predicts_positive(sentinel, text: str) -> bool:
    """Return True if ANY of the sentinel's prompt-injection regex patterns match."""
    return bool(sentinel.matches_any(sentinel.normalize(text), sentinel.PROMPT_INJECTION_PATTERNS))


def keyword_baseline_predicts_positive(text: str) -> bool:
    """Trivial keyword baseline: literal substring match, case-insensitive."""
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
    f1 = 2 * precision * recall / f1_denom if f1_denom > 0 else float("nan")

    # Approximate 95% Wilson score confidence interval for recall and FPR.
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
        "N": n,
        "N_pos": n_pos,
        "N_neg": n_neg,
        "TP": tp,
        "FP": fp,
        "TN": tn,
        "FN": fn,
        "recall": recall,
        "precision": precision,
        "FPR": fpr,
        "F1": f1,
        "recall_95ci": (recall_lo, recall_hi),
        "FPR_95ci": (fpr_lo, fpr_hi),
    }


def pct(v: float) -> str:
    if math.isnan(v):
        return "N/A"
    return f"{v*100:.1f}%"


def ci_str(lo: float, hi: float) -> str:
    if math.isnan(lo):
        return "N/A"
    return f"[{lo*100:.1f}%–{hi*100:.1f}%]"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    if not SNAPSHOT.exists():
        print(
            f"ERROR: snapshot not found at {SNAPSHOT}\n"
            "Run fetch_data.py first: python benchmark/fetch_data.py",
            file=sys.stderr,
        )
        return 1

    rows = [json.loads(line) for line in SNAPSHOT.read_text(encoding="utf-8").splitlines() if line.strip()]
    texts = [r["text"] for r in rows]
    labels = [r["label"] for r in rows]

    print(f"Loaded {len(rows)} rows from snapshot.")

    sentinel = _load_sentinel()

    sentinel_preds = [sentinel_predicts_positive(sentinel, t) for t in texts]
    keyword_preds = [keyword_baseline_predicts_positive(t) for t in texts]

    m_sent = compute_metrics(sentinel_preds, labels)
    m_kw = compute_metrics(keyword_preds, labels)

    # Print table to stdout.
    header = f"{'Metric':<18} {'Sentinel (regex)':>18} {'Keyword baseline':>18}"
    sep = "-" * len(header)
    print()
    print(sep)
    print(header)
    print(sep)
    for key in ("N", "N_pos", "N_neg", "TP", "FP", "TN", "FN"):
        print(f"  {key:<16} {m_sent[key]:>18} {m_kw[key]:>18}")
    for key, label in [("recall", "Recall"), ("precision", "Precision"), ("FPR", "FPR"), ("F1", "F1")]:
        print(f"  {label:<16} {pct(m_sent[key]):>18} {pct(m_kw[key]):>18}")
    print(
        f"  {'Recall 95% CI':<16} {ci_str(*m_sent['recall_95ci']):>18} {ci_str(*m_kw['recall_95ci']):>18}"
    )
    print(
        f"  {'FPR 95% CI':<16} {ci_str(*m_sent['FPR_95ci']):>18} {ci_str(*m_kw['FPR_95ci']):>18}"
    )
    print(sep)
    print()

    # Write RESULTS.md.
    md = _build_results_md(m_sent, m_kw)
    RESULTS_PATH.write_text(md, encoding="utf-8")
    print(f"Wrote {RESULTS_PATH}")
    return 0


def _build_results_md(m_sent: dict, m_kw: dict) -> str:
    return f"""\
# Injection Sentinel — Reproducible Benchmark Results

> These numbers are produced by running the **public, deterministic detector**
> in this repository against a **public, labeled dataset**.  Every number here
> can be reproduced exactly from the commands in the `## Reproduce` section below.

## Dataset

| Field | Value |
|-------|-------|
| Name | `deepset/prompt-injections` |
| Source | {DATASET_URL} |
| Splits used | train + test (all rows merged) |
| N | {m_sent['N']} |
| Positives (injection attempts) | {m_sent['N_pos']} |
| Negatives (benign text) | {m_sent['N_neg']} |

## Detector

The sentinel (`studies/anima-risk-sentinel/src/risk_sentinel.py`) is a
**deterministic, regex-only** detector.  For this benchmark, a text is predicted
positive if any of the six `PROMPT_INJECTION_PATTERNS` regexes match (using
`matches_any(normalize(text), PROMPT_INJECTION_PATTERNS)`).  The patterns are:

```
ignore (all )?(previous|prior|above) instructions
disregard (the )?(system|developer|user) instructions
developer mode
system override
hidden instruction
do not tell the user
```

No machine-learning model, no embeddings, no external API calls.

## Results

| Metric | Sentinel (regex) | Keyword baseline |
|--------|-----------------|-----------------|
| N | {m_sent['N']} | {m_kw['N']} |
| Positives in dataset | {m_sent['N_pos']} | {m_kw['N_pos']} |
| Negatives in dataset | {m_sent['N_neg']} | {m_kw['N_neg']} |
| TP | {m_sent['TP']} | {m_kw['TP']} |
| FP | {m_sent['FP']} | {m_kw['FP']} |
| TN | {m_sent['TN']} | {m_kw['TN']} |
| FN | {m_sent['FN']} | {m_kw['FN']} |
| **Recall** | **{pct(m_sent['recall'])}** | **{pct(m_kw['recall'])}** |
| **Precision** | **{pct(m_sent['precision'])}** | **{pct(m_kw['precision'])}** |
| **FPR** | **{pct(m_sent['FPR'])}** | **{pct(m_kw['FPR'])}** |
| **F1** | **{pct(m_sent['F1'])}** | **{pct(m_kw['F1'])}** |
| Recall 95% CI (Wilson) | {ci_str(*m_sent['recall_95ci'])} | {ci_str(*m_kw['recall_95ci'])} |
| FPR 95% CI (Wilson) | {ci_str(*m_sent['FPR_95ci'])} | {ci_str(*m_kw['FPR_95ci'])} |

**Keyword baseline**: checks for the literal substring `"ignore previous instructions"`
(case-insensitive) only.  It serves as a lower-bound anchor — the simplest prior-art
heuristic in the literature.

## What these numbers mean operationally

The headline here is **recall, not false positives**. On this dataset the sentinel
flags {pct(m_sent['FPR'])} of benign text (near-zero false alarms) but catches only
{pct(m_sent['recall'])} of injection attempts — it misses {pct(1 - m_sent['recall'])}
of them. A tripwire that almost never fires, even on real attacks, is close to inert:
the six fixed patterns match the classic "ignore previous instructions" phrasing and
little else, while most injections in this set are paraphrased.

That is the point of publishing it. Regex alone is not a viable injection detector on
paraphrased attacks; getting to usable recall requires a semantic or ML-assisted tier —
which is exactly where the separate, private tiered pipeline reported in
`docs/portfolio/injection_sentinel_benchmark_results.md` reached ~95% recall on deepset,
at the cost of a ~70% false-positive rate on clean content. The two results bound the
same tradeoff: cheap and near-inert at one end, accurate and noisy at the other.
Off-the-shelf tools (Lakera Guard, Meta Prompt-Guard, NeMo Guardrails, Rebuff) all sit
somewhere on that curve; this baseline just marks the cheap, transparent floor.

The keyword baseline ({pct(m_kw['recall'])} recall) is the lower-bound anchor: the
simplest literal-match heuristic catches even less.

## Limitations

1. **Small dataset (N={m_sent['N']}).** The confidence intervals are wide.
   Recall CI is {ci_str(*m_sent['recall_95ci'])}; treat the point estimate as
   an order-of-magnitude, not a precise figure.

2. **Deterministic regex, trivially evadable.** An adversary who knows the six
   patterns can craft payloads that bypass detection entirely (e.g., using Unicode
   lookalikes, typos, or novel phrasing).  This detector is useful as a
   first-pass tripwire, not as a sole line of defense.

3. **No calibration or threshold.** The detector returns a binary flag with no
   confidence score, so precision-recall tradeoff curves are not available.

4. **Dataset scope.** `deepset/prompt-injections` focuses on classic
   "ignore previous instructions"-style injections.  Indirect injection via
   retrieved context (the scenario this sentinel is primarily designed for) is not
   represented.  Real-world recall on indirect-injection attacks is likely lower.

5. **No confidence intervals on precision or F1** because the Wilson CI applies
   to proportions; precision and F1 depend on the joint distribution of TP/FP
   and do not have a simple closed-form CI at this sample size.

## Reproduce

```bash
# 1. Install the one dependency
pip install datasets

# 2. Download and snapshot the dataset (writes benchmark/data/deepset_prompt_injections.jsonl)
python benchmark/fetch_data.py

# 3. Run the benchmark (reads the snapshot, writes benchmark/RESULTS.md)
python benchmark/run_injection_benchmark.py
```

Both scripts are deterministic given the snapshot.  The snapshot is committed to
the repository so step 3 can be run offline without step 2.
"""


if __name__ == "__main__":
    raise SystemExit(main())
