#!/usr/bin/env python3
"""Generate a negative-space risk delta matrix."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "reports" / "risk_delta_matrix.md"


def load_json(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text())


def score_cell(delta: dict[str, Any], risk: dict[str, Any]) -> int:
    surface_overlap = len(set(delta["surfaces"]) & set(risk["surfaces"]))
    authority_count = len(delta.get("new_authorities", []))
    evidence_count = len(risk.get("known_evidence", []))
    return surface_overlap * 4 + min(authority_count, 3) * 2 + min(evidence_count, 3)


def cell_status(score: int) -> str:
    if score >= 13:
        return "probe_now"
    if score >= 8:
        return "watchlist"
    return "low_priority"


def generate_cells(deltas: list[dict[str, Any]], risks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cells: list[dict[str, Any]] = []
    for delta in deltas:
        for risk in risks:
            overlap = sorted(set(delta["surfaces"]) & set(risk["surfaces"]))
            if not overlap:
                continue
            score = score_cell(delta, risk)
            if score < 8:
                continue
            cells.append(
                {
                    "delta": delta["name"],
                    "risk": risk["name"],
                    "score": score,
                    "status": cell_status(score),
                    "overlap": overlap,
                    "safe_probe": safe_probe(delta, risk, overlap),
                }
            )
    return sorted(cells, key=lambda cell: (-cell["score"], cell["delta"], cell["risk"]))


def safe_probe(delta: dict[str, Any], risk: dict[str, Any], overlap: list[str]) -> str:
    overlap_text = ", ".join(overlap) if overlap else "shared operating context"
    return (
        f"Create a synthetic fixture for {delta['name']} x {risk['name']} "
        f"covering {overlap_text}; avoid raw exploit content and score first useful intervention point."
    )


def render(cells: list[dict[str, Any]]) -> str:
    lines = [
        "# Risk Delta Matrix",
        "",
        "Status: generated negative-space risk discovery output",
        "",
        "This report identifies capability/risk cells worth probing. It does not claim the risks are real-world prevalent or unknown to any specific team.",
        "",
        "| Capability Delta | Risk Class | Score | Status | Shared Surfaces | Safe Probe |",
        "|---|---|---:|---|---|---|",
    ]
    for cell in cells:
        lines.append(
            "| {delta} | {risk} | {score} | {status} | {overlap} | {probe} |".format(
                delta=cell["delta"],
                risk=cell["risk"],
                score=cell["score"],
                status=cell["status"],
                overlap=", ".join(cell["overlap"]) or "-",
                probe=cell["safe_probe"],
            )
        )
    lines.extend(
        [
            "",
            "## Next Action",
            "",
            "Promote `probe_now` cells into safe synthetic runs, then convert findings into structured agentic risk traces.",
            "",
        ]
    )
    return "\n".join(lines)


def generate(output: Path = DEFAULT_OUTPUT) -> str:
    deltas = load_json(MODULE_ROOT / "data" / "capability_deltas.json")
    risks = load_json(MODULE_ROOT / "data" / "risk_classes.json")
    report = render(generate_cells(deltas, risks))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = generate(args.output)
    print(f"Wrote {args.output}")
    print(f"{len(report.splitlines())} lines")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
