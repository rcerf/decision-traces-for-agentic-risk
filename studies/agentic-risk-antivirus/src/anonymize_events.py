#!/usr/bin/env python3
"""Create aggregate-safe telemetry from local risk events."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_result(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def aggregate(result: dict[str, Any]) -> dict[str, Any]:
    events = result.get("events", [])
    signatures = sorted({event["signature_id"] for event in events})
    sessions = sorted({event["session_id"] for event in events})
    categories = sorted({event["category"] for event in events})
    severities = sorted({event["severity"] for event in events})

    return {
        "privacy_policy": "aggregate_only_no_raw_prompt_output_or_tool_args",
        "source_event_count": len(events),
        "affected_session_count": len(sessions),
        "signature_ids": signatures,
        "categories": categories,
        "severities": severities,
        "summary": result.get("summary", {}),
        "event_fingerprints": [
            {
                "signature_id": event["signature_id"],
                "category": event["category"],
                "severity": event["severity"],
                "stage": event["stage"],
                "evidence_hash": event["evidence_hash"],
            }
            for event in events
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("events", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rendered = json.dumps(aggregate(load_result(args.events)), indent=2)
    if args.output:
        args.output.write_text(rendered)
        print(f"Wrote {args.output}")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

