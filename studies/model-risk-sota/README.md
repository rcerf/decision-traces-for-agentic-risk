# Model-Risk SOTA Review

Date: 2026-07-02  
Status: public-source pressure test for the portfolio prototype

## Bottom Line

This project is best positioned as an operating layer for agentic risk intelligence, not as a new benchmark or production detector.

The useful claim is:

> Agentic risk analysis needs a trace layer that connects weak signals, eval findings, incidents, public research, product launches, owners, mitigations, residual gaps, and next review points.

That claim lines up closely with OpenAI's Agentic Risk Analyst role language: current operating picture, weak-signal synthesis, cross-functional owners, mitigations, dependencies, residual risk, metrics, and decision-ready assessments.

The updated framing is deliberately live-field rather than solved-system: new models, product surfaces, public discoveries, and agent-on-agent pressure will keep changing the risk landscape. The useful work is to keep the operating picture current and convert credible signals into safe probes, patch objects, and residual-risk monitors.

## What Looks Strong

- The core artifact is a structured decision trace, not just a free-text incident note.
- The repo treats risk as lifecycle behavior: ingress, trajectory, draft, and final response.
- The public-signal intake layer is a strong match for SIA-style weak-signal work.
- The sample brief turns technical findings into owners, controls, residual risk, and next review.
- The project is honest about being synthetic and public-safe.

## What Is Not Yet Strong Enough

- No executable benchmark adapter yet.
- No measured precision/recall, false-positive cost, or utility/security tradeoff.
- No formal schema crosswalk to OWASP, MITRE ATLAS, NIST AI RMF, MIT AI Risk Repository, MAESTRO, or OpenAI Preparedness categories.
- Threat-model fields are still too light: trust boundary, attacker capability, tool authority, exfiltration channel, reversibility, and autonomy horizon should become first-class.
- Memory, multi-agent delegation, and benchmark-integrity risks are underdeveloped.

## Best Next Credibility Jump

Build one small adapter that converts an existing open eval or benchmark result into this repo's trace format.

Recommended targets:

1. Inspect AI plus AgentHarm, because Inspect is a practical eval harness and AgentHarm is already available through Inspect Evals.
2. AgentDojo, because it directly stresses prompt injection against tool-using agents and makes utility/security tradeoffs explicit.
3. A small hand-authored public-safe benchmark fixture if installation time is too high, with the adapter interface designed so a real benchmark can replace it later.

The deliverable should be:

```text
benchmark/eval run
  -> normalized finding
  -> agentic risk trace JSON
  -> sample operating-picture update
  -> control-effectiveness note
```

## Intended Audience

- Reviewers who own a current-risk operating picture for agentic systems.
- Strategic-intelligence, trust & safety, and risk-operations readers evaluating whether this artifact improves current-risk operating clarity.

## Recommended Reader Path

For the project artifact:

1. `README.md`
2. `docs/portfolio/hiring_manager_tour.md`
3. `reports/sample_agentic_risk_brief.md`
4. `docs/portfolio/end_to_end_case_study.md`

For the SOTA pressure test:

1. `studies/model-risk-sota/research_memo.md`
2. `studies/model-risk-sota/sota_research_memo.md`
3. `studies/model-risk-sota/working_paper_outline_negative_space_risk_discovery.md`

## Working Hypothesis

Agentic risk analysis should be treated as a current-risk intelligence system. The useful unit is not only a policy violation or unsafe final answer; it is an observable decision trace that links source signal, context provenance, agent trajectory, tool authority, approval state, output behavior, mitigation owner, residual risk, and next review.

A corpus of those traces can support both reactive incident review and proactive gap-finding.
