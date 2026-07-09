# -*- coding: utf-8 -*-
"""
# IMPLEMENTS: studies/internal-signal-probe -- TF-IDF lexical control vs activation probe

Control experiment: does the activation probe detect structural signal in the model's
internal representation, or is it just detecting injection VOCABULARY that a bag-of-words
classifier would also catch?

Uses EXACT same balanced subsamples (seed=42) as run_probe_experiment.py.
Reads cached activation features from artifacts/ for layer-0 comparison.
Updates artifacts/results.json in place with lexical and layer-0 cross-dataset fields.
"""

import json
import pickle
import sys
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

SRC_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC_DIR))
from run_probe_experiment import (
    load_deepset,
    load_xtram1,
    make_probe_pipeline,
    cross_dataset_auc,
    ARTIFACTS_DIR,
)

SEED = 42


# ---------------------------------------------------------------------------
# TF-IDF pipeline
# ---------------------------------------------------------------------------

def make_tfidf_pipeline() -> Pipeline:
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 2),
            max_features=50000,
            sublinear_tf=True,
            min_df=2,
        )),
        ("lr", LogisticRegression(
            max_iter=1000, C=1.0, solver="lbfgs", class_weight="balanced"
        )),
    ])


def tfidf_auc(train_texts, train_labels, test_texts, test_labels) -> float:
    y_train = np.array(train_labels)
    y_test = np.array(test_labels)
    pipe = make_tfidf_pipeline()
    pipe.fit(train_texts, y_train)
    pred = pipe.predict_proba(test_texts)[:, 1]
    return float(roc_auc_score(y_test, pred))


# ---------------------------------------------------------------------------
# Layer-0 cross-dataset using cached features
# ---------------------------------------------------------------------------

