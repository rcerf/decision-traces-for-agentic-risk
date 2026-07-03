#!/usr/bin/env python3
"""Ingest MIT AI Incident Tracker trend/insight text as source signals."""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path
from urllib.request import Request, urlopen

from ingest_common import USER_AGENT, clean_text, source_signal, stable_id, today, write_json


DEFAULT_URL = "https://airisk.mit.edu/ai-incident-tracker/incident-timeline"


def fetch_html(url: str) -> str:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", "ignore")


def strip_tags(fragment: str) -> str:
    text = re.sub(r"<script.*?</script>", " ", fragment, flags=re.I | re.S)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return clean_text(html.unescape(text))


def extract_insights(html_text: str) -> list[str]:
    list_items = [strip_tags(match) for match in re.findall(r"<li[^>]*>(.*?)</li>", html_text, flags=re.I | re.S)]
    filtered = []
    for item in list_items:
        if "Insights:" in item:
            item = item.split("Insights:", 1)[1]
        item = clean_text(item.strip(" ]"))
        if item and any(token in item.lower() for token in ("incident", "harm", "risk", "fraud", "scam", "severity", "intentionally")):
            filtered.append(item)
    if filtered:
        return filtered[:8]

    text = strip_tags(html_text)
    candidates = []
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        lower = sentence.lower()
        if any(token in lower for token in ("reported incidents", "harm", "risk", "fraud", "scams", "intentionally caused")):
            candidates.append(sentence)
    return candidates[:8]


def insights_to_signals(insights: list[str], source_url: str) -> list[dict]:
    signals = []
    for idx, insight in enumerate(insights, start=1):
        signal_id = stable_id("SIG-MIT", str(idx), insight)
        probe_id = stable_id("PROBE-MIT", str(idx), insight)
        signals.append(
            source_signal(
                signal_id=signal_id,
                title=f"MIT AI Incident Tracker insight {idx}",
                source_tier=2,
                source_type="incident_database",
                source_name="MIT AI Incident Tracker",
                source_url=source_url,
                observed_at=today(),
                summary=insight,
                risk_hypothesis="Incident trends can identify publicly salient harm categories that should be mapped to agentic surfaces and safe probes.",
                affected_surfaces=["governance", "final_output"],
                risk_categories=["incident_taxonomy", "real_world_harm", "public_salience"],
                evidence_status="corroborated",
                novelty=3,
                actionability=3,
                source_reliability=4,
                raw_detail_policy="safe_to_store",
                probe_id=probe_id,
                probe_description="Translate the trend into a taxonomy-gap question and identify whether the current probe set covers the harm pathway.",
                expected_detection_stage="governance",
                safe_reproduction="Use trend-level categories and synthetic probes rather than reproducing incident details.",
                notes="Generated from MIT AI Incident Tracker trend page; treat LLM-classified trends as indicative.",
            )
        )
    return signals


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--html-file", help="Use local HTML fixture instead of fetching URL")
    parser.add_argument("--output")
    args = parser.parse_args()

    html_text = Path(args.html_file).read_text() if args.html_file else fetch_html(args.url)
    write_json(insights_to_signals(extract_insights(html_text), args.url), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
