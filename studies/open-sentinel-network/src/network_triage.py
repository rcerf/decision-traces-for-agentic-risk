#!/usr/bin/env python3
"""Render an aggregate-only opt-in signal-sharing triage report."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = MODULE_ROOT / "data" / "sample_sentinel_nodes.json"
DEFAULT_OUTPUT = REPO_ROOT / "reports" / "open_sentinel_network_assessment.md"

RAW_FIELD_NAMES = {
    "raw_prompt",
    "raw_output",
    "raw_tool_args",
    "raw_document",
    "raw_file",
    "evidence_text",
    "private_text",
}


def load_nodes(path: Path = DEFAULT_INPUT) -> list[dict[str, Any]]:
    return json.loads(path.read_text())


def find_raw_fields(value: Any, path: str = "$") -> list[str]:
    if isinstance(value, dict):
        hits: list[str] = []
        for key, item in value.items():
            item_path = f"{path}.{key}"
            if key in RAW_FIELD_NAMES:
                hits.append(item_path)
            hits.extend(find_raw_fields(item, item_path))
        return hits
    if isinstance(value, list):
        hits = []
        for index, item in enumerate(value):
            hits.extend(find_raw_fields(item, f"{path}[{index}]"))
        return hits
    return []


def assert_privacy_safe(nodes: list[dict[str, Any]]) -> None:
    raw_hits = find_raw_fields(nodes)
    if raw_hits:
        raise ValueError(f"Raw fields are not allowed in aggregate network data: {raw_hits}")

    for node in nodes:
        privacy = node.get("privacy", {})
        if privacy.get("raw_upload_enabled"):
            raise ValueError(f"{node['node_id']} enables raw upload")
        if not privacy.get("aggregate_only"):
            raise ValueError(f"{node['node_id']} is not aggregate-only")
        if privacy.get("private_data_leaves_device"):
            raise ValueError(f"{node['node_id']} leaks private data")
        for event in node.get("events", []):
            if event.get("contains_raw_content") or event.get("contains_private_data"):
                raise ValueError(f"{event['event_id']} is not safe to aggregate")


def event_score(event: dict[str, Any]) -> int:
    score = 0
    if event.get("signature_hit"):
        score += 3
    if float(event.get("entropy", 0.0)) >= 2.0:
        score += 2
    if float(event.get("top_choice_margin", 1.0)) <= 0.1:
        score += 2
    if float(event.get("sample_disagreement", 0.0)) >= 0.5:
        score += 2
    if float(event.get("model_disagreement", 0.0)) >= 0.5:
        score += 2
    if event.get("external_side_effect"):
        score += 3
    if event.get("red_team_generated"):
        score += 1
    return score


def route_event(event: dict[str, Any]) -> str:
    score = event_score(event)
    if score >= 9:
        return "auto_promote_patch_candidate"
    if score >= 5:
        return "agentic_review_queue"
    return "aggregate_watch"


def summarize(nodes: list[dict[str, Any]]) -> dict[str, Any]:
    assert_privacy_safe(nodes)
    routes: Counter[str] = Counter()
    categories: Counter[str] = Counter()
    patch_channels: Counter[str] = Counter(node["patch_channel"] for node in nodes)
    modes: Counter[str] = Counter(node["mode"] for node in nodes)
    event_rows: list[dict[str, Any]] = []

    for node in nodes:
        for event in node.get("events", []):
            route = route_event(event)
            score = event_score(event)
            routes[route] += 1
            categories[event["category"]] += 1
            event_rows.append(
                {
                    "node_id": node["node_id"],
                    "event_id": event["event_id"],
                    "category": event["category"],
                    "score": score,
                    "route": route,
                    "entropy": event["entropy"],
                    "margin": event["top_choice_margin"],
                    "sample_disagreement": event["sample_disagreement"],
                    "model_disagreement": event["model_disagreement"],
                    "patch_version": event["patch_version"],
                }
            )

    return {
        "node_count": len(nodes),
        "event_count": len(event_rows),
        "routes": dict(routes),
        "categories": dict(categories),
        "patch_channels": dict(patch_channels),
        "modes": dict(modes),
        "events": sorted(event_rows, key=lambda row: (-row["score"], row["event_id"])),
    }


def render(summary: dict[str, Any]) -> str:
    def format_counts(counts: dict[str, int]) -> str:
        return ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))

    lines = [
        "# Opt-In Signal-Sharing Concept Assessment",
        "",
        "Date: 2026-07-02  ",
        "Status: synthetic aggregate-only network triage output",
        "",
        "## Bottom Line",
        "",
        "An opt-in signal-sharing network could let users contribute to agentic-risk discovery without sending private data to a central service. This is a synthetic concept report: the local monitor stays inspectable, raw content remains local by default, and uncertainty-gated triage is a hypothesis to test, not a proven reduction in human review.",
        "",
        "This report is generated from synthetic node events only. It does not claim production prevalence, precision/recall, or private telemetry performance.",
        "",
        "## Sovereign OS Routing-Gate Transfer",
        "",
        "The relevant Sovereign OS pattern is cheap local uncertainty measurement followed by route selection. In this risk version, deterministic signatures, uncertainty, top-choice margin, sample disagreement, model disagreement, challenge mode, and side-effect awareness could help decide whether an event stays in aggregate watch, enters agentic review, or becomes a patch candidate.",
        "",
        "```text",
        "local monitor event",
        "  -> privacy invariant check",
        "  -> deterministic signature and uncertainty scoring",
        "  -> route decision",
        "  -> aggregate-only telemetry",
        "  -> patch prioritization",
        "  -> signed patch distribution",
        "```",
        "",
        "## Network Summary",
        "",
        f"- Nodes: {summary['node_count']}",
        f"- Aggregate events: {summary['event_count']}",
        f"- Node modes: {format_counts(summary['modes'])}",
        f"- Patch channels: {format_counts(summary['patch_channels'])}",
        f"- Routes: {format_counts(summary['routes'])}",
        "",
        "## Routed Events",
        "",
        "| Node | Event | Category | Score | Route | Entropy | Margin | Sample Disagreement | Model Disagreement | Patch Version |",
        "|---|---|---|---:|---|---:|---:|---:|---:|---|",
    ]
    for event in summary["events"]:
        lines.append(
            "| {node_id} | {event_id} | {category} | {score} | {route} | {entropy:.2f} | {margin:.2f} | {sample_disagreement:.2f} | {model_disagreement:.2f} | {patch_version} |".format(
                **event
            )
        )
    lines.extend(
        [
            "",
            "## Privacy Invariants",
            "",
            "- No raw prompt fields are accepted.",
            "- No raw output fields are accepted.",
            "- No raw tool arguments, files, documents, or evidence text are accepted.",
            "- Nodes must be aggregate-only.",
            "- Nodes must report that private data does not leave the device.",
            "- Events marked as containing raw content or private data are rejected before aggregation.",
            "",
            "## Patch Distribution Model",
            "",
            "- Stable channel receives conservative signature and mitigation updates.",
            "- Preview channel receives early patch packs, eval fixtures, and red-team challenges.",
            "- Patch packs should be signed, versioned, inspectable, and reversible.",
            "- Local clients should report only patch version, route decision, risk category, uncertainty buckets, and aggregate counts.",
            "",
            "## Best Next Build",
            "",
            "Add a signed patch-manifest simulator and a local privacy-inspector command that verifies the outbound payload contains no raw prompts, outputs, files, or tool arguments.",
            "",
        ]
    )
    return "\n".join(lines)


def generate(input_path: Path = DEFAULT_INPUT, output_path: Path = DEFAULT_OUTPUT) -> str:
    report = render(summarize(load_nodes(input_path)))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = generate(args.input, args.output)
    print(f"Wrote {args.output}")
    print(f"{len(report.splitlines())} lines")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
