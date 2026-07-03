#!/usr/bin/env python3
"""Convert source signals into taxonomy candidates and a safe probe backlog."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


REQUIRED = {
    "signal_id",
    "title",
    "source_tier",
    "source_type",
    "source_name",
    "source_url",
    "observed_at",
    "summary",
    "risk_hypothesis",
    "affected_surfaces",
    "risk_categories",
    "evidence_status",
    "novelty",
    "actionability",
    "source_reliability",
    "raw_detail_policy",
    "proposed_probe",
}

EVIDENCE_WEIGHT = {
    "unverified": 0,
    "corroborated": 1,
    "reproduced": 2,
    "benchmark": 2,
    "authoritative": 2,
}


@dataclass(frozen=True)
class ProbeBacklogItem:
    probe_id: str
    source_signal: str
    priority: int
    title: str
    risk_categories: list[str]
    affected_surfaces: list[str]
    expected_detection_stage: str
    description: str
    safe_reproduction: str
    review_required: bool
    raw_detail_policy: str


def load_signals(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text())
    if not isinstance(data, list):
        raise ValueError("source signal file must contain a JSON array")
    return data


def validate_signal(signal: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED - set(signal))
    if missing:
        errors.append(f"missing required fields: {', '.join(missing)}")

    if signal.get("source_tier") not in {0, 1, 2, 3}:
        errors.append(f"invalid source_tier: {signal.get('source_tier')}")

    for field in ("novelty", "actionability", "source_reliability"):
        value = signal.get(field)
        if not isinstance(value, int) or not 1 <= value <= 5:
            errors.append(f"{field} must be integer 1-5")

    if signal.get("raw_detail_policy") not in {"safe_to_store", "summarize_only", "do_not_reproduce"}:
        errors.append(f"invalid raw_detail_policy: {signal.get('raw_detail_policy')}")

    probe = signal.get("proposed_probe", {})
    for key in ("probe_id", "description", "expected_detection_stage", "safe_reproduction"):
        if key not in probe:
            errors.append(f"proposed_probe missing {key}")

    if not signal.get("risk_categories"):
        errors.append("risk_categories cannot be empty")
    if not signal.get("affected_surfaces"):
        errors.append("affected_surfaces cannot be empty")

    return errors


def priority(signal: dict[str, Any]) -> int:
    """Compute a 0-100 operational priority.

    Novel signals are useful, but actionability and reliability matter more for
    probe generation. Tier 3 social signals can still rise if they are highly
    novel and actionable, but they route to human review until corroborated.
    """

    novelty = int(signal["novelty"])
    actionability = int(signal["actionability"])
    reliability = int(signal["source_reliability"])
    evidence = EVIDENCE_WEIGHT.get(signal["evidence_status"], 0)
    tier = int(signal["source_tier"])
    tier_bonus = {0: 12, 1: 10, 2: 6, 3: 0}[tier]

    score = (novelty * 4) + (actionability * 8) + (reliability * 5) + (evidence * 6) + tier_bonus
    return min(100, score)


def review_required(signal: dict[str, Any]) -> bool:
    return (
        signal["source_tier"] == 3
        or signal["evidence_status"] == "unverified"
        or signal["raw_detail_policy"] == "do_not_reproduce"
    )


def build_probe(signal: dict[str, Any]) -> ProbeBacklogItem:
    probe = signal["proposed_probe"]
    return ProbeBacklogItem(
        probe_id=probe["probe_id"],
        source_signal=signal["signal_id"],
        priority=priority(signal),
        title=signal["title"],
        risk_categories=sorted(signal["risk_categories"]),
        affected_surfaces=sorted(signal["affected_surfaces"]),
        expected_detection_stage=probe["expected_detection_stage"],
        description=probe["description"],
        safe_reproduction=probe["safe_reproduction"],
        review_required=review_required(signal),
        raw_detail_policy=signal["raw_detail_policy"],
    )


def summarize(signals: list[dict[str, Any]]) -> dict[str, Any]:
    by_tier: dict[str, int] = {}
    by_category: dict[str, int] = {}
    by_surface: dict[str, int] = {}
    review_queue: list[str] = []
    no_raw_reproduction: list[str] = []

    probes = [build_probe(signal) for signal in signals]
    probes.sort(key=lambda item: (-item.priority, item.probe_id))

    for signal in signals:
        tier = str(signal["source_tier"])
        by_tier[tier] = by_tier.get(tier, 0) + 1
        if review_required(signal):
            review_queue.append(signal["signal_id"])
        if signal["raw_detail_policy"] == "do_not_reproduce":
            no_raw_reproduction.append(signal["signal_id"])

        for category in signal["risk_categories"]:
            by_category[category] = by_category.get(category, 0) + 1
        for surface in signal["affected_surfaces"]:
            by_surface[surface] = by_surface.get(surface, 0) + 1

    return {
        "signal_count": len(signals),
        "by_source_tier": dict(sorted(by_tier.items())),
        "taxonomy_candidates": dict(sorted(by_category.items())),
        "affected_surfaces": dict(sorted(by_surface.items())),
        "review_queue": sorted(review_queue),
        "do_not_reproduce_raw_details": sorted(no_raw_reproduction),
        "probe_backlog": [asdict(probe) for probe in probes],
    }


def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else Path("data/source_signals/sample_public_signals.json")
    signals = load_signals(path)

    failed = False
    for signal in signals:
        errors = validate_signal(signal)
        if errors:
            failed = True
            print(f"FAIL {signal.get('signal_id', '<missing id>')}", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)

    if failed:
        return 1

    print(json.dumps(summarize(signals), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
