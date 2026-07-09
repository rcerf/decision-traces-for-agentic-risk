# Injection Sentinel — Reproducible Benchmark Results

> These numbers are produced by running the **public, deterministic detector**
> in this repository against a **public, labeled dataset**.  Every number here
> can be reproduced exactly from the commands in the `## Reproduce` section below.

## Dataset

| Field | Value |
|-------|-------|
| Name | `deepset/prompt-injections` |
| Source | https://huggingface.co/datasets/deepset/prompt-injections |
| Splits used | train + test (all rows merged) |
| N | 662 |
| Positives (injection attempts) | 263 |
| Negatives (benign text) | 399 |

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
| N | 662 | 662 |
| Positives in dataset | 263 | 263 |
| Negatives in dataset | 399 | 399 |
| TP | 2 | 0 |
| FP | 0 | 0 |
| TN | 399 | 399 |
| FN | 261 | 263 |
| **Recall** | **0.8%** | **0.0%** |
| **Precision** | **100.0%** | **N/A** |
| **FPR** | **0.0%** | **0.0%** |
| **F1** | **1.5%** | **N/A** |
| Recall 95% CI (Wilson) | [0.2%–2.7%] | [0.0%–1.4%] |
| FPR 95% CI (Wilson) | [0.0%–1.0%] | [0.0%–1.0%] |

**Keyword baseline**: checks for the literal substring `"ignore previous instructions"`
(case-insensitive) only.  It serves as a lower-bound anchor — the simplest prior-art
heuristic in the literature.

## What these numbers mean operationally

The headline here is **recall, not false positives**. On this dataset the sentinel
flags 0.0% of benign text (near-zero false alarms) but catches only
0.8% of injection attempts — it misses 99.2%
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

The keyword baseline (0.0% recall) is the lower-bound anchor: the
simplest literal-match heuristic catches even less.

## Limitations

1. **Small dataset (N=662).** The confidence intervals are wide.
   Recall CI is [0.2%–2.7%]; treat the point estimate as
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
