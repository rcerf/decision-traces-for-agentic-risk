#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if command -v python >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python)"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  echo "ERROR: neither python nor python3 is available on PATH" >&2
  exit 127
fi

run() {
  local label="$1"
  shift
  echo
  echo "==> RUNNING: ${label}"
  "$@"
}

skip() {
  local label="$1"
  local reason="$2"
  echo
  echo "==> SKIPPED (${reason}): ${label}"
}

has_cached_qwen_harness_model() {
  local cache_root="${HF_HOME:-${HOME}/.cache/huggingface}/hub"
  [[ -d "${cache_root}/models--Qwen--Qwen2.5-1.5B-Instruct" ]] \
    || [[ -d "${cache_root}/models--Qwen--Qwen2.5-0.5B-Instruct" ]]
}

run "pytest full suite" "$PYTHON_BIN" -m pytest -q
run "benchmark regex injection benchmark" "$PYTHON_BIN" benchmark/run_injection_benchmark.py
run "deterministic eval scorer" "$PYTHON_BIN" evals/run_eval.py

if has_cached_qwen_harness_model; then
  run "detonation harness factory (cached small Qwen only)" \
    env HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 "$PYTHON_BIN" studies/detonation-harness/src/run_factory.py
else
  skip "detonation harness factory" "small Qwen model is not cached locally; avoiding model download"
fi

if [[ -f studies/injection-ontology/corpus_cache/hackaprompt_cache.json ]]; then
  run "injection ontology classifier from local cache" \
    "$PYTHON_BIN" studies/injection-ontology/classify.py --sample 3000
else
  skip "injection ontology classifier" "raw corpus cache is absent; avoiding corpus download"
fi

run "injection corpus results recompute from existing outcomes" \
  "$PYTHON_BIN" studies/injection-corpus-detonation/recompute_results.py \
    --scaling-files \
    studies/injection-corpus-detonation/outcomes_qwen2_5_3b_instruct.jsonl \
    studies/injection-corpus-detonation/outcomes_qwen2_5_7b_instruct.jsonl

run "provenance action gate results generator" \
  "$PYTHON_BIN" studies/provenance-action-gate/src/compare_detection_vs_gate.py

skip "benchmark/run_model_benchmark.py" "loads ProtectAI DeBERTa and is documented as a 3-5 minute model inference run"
skip "benchmark/train_classifier.py" "trains and writes model artifacts; MODEL_RESULTS.md already records existing capability numbers"
skip "studies/injection-corpus-detonation/run_corpus.py" "150-case model run is documented as 25.2 minutes"
skip "studies/injection-corpus-detonation/run_capability_scaling.py" "larger-model scaling is outside the bounded cycle"
skip "benchmark/fetch_data.py and benchmark/fetch_second_dataset.py" "network fetches are not needed because snapshots are present"
skip "studies/injection-corpus-detonation/fetch_injecagent.py" "raw payload cache fetch is gitignored and not needed for recompute"

echo
echo "run_all.sh complete"
