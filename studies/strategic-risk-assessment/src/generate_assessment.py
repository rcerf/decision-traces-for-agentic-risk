#!/usr/bin/env python3
"""Generate a public-signal agentic risk assessment from structured hypotheses."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = MODULE_ROOT / "data" / "public_signal_risk_hypotheses.json"
DEFAULT_OUTPUT = REPO_ROOT / "reports" / "agentic_risk_assessment_public_signals.md"

REQUIRED_FIELDS = {
    "risk_id",
    "title",
    "thesis",
    "likelihood",
    "impact",
    "novelty",
    "actionability",
    "confidence",
    "affected_surfaces",
    "why_might_be_under_instrumented",
    "likely_failure_path",
    "early_indicators",
    "safe_probe",
    "decision_needed",
    "sources",
}


@dataclass(frozen=True)
class RankedRisk:
    priority_score: int
    priority_band: str
    item: dict[str, Any]


def load_hypotheses(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text())
    if not isinstance(data, list):
        raise ValueError("risk hypothesis input must be a JSON array")
    return data


def validate_hypothesis(item: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_FIELDS - set(item))
    if missing:
        errors.append(f"missing required fields: {', '.join(missing)}")

    for field in ("likelihood", "impact", "novelty", "actionability"):
        value = item.get(field)
        if not isinstance(value, int) or not 1 <= value <= 5:
            errors.append(f"{field} must be integer 1-5")

    if item.get("confidence") not in {"low", "medium", "high"}:
        errors.append("confidence must be low, medium, or high")

    for field in ("affected_surfaces", "early_indicators", "sources"):
        value = item.get(field)
        if not isinstance(value, list) or not value:
            errors.append(f"{field} must be a non-empty list")

    for source in item.get("sources", []):
        if not isinstance(source, dict) or not source.get("label") or not source.get("url"):
            errors.append("each source must include label and url")

    return errors


def priority_score(item: dict[str, Any]) -> int:
    """Score public-signal hypotheses for analyst attention.

    Impact and likelihood dominate. Actionability matters because this artifact
    should recommend testable next steps, not only interesting speculation.
    Novelty gets a smaller weight so mature risks remain prioritized when they
    are operationally important.
    """

    return (
        int(item["likelihood"]) * 10
        + int(item["impact"]) * 10
        + int(item["actionability"]) * 6
        + int(item["novelty"]) * 4
    )


def priority_band(score: int) -> str:
    if score >= 125:
        return "immediate assessment"
    if score >= 110:
        return "near-term assessment"
    if score >= 95:
        return "watchlist with probe"
    return "watchlist"


def rank_hypotheses(items: list[dict[str, Any]]) -> list[RankedRisk]:
    ranked = [
        RankedRisk(
            priority_score=priority_score(item),
            priority_band=priority_band(priority_score(item)),
            item=item,
        )
        for item in items
    ]
    return sorted(
        ranked,
        key=lambda risk: (
            -risk.priority_score,
            -int(risk.item["impact"]),
            -int(risk.item["likelihood"]),
            risk.item["risk_id"],
        ),
    )


def surfaces_summary(ranked: list[RankedRisk]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for risk in ranked:
        for surface in risk.item["affected_surfaces"]:
            counts[surface] = counts.get(surface, 0) + 1
    return dict(sorted(counts.items(), key=lambda entry: (-entry[1], entry[0])))


def format_sources(sources: list[dict[str, str]]) -> str:
    return "; ".join(f"[{source['label']}]({source['url']})" for source in sources)


def render_markdown(ranked: list[RankedRisk], generated_on: date) -> str:
    surface_counts = surfaces_summary(ranked)
    top_risks = ranked[:5]
    lines: list[str] = [
        "# Public-Signal Agentic Risk Assessment",
        "",
        f"Generated: {generated_on.isoformat()}",
        "",
        "Intended audience: reviewers with operational agentic-risk or risk-intelligence responsibility.",
        "",
        "Important caveat: this assessment uses public information only. It does not claim these risks are unknown to OpenAI. It identifies plausible under-owned, under-measured, or under-instrumented risk hypotheses that are worth testing for coverage.",
        "",
        "## Method",
        "",
        "- Start with public signals from OpenAI product/system materials, safety research, standards, and agentic-risk benchmarks.",
        "- Convert each signal into a testable risk hypothesis.",
        "- Rank by likelihood, impact, actionability, and novelty.",
        "- Preserve the safe probe and decision needed so the assessment can feed an operating backlog.",
        "",
        "Scoring formula:",
        "",
        "```text",
        "priority = likelihood*10 + impact*10 + actionability*6 + novelty*4",
        "```",
        "",
        "The weights are illustrative: they encode a preference for likelihood and impact over actionability and novelty, and are not calibrated against outcome data.",
        "",
        "## Key Judgments",
        "",
        "1. The highest-priority risks are not isolated unsafe answers. They are state/action integrity failures across retrieval, connectors, tools, approvals, memory, and handoffs.",
        "2. The most valuable analyst work is joining weak signals into a trace: what the agent read, believed, called, changed, asked approval for, and exposed.",
        "3. The central coverage question is not whether a risk exists in a taxonomy. It is whether there is evidence of control effectiveness, ownership, residual risk, and next review.",
        "4. Public evidence points to one practical next product: convert eval/incident/research signals into structured traces and operating-picture updates.",
        "",
        "## Top Risks",
        "",
    ]

    for index, risk in enumerate(top_risks, start=1):
        item = risk.item
        lines.extend(
            [
                f"### {index}. {item['title']}",
                "",
                f"Priority: {risk.priority_score} ({risk.priority_band})  ",
                f"Confidence: {item['confidence']}  ",
                f"Scores: likelihood {item['likelihood']}/5, impact {item['impact']}/5, actionability {item['actionability']}/5, novelty {item['novelty']}/5",
                "",
                f"Thesis: {item['thesis']}",
                "",
                f"Most likely failure path: {item['likely_failure_path']}",
                "",
                f"Why it may be under-instrumented: {item['why_might_be_under_instrumented']}",
                "",
                "Early indicators:",
            ]
        )
        for indicator in item["early_indicators"]:
            lines.append(f"- {indicator}")
        lines.extend(
            [
                "",
                f"Safe probe: {item['safe_probe']}",
                "",
                f"Decision needed: {item['decision_needed']}",
                "",
                f"Relevant sources: {format_sources(item['sources'])}",
                "",
            ]
        )

    lines.extend(
        [
            "## Coverage Map",
            "",
            "| Surface | Count |",
            "|---|---:|",
        ]
    )
    for surface, count in surface_counts.items():
        lines.append(f"| {surface} | {count} |")

    lines.extend(
        [
            "",
            "## Product Output",
            "",
            "This report was generated from structured input rather than hand-written alone.",
            "",
            "Run:",
            "",
            "```bash",
            "python3 studies/strategic-risk-assessment/src/generate_assessment.py --output reports/agentic_risk_assessment_public_signals.md",
            "```",
            "",
            "Input:",
            "",
            "- `studies/strategic-risk-assessment/data/public_signal_risk_hypotheses.json`",
            "",
            "The next implementation step is to replace hand-curated hypotheses with merged outputs from the risk-intelligence intake adapters, benchmark-to-trace conversion, and human review.",
            "",
        ]
    )
    return "\n".join(lines)


def generate(input_path: Path = DEFAULT_INPUT, output_path: Path = DEFAULT_OUTPUT) -> str:
    items = load_hypotheses(input_path)
    failures: list[str] = []
    for item in items:
        errors = validate_hypothesis(item)
        if errors:
            failures.extend(f"{item.get('risk_id', '<missing id>')}: {error}" for error in errors)
    if failures:
        raise ValueError("\n".join(failures))

    report = render_markdown(rank_hypotheses(items), date.today())
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

