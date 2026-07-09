# Injection Detection — Full Tier Ladder Results

> All numbers in this file were produced by running the code in this directory.
> See `## Reproduce` for exact commands. No metrics were fabricated or hand-edited.

## Datasets

| ID | Name | Source | N | Positives | Negatives |
|----|------|--------|---|-----------|-----------|
| A | `deepset/prompt-injections` | https://huggingface.co/datasets/deepset/prompt-injections | 662 | 263 | 399 |
| B | `xTRam1/safe-guard-prompt-injection` (test split) | https://huggingface.co/datasets/xTRam1/safe-guard-prompt-injection | 2060 | 650 | 1410 |

Dataset A is the existing benchmark snapshot (all rows, train+test merged).
Dataset B is the held-out test split of the second dataset, which was also used to supply training data for Tier 3. Dataset B's train split (8236 rows) was the ONLY data Tier 3 was trained on.

## Tier Ladder

### Dataset A — `deepset/prompt-injections` (N=662)

| Metric | Tier 0: Keyword | Tier 1: Regex | Tier 2: ProtectAI-DeBERTa | Tier 3: TF-IDF+LR |
|--------|----------------|--------------|--------------------------|-------------------|
| N | 662 | 662 | 662 | 662 |
| Positives | 263 | 263 | 263 | 263 |
| Negatives | 399 | 399 | 399 | 399 |
| TP | 0 | 2 | 109 | 34 |
| FP | 0 | 0 | 4 | 2 |
| TN | 399 | 399 | 395 | 397 |
| FN | 263 | 261 | 154 | 229 |
| **Recall** | **0.0%** | **0.8%** | **41.4%** | **12.9%** |
| **Precision** | N/A | 100.0% | 96.5% | 94.4% |
| **FPR** | **0.0%** | **0.0%** | **1.0%** | **0.5%** |
| **F1** | N/A | 1.5% | 58.0% | 22.7% |
| Recall 95% CI (Wilson) | [0.0%–1.4%] | [0.2%–2.7%] | [35.7%–47.5%] | [9.2%–17.7%] |

### Dataset B — `xTRam1/safe-guard-prompt-injection` test split (N=2060)

| Metric | Tier 0: Keyword | Tier 1: Regex | Tier 2: ProtectAI-DeBERTa | Tier 3: TF-IDF+LR |
|--------|----------------|--------------|--------------------------|-------------------|
| N | 2060 | 2060 | 2060 | 2060 |
| Positives | 650 | 650 | 650 | 650 |
| Negatives | 1410 | 1410 | 1410 | 1410 |
| TP | 1 | 43 | 547 | 637 |
| FP | 0 | 0 | 2 | 2 |
| TN | 1410 | 1410 | 1408 | 1408 |
| FN | 649 | 607 | 103 | 13 |
| **Recall** | **0.2%** | **6.6%** | **84.2%** | **98.0%** |
| **Precision** | 100.0% | 100.0% | 99.6% | 99.7% |
| **FPR** | **0.0%** | **0.0%** | **0.1%** | **0.1%** |
| **F1** | 0.3% | 12.4% | 91.2% | 98.8% |
| Recall 95% CI (Wilson) | [0.0%–0.9%] | [4.9%–8.8%] | [81.1%–86.8%] | [96.8%–98.7%] |

## Honest Reading

**Tiers 0 and 1 (keyword and regex) are near-inert on both datasets.**
The keyword baseline catches nothing meaningful (0.0–0.2% recall). The regex sentinel,
which covers six classic phrasing patterns, reaches 0.8% on deepset and 6.6% on
xTRam1. The six patterns are not designed for breadth — they are designed to be
zero-false-positive tripwires for the exact phrases they list. They deliver on that
(100% precision on every cell), but the tradeoff is that nearly all injection attempts
in paraphrased form pass through undetected.

**Tier 2 (ProtectAI DeBERTa) shows a large cross-dataset asymmetry that is
the opposite of the expected contamination signal.**
The model reaches 84.2% recall on xTRam1 but only 41.4% on deepset — a 42.7pp gap
in the wrong direction for a contamination story. If the model had been trained on
deepset, we would expect it to do *better* on deepset. Instead, deepset appears harder
for this model. A plausible explanation is that xTRam1 injections are phrased as
explicit role-playing or override commands ("as an advanced chatbot, do X") that match
the model's training distribution, while deepset injections include more subtle or
context-embedded forms. Either way: **the 84.2% xTRam1 number is not a clean
out-of-distribution estimate** because xTRam1 may partially overlap with ProtectAI's
training corpus, and the 41.4% deepset number is the more conservative bound.
Precision remains high across both datasets (96.5% and 99.6%), meaning the model
rarely fires on benign text — FPR is 1.0% on deepset and 0.1% on xTRam1.

