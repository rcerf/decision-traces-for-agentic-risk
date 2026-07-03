#!/usr/bin/env python3
"""Render a public-safe patch-loop case study."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = MODULE_ROOT / "data" / "agent_on_agent_patch_loop.json"
DEFAULT_OUTPUT = REPO_ROOT / "reports" / "agent_on_agent_patch_loop_case.md"

FORBIDDEN_RAW_DETAIL_MARKERS = [
    "ignore previous instructions",
    "disregard system",
    "developer mode",
    "jailbreak prompt",
    "exploit recipe",
    "step-by-step exploit",
]


def load_case(path: Path = DEFAULT_INPUT) -> dict[str, Any]:
    return json.loads(path.read_text())


def flatten_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        strings: list[str] = []
        for item in value:
            strings.extend(flatten_strings(item))
        return strings
    if isinstance(value, dict):
        strings = []
        for item in value.values():
            strings.extend(flatten_strings(item))
        return strings
    return []


def assert_public_safe(case: dict[str, Any]) -> None:
    joined = "\n".join(flatten_strings(case)).lower()
    for marker in FORBIDDEN_RAW_DETAIL_MARKERS:
        if marker in joined:
            raise ValueError(f"Case includes forbidden raw-detail marker: {marker}")


def bullet(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items]


def render(case: dict[str, Any]) -> str:
    assert_public_safe(case)
    signal = case["source_signal"]
    cell = case["risk_delta_cell"]
    probe = case["safe_probe"]
    run = case["observable_run_summary"]
    sentinel = case["sentinel_event"]
    trace = case["decision_trace_summary"]
    patch = case["patch_object"]
    monitor = case["residual_monitor"]

    lines = [
        f"# {case['title']}",
        "",
        f"Case: `{case['case_id']}`  ",
        "Status: synthetic public-safe patch-loop case",
        "",
        "## Caveat",
        "",
        case["caveat"],
        "",
        "No raw exploit content is preserved. The useful artifact is the operating loop, not the prompt content.",
        "",
        "## Loop",
        "",
        "```text",
        "safe signal summary",
        "  -> risk-delta cell",
        "  -> safe probe",
        "  -> observable run summary",
        "  -> sentinel event",
        "  -> decision trace summary",
        "  -> patch object",
        "  -> residual monitor",
        "```",
        "",
        "## Source Signal",
        "",
        f"- Source type: {signal['source_type']}",
        f"- Confidence: {signal['source_confidence']}",
        f"- Raw-detail policy: `{signal['raw_detail_policy']}`",
        f"- Summary: {signal['summary']}",
        "",
        "## Risk-Delta Cell",
        "",
        f"- Capability delta: {cell['capability_delta']}",
        f"- Risk class: {cell['risk_class']}",
        f"- Shared surfaces: {', '.join(cell['shared_surfaces'])}",
        f"- Why it matters: {cell['why_it_matters']}",
        "",
        "## Safe Probe",
        "",
        f"- Probe: `{probe['probe_id']}`",
        f"- Description: {probe['description']}",
        "",
        "Safety controls:",
        "",
        *bullet(probe["safety_controls"]),
        "",
        "## Observable Run Summary",
        "",
        f"- Target task: {run['target_task']}",
        f"- Observed failure mode: {run['observed_failure_mode']}",
        f"- First useful intervention: `{run['first_useful_intervention']}`",
        f"- Affected controls: {', '.join(run['affected_controls'])}",
        "",
        "## Sentinel Event",
        "",
        f"- Stage: `{sentinel['stage']}`",
        f"- Category: `{sentinel['category']}`",
        f"- Severity: `{sentinel['severity']}`",
        f"- Signal: {sentinel['signal']}",
        f"- Recommended action: {sentinel['recommended_action']}",
        "",
        "## Decision Trace Summary",
        "",
        f"- Owner: {trace['owner']}",
        f"- Decision needed: {trace['decision_needed']}",
        f"- Residual risk: {trace['residual_risk']}",
        "",
        "## Patch Object",
        "",
        f"- Type: `{patch['type']}`",
        f"- Description: {patch['description']}",
        f"- Verification: {patch['verification']}",
        f"- Rollout note: {patch['rollout_note']}",
        "",
        "## Residual Monitor",
        "",
        f"- Monitor: `{monitor['monitor_id']}`",
        "",
        "Metrics:",
        "",
        *bullet(monitor["metrics"]),
        "",
        f"Reopen trigger: {monitor['reopen_trigger']}",
        "",
    ]
    return "\n".join(lines)


def generate(input_path: Path = DEFAULT_INPUT, output_path: Path = DEFAULT_OUTPUT) -> str:
    report = render(load_case(input_path))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = generate(args.input, args.output)
    print(f"Wrote {args.output}")
    print(f"{len(report.splitlines())} lines")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

