# -*- coding: utf-8 -*-
"""
# IMPLEMENTS: studies/internal-signal-probe -- internal-representation probe vs output-entropy head-to-head
#
# Hypothesis: Prompt injection lives in the model's residual-stream activations, NOT its output
# entropy distribution (which was already falsified as a signal, d'~0.07).
#
# Based loosely on the spirit of:
#   - Arditi et al. 2024 "Refusal in LLMs is mediated by a single direction"
#   - Anthropic "Towards Monosemanticity" / "Scaling Monosemanticity" (SAE feature work)
#   - Anthropic "On the Biology of a Large Language Model" (confident-confabulation circuits)
#
# This is a linear activation probe -- NOT SAE / mechanistic interpretability. It tests whether
# a direction in the residual stream is linearly predictive of injection labels, without
# claiming to identify circuits or causal mechanisms.
"""

import argparse
import json
import os
import pickle
import warnings
from pathlib import Path

import numpy as np
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from transformers import AutoTokenizer, AutoModelForCausalLM

warnings.filterwarnings("ignore", category=UserWarning)

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "benchmark" / "data"
STUDY_DIR = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = STUDY_DIR / "artifacts"
ARTIFACTS_DIR.mkdir(exist_ok=True)

MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"

# Subsample caps per class -- keeps CPU runtime tractable
SUBSAMPLE_PER_CLASS = 250


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_deepset(seed: int = 42) -> tuple:
    """Load deepset using its built-in train/test split, then subsample."""
    path = DATA_DIR / "deepset_prompt_injections.jsonl"
    train_texts, train_labels = [], []
    test_texts, test_labels = [], []
    with open(path) as f:
        for line in f:
            r = json.loads(line)
            if r.get("split") == "train":
                train_texts.append(r["text"])
                train_labels.append(int(r["label"]))
            else:
                test_texts.append(r["text"])
                test_labels.append(int(r["label"]))

    train_texts, train_labels = _balanced_subsample(
        train_texts, train_labels, SUBSAMPLE_PER_CLASS, seed
    )
    test_texts, test_labels = _balanced_subsample(
        test_texts, test_labels, SUBSAMPLE_PER_CLASS, seed
    )
    return train_texts, train_labels, test_texts, test_labels


def load_xtram1(seed: int = 42) -> tuple:
    """Load xTRam1 using its built-in train/test split, then subsample."""
    def _read(fname):
        texts, labels = [], []
        with open(DATA_DIR / fname) as f:
            for line in f:
                r = json.loads(line)
                texts.append(r["text"])
                labels.append(int(r["label"]))
        return texts, labels

    tr_texts, tr_labels = _read("xtram1_injection_train.jsonl")
    te_texts, te_labels = _read("xtram1_injection_test.jsonl")
    tr_texts, tr_labels = _balanced_subsample(tr_texts, tr_labels, SUBSAMPLE_PER_CLASS, seed)
    te_texts, te_labels = _balanced_subsample(te_texts, te_labels, SUBSAMPLE_PER_CLASS, seed)
    return tr_texts, tr_labels, te_texts, te_labels


def _balanced_subsample(texts, labels, n_per_class: int, seed: int):
    rng = np.random.default_rng(seed)
    texts_arr = np.array(texts, dtype=object)
    labels_arr = np.array(labels)
    out_t, out_l = [], []
    for cls in [0, 1]:
        idx = np.where(labels_arr == cls)[0]
        chosen = rng.choice(idx, size=min(n_per_class, len(idx)), replace=False)
        out_t.extend(texts_arr[chosen].tolist())
        out_l.extend(labels_arr[chosen].tolist())
    return out_t, out_l


# ---------------------------------------------------------------------------
# Feature extraction -- residual stream + entropy
# ---------------------------------------------------------------------------

def load_model_and_tokenizer(device: str = "cpu"):
    print(f"[model] Loading {MODEL_ID} ...")
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        output_hidden_states=True,
        torch_dtype=torch.float32,
    ).to(device)
    model.eval()
    print(f"[model] Loaded. Layers: {model.config.num_hidden_layers}, hidden={model.config.hidden_size}")
    return model, tok


