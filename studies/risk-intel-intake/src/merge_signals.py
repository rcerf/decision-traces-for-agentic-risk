#!/usr/bin/env python3
"""Merge source_signal JSON arrays and deduplicate by source URL/title."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ingest_common import stable_id, write_json


def load_array(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text())
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array")
    return [item for item in data if isinstance(item, dict)]


def dedupe_key(signal: dict[str, Any]) -> str:
    url = str(signal.get("source_url", "")).strip().lower()
    title = str(signal.get("title", "")).strip().lower()
    return stable_id("KEY", url, title)


def merge(paths: list[Path]) -> list[dict[str, Any]]:
    by_key: dict[str, dict[str, Any]] = {}
    for path in paths:
        for signal in load_array(path):
            key = dedupe_key(signal)
            if key not in by_key:
                by_key[key] = signal
                continue

            existing = by_key[key]
            existing_notes = existing.get("notes", "")
            new_notes = signal.get("notes", "")
            if new_notes and new_notes not in existing_notes:
                existing["notes"] = (existing_notes + " | " + new_notes).strip(" |")

    return list(by_key.values())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", help="JSON array files to merge")
    parser.add_argument("--output")
    args = parser.parse_args()

    write_json(merge([Path(path) for path in args.inputs]), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
