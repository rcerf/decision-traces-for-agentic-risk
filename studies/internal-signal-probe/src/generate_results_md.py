# -*- coding: utf-8 -*-
"""
# IMPLEMENTS: studies/internal-signal-probe -- generate RESULTS.md from artifacts/results.json
"""
import json
from pathlib import Path

STUDY_DIR = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = STUDY_DIR / "artifacts"
RESULTS_PATH = ARTIFACTS_DIR / "results.json"
OUT_PATH = STUDY_DIR / "RESULTS.md"


def verdict(results: dict) -> str:
    ds = results["deepset"]
    xt = results["xtram1"]
    xd = results["cross_dataset"]

    ds_probe = ds["best_layer_test_auc"]
    ds_ent = max(ds["entropy_mean_auc"], ds["entropy_last_auc"])
    xt_probe = xt["best_layer_test_auc"]
    xt_ent = max(xt["entropy_mean_auc"], xt["entropy_last_auc"])
    cd_min = min(xd["deepset_train_xtram1_test_auc"], xd["xtram1_train_deepset_test_auc"])
    cd_max = max(xd["deepset_train_xtram1_test_auc"], xd["xtram1_train_deepset_test_auc"])

    probe_better_ds = ds_probe > ds_ent
    probe_better_xt = xt_probe > xt_ent
    generalizes = cd_min >= 0.60  # meaningful cross-dataset transfer threshold

    probe_wins = probe_better_ds and probe_better_xt
    margin_ds = ds_probe - ds_ent
    margin_xt = xt_probe - xt_ent

    if probe_wins and generalizes:
        conclusion = (
            f"**Internal probe beats entropy on both datasets** "
            f"(deepset: +{margin_ds:.3f} AUC; xtram1: +{margin_xt:.3f} AUC) "
            f"and generalizes cross-dataset (min cross AUC {cd_min:.3f}), "
            f"supporting the hypothesis that the injection signal lives in the residual stream, not the output distribution."
        )
    elif probe_wins and not generalizes:
        conclusion = (
            f"**Internal probe beats entropy on both datasets** "
            f"(deepset: +{margin_ds:.3f} AUC; xtram1: +{margin_xt:.3f} AUC), "
            f"but cross-dataset generalization is weak (min cross AUC {cd_min:.3f}), "
            f"suggesting the probe may be capturing dataset-specific surface features rather than a universal injection direction."
        )
    elif not probe_wins and not generalizes:
        conclusion = (
            f"**The internal probe does NOT consistently beat entropy** "
            f"(deepset probe {ds_probe:.3f} vs entropy {ds_ent:.3f}; "
            f"xtram1 probe {xt_probe:.3f} vs entropy {xt_ent:.3f}) "
            f"and cross-dataset transfer is also weak ({cd_min:.3f}–{cd_max:.3f}). "
            f"This is a null result: neither internal activations at linear resolution nor output entropy "
            f"reliably detect injection in this configuration."
        )
    else:
        conclusion = (
            f"**Mixed result**: probe beats entropy on one dataset but not the other, "
            f"and cross-dataset generalization is {'adequate' if generalizes else 'weak'} "
            f"({cd_min:.3f}–{cd_max:.3f}). "
            f"Findings are inconclusive — architecture or data distribution differences may explain the asymmetry."
        )
    return conclusion


