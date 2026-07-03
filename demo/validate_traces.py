#!/usr/bin/env python3
"""Validate synthetic agentic risk traces.

This intentionally uses only the Python standard library. It is not a full
JSON Schema implementation; it checks the fields that matter for the demo:
required keys, enum values, and high/critical traces lacking approval gates.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


REQUIRED = {
    "trace_id",
    "title",
    "source_signal",
    "agentic_surface",
    "risk_category",
    "evidence",
    "confidence",
    "severity",
    "recommended_action",
    "owner",
    "mitigation_status",
    "human_approval",
    "residual_risk",
    "next_review",
}

CONFIDENCE = {"low", "medium", "high"}
SEVERITY = {"low", "medium", "high", "critical"}
MITIGATION_STATUS = {"none", "proposed", "in_progress", "deployed", "needs_review"}
APPROVAL_GATES = {
    "none",
    "before_external_side_effect",
    "before_sensitive_data_access",
    "before_cross_connector_action",
    "before_high_risk_advice",
    "before_policy_exception",
}


def load_trace(path: Path) -> dict:
    with path.open() as fh:
        return json.load(fh)


def validate_trace(trace: dict) -> list[str]:
    errors: list[str] = []

    missing = sorted(REQUIRED - set(trace))
    if missing:
        errors.append(f"missing required fields: {', '.join(missing)}")

    if trace.get("confidence") not in CONFIDENCE:
        errors.append(f"invalid confidence: {trace.get('confidence')}")

    if trace.get("severity") not in SEVERITY:
        errors.append(f"invalid severity: {trace.get('severity')}")

    if trace.get("mitigation_status") not in MITIGATION_STATUS:
        errors.append(f"invalid mitigation_status: {trace.get('mitigation_status')}")

    evidence = trace.get("evidence", {})
    for key in ("observed_behavior", "why_it_matters", "open_questions"):
        if key not in evidence:
            errors.append(f"evidence missing {key}")

    approval = trace.get("human_approval", {})
    if "required" not in approval:
        errors.append("human_approval missing required")
    if approval.get("approval_gate") not in APPROVAL_GATES:
        errors.append(f"invalid approval_gate: {approval.get('approval_gate')}")

    if trace.get("severity") in {"high", "critical"}:
        if not approval.get("required"):
            errors.append("high/critical trace lacks human approval requirement")
        if approval.get("approval_gate") == "none":
            errors.append("high/critical trace lacks approval gate")

    if trace.get("severity") in {"high", "critical"} and not trace.get("owner"):
        errors.append("high/critical trace lacks owner")

    return errors


def summarize(traces: list[dict]) -> dict:
    by_severity: dict[str, int] = {}
    by_category: dict[str, int] = {}
    high_without_deployed_mitigation = []

    for trace in traces:
        sev = trace["severity"]
        cat = trace["risk_category"]
        by_severity[sev] = by_severity.get(sev, 0) + 1
        by_category[cat] = by_category.get(cat, 0) + 1
        if sev in {"high", "critical"} and trace["mitigation_status"] != "deployed":
            high_without_deployed_mitigation.append(trace["trace_id"])

    return {
        "trace_count": len(traces),
        "by_severity": dict(sorted(by_severity.items())),
        "by_category": dict(sorted(by_category.items())),
        "high_or_critical_without_deployed_mitigation": high_without_deployed_mitigation,
    }


def main(argv: list[str]) -> int:
    examples_dir = Path(argv[1]) if len(argv) > 1 else Path("examples")
    paths = sorted(examples_dir.glob("*.json"))
    if not paths:
        print(f"No trace files found in {examples_dir}", file=sys.stderr)
        return 2

    traces = []
    failed = False
    for path in paths:
        trace = load_trace(path)
        traces.append(trace)
        errors = validate_trace(trace)
        if errors:
            failed = True
            print(f"FAIL {path.name}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {path.name}")

    print("\nSummary")
    print(json.dumps(summarize(traces), indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
