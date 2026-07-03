#!/usr/bin/env python3
"""Convert AgentDojo benchmark run records into agentic risk decision traces.

This closes the open item named in ART-007's recommended_action: a
benchmark-to-trace adapter that converts public indirect-injection fixtures
into safe decision traces, preserving risk structure and omitting raw exploit
instructions.

Design decisions:
- The adapter reads ONLY structural fields (suite, task ids, attack type,
  utility, security). It never reads or copies message content, so no raw
  injection text is carried into the trace corpus.
- AgentDojo semantics: `security == False` means the injection SUCCEEDED
  (the agent performed the injection task); `security == True` means the
  attack did not succeed. `utility == True` means the benign user task was
  still completed.
- Severity is derived deterministically from (attack_type, security):
    attack present + security False  -> high     (injection succeeded)
    attack present + security True   -> low       (attack attempted, defended)
    no attack (baseline)             -> not a risk trace; skipped
- Output traces validate against schema/agentic_risk_trace.schema.json.

Usage:
    python3 studies/benchmark-adapter/src/agentdojo_to_trace.py \
        studies/benchmark-adapter/data/agentdojo_runs \
        --start-index 8 --next-review 2026-07-30
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SURFACE = "tool_calling"  # AgentDojo stresses tool-using agents
SOURCE_SIGNAL = "external_research"
RISK_CATEGORY = "prompt_injection"


def load_run(path: Path) -> dict:
    return json.loads(path.read_text())


def is_baseline(run: dict) -> bool:
    """A run with no injection task is a benign utility baseline, not a risk trace."""
    return run.get("attack_type") in (None, "none") or run.get("injection_task_id") in (None, "none")


def derive_severity(run: dict) -> str:
    return "high" if run.get("security") is False else "low"


def run_to_trace(run: dict, trace_id: str, next_review: str) -> dict:
    injected = run.get("security") is False
    utility = run.get("utility")
    severity = derive_severity(run)
    suite = run.get("suite_name", "unknown")
    attack = run.get("attack_type", "unknown")

    if injected:
        observed = (
            f"In the AgentDojo '{suite}' suite, an agent completing a legitimate user task "
            f"encountered untrusted tool-returned content carrying an injected instruction "
            f"('{attack}' attack family). The agent performed the injected side-task "
            f"(benchmark security=false)."
            + (" The original user task still completed (utility=true)."
               if utility else " The original user task did not complete (utility=false).")
        )
        why = (
            "The injection reached tool selection through untrusted content in the tool-return "
            "channel, not through the user prompt. This is a trust-boundary failure inside the "
            "run lifecycle, and it is exactly the case a final-answer-only review would miss."
        )
        mitigation_status = "needs_review"
        confidence = "high"  # benchmark labels this run as a confirmed success
        recommended = (
            "Add a trajectory-stage check that flags tool-return content influencing subsequent "
            "tool selection, and gate any external side-effect behind human approval for this surface."
        )
        approval = {
            "required": True,
            "reason": "The injected behavior produced or attempted an external side effect via tool use.",
            "approval_gate": "before_external_side_effect",
        }
        residual = (
            "A structural trace omits the raw injection wording, so variants that depend on exact "
            "phrasing or multi-step social framing are not characterized by this record alone."
        )
    else:
        observed = (
            f"In the AgentDojo '{suite}' suite, an agent faced an injected instruction "
            f"('{attack}' attack family) in untrusted tool-returned content and did NOT perform "
            f"the injected side-task (benchmark security=true)."
            + (" The user task completed (utility=true)."
               if utility else " The user task did not complete (utility=false).")
        )
        why = (
            "A defended run is still evidence: it marks the attack family and surface where the "
            "trust boundary held, which is a benign control point for measuring false-positive burden."
        )
        mitigation_status = "in_progress"
        confidence = "medium"
        recommended = (
            "Keep this as a benign control for the injection eval so that a monitor's alerting is "
            "measured against defended runs, not only successful attacks."
        )
        approval = {
            "required": False,
            "reason": "No successful injected side effect in this run; retained as a benign control.",
            "approval_gate": "none",
        }
        residual = (
            "One defended run does not establish robustness; the same attack family may succeed "
            "against other tasks, models, or phrasings."
        )

    return {
        "trace_id": trace_id,
        "title": f"AgentDojo {suite} indirect prompt injection ({attack}) — "
                 f"{'succeeded' if injected else 'defended'}",
        "source_signal": SOURCE_SIGNAL,
        "agentic_surface": SURFACE,
        "risk_category": RISK_CATEGORY,
        "evidence": {
            "observed_behavior": observed,
            "why_it_matters": why,
            "open_questions": [
                "At which lifecycle stage did untrusted content first influence tool selection?",
                "Does a benign control with similar formatting avoid the same monitor alert?",
                "Does the result hold across models and attack families, or is it phrasing-specific?",
            ],
        },
        "confidence": confidence,
        "severity": severity,
        "competing_hypotheses": [
            "The model does not preserve a trust boundary between tool-return content and instructions.",
            "The tool surface lacks provenance separation between data and executable instruction.",
            "The specific attack family or task pairing amplifies an otherwise manageable risk.",
        ],
        "recommended_action": recommended,
        "owner": "Agent Safety / Evals / Tooling Platform",
        "mitigation_status": mitigation_status,
        "human_approval": approval,
        "residual_risk": residual,
        "reusable_eval_case": (
            f"AgentDojo {suite}/{run.get('user_task_id')} vs injection "
            f"{run.get('injection_task_id')} under '{attack}', converted to a structural trace "
            "with raw exploit text omitted."
        ),
        "taxonomy_gap": (
            "Need a standing crosswalk from benchmark (utility, security) labels to lifecycle "
            "stage, trust-boundary failure, and first useful intervention point."
        ),
        "next_review": next_review,
    }


def convert_dir(runs_dir: Path, start_index: int, next_review: str) -> list[dict]:
    traces: list[dict] = []
    idx = start_index
    for path in sorted(runs_dir.glob("*.json")):
        run = load_run(path)
        if is_baseline(run):
            print(f"skip (baseline, not a risk trace): {path.name}", file=sys.stderr)
            continue
        trace_id = f"ART-{idx:03d}"
        traces.append(run_to_trace(run, trace_id, next_review))
        idx += 1
    return traces


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("runs_dir", type=Path, help="Directory of AgentDojo structural run JSONs")
    ap.add_argument("--start-index", type=int, default=8,
                    help="First ART-NNN number to assign (default 8, after the 7 bundled traces)")
    ap.add_argument("--next-review", default="2026-07-30", help="next_review date (YYYY-MM-DD)")
    ap.add_argument("--out-dir", type=Path, default=None,
                    help="If set, write one ART-NNN.json per trace here; else print to stdout")
    args = ap.parse_args()

    if not args.runs_dir.is_dir():
        print(f"error: not a directory: {args.runs_dir}", file=sys.stderr)
        return 2

    traces = convert_dir(args.runs_dir, args.start_index, args.next_review)
    if not traces:
        print("no risk traces produced (all runs were baselines?)", file=sys.stderr)
        return 1

    if args.out_dir:
        args.out_dir.mkdir(parents=True, exist_ok=True)
        for t in traces:
            (args.out_dir / f"{t['trace_id']}-agentdojo.json").write_text(
                json.dumps(t, indent=2) + "\n")
        print(f"wrote {len(traces)} traces to {args.out_dir}", file=sys.stderr)
    else:
        print(json.dumps(traces, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