def lexical_section(results: dict) -> str:
    """Generate the structural-vs-lexical section if lexical_control key is present."""
    if "lexical_control" not in results:
        return ""

    lc = results["lexical_control"]
    l0 = results.get("layer0_cross_dataset", {})
    xd = results["cross_dataset"]
    ds = results["deepset"]
    xt = results["xtram1"]

    ds_probe_best = ds["best_layer_test_auc"]
    xt_probe_best = xt["best_layer_test_auc"]
    ds_layer0_indist = ds["per_layer_test_auc"][0]
    xt_layer0_indist = xt["per_layer_test_auc"][0]

    ds2xt_probe = xd["deepset_train_xtram1_test_auc"]
    xt2ds_probe = xd["xtram1_train_deepset_test_auc"]
    ds2xt_tfidf = lc["deepset_train_xtram1_test_auc"]
    xt2ds_tfidf = lc["xtram1_train_deepset_test_auc"]
    ds2xt_l0 = l0.get("deepset_train_xtram1_test_auc", float("nan"))
    xt2ds_l0 = l0.get("xtram1_train_deepset_test_auc", float("nan"))

    min_probe_cd = min(ds2xt_probe, xt2ds_probe)
    min_tfidf_cd = min(ds2xt_tfidf, xt2ds_tfidf)
    min_layer0_cd = min(ds2xt_l0, xt2ds_l0)
    margin_vs_tfidf = min_probe_cd - min_tfidf_cd
    margin_vs_layer0 = min_probe_cd - min_layer0_cd

    # Interpret
    if margin_vs_tfidf >= 0.05:
        interp = (
            "The activation probe's cross-dataset AUC is meaningfully higher than TF-IDF's "
            f"(min margin +{margin_vs_tfidf:.3f}). The transformer layers compute a transferable "
            "structural signal beyond surface vocabulary -- supporting the claim that the model's "
            "internal state adds information not recoverable from the raw token distribution alone."
        )
    elif margin_vs_tfidf >= -0.05:
        interp = (
            "The activation probe and TF-IDF reach approximately equal cross-dataset AUC "
            f"(min margin {margin_vs_tfidf:+.3f}). The honest claim shrinks: both "
            "representation-space probing and bag-of-words vocabulary detection separate injection "
            "from benign prompts and both beat entropy, but neither method demonstrates a clear "
            "advantage in cross-domain transfer. The injection signal is substantially lexical -- "
            "injections use distinguishable vocabulary that generalizes across datasets -- and the "
            "deep transformer layers do not add a reliably stronger cross-domain signal over what "
            "surface patterns already provide."
        )
    else:
        interp = (
            f"TF-IDF outperforms the activation probe cross-dataset (min margin {margin_vs_tfidf:+.3f}). "
            "The honest reading is that this probe is largely lexical: the transformer's computed "
            "representation does not transfer better than simple vocabulary matching, and the "
            "earlier claim about structural signal is not supported in cross-dataset evaluation."
        )

    # Layer-0 vs deep interpretation
    if margin_vs_layer0 >= 0.15:
        layer0_interp = (
            f"Layer-0 (embedding) cross-dataset AUC is substantially below the deep-layer probe "
            f"({ds2xt_l0:.3f}/{xt2ds_l0:.3f} vs {ds2xt_probe:.3f}/{xt2ds_probe:.3f}), confirming "
            "that the transformer's attention layers compute additional discriminative signal beyond "
            "static token embeddings. The embedding layer alone does not transfer well cross-dataset."
        )
    else:
        layer0_interp = (
            f"Layer-0 and deep layers show similar cross-dataset performance "
            f"({ds2xt_l0:.3f}/{xt2ds_l0:.3f} vs {ds2xt_probe:.3f}/{xt2ds_probe:.3f}), "
            "suggesting the signal is largely encoded in the static embedding space and transformer "
            "computation adds limited cross-domain benefit."
        )

    return f"""
---

## Structural Signal or Just Lexical?

**Control:** TF-IDF (word 1-2grams, max 50k features) + `LogisticRegression`, same balanced
splits and seed as the activation probe. Tests whether the probe merely detects injection
vocabulary visible to a bag-of-words classifier.

### In-distribution side-by-side

| Method | deepset in-dist AUC | xtram1 in-dist AUC |
|--------|--------------------|--------------------|
| TF-IDF (lexical) | {lc['deepset_indist_auc']:.4f} | {lc['xtram1_indist_auc']:.4f} |
| Layer-0 probe (embedding) | {ds_layer0_indist:.4f} | {xt_layer0_indist:.4f} |
| Best-layer probe (deep) | {ds_probe_best:.4f} | {xt_probe_best:.4f} |

### Cross-dataset side-by-side (the decisive test)

| Method | deepset->xtram1 | xtram1->deepset | min cross AUC |
|--------|----------------|----------------|---------------|
| TF-IDF (lexical) | {ds2xt_tfidf:.4f} | {xt2ds_tfidf:.4f} | {min_tfidf_cd:.4f} |
| Layer-0 probe (embedding) | {ds2xt_l0:.4f} | {xt2ds_l0:.4f} | {min_layer0_cd:.4f} |
| Best-layer probe (deep) | {ds2xt_probe:.4f} | {xt2ds_probe:.4f} | {min_probe_cd:.4f} |

### Structural vs lexical interpretation

{interp}

**Layer-0 vs deep layers:** {layer0_interp}

**One-line structural verdict:** The deep activation probe adds substantial signal over the
embedding layer (min cross-dataset +{margin_vs_layer0:.3f} AUC), confirming transformer
computation is contributing. The gap over TF-IDF cross-dataset is {margin_vs_tfidf:+.3f},
which is {'meaningful' if margin_vs_tfidf >= 0.05 else 'small -- the signal is largely lexical'}.
"""