def extract_features_batch(
    texts,
    model,
    tokenizer,
    device: str = "cpu",
    max_length: int = 256,
    batch_size: int = 4,
) -> dict:
    """
    Returns dict with keys:
        last_token: shape (N, n_layers+1, hidden_size) -- includes embedding layer (layer 0)
        mean_pool:  shape (N, n_layers+1, hidden_size)
        token_entropy:      shape (N,) -- mean per-token predictive entropy over prompt tokens
        last_token_entropy: shape (N,) -- entropy of next-token distribution at last position
    """
    n = len(texts)
    n_layers = model.config.num_hidden_layers + 1  # +1 for embedding layer (layer 0)
    hidden_size = model.config.hidden_size

    last_token_all = np.zeros((n, n_layers, hidden_size), dtype=np.float32)
    mean_pool_all = np.zeros((n, n_layers, hidden_size), dtype=np.float32)
    token_entropy_all = np.zeros(n, dtype=np.float32)
    last_token_entropy_all = np.zeros(n, dtype=np.float32)

    for batch_start in range(0, n, batch_size):
        batch_texts = texts[batch_start : batch_start + batch_size]
        enc = tokenizer(
            batch_texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=max_length,
        ).to(device)

        with torch.no_grad():
            out = model(**enc)

        # hidden_states: tuple of (n_layers+1) tensors, each (B, seq_len, hidden)
        hidden_states = out.hidden_states  # len = n_layers + 1
        logits = out.logits  # (B, seq_len, vocab)

        attention_mask = enc["attention_mask"]  # (B, seq_len)
        B = attention_mask.shape[0]

        # Find real last-token position per item (last non-pad)
        seq_lengths = attention_mask.sum(dim=1) - 1  # (B,) -- index of last real token

        for b in range(B):
            global_idx = batch_start + b
            if global_idx >= n:
                break
            last_pos = seq_lengths[b].item()
            mask_b = attention_mask[b].bool()  # (seq_len,)

            for layer_i, hs in enumerate(hidden_states):
                last_vec = hs[b, last_pos, :].cpu().numpy()
                mean_vec = hs[b, mask_b, :].mean(dim=0).cpu().numpy()
                last_token_all[global_idx, layer_i] = last_vec
                mean_pool_all[global_idx, layer_i] = mean_vec

            # --- Entropy computation ---
            # Per-token predictive entropy: H(p) = -sum p log p at each position
            logits_b = logits[b, mask_b, :]  # (seq_real, vocab)
            probs = torch.softmax(logits_b.float(), dim=-1)
            probs_clamped = probs.clamp(min=1e-12)
            per_pos_entropy = -(probs_clamped * probs_clamped.log()).sum(dim=-1)  # (seq_real,)
            token_entropy_all[global_idx] = per_pos_entropy.mean().item()

            # last-token entropy: distribution at the very last real position
            last_probs = probs[-1]  # vocab
            last_entropy = -(last_probs.clamp(min=1e-12) * last_probs.clamp(min=1e-12).log()).sum()
            last_token_entropy_all[global_idx] = last_entropy.item()

        done = min(batch_start + batch_size, n)
        print(f"  [{done}/{n}] features extracted", end="\r", flush=True)

    print()
    return {
        "last_token": last_token_all,
        "mean_pool": mean_pool_all,
        "token_entropy": token_entropy_all,
        "last_token_entropy": last_token_entropy_all,
    }


def get_or_compute_features(name: str, texts, model, tokenizer, device: str = "cpu") -> dict:
    cache_path = ARTIFACTS_DIR / f"features_{name}.pkl"
    if cache_path.exists():
        print(f"[cache] Loading cached features for '{name}' from {cache_path}")
        with open(cache_path, "rb") as f:
            return pickle.load(f)
    print(f"[extract] Computing features for '{name}' ({len(texts)} prompts) ...")
    feats = extract_features_batch(texts, model, tokenizer, device=device)
    with open(cache_path, "wb") as f:
        pickle.dump(feats, f)
    print(f"[cache] Saved to {cache_path}")
    return feats


# ---------------------------------------------------------------------------
# Probe training / evaluation
# ---------------------------------------------------------------------------

def make_probe_pipeline() -> Pipeline:
    return Pipeline([
        ("scaler", StandardScaler()),
        ("lr", LogisticRegression(
            max_iter=1000, C=1.0, solver="lbfgs", class_weight="balanced"
        )),
    ])


def probe_all_layers(train_feats, train_labels, test_feats, test_labels):
    """
    train_feats / test_feats: (N, n_layers, hidden_size)
    Returns: train_cv_aucs, test_aucs, best_layer_idx, best_probe
    """
    n_layers = train_feats.shape[1]
    y_train = np.array(train_labels)
    y_test = np.array(test_labels)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    train_cv_aucs = []
    test_aucs = []

    for layer_i in range(n_layers):
        X_tr = train_feats[:, layer_i, :]
        X_te = test_feats[:, layer_i, :]

        pipe = make_probe_pipeline()
        cv_scores = cross_val_score(pipe, X_tr, y_train, cv=cv, scoring="roc_auc", n_jobs=1)
        train_cv_aucs.append(float(cv_scores.mean()))

        # Fit on full train, evaluate on test
        pipe.fit(X_tr, y_train)
        test_pred = pipe.predict_proba(X_te)[:, 1]
        test_auc = roc_auc_score(y_test, test_pred)
        test_aucs.append(float(test_auc))

    best_layer = int(np.argmax(train_cv_aucs))
    # Refit best probe on full train
    X_tr_best = train_feats[:, best_layer, :]
    best_probe = make_probe_pipeline()
    best_probe.fit(X_tr_best, y_train)

    return train_cv_aucs, test_aucs, best_layer, best_probe


