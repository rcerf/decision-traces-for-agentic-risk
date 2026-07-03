"""Shared helpers for risk-intelligence ingestion adapters."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen


USER_AGENT = "decision-traces-risk-intel/0.1 (mailto:rcerf@alumni.princeton.edu)"


def today() -> str:
    return dt.date.today().isoformat()


def stable_id(prefix: str, *parts: str, length: int = 10) -> str:
    digest = hashlib.sha1("||".join(parts).encode("utf-8")).hexdigest()[:length].upper()
    return f"{prefix}-{digest}"


def clean_text(text: Any) -> str:
    text = str(text or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def read_json_path_or_url(path_or_url: str) -> Any:
    if path_or_url.startswith(("http://", "https://")):
        req = Request(path_or_url, headers={"User-Agent": USER_AGENT})
        with urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    return json.loads(Path(path_or_url).read_text())


def write_json(data: Any, output_path: str | None) -> None:
    payload = json.dumps(data, indent=2)
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(payload + "\n")
    else:
        print(payload)


def source_signal(
    *,
    signal_id: str,
    title: str,
    source_tier: int,
    source_type: str,
    source_name: str,
    source_url: str,
    observed_at: str,
    summary: str,
    risk_hypothesis: str,
    affected_surfaces: list[str],
    risk_categories: list[str],
    evidence_status: str,
    novelty: int,
    actionability: int,
    source_reliability: int,
    raw_detail_policy: str,
    probe_id: str,
    probe_description: str,
    expected_detection_stage: str,
    safe_reproduction: str,
    notes: str = "",
) -> dict[str, Any]:
    return {
        "signal_id": signal_id,
        "title": clean_text(title),
        "source_tier": source_tier,
        "source_type": source_type,
        "source_name": clean_text(source_name),
        "source_url": source_url,
        "observed_at": observed_at,
        "summary": clean_text(summary),
        "risk_hypothesis": clean_text(risk_hypothesis),
        "affected_surfaces": affected_surfaces,
        "risk_categories": risk_categories,
        "evidence_status": evidence_status,
        "novelty": novelty,
        "actionability": actionability,
        "source_reliability": source_reliability,
        "raw_detail_policy": raw_detail_policy,
        "proposed_probe": {
            "probe_id": probe_id,
            "description": clean_text(probe_description),
            "expected_detection_stage": expected_detection_stage,
            "safe_reproduction": clean_text(safe_reproduction),
        },
        "notes": clean_text(notes),
    }