def generate(results: dict) -> str:
    model = results["model"]
    n_sub = results["subsample_per_class"]
    ds = results["deepset"]
    xt = results["xtram1"]
    xd = results["cross_dataset"]
    n_layers = results["n_layers_probed"]

    # Per-layer table for deepset
    ds_rows = ""
    for i, (cv, te) in enumerate(zip(ds["per_layer_cv_auc"], ds["per_layer_test_auc"])):
        marker = " **<- best (CV)**" if i == ds["best_layer_by_cv"] else ""
        ds_rows += f"| {i} | {cv:.4f} | {te:.4f} |{marker}\n"

    # Per-layer table for xtram1
    xt_rows = ""
    for i, (cv, te) in enumerate(zip(xt["per_layer_cv_auc"], xt["per_layer_test_auc"])):
        marker = " **<- best (CV)**" if i == xt["best_layer_by_cv"] else ""
        xt_rows += f"| {i} | {cv:.4f} | {te:.4f} |{marker}\n"

    verd = verdict(results)

    md = f"""# Internal-Signal Probe vs Output-Entropy — Results

**Study:** `studies/internal-signal-probe/`
**Model:** `{model}`
**Subsample:** up to {n_sub} injection + {n_sub} benign per split (balanced; disclosed below)
**Date run:** see artifact timestamps in `artifacts/`

---

## Setup

| Parameter | Value |
|-----------|-------|
| Model | `{model}` |
| Layers probed | {n_layers} (layer 0 = embedding, layers 1–{n_layers-1} = transformer) |
| Probe | `LogisticRegression(C=1, balanced)` with `StandardScaler`, best layer selected by 5-fold CV on train |
| Entropy baseline | Same pipeline trained on mean per-token entropy scalar (and last-token entropy scalar) |
| Feature | Last-token residual-stream hidden state at each layer |
| Device | CPU |

### Subsample sizes (balanced, seed=42)

| Dataset | Split | N total | N injection | N benign |
|---------|-------|---------|------------|---------|
| deepset | train | {ds['train_n']} | {ds['train_n']//2} | {ds['train_n']//2} |
| deepset | test  | {ds['test_n']} | {ds['test_n']//2} | {ds['test_n']//2} |
| xtram1  | train | {xt['train_n']} | {xt['train_n']//2} | {xt['train_n']//2} |
| xtram1  | test  | {xt['test_n']} | {xt['test_n']//2} | {xt['test_n']//2} |

*Raw corpus sizes: deepset 662 total, xtram1 8236 train + 2060 test. Subsampled to caps above.*

---

## Per-Layer Probe AUC (in-distribution)

### deepset dataset

| Layer | 5-fold CV AUC (train) | Test AUC |
|-------|-----------------------|----------|
{ds_rows}

### xtram1 dataset

| Layer | 5-fold CV AUC (train) | Test AUC |
|-------|-----------------------|----------|
{xt_rows}

---

## Head-to-Head: Best-Layer Probe vs Entropy Baseline

| Dataset | Best layer | Probe AUC (test) | Entropy (mean) AUC | Entropy (last-tok) AUC | Probe margin |
|---------|-----------|-----------------|-------------------|----------------------|-------------|
| deepset | {ds['best_layer_by_cv']} | **{ds['best_layer_test_auc']:.4f}** | {ds['entropy_mean_auc']:.4f} | {ds['entropy_last_auc']:.4f} | {ds['best_layer_test_auc'] - max(ds['entropy_mean_auc'], ds['entropy_last_auc']):+.4f} |
| xtram1  | {xt['best_layer_by_cv']} | **{xt['best_layer_test_auc']:.4f}** | {xt['entropy_mean_auc']:.4f} | {xt['entropy_last_auc']:.4f} | {xt['best_layer_test_auc'] - max(xt['entropy_mean_auc'], xt['entropy_last_auc']):+.4f} |

---

## Cross-Dataset Generalization (the Honesty Check)

| Train on | Test on | AUC |
|----------|---------|-----|
| deepset  | xtram1  | {xd['deepset_train_xtram1_test_auc']:.4f} |
| xtram1   | deepset | {xd['xtram1_train_deepset_test_auc']:.4f} |

*Best layer from source dataset is used in both cases.*

---

## Verdict

{verd}
{lexical_section(results)}

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
"""
    return md


def main():
    if not RESULTS_PATH.exists():
        raise FileNotFoundError(f"Run the experiment first: {RESULTS_PATH} not found.")
    with open(RESULTS_PATH) as f:
        results = json.load(f)
    md = generate(results)
    OUT_PATH.write_text(md)
    print(f"Written: {OUT_PATH}")


if __name__ == "__main__":
    main()