def layer0_cross_dataset_auc(train_feat_name: str, train_labels,
                              test_feat_name: str, test_labels) -> float:
    """Load cached feature PKL, extract layer 0, train probe, return cross-dataset AUC."""
    tr_path = ARTIFACTS_DIR / f"features_{train_feat_name}.pkl"
    te_path = ARTIFACTS_DIR / f"features_{test_feat_name}.pkl"
    if not tr_path.exists() or not te_path.exists():
        raise FileNotFoundError(
            f"Feature cache not found. Run run_probe_experiment.py first.\n"
            f"  Expected: {tr_path}\n  Expected: {te_path}"
        )
    with open(tr_path, "rb") as f:
        tr_feats = pickle.load(f)
    with open(te_path, "rb") as f:
        te_feats = pickle.load(f)
    return cross_dataset_auc(
        tr_feats["last_token"], train_labels,
        te_feats["last_token"], test_labels,
        best_layer=0,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("\n=== Loading data (seed=42, same splits as main experiment) ===")
    ds_tr_t, ds_tr_l, ds_te_t, ds_te_l = load_deepset(seed=SEED)
    xt_tr_t, xt_tr_l, xt_te_t, xt_te_l = load_xtram1(seed=SEED)

    print(f"deepset  train: {len(ds_tr_t)} | test: {len(ds_te_t)}")
    print(f"xtram1   train: {len(xt_tr_t)} | test: {len(xt_te_t)}")

    # ---- TF-IDF in-distribution ----
    print("\n=== TF-IDF in-distribution ===")
    ds_tfidf_indist = tfidf_auc(ds_tr_t, ds_tr_l, ds_te_t, ds_te_l)
    xt_tfidf_indist = tfidf_auc(xt_tr_t, xt_tr_l, xt_te_t, xt_te_l)
    print(f"  deepset in-dist TF-IDF AUC:  {ds_tfidf_indist:.4f}")
    print(f"  xtram1  in-dist TF-IDF AUC:  {xt_tfidf_indist:.4f}")

    # ---- TF-IDF cross-dataset ----
    print("\n=== TF-IDF cross-dataset ===")
    ds2xt_tfidf = tfidf_auc(ds_tr_t, ds_tr_l, xt_te_t, xt_te_l)
    xt2ds_tfidf = tfidf_auc(xt_tr_t, xt_tr_l, ds_te_t, ds_te_l)
    print(f"  deepset->xtram1 TF-IDF AUC:  {ds2xt_tfidf:.4f}")
    print(f"  xtram1->deepset TF-IDF AUC:  {xt2ds_tfidf:.4f}")

    # ---- Layer-0 cross-dataset (from cached features) ----
    print("\n=== Layer-0 (embedding) cross-dataset ===")
    ds2xt_layer0 = layer0_cross_dataset_auc("deepset_train", ds_tr_l, "xtram1_test", xt_te_l)
    xt2ds_layer0 = layer0_cross_dataset_auc("xtram1_train", xt_tr_l, "deepset_test", ds_te_l)
    print(f"  deepset->xtram1 layer-0 AUC: {ds2xt_layer0:.4f}")
    print(f"  xtram1->deepset layer-0 AUC: {xt2ds_layer0:.4f}")

    # ---- Load existing results and update ----
    results_path = ARTIFACTS_DIR / "results.json"
    with open(results_path) as f:
        results = json.load(f)

    results["lexical_control"] = {
        "tfidf_ngram_range": "1-2",
        "tfidf_max_features": 50000,
        "deepset_indist_auc": ds_tfidf_indist,
        "xtram1_indist_auc": xt_tfidf_indist,
        "deepset_train_xtram1_test_auc": ds2xt_tfidf,
        "xtram1_train_deepset_test_auc": xt2ds_tfidf,
    }
    results["layer0_cross_dataset"] = {
        "deepset_train_xtram1_test_auc": ds2xt_layer0,
        "xtram1_train_deepset_test_auc": xt2ds_layer0,
    }

    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n[save] Updated {results_path}")

    # ---- Print comparison table ----
    ds_probe_cd = results["cross_dataset"]["deepset_train_xtram1_test_auc"]
    xt_probe_cd = results["cross_dataset"]["xtram1_train_deepset_test_auc"]
    ds_probe_best = results["deepset"]["best_layer_test_auc"]
    xt_probe_best = results["xtram1"]["best_layer_test_auc"]
    ds_layer0_indist = results["deepset"]["per_layer_test_auc"][0]
    xt_layer0_indist = results["xtram1"]["per_layer_test_auc"][0]

    print("\n" + "=" * 70)
    print("STRUCTURAL vs LEXICAL COMPARISON")
    print("=" * 70)
    print(f"\n{'Method':<35} {'deepset in-dist':>15} {'xtram1 in-dist':>15}")
    print("-" * 65)
    print(f"{'TF-IDF (bag-of-words)':<35} {ds_tfidf_indist:>15.4f} {xt_tfidf_indist:>15.4f}")
    print(f"{'Layer 0 probe (embedding)':<35} {ds_layer0_indist:>15.4f} {xt_layer0_indist:>15.4f}")
    print(f"{'Best-layer probe (deep)':<35} {ds_probe_best:>15.4f} {xt_probe_best:>15.4f}")

    print(f"\n{'Method':<35} {'ds->xtram1':>12} {'xtram1->ds':>12}")
    print("-" * 59)
    print(f"{'TF-IDF (lexical)':<35} {ds2xt_tfidf:>12.4f} {xt2ds_tfidf:>12.4f}")
    print(f"{'Layer-0 probe (embedding)':<35} {ds2xt_layer0:>12.4f} {xt2ds_layer0:>12.4f}")
    print(f"{'Best-layer probe (deep)':<35} {ds_probe_cd:>12.4f} {xt_probe_cd:>12.4f}")

    # ---- Verdict ----
    min_probe_cd = min(ds_probe_cd, xt_probe_cd)
    min_tfidf_cd = min(ds2xt_tfidf, xt2ds_tfidf)
    min_layer0_cd = min(ds2xt_layer0, xt2ds_layer0)
    margin_probe_vs_tfidf = min_probe_cd - min_tfidf_cd
    margin_deep_vs_layer0 = min_probe_cd - min_layer0_cd

    print(f"\n--- Cross-dataset margins ---")
    print(f"  Best-layer probe - TF-IDF (min cross AUC): {margin_probe_vs_tfidf:+.4f}")
    print(f"  Best-layer probe - Layer-0  (min cross AUC): {margin_deep_vs_layer0:+.4f}")

    return {
        "ds_tfidf_indist": ds_tfidf_indist,
        "xt_tfidf_indist": xt_tfidf_indist,
        "ds2xt_tfidf": ds2xt_tfidf,
        "xt2ds_tfidf": xt2ds_tfidf,
        "ds2xt_layer0": ds2xt_layer0,
        "xt2ds_layer0": xt2ds_layer0,
    }


if __name__ == "__main__":
    main()
