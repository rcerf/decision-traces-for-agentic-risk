"""Recompute RESULTS.md from existing outcomes files (no model inference).

# IMPLEMENTS: injection-corpus-detonation/recompute_results.py
# EXTENDS: studies/injection-corpus-detonation/run_corpus.py

Reads outcomes.jsonl (and optionally outcomes_*.jsonl for scaling rows),
recomputes all aggregate stats, and rewrites RESULTS.md.  Run this after
updating run_corpus.py analysis logic without needing a full model re-run.

Usage:
    python3 recompute_results.py
    python3 recompute_results.py --scaling-files outcomes_qwen2_5_3b_instruct.jsonl
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

STUDY_ROOT = Path(__file__).parent
OUTCOMES_PATH = STUDY_ROOT / "outcomes.jsonl"
RESULTS_PATH = STUDY_ROOT / "RESULTS.md"


def load_outcomes(path: Path) -> list[dict]:
    """Load a JSONL outcomes file."""
    outcomes = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                outcomes.append(json.loads(line))
    return outcomes


def outcomes_to_stats(outcomes: list[dict]) -> dict:
    """Compute stats from outcomes list — delegates to run_corpus.compute_stats."""
    import sys
    if str(STUDY_ROOT) not in sys.path:
        sys.path.insert(0, str(STUDY_ROOT))
    from run_corpus import compute_stats
    return compute_stats(outcomes)


def scaling_row(outcomes: list[dict], outcomes_path: Path) -> str:
    """Build one capability-scaling table row from an outcomes file."""
    if not outcomes:
        return ""
    stats = outcomes_to_stats(outcomes)
    model_id = outcomes[0].get("model", "unknown")
    n = stats["total_cases"]
    eng = stats["engagement_rate"]
    asr = stats["attack_success_rate"]
    n_suc = stats["successful_attacks"]
    prov_rate = stats.get("provenance_only_catch_rate_on_success", 0.0)
    n_prov = stats.get("provenance_only_catch_on_success", 0)
    prec_rate = stats.get("precise_catch_rate_on_success",
                          stats.get("behavioral_catch_rate_on_success", 0.0))
    n_prec = stats.get("precise_catch_on_success",
                       stats.get("behavioral_catch_on_success", 0))
    goal_bd = stats.get("goal_breakdown", {})
    goal_asr = " / ".join(
        f"{gs['attack_success_rate']:.1%}"
        for _, gs in sorted(goal_bd.items())
    )
    # Extract param label from model_id
    mid = model_id.lower()
    plabel = next((lb.upper() for lb in ["0.5b", "1.5b", "3b", "7b", "8b"] if lb in mid), "?B")
    return (
        f"| {model_id} | {plabel} | n={n}, seed=42 | "
        f"{eng:.1%} | {asr:.1%} (n={n_suc}) | "
        f"{goal_asr} | "
        f"{prov_rate:.1%} ({n_prov}/{n_suc}) | "
        f"{prec_rate:.1%} ({n_prec}/{n_suc}) |"
    )


def build_scaling_table(main_outcomes: list[dict], extra_paths: list[Path]) -> str:
    """Assemble the full scaling table markdown."""
    header = (
        "| Model | Params | Sample | Tool-engagement | Attack-success% | "
        "by goal (data-stealing / direct-harm) | Prov-Only catch | Precise catch |\n"
        "|-------|--------|--------|-----------------|-----------------|"
        "----------------------------------------|-----------------|---------------|\n"
    )
    rows = [scaling_row(main_outcomes, OUTCOMES_PATH)]
    for p in extra_paths:
        if p.exists():
            extra_outcomes = load_outcomes(p)
            rows.append(scaling_row(extra_outcomes, p))
        else:
            rows.append(f"| (file not found: {p.name}) | — | — | — | — | — | — | — |")
    return header + "\n".join(r for r in rows if r)


def main(scaling_files: list[Path]) -> None:
    """Recompute and write RESULTS.md."""
    print(f"Loading {OUTCOMES_PATH} ...")
    outcomes = load_outcomes(OUTCOMES_PATH)
    print(f"  {len(outcomes)} records")

    stats = outcomes_to_stats(outcomes)
    elapsed_min = 25.2  # original run wall time — preserved for accuracy
    model_id = outcomes[0].get("model", "Qwen/Qwen2.5-1.5B-Instruct")
    sample_info = "Stratified random, 75 per attacker-goal from base splits, seed=42"

    scaling_table_md = build_scaling_table(outcomes, scaling_files)

    import sys
    if str(STUDY_ROOT) not in sys.path:
        sys.path.insert(0, str(STUDY_ROOT))
    from run_corpus import write_results_md
    write_results_md(
        stats=stats,
        sample_info=sample_info,
        model_id=model_id,
        elapsed=elapsed_min * 60,
        scaling_table_md=scaling_table_md,
    )
    print("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recompute RESULTS.md from outcomes files")
    parser.add_argument(
        "--scaling-files",
        nargs="*",
        type=Path,
        default=[],
        help="Extra outcomes_*.jsonl files for capability-scaling rows",
    )
    args = parser.parse_args()
    main(args.scaling_files)
