#!/usr/bin/env python3
"""Ingest AI Incident Database lookups or incident snapshots.

AIID exposes a public lookup-by-URL endpoint. For bulk intake, this adapter also
supports local or remote JSON snapshots, because public exports can move without
changing the downstream source_signal schema.
"""

from __future__ import annotations

import argparse
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from ingest_common import USER_AGENT, clean_text, read_json_path_or_url, source_signal, stable_id, today, write_json


AIID_LOOKUP = "https://incidentdatabase.ai/api/lookupbyurl"


def lookup_url(url: str) -> dict[str, Any]:
    req = Request(f"{AIID_LOOKUP}?{urlencode({'url': url})}", headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=30) as response:
        return read_response_json(response)


def read_response_json(response) -> Any:
    import json

    return json.loads(response.read().decode("utf-8"))


def lookup_records_to_signals(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    signals = []
    for record in records:
        url = record["url"]
        result = lookup_url(url)
        result_count = len(result.get("results", [])) if isinstance(result, dict) else 0
        title = record.get("title") or f"AIID lookup for {url}"
        signal_id = stable_id("SIG-AIID", url)
        probe_id = stable_id("PROBE-AIID", url)
        signals.append(
            source_signal(
                signal_id=signal_id,
                title=title,
                source_tier=2,
                source_type="incident_database",
                source_name="AI Incident Database lookupbyurl",
                source_url=url,
                observed_at=record.get("observed_at") or today(),
                summary=f"AIID lookup returned {result_count} matching result(s) for the source URL.",
                risk_hypothesis="Incident-linked public reports can reveal real-world harms that should broaden the probe backlog beyond security-only failure modes.",
                affected_surfaces=["governance", "final_output"],
                risk_categories=["incident_taxonomy", "real_world_harm", "severity_mapping"],
                evidence_status="corroborated" if result_count else "unverified",
                novelty=3,
                actionability=3 if result_count else 2,
                source_reliability=4,
                raw_detail_policy="safe_to_store",
                probe_id=probe_id,
                probe_description="If the URL maps to an incident, abstract the harm pathway into one or more safe agentic-risk probes.",
                expected_detection_stage="governance",
                safe_reproduction="Use incident category summaries and synthetic placeholders rather than recreating harmful details.",
                notes=f"lookup_result_count={result_count}",
            )
        )
    return signals


def snapshot_item_to_signal(item: dict[str, Any]) -> dict[str, Any]:
    incident_id = clean_text(item.get("incident_id") or item.get("id") or item.get("number") or item.get("url"))
    title = clean_text(item.get("title") or item.get("name") or item.get("description") or f"AI incident {incident_id}")
    url = clean_text(item.get("url") or item.get("source_url") or item.get("report_url") or "manual-snapshot")
    summary = clean_text(item.get("summary") or item.get("description") or item.get("text") or title)
    signal_id = stable_id("SIG-AIID", incident_id, title)
    probe_id = stable_id("PROBE-AIID", incident_id, title)
    return source_signal(
        signal_id=signal_id,
        title=title,
        source_tier=2,
        source_type="incident_database",
        source_name="AI Incident Database snapshot",
        source_url=url,
        observed_at=clean_text(item.get("date") or item.get("observed_at") or today())[:10],
        summary=summary[:900],
        risk_hypothesis="This incident suggests a real-world harm pathway that may require an agentic-risk taxonomy cell or probe.",
        affected_surfaces=["governance", "final_output"],
        risk_categories=["incident_taxonomy", "real_world_harm", "severity_mapping"],
        evidence_status="corroborated",
        novelty=3,
        actionability=3,
        source_reliability=4,
        raw_detail_policy="summarize_only",
        probe_id=probe_id,
        probe_description="Map the incident harm pathway to affected agentic surfaces and create a safe synthetic reproduction.",
        expected_detection_stage="governance",
        safe_reproduction="Use only high-level incident summary and category labels.",
        notes="Generated from AIID-style snapshot input.",
    )


def snapshot_to_signals(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, dict):
        for key in ("incidents", "reports", "results", "data"):
            if isinstance(data.get(key), list):
                data = data[key]
                break
    if not isinstance(data, list):
        raise ValueError("snapshot input must be a list or contain incidents/reports/results/data list")
    return [snapshot_item_to_signal(item) for item in data if isinstance(item, dict)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lookup-urls", help="JSON list of {url,title,observed_at} records to enrich with AIID lookupbyurl")
    parser.add_argument("--snapshot", help="Local path or URL for AIID-style JSON snapshot")
    parser.add_argument("--output")
    args = parser.parse_args()

    if not args.lookup_urls and not args.snapshot:
        parser.error("provide --lookup-urls or --snapshot")

    signals = []
    if args.lookup_urls:
        signals.extend(lookup_records_to_signals(read_json_path_or_url(args.lookup_urls)))
    if args.snapshot:
        signals.extend(snapshot_to_signals(read_json_path_or_url(args.snapshot)))

    write_json(signals, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
