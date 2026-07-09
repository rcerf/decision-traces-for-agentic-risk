#!/usr/bin/env python3
"""Validate agentic risk traces against the shipped JSON Schema.

Uses jsonschema.validate for structural validation (required fields, enum
values, object shapes) and then applies a small set of cross-field
business-logic checks that cannot be expressed in JSON Schema alone (e.g.,
high/critical traces must declare active approval gates).

Coverage:
- examples/*.json
- examples/real_incidents/*.json  (and any future subdirectories)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema


# Resolved relative to this file so the script works from any cwd.
_SCHEMA_PATH = (
    Path(__file__).resolve().parent.parent / "schema" / "agentic_risk_trace.schema.json"
)
_SCHEMA: dict | None = None


def _load_schema() -> dict:
    global _SCHEMA
    if _SCHEMA is None:
        _SCHEMA = json.loads(_SCHEMA_PATH.read_text())
    return _SCHEMA


def load_trace(path: Path) -> dict:
    with path.open() as fh:
        return json.load(fh)


def validate_trace(trace: dict) -> list[str]:
    """Validate a single trace.

    Returns a list of error strings.  An empty list means PASS.

    Step 1 — JSON Schema: structural conformance against
    schema/agentic_risk_trace.schema.json (required fields, types, enums).

    Step 2 — Business logic: cross-field rules not expressible in JSON Schema
    (severity × approval_gate combinations that indicate missing controls).
    """
    errors: list[str] = []
    schema = _load_schema()

    # --- Step 1: JSON Schema structural validation ---
    try:
        jsonschema.validate(trace, schema)
    except jsonschema.ValidationError as e:
        errors.append(f"schema: {e.message}")
        # Structural failure; skip cross-field checks that assume field presence.
        return errors

    # --- Step 2: Cross-field business-logic checks ---
    approval = trace.get("human_approval", {})
    severity = trace.get("severity")

    if severity in {"high", "critical"}:
        if not approval.get("required"):
            errors.append("high/critical trace lacks human approval requirement")
        if approval.get("approval_gate") == "none":
            errors.append("high/critical trace lacks approval gate")
        if not trace.get("owner"):
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
    # rglob finds root-level traces and all subdirectories (e.g. real_incidents/).
    paths = sorted(examples_dir.rglob("*.json"))
    if not paths:
        print(f"No trace files found in {examples_dir}", file=sys.stderr)
        return 2

    traces = []
    failed = False
    for path in paths:
        trace = load_trace(path)
        traces.append(trace)
        errors = validate_trace(trace)
        # Show path relative to examples_dir so subdirectory is visible.
        try:
            label = path.relative_to(examples_dir)
        except ValueError:
            label = path.name
        if errors:
            failed = True
            print(f"FAIL {label}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {label}")

    print("\nSummary")
    print(json.dumps(summarize(traces), indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