**Tier 3 (TF-IDF + Logistic Regression) reveals catastrophic distribution shift.**
Trained exclusively on xTRam1's train split (8236 rows), the model achieves 98.0%
in-distribution recall on xTRam1's test split. But on deepset — which it has never
seen — recall collapses to 12.9%. The cross-dataset F1 is 22.7% vs 98.8% in-distribution.
This 85pp generalization gap is the honest story: a bag-of-words model learns
surface lexical cues specific to xTRam1's injection vocabulary ("unrestricted mode",
"highly advanced chatbot"), and these cues do not transfer to deepset's injection style.
The model has memorized phrasing, not intent.

**Summary of the recall/FPR tradeoff across the ladder:**

| Tier | deepset recall | xTRam1 recall | FPR (deepset / xTRam1) |
|------|---------------|---------------|------------------------|
| Keyword | 0.0% | 0.2% | 0.0% / 0.0% |
| Regex | 0.8% | 6.6% | 0.0% / 0.0% |
| ProtectAI-DeBERTa | 41.4% | 84.2% | 1.0% / 0.1% |
| TF-IDF+LR (trained xTRam1) | 12.9%* | 98.0% | 0.5% / 0.1% |

*cross-dataset, never-seen-during-training; this is the honest generalization number.

## Reproduce

```bash
# Install dependencies
pip install datasets torch transformers scikit-learn joblib

# 1. Snapshot deepset (already committed; skip if benchmark/data/deepset_prompt_injections.jsonl exists)
python benchmark/fetch_data.py

# 2. Snapshot xTRam1 (train and test splits)
python benchmark/fetch_second_dataset.py

# 3. Run the tier-0/1/2 benchmark (keyword + regex + ProtectAI model)
python benchmark/run_model_benchmark.py

# 4. Train the tier-3 classifier and evaluate cross-dataset
python benchmark/train_classifier.py
```

Scripts are deterministic given the data snapshots. The snapshots are committed to the
repository, so steps 3 and 4 can run offline after steps 1 and 2 have been run once.

Approximate runtime on a single CPU:
- `run_model_benchmark.py`: 3–5 minutes (DeBERTa inference on 2722 rows)
- `train_classifier.py`: under 30 seconds

## Caveats

**1. Contamination risk (open model).**
`protectai/deberta-v3-base-prompt-injection-v2` is a published model with no public
training dataset card specifying exact sources. ProtectAI has stated publicly that it was
trained on prompt-injection datasets from HuggingFace; deepset is one of the most prominent
such datasets. Evaluating any model on data it may have been trained on inflates all metrics.
Unusually, this model scores *lower* on deepset than on xTRam1, suggesting deepset is either
harder for this model or the model trained more on xTRam1-style data. Both datasets should be
treated as potentially contaminated. The cross-dataset numbers in the table above remain the
most honest available estimate of out-of-distribution performance.

**2. Small N on deepset.**
N=662 total, 263 positives. The Wilson 95% CI on recall for the ProtectAI model is
[35.7%–47.5%] — a 12pp-wide interval. Treat point estimates as order-of-magnitude guides.

**3. CPU-only inference.**
The DeBERTa model was run on CPU (Apple M-series, MPS not used). Batch size 16.
Scores are deterministic — no sampling is involved in text-classification inference.

**4. Label definitions differ across datasets.**
Deepset labels: 1 = "prompt injection attempt" (instruction-override phrasing).
xTRam1 labels: 1 = injection attempt covering roleplay-override, jailbreak, and credential-
extraction patterns. The broader xTRam1 definition partially explains why models that
generalize well on xTRam1 may underperform on deepset's narrower, more uniform format.

**5. No threshold sweep.**
All tiers except the keyword baseline produce a continuous score internally (the DeBERTa
and logistic regression outputs). This benchmark reports a single default threshold
(0.5 for the logistic regression; argmax for DeBERTa). ROC/PR curve analysis would show
additional tradeoff points not reported here.

**6. The existing RESULTS.md (regex-only) remains accurate.**
This file extends rather than replaces it. The regex numbers here agree with RESULTS.md
to within rounding.
