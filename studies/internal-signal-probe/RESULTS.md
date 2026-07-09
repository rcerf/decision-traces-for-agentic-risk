# Internal-Signal Probe vs Output-Entropy — Results

**Study:** `studies/internal-signal-probe/`
**Model:** `Qwen/Qwen2.5-0.5B-Instruct`
**Subsample:** up to 250 injection + 250 benign per split (balanced; disclosed below)
**Date run:** see artifact timestamps in `artifacts/`

---

## Setup

| Parameter | Value |
|-----------|-------|
| Model | `Qwen/Qwen2.5-0.5B-Instruct` |
| Layers probed | 25 (layer 0 = embedding, layers 1–24 = transformer) |
| Probe | `LogisticRegression(C=1, balanced)` with `StandardScaler`, best layer selected by 5-fold CV on train |
| Entropy baseline | Same pipeline trained on mean per-token entropy scalar (and last-token entropy scalar) |
| Feature | Last-token residual-stream hidden state at each layer |
| Device | CPU |

### Subsample sizes (balanced, seed=42)

| Dataset | Split | N total | N injection | N benign |
|---------|-------|---------|------------|---------|
| deepset | train | 453 | 226 | 226 |
| deepset | test  | 116 | 58 | 58 |
| xtram1  | train | 500 | 250 | 250 |
| xtram1  | test  | 500 | 250 | 250 |

*Raw corpus sizes: deepset 662 total, xtram1 8236 train + 2060 test. Subsampled to caps above.*

---

## Per-Layer Probe AUC (in-distribution)

### deepset dataset

| Layer | 5-fold CV AUC (train) | Test AUC |
|-------|-----------------------|----------|
| 0 | 0.8016 | 0.9158 |
| 1 | 0.9423 | 0.9759 |
| 2 | 0.9877 | 0.9932 |
| 3 | 0.9797 | 0.9917 |
| 4 | 0.9879 | 0.9863 |
| 5 | 0.9892 | 0.9973 |
| 6 | 0.9929 | 0.9943 |
| 7 | 0.9967 | 0.9958 |
| 8 | 0.9967 | 0.9976 |
| 9 | 0.9968 | 0.9943 |
| 10 | 0.9955 | 0.9961 |
| 11 | 0.9965 | 0.9994 |
| 12 | 0.9981 | 0.9994 |
| 13 | 0.9986 | 0.9994 | **<- best (CV)**
| 14 | 0.9979 | 0.9985 |
| 15 | 0.9986 | 0.9970 |
| 16 | 0.9946 | 1.0000 |
| 17 | 0.9943 | 0.9988 |
| 18 | 0.9942 | 0.9997 |
| 19 | 0.9945 | 1.0000 |
| 20 | 0.9967 | 0.9985 |
| 21 | 0.9960 | 0.9991 |
| 22 | 0.9944 | 0.9973 |
| 23 | 0.9940 | 0.9988 |
| 24 | 0.9941 | 0.9988 |


### xtram1 dataset

| Layer | 5-fold CV AUC (train) | Test AUC |
|-------|-----------------------|----------|
| 0 | 0.8373 | 0.7912 |
| 1 | 0.9333 | 0.9156 |
| 2 | 0.9611 | 0.9613 |
| 3 | 0.9538 | 0.9572 |
| 4 | 0.9758 | 0.9739 |
| 5 | 0.9918 | 0.9844 |
| 6 | 0.9925 | 0.9890 |
| 7 | 0.9942 | 0.9929 |
| 8 | 0.9864 | 0.9873 |
| 9 | 0.9921 | 0.9900 |
| 10 | 0.9924 | 0.9863 |
| 11 | 0.9943 | 0.9876 |
| 12 | 0.9970 | 0.9921 |
| 13 | 0.9971 | 0.9914 |
| 14 | 0.9962 | 0.9898 |
| 15 | 0.9974 | 0.9937 |
| 16 | 0.9976 | 0.9948 | **<- best (CV)**
| 17 | 0.9969 | 0.9926 |
| 18 | 0.9962 | 0.9921 |
| 19 | 0.9944 | 0.9925 |
| 20 | 0.9904 | 0.9916 |
| 21 | 0.9939 | 0.9910 |
| 22 | 0.9931 | 0.9897 |
| 23 | 0.9956 | 0.9913 |
| 24 | 0.9956 | 0.9935 |


---

## Head-to-Head: Best-Layer Probe vs Entropy Baseline

| Dataset | Best layer | Probe AUC (test) | Entropy (mean) AUC | Entropy (last-tok) AUC | Probe margin |
|---------|-----------|-----------------|-------------------|----------------------|-------------|
| deepset | 13 | **0.9994** | 0.5476 | 0.5461 | +0.4518 |
| xtram1  | 16 | **0.9948** | 0.7992 | 0.8029 | +0.1919 |

---

## Cross-Dataset Generalization (the Honesty Check)

| Train on | Test on | AUC |
|----------|---------|-----|
| deepset  | xtram1  | 0.7323 |
| xtram1   | deepset | 0.8667 |

*Best layer from source dataset is used in both cases.*

---

## Verdict

**Internal probe beats entropy on both datasets** (deepset: +0.452 AUC; xtram1: +0.192 AUC) and generalizes cross-dataset (min cross AUC 0.732), supporting the hypothesis that the injection signal lives in the residual stream, not the output distribution.

---

