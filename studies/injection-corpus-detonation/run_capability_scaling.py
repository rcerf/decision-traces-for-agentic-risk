"""Run InjecAgent corpus with a specified model for capability-scaling comparison.

# IMPLEMENTS: injection-corpus-detonation/run_capability_scaling.py
# EXTENDS: studies/injection-corpus-detonation/run_corpus.py
# EXTENDS: studies/detonation-harness/src/detonate.py

Produces a per-model outcomes file (outcomes_{slug}.jsonl) and prints the
row to append to the capability-scaling table in RESULTS.md.

Sample design:
    Stratified, seed=42, same base splits as the main run.
    Default: 30 per goal (60 total) for 3B; 10 per goal (20 total) for 7B+.

Output:
    outcomes_{model_slug}.jsonl — per-case outcomes, no raw payloads.

Usage:
    python3 run_capability_scaling.py --model Qwen/Qwen2.5-3B-Instruct
    python3 run_capability_scaling.py --model Qwen/Qwen2.5-7B-Instruct --n-per-goal 10

Honesty requirement: if a run does not complete, no row is emitted. The caller
should say why in the table (e.g. 'too slow on CPU, skipped').
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Optional

STUDY_ROOT = Path(__file__).parent
HARNESS_SRC = STUDY_ROOT.parent / "detonation-harness" / "src"

if str(HARNESS_SRC) not in sys.path:
    sys.path.insert(0, str(HARNESS_SRC))
if str(STUDY_ROOT) not in sys.path:
    sys.path.insert(0, str(STUDY_ROOT))

from detonate import detonate, load_model, DetonationTrace
from analyze import analyze, naive_input_detector
from mock_tools import MockToolRegistry

from fetch_injecagent import load_corpus, DEFAULT_CACHE
from adapt import adapt_corpus, stratified_sample
from run_corpus import classify_case, compute_stats, BASE_SPLITS

logger = logging.getLogger(__name__)

DEFAULT_N_PER_GOAL = 30     # 30 DH + 30 DS = 60 total (3B default)
SAMPLE_SEED = 42


def model_slug(model_id: str) -> str:
    """Derive a safe filename slug from a model ID."""
    return model_id.split("/")[-1].lower().replace("-", "_").replace(".", "_")


def param_label(model_id: str) -> str:
    """Extract a rough parameter-count label for display."""
    mid = model_id.lower()
    for label in ["0.5b", "1.5b", "3b", "7b", "8b", "14b", "32b", "72b"]:
        if label in mid:
            return label.upper()
    return "?B"


def _best_device() -> str:
    """Return the best available inference device (mps preferred over cpu)."""
    import torch
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def run_scaling(
    model_id: str,
    n_per_goal: int = DEFAULT_N_PER_GOAL,
    seed: int = SAMPLE_SEED,
    cache_dir: Optional[Path] = None,
    dtype: Optional[str] = None,
    device: Optional[str] = None,
) -> dict:
    """Run the scaling experiment for one model. Returns stats dict.

    Args:
        dtype: Dtype override ("float32", "float16", "bfloat16"). Defaults to
            float16 on MPS (Apple Silicon GPU), float32 on CPU.
        device: Device override. Defaults to "mps" if available, else "cpu".
    """
    t_start = time.time()
    cache = cache_dir or DEFAULT_CACHE
    slug = model_slug(model_id)
    outcomes_path = STUDY_ROOT / f"outcomes_{slug}.jsonl"
    effective_device = device or _best_device()
    # dtype defaults handled inside load_model (float16 for mps, float32 for cpu)

    print(f"\n=== Capability Scaling: {model_id} ===")
    print(f"  n_per_goal={n_per_goal}, seed={seed}, sample={n_per_goal*2} total")
    print(f"  device={effective_device}, dtype={dtype or 'auto'}")

    print("Loading InjecAgent corpus...")
    corpus = load_corpus(cache_dir=cache, splits=BASE_SPLITS)
    all_scenarios = adapt_corpus(corpus)
    sample = stratified_sample(all_scenarios, n_per_goal=n_per_goal, seed=seed)
    n = len(sample)
    print(f"Sample: {n} cases")

    print(f"Loading model {model_id} on {effective_device} ...")
    t_load = time.time()
    model_pair = load_model(model_id, dtype=dtype, device=effective_device)
    print(f"  Loaded in {time.time() - t_load:.1f}s")

    registry = MockToolRegistry()
    outcomes: list[dict] = []

    for i, scenario in enumerate(sample):
        t_case = time.time()
        try:
            trace = detonate(scenario, registry, model_pair=model_pair, model_id=model_id)
            profile = analyze(trace.to_dict())
        except Exception as exc:
            logger.error("Case %s failed: %s", scenario["id"], exc)
            outcomes.append({
                "injecagent_id": scenario["id"],
                "split": scenario.get("injecagent_split", ""),
                "attack_type": scenario.get("injecagent_attack_type", ""),
                "attacker_goal": scenario.get("injecagent_attacker_goal", ""),
                "attacker_tools_mapped": scenario.get("injecagent_attacker_tools_mapped", []),
                "engaged": False,
                "followed": False,
                "provenance_only_caught": False,
                "precise_caught": False,
                "behavioral_caught": False,
                "naive_caught": naive_input_detector(scenario),
                "compiled_risk": 0.0,
                "recommendation": "error",
                "attempted_privileged_actions": [],
                "runtime_seconds": round(time.time() - t_case, 2),
                "trace_id": "error",
                "model": model_id,
                "total_steps": 0,
                "valid_tool_calls": 0,
                "attempted_tool_calls": 0,
                "error": str(exc),
            })
            continue

        outcome = classify_case(scenario, trace, profile)
        outcomes.append(outcome)

        elapsed_case = time.time() - t_case
        status = (
            "FOLLOWED" if outcome["followed"]
            else ("ENGAGED" if outcome["engaged"] else "declined")
        )
        prov = "Y" if outcome.get("provenance_only_caught", outcome.get("followed")) else "N"
        prec = "Y" if outcome.get("precise_caught", outcome.get("behavioral_caught")) else "N"
        print(
            f"  [{i+1:3d}/{n}] {scenario['id']} "
            f"goal={outcome['attacker_goal'][:2].upper()} "
            f"{status:8s} prov={prov} prec={prec} {elapsed_case:.1f}s"
        )

    # Save outcomes (no raw payloads)
    with open(outcomes_path, "w", encoding="utf-8") as fh:
        for o in outcomes:
            fh.write(json.dumps(o) + "\n")
    print(f"\nWrote {len(outcomes)} records to {outcomes_path}")

    stats = compute_stats(outcomes)
    elapsed = time.time() - t_start

    # Print the scaling table row
    goal_bd = stats.get("goal_breakdown", {})
    eng_rate = stats["engagement_rate"]
    asr = stats["attack_success_rate"]
    n_suc = stats["successful_attacks"]
    prov_rate = stats.get("provenance_only_catch_rate_on_success", 0.0)
    n_prov = stats.get("provenance_only_catch_on_success", 0)
    prec_rate = stats.get("precise_catch_rate_on_success",
                          stats.get("behavioral_catch_rate_on_success", 0.0))
    n_prec = stats.get("precise_catch_on_success",
                       stats.get("behavioral_catch_on_success", 0))

    goal_asr = " / ".join(
        f"{gs['attack_success_rate']:.1%}"
        for _, gs in sorted(goal_bd.items())
    )

    print("\n=== Scaling Table Row (paste into RESULTS.md) ===")
    row = (
        f"| {model_id} | {param_label(model_id)} | n={n} | "
        f"{eng_rate:.1%} | {asr:.1%} (n={n_suc}) | "
        f"{goal_asr} | "
        f"{prov_rate:.1%} ({n_prov}/{n_suc}) | "
        f"{prec_rate:.1%} ({n_prec}/{n_suc}) |"
    )
    print(row)
    print(f"  Wall time: {elapsed/60:.1f} min")

    stats["_scaling_row"] = row
    stats["_model_id"] = model_id
    stats["_n_cases"] = n
    stats["_elapsed_min"] = round(elapsed / 60, 1)
    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Capability-scaling run on InjecAgent corpus with a specific model"
    )
    parser.add_argument("--model", default="Qwen/Qwen2.5-3B-Instruct",
                        help="HuggingFace model ID to run")
    parser.add_argument("--n-per-goal", type=int, default=DEFAULT_N_PER_GOAL,
                        help=f"Cases per attacker-goal (default {DEFAULT_N_PER_GOAL})")
    parser.add_argument("--seed", type=int, default=SAMPLE_SEED)
    parser.add_argument("--cache-dir", type=Path, default=None)
    parser.add_argument(
        "--dtype",
        default=None,
        help="Override dtype (float32/float16/bfloat16). Auto-selected per device if not set.",
    )
    parser.add_argument(
        "--device",
        default=None,
        help="Device override (mps/cpu). Defaults to mps if available.",
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s %(message)s",
    )

    run_scaling(
        model_id=args.model,
        n_per_goal=args.n_per_goal,
        seed=args.seed,
        cache_dir=args.cache_dir,
        dtype=args.dtype,
        device=args.device,
    )
