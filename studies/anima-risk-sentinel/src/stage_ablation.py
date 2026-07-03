#!/usr/bin/env python3
"""Compare staged sentinel coverage against final-only review."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SENTINEL_PATH = ROOT / "src" / "risk_sentinel.py"

spec = importlib.util.spec_from_file_location("risk_sentinel", SENTINEL_PATH)
risk_sentinel = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = risk_sentinel
spec.loader.exec_module(risk_sentinel)


CONDITIONS = {
    "final_only": {"final"},
    "ingress_final": {"ingress", "final"},
    "ingress_trajectory_final": {"ingress", "trajectory", "final"},
    "full_pipeline": {"ingress", "trajectory", "draft", "final"},
}


def condition_report(report: dict, enabled_stages: set[str]) -> dict:
    events = [ev for ev in report["events"] if ev["stage"] in enabled_stages]
    first_stage = "none"
    if events:
        for stage in risk_sentinel.STAGE_ORDER:
            if any(ev["stage"] == stage for ev in events):
                first_stage = stage
                break

    categories = sorted({ev["category"] for ev in events})
    return {
        "risk_present": bool(events),
        "first_detection_stage": first_stage,
        "event_count": len(events),
        "categories": categories,
    }


def run_ablation(input_path: Path) -> dict:
    runs = risk_sentinel.load_runs(input_path)
    base_reports = [risk_sentinel.analyze_run(run) for run in runs]

    conditions = {}
    for name, stages in CONDITIONS.items():
        per_run = {}
        detected = 0
        total_events = 0
        for report in base_reports:
            cr = condition_report(report, stages)
            per_run[report["run_id"]] = cr
            detected += int(cr["risk_present"])
            total_events += cr["event_count"]
        conditions[name] = {
            "detected_runs": detected,
            "total_events": total_events,
            "per_run": per_run,
        }

    return {
        "run_count": len(base_reports),
        "conditions": conditions,
    }


def main(argv: list[str]) -> int:
    input_path = Path(argv[1]) if len(argv) > 1 else ROOT / "data" / "runs"
    print(json.dumps(run_ablation(input_path), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