## Structural Signal or Just Lexical?

**Control:** TF-IDF (word 1-2grams, max 50k features) + `LogisticRegression`, same balanced
splits and seed as the activation probe. Tests whether the probe merely detects injection
vocabulary visible to a bag-of-words classifier.

### In-distribution side-by-side

| Method | deepset in-dist AUC | xtram1 in-dist AUC |
|--------|--------------------|--------------------|
| TF-IDF (lexical) | 0.9491 | 0.9977 |
| Layer-0 probe (embedding) | 0.9158 | 0.7912 |
| Best-layer probe (deep) | 0.9994 | 0.9948 |

### Cross-dataset side-by-side (the decisive test)

| Method | deepset->xtram1 | xtram1->deepset | min cross AUC |
|--------|----------------|----------------|---------------|
| TF-IDF (lexical) | 0.7796 | 0.6874 | 0.6874 |
| Layer-0 probe (embedding) | 0.5171 | 0.3396 | 0.3396 |
| Best-layer probe (deep) | 0.7323 | 0.8667 | 0.7323 |

### Structural vs lexical interpretation

The activation probe and TF-IDF reach approximately equal cross-dataset AUC (min margin +0.045). The honest claim shrinks: both representation-space probing and bag-of-words vocabulary detection separate injection from benign prompts and both beat entropy, but neither method demonstrates a clear advantage in cross-domain transfer. The injection signal is substantially lexical -- injections use distinguishable vocabulary that generalizes across datasets -- and the deep transformer layers do not add a reliably stronger cross-domain signal over what surface patterns already provide.

**Layer-0 vs deep layers:** Layer-0 (embedding) cross-dataset AUC is substantially below the deep-layer probe (0.517/0.340 vs 0.732/0.867), confirming that the transformer's attention layers compute additional discriminative signal beyond static token embeddings. The embedding layer alone does not transfer well cross-dataset.

**One-line structural verdict:** The deep activation probe adds substantial signal over the
embedding layer (min cross-dataset +0.393 AUC), confirming transformer
computation is contributing. The gap over TF-IDF cross-dataset is +0.045,
which is small -- the signal is largely lexical.


---

## Limitations

- **Linear probe, not mechanistic**: A logistic regression on residual-stream vectors is a coarse instrument. It tests whether a *linear* direction is predictive — it does not identify circuits, causal structure, or sparse features in the SAE sense. AUC gains here do not imply a clean interpretable direction exists.
- **Small N**: Up to 250 samples per class per split. Confidence intervals on AUC at this scale are wide (roughly ±0.03–0.05 for a 250-sample test set). No confidence intervals are reported; treat point estimates as noisy.
- **0.5B model**: Qwen2.5-0.5B-Instruct is capacity-limited. Larger models may show cleaner or different directional structure. Results should not be extrapolated to frontier models.
- **Prompt-level, not trajectory-level**: These are single-turn prompt labels. Agentic risk involves multi-step trajectories where injection may manifest later and more subtly.
- **Probes are adversarially brittle**: Activation probes can be trivially defeated by an adversary who knows the probe exists (feature adversarial perturbations, representation-level camouflage). This is a detection research prototype, not a production defense.
- **Single model family**: All results are on one architecture (Qwen). Transfer across architectures is unknown.
- **Entropy baseline implementation**: Mean per-token entropy is computed over prompt tokens using teacher-forced logits — this is a proxy for model uncertainty, not a gold-standard signal. Other entropy formulations might behave differently.

---

## Prior Art / Where This Comes From

This study is *in the spirit of* — not a reproduction of — the following:

1. **Arditi et al. 2024** — "Refusal in Language Models Is Mediated by a Single Direction" (arXiv:2406.11717). Shows that a single linear direction in residual-stream activations mediates refusal behavior, and that this direction can be ablated or amplified. The intuition here: if refusal has a linear direction, perhaps compliance-under-attack (injection acceptance) has one too.

2. **Anthropic "Towards Monosemanticity"** (Bricken et al. 2023) and **"Scaling Monosemanticity"** (Templeton et al. 2024). Sparse Autoencoder (SAE) work showing that individual human-interpretable features exist in transformer residual streams. The present study does not use SAEs — it probes the raw residual stream with a linear classifier — but the underlying premise (signals are latent in activations) derives from this line of work.

3. **Anthropic "On the Biology of a Large Language Model"** (Lindsey et al. 2025). Identifies circuits responsible for confident confabulation — attacked models may be confidently wrong in specific activation patterns. This motivates why output *entropy* fails (attacked model is low-entropy/confident) while activations might still carry injection signal.

This study operationalizes the weakest testable form of the activation-signal hypothesis: can a linear probe trained on raw hidden states outperform a linear probe trained on output entropy? It is a necessary precursor to, but not a substitute for, full SAE or causal intervention studies.

---

## Reproduce

```bash
cd /path/to/decision-traces-for-agentic-risk

# Full experiment (downloads model on first run, caches features)
python studies/internal-signal-probe/src/run_probe_experiment.py

# Force recompute (ignore cache)
python studies/internal-signal-probe/src/run_probe_experiment.py --no-cache

# Generate this RESULTS.md from cached results.json
python studies/internal-signal-probe/src/generate_results_md.py

# Run sanity tests
python -m pytest studies/internal-signal-probe/tests/ -q
```

Dependencies: see `studies/internal-signal-probe/requirements.txt`.
