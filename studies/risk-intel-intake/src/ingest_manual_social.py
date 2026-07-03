#!/usr/bin/env python3
"""Normalize curated social/web observations into review-gated source signals."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

from ingest_common import read_json_path_or_url, source_signal, stable_id, today, write_json


def load_records(path: str) -> list[dict[str, Any]]:
    if path.endswith(".csv"):
        with Path(path).open(newline="") as fh:
            return list(csv.DictReader(fh))
    data = read_json_path_or_url(path)
    if not isinstance(data, list):
        raise ValueError("manual social input must be a JSON array or CSV")
    return data


def split_list(value: Any, default: list[str]) -> list[str]:
    if isinstance(value, list):
        return value
    if not value:
        return default
    return [item.strip() for item in str(value).split(",") if item.strip()]


def normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    url = record.get("source_url") or record.get("url") or "manual-curation"
    title = record.get("title") or "Curated social/web weak signal"
    signal_id = stable_id("SIG-SOCIAL", str(url), str(title))
    probe_id = stable_id("PROBE-SOCIAL", str(url), str(title))
    raw_policy = record.get("raw_detail_policy") or "do_not_reproduce"

    return source_signal(
        signal_id=signal_id,
        title=title,
        source_tier=3,
        source_type="social",
        source_name=record.get("source_name") or "Curated social/web stream",
        source_url=url,
        observed_at=(record.get("observed_at") or today())[:10],
        summary=record.get("summary") or "Manual weak signal requiring review.",
        risk_hypothesis=record.get("risk_hypothesis") or "This public weak signal may imply a candidate agentic-risk pattern.",
        affected_surfaces=split_list(record.get("affected_surfaces"), ["ingress", "final_output"]),
        risk_categories=split_list(record.get("risk_categories"), ["jailbreak_motif"]),
        evidence_status=record.get("evidence_status") or "unverified",
        novelty=int(record.get("novelty") or 4),
        actionability=int(record.get("actionability") or 3),
        source_reliability=int(record.get("source_reliability") or 2),
        raw_detail_policy=raw_policy,
        probe_id=probe_id,
        probe_description=record.get("safe_probe_description") or "Create a harmless probe for the abstracted pattern.",
        expected_detection_stage=record.get("expected_detection_stage") or "ingress",
        safe_reproduction=record.get("safe_reproduction") or "Use benign placeholders and do not reproduce raw exploit details.",
        notes=record.get("notes") or "Generated from review-gated manual/social intake.",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="JSON or CSV curated observations")
    parser.add_argument("--output")
    args = parser.parse_args()

    signals = [normalize_record(record) for record in load_records(args.input)]
    write_json(signals, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
