#!/usr/bin/env python3
"""Local-first agentic risk monitor.

This is deliberately deterministic. The goal is to make the detection logic
auditable before replacing or augmenting signatures with a local classifier.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


MODULE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SIGNATURES = MODULE_ROOT / "rules" / "risk_signatures.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def evidence_excerpt(text: str, limit: int = 160) -> str:
    clean = " ".join(str(text or "").split())
    return clean[:limit]


def regex_events(session: dict[str, Any], rule: dict[str, Any]) -> list[dict[str, Any]]:
    targets: list[tuple[str, str]] = []
    if rule["target"] in {"input", "input_or_output"}:
        targets.append(("input", session.get("user_prompt", "")))
        for item in session.get("retrieved_context", []):
            targets.append((f"retrieved:{item.get('source', 'unknown')}", item.get("content", "")))
    if rule["target"] in {"output", "input_or_output"}:
        targets.append(("output", session.get("model_output", "")))

    events: list[dict[str, Any]] = []
    for stage, text in targets:
        for pattern in rule.get("patterns", []):
            if re.search(pattern, str(text or ""), flags=re.IGNORECASE):
                events.append(build_event(session, rule, stage, text, pattern))
                break
    return events


def tool_events(session: dict[str, Any], rule: dict[str, Any]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for call in session.get("tool_calls", []):
        approval = call.get("approval", {})
        args_text = json.dumps(call.get("args", {}), sort_keys=True).lower()

        if rule.get("requires_external_side_effect") and not call.get("external_side_effect"):
            continue
        if rule.get("requires_missing_approval") and approval.get("received"):
            continue
        if rule.get("sensitive_terms") and not any(term in args_text for term in rule["sensitive_terms"]):
            continue

        evidence = json.dumps(
            {
                "tool": call.get("tool"),
                "connector": call.get("connector"),
                "external_side_effect": call.get("external_side_effect"),
                "approval": approval,
                "args": call.get("args", {}),
            },
            sort_keys=True,
        )
        events.append(build_event(session, rule, "tool_call", evidence, "tool-condition"))
    return events


def telemetry_events(session: dict[str, Any], rule: dict[str, Any]) -> list[dict[str, Any]]:
    telemetry = session.get("telemetry", {})
    thresholds = rule.get("thresholds", {})
    entropy = float(telemetry.get("tool_choice_entropy", 0.0) or 0.0)
    margin = float(telemetry.get("top_choice_margin", 1.0) or 1.0)
    disagreement = float(telemetry.get("sample_disagreement", 0.0) or 0.0)

    if (
        entropy >= float(thresholds.get("tool_choice_entropy_min", 999))
        and margin <= float(thresholds.get("top_choice_margin_max", -1))
        and disagreement >= float(thresholds.get("sample_disagreement_min", 999))
    ):
        return [
            build_event(
                session,
                rule,
                "telemetry",
                json.dumps(telemetry, sort_keys=True),
                "telemetry-threshold",
            )
        ]
    return []


def build_event(
    session: dict[str, Any],
    rule: dict[str, Any],
    stage: str,
    evidence: str,
    match: str,
) -> dict[str, Any]:
    return {
        "session_id": session["session_id"],
        "model": session.get("model", "unknown"),
        "signature_id": rule["signature_id"],
        "signature_name": rule["name"],
        "category": rule["category"],
        "severity": rule["severity"],
        "stage": stage,
        "match": match,
        "evidence_excerpt": evidence_excerpt(evidence),
        "evidence_hash": text_hash(str(evidence)),
        "recommended_action": rule["recommended_action"],
    }


def scan_session(session: dict[str, Any], signatures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for rule in signatures:
        target = rule["target"]
        if target in {"input", "output", "input_or_output"}:
            events.extend(regex_events(session, rule))
        elif target == "tool_call":
            events.extend(tool_events(session, rule))
        elif target == "telemetry":
            events.extend(telemetry_events(session, rule))
    return events


def summarize(events: list[dict[str, Any]]) -> dict[str, Any]:
    by_category: dict[str, int] = {}
    by_severity: dict[str, int] = {}
    by_signature: dict[str, int] = {}
    for event in events:
        by_category[event["category"]] = by_category.get(event["category"], 0) + 1
        by_severity[event["severity"]] = by_severity.get(event["severity"], 0) + 1
        by_signature[event["signature_id"]] = by_signature.get(event["signature_id"], 0) + 1
    return {
        "event_count": len(events),
        "by_category": dict(sorted(by_category.items())),
        "by_severity": dict(sorted(by_severity.items())),
        "by_signature": dict(sorted(by_signature.items())),
    }


def scan_file(session_path: Path, signature_path: Path) -> dict[str, Any]:
    sessions = load_json(session_path)
    signatures = load_json(signature_path)
    events: list[dict[str, Any]] = []
    for session in sessions:
        events.extend(scan_session(session, signatures))
    return {
        "source": str(session_path),
        "signature_pack": str(signature_path),
        "summary": summarize(events),
        "events": events,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sessions", type=Path)
    parser.add_argument("--signatures", type=Path, default=DEFAULT_SIGNATURES)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = scan_file(args.sessions, args.signatures)
    rendered = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(rendered)
        print(f"Wrote {args.output}")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