def entropy_baseline_auc(train_feats, train_labels, test_feats, test_labels,
                         entropy_key: str = "token_entropy") -> float:
    """Train logistic probe on entropy scalar, return test AUC."""
    y_train = np.array(train_labels)
    y_test = np.array(test_labels)
    X_tr = train_feats[entropy_key].reshape(-1, 1)
    X_te = test_feats[entropy_key].reshape(-1, 1)
    pipe = make_probe_pipeline()
    pipe.fit(X_tr, y_train)
    pred = pipe.predict_proba(X_te)[:, 1]
    return float(roc_auc_score(y_test, pred))


def cross_dataset_auc(train_feats, train_labels, test_feats, test_labels, best_layer: int) -> float:
    """Apply probe trained at best_layer on one dataset to a different dataset."""
    y_train = np.array(train_labels)
    y_test = np.array(test_labels)
    X_tr = train_feats[:, best_layer, :]
    X_te = test_feats[:, best_layer, :]
    pipe = make_probe_pipeline()
    pipe.fit(X_tr, y_train)
    pred = pipe.predict_proba(X_te)[:, 1]
    return float(roc_auc_score(y_test, pred))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Internal-signal probe vs entropy baseline")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--no-cache", action="store_true", help="Force recompute features")
    args = parser.parse_args()

    if args.no_cache:
        for p in ARTIFACTS_DIR.glob("features_*.pkl"):
            p.unlink()
            print(f"[cache] Removed {p}")

    # ---- Load data ----
    print("\n=== Loading data ===")
    ds_tr_t, ds_tr_l, ds_te_t, ds_te_l = load_deepset(seed=args.seed)
    xt_tr_t, xt_tr_l, xt_te_t, xt_te_l = load_xtram1(seed=args.seed)

    print(f"deepset  train: {len(ds_tr_t)} ({sum(ds_tr_l)} inj / {sum(1 for x in ds_tr_l if x==0)} benign)")
    print(f"deepset  test:  {len(ds_te_t)} ({sum(ds_te_l)} inj / {sum(1 for x in ds_te_l if x==0)} benign)")
    print(f"xtram1   train: {len(xt_tr_t)} ({sum(xt_tr_l)} inj / {sum(1 for x in xt_tr_l if x==0)} benign)")
    print(f"xtram1   test:  {len(xt_te_t)} ({sum(xt_te_l)} inj / {sum(1 for x in xt_te_l if x==0)} benign)")

    # ---- Load model ----
    print("\n=== Loading model ===")
    model, tokenizer = load_model_and_tokenizer(device=args.device)
    n_layers = model.config.num_hidden_layers + 1  # includes embedding layer

    # ---- Extract features ----
    print("\n=== Extracting features ===")
    ds_tr_f = get_or_compute_features("deepset_train", ds_tr_t, model, tokenizer, args.device)
    ds_te_f = get_or_compute_features("deepset_test", ds_te_t, model, tokenizer, args.device)
    xt_tr_f = get_or_compute_features("xtram1_train", xt_tr_t, model, tokenizer, args.device)
    xt_te_f = get_or_compute_features("xtram1_test", xt_te_t, model, tokenizer, args.device)

    # ---- Probe: per-layer AUC (last-token hidden state) ----
    print("\n=== Probing layers (deepset, last-token) ===")
    ds_cv_aucs, ds_test_aucs, ds_best_layer, ds_best_probe = probe_all_layers(
        ds_tr_f["last_token"], ds_tr_l,
        ds_te_f["last_token"], ds_te_l,
    )

    print("\n=== Probing layers (xtram1, last-token) ===")
    xt_cv_aucs, xt_test_aucs, xt_best_layer, xt_best_probe = probe_all_layers(
        xt_tr_f["last_token"], xt_tr_l,
        xt_te_f["last_token"], xt_te_l,
    )

    # ---- Entropy baseline ----
    print("\n=== Entropy baseline ===")
    ds_ent_auc_mean = entropy_baseline_auc(ds_tr_f, ds_tr_l, ds_te_f, ds_te_l, "token_entropy")
    ds_ent_auc_last = entropy_baseline_auc(ds_tr_f, ds_tr_l, ds_te_f, ds_te_l, "last_token_entropy")
    xt_ent_auc_mean = entropy_baseline_auc(xt_tr_f, xt_tr_l, xt_te_f, xt_te_l, "token_entropy")
    xt_ent_auc_last = entropy_baseline_auc(xt_tr_f, xt_tr_l, xt_te_f, xt_te_l, "last_token_entropy")

    # ---- Cross-dataset ----
    print("\n=== Cross-dataset generalization ===")
    ds2xt_auc = cross_dataset_auc(
        ds_tr_f["last_token"], ds_tr_l,
        xt_te_f["last_token"], xt_te_l,
        ds_best_layer,
    )
    xt2ds_auc = cross_dataset_auc(
        xt_tr_f["last_token"], xt_tr_l,
        ds_te_f["last_token"], ds_te_l,
        xt_best_layer,
    )

    # ---- Save best probes ----
    probe_path = ARTIFACTS_DIR / "best_probes.pkl"
    with open(probe_path, "wb") as f:
        pickle.dump({
            "deepset_best_layer": ds_best_layer,
            "deepset_best_probe": ds_best_probe,
            "xtram1_best_layer": xt_best_layer,
            "xtram1_best_probe": xt_best_probe,
        }, f)
    print(f"[save] Best probes saved to {probe_path}")

    # ---- Results summary ----
    results = {
        "model": MODEL_ID,
        "subsample_per_class": SUBSAMPLE_PER_CLASS,
        "n_layers_probed": n_layers,
        "deepset": {
            "train_n": len(ds_tr_t),
            "test_n": len(ds_te_t),
            "best_layer_by_cv": ds_best_layer,
            "best_layer_test_auc": ds_test_aucs[ds_best_layer],
            "per_layer_cv_auc": ds_cv_aucs,
            "per_layer_test_auc": ds_test_aucs,
            "entropy_mean_auc": ds_ent_auc_mean,
            "entropy_last_auc": ds_ent_auc_last,
        },
        "xtram1": {
            "train_n": len(xt_tr_t),
            "test_n": len(xt_te_t),
            "best_layer_by_cv": xt_best_layer,
            "best_layer_test_auc": xt_test_aucs[xt_best_layer],
            "per_layer_cv_auc": xt_cv_aucs,
            "per_layer_test_auc": xt_test_aucs,
            "entropy_mean_auc": xt_ent_auc_mean,
            "entropy_last_auc": xt_ent_auc_last,
        },
        "cross_dataset": {
            "deepset_train_xtram1_test_auc": ds2xt_auc,
            "xtram1_train_deepset_test_auc": xt2ds_auc,
        },
    }

    results_path = ARTIFACTS_DIR / "results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n[save] Full results saved to {results_path}")

    # ---- Print summary ----
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"\nModel: {MODEL_ID}")
    print(f"Subsample: up to {SUBSAMPLE_PER_CLASS} per class per split")
    print(f"Layers probed: {n_layers} (0=embedding, 1..{n_layers-1}=transformer layers)")

    print(f"\n--- deepset (train->test, in-distribution) ---")
    print(f"  Best layer (by 5-fold CV): {ds_best_layer}")
    print(f"  Best-layer probe AUC (test):      {ds_test_aucs[ds_best_layer]:.4f}")
    print(f"  Entropy (mean per-token) AUC:     {ds_ent_auc_mean:.4f}")
    print(f"  Entropy (last-token) AUC:         {ds_ent_auc_last:.4f}")

    print(f"\n--- xtram1 (train->test, in-distribution) ---")
    print(f"  Best layer (by 5-fold CV): {xt_best_layer}")
    print(f"  Best-layer probe AUC (test):      {xt_test_aucs[xt_best_layer]:.4f}")
    print(f"  Entropy (mean per-token) AUC:     {xt_ent_auc_mean:.4f}")
    print(f"  Entropy (last-token) AUC:         {xt_ent_auc_last:.4f}")

    print(f"\n--- Cross-dataset generalization (the honest check) ---")
    print(f"  deepset->xtram1 AUC:  {ds2xt_auc:.4f}")
    print(f"  xtram1->deepset AUC:  {xt2ds_auc:.4f}")

    print(f"\n--- Per-layer test AUC (deepset) ---")
    for i, auc in enumerate(ds_test_aucs):
        marker = " <-- best (CV)" if i == ds_best_layer else ""
        print(f"  Layer {i:2d}: {auc:.4f}{marker}")

    print(f"\n--- Per-layer test AUC (xtram1) ---")
    for i, auc in enumerate(xt_test_aucs):
        marker = " <-- best (CV)" if i == xt_best_layer else ""
        print(f"  Layer {i:2d}: {auc:.4f}{marker}")

    return results


if __name__ == "__main__":
    main()
