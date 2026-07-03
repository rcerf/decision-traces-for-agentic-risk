#!/usr/bin/env python3
"""Ingest arXiv search results into source_signal records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

from ingest_common import USER_AGENT, clean_text, source_signal, stable_id, today, write_json


ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV_API = "https://export.arxiv.org/api/query"


def fetch_arxiv(query: str, max_results: int) -> str:
    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    req = Request(f"{ARXIV_API}?{urlencode(params)}", headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8")


def parse_feed(xml_text: str) -> list[dict[str, str]]:
    root = ET.fromstring(xml_text)
    records = []
    for entry in root.findall(f"{ATOM}entry"):
        link = ""
        for link_el in entry.findall(f"{ATOM}link"):
            if link_el.attrib.get("rel") == "alternate" or not link:
                link = link_el.attrib.get("href", link)
        records.append(
            {
                "id": clean_text(entry.findtext(f"{ATOM}id")),
                "title": clean_text(entry.findtext(f"{ATOM}title")),
                "summary": clean_text(entry.findtext(f"{ATOM}summary")),
                "published": clean_text(entry.findtext(f"{ATOM}published"))[:10] or today(),
                "updated": clean_text(entry.findtext(f"{ATOM}updated"))[:10] or today(),
                "link": link,
            }
        )
    return records


def query_to_signals(query_cfg: dict[str, Any], feed_records: list[dict[str, str]]) -> list[dict[str, Any]]:
    signals = []
    for record in feed_records:
        arxiv_url = record["link"] or record["id"]
        signal_id = stable_id("SIG-ARXIV", query_cfg["name"], arxiv_url)
        probe_id = stable_id("PROBE-ARXIV", query_cfg["name"], arxiv_url)
        signals.append(
            source_signal(
                signal_id=signal_id,
                title=record["title"],
                source_tier=1,
                source_type="research",
                source_name="arXiv",
                source_url=arxiv_url,
                observed_at=record["updated"] or record["published"],
                summary=record["summary"][:900],
                risk_hypothesis=(
                    "This research result may describe an agentic AI risk, guardrail gap, "
                    "or evaluation method worth translating into a safe probe."
                ),
                affected_surfaces=query_cfg["affected_surfaces"],
                risk_categories=query_cfg["risk_categories"],
                evidence_status="unverified",
                novelty=3,
                actionability=3,
                source_reliability=4,
                raw_detail_policy="summarize_only",
                probe_id=probe_id,
                probe_description=f"Review the paper and convert any safe, relevant finding into a probe for {query_cfg['name']}.",
                expected_detection_stage=query_cfg["proposed_probe_stage"],
                safe_reproduction="Use paper abstractions and synthetic fixtures; do not copy operational exploit strings.",
                notes=f"Generated from arXiv query: {query_cfg['query']}",
            )
        )
    return signals


def load_config(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="data/config/arxiv_queries.json")
    parser.add_argument("--output")
    parser.add_argument("--max-results", type=int, help="Override max_results for each query")
    args = parser.parse_args()

    signals = []
    for query_cfg in load_config(Path(args.config)):
        max_results = args.max_results or int(query_cfg.get("max_results", 5))
        feed = fetch_arxiv(query_cfg["query"], max_results)
        signals.extend(query_to_signals(query_cfg, parse_feed(feed)))

    write_json(signals, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
