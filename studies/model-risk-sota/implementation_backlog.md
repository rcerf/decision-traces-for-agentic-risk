# SOTA Upgrade Backlog

Status: prioritized next work for making the portfolio artifact more technically credible.

## Priority 1: Benchmark-To-Trace Adapter

Goal: prove that the trace format can ingest a real eval result instead of only hand-authored synthetic examples.

Candidate paths:

- Inspect AI plus AgentHarm.
- AgentDojo prompt-injection benchmark.
- A small local fixture shaped like a benchmark result, with clear TODOs for replacing it with a real benchmark run.

Acceptance criteria:

- One script converts benchmark-like findings into `schema/agentic_risk_trace.schema.json`.
- Converted traces validate with `demo/validate_traces.py`.
- A short report summarizes detection stage, category, severity, mitigation, residual gap, and next review.

Related progress:

- `studies/risk-delta-matrix/` now generates negative-space probe candidates from capability deltas and risk classes.
- `studies/agentic-risk-antivirus/` now demonstrates a local-first signature monitor and aggregate-only export path.

## Priority 2: Framework Crosswalk

Goal: avoid taxonomy reinvention and show fluency with existing risk frameworks.

Add mappings for:

- OWASP LLM Top 10.
- MITRE ATLAS.
- NIST AI RMF / GenAI profile.
- MIT AI Risk Repository.
- CSA MAESTRO.
- OpenAI Preparedness categories where relevant.

Acceptance criteria:

- Schema supports optional `framework_mappings`.
- At least six example traces include mappings.
- A generated markdown table shows category coverage and unmapped gaps.

## Priority 3: Threat-Model Fields

Goal: make each trace more useful to security, safety, product, and governance reviewers.

Suggested fields:

- `attacker_capability`
- `trust_boundary`
- `authority_source`
- `data_flow`
- `tool_permissions`
- `external_side_effect`
- `reversibility`
- `exfiltration_channel`
- `autonomy_horizon`
- `human_checkpoint_density`
- `preconditions`
- `postconditions`
- `control_evidence`
- `benchmark_source`

Acceptance criteria:

- Schema supports the fields without breaking existing traces.
- Validator flags missing threat-model fields for high and critical traces as warnings.
- The sample brief uses the new fields in at least one decision.

## Priority 4: Control-Effectiveness Scorecard

Goal: move from "control exists" to "control worked under this test, with this tradeoff."

Track:

- Benign utility before/after.
- Attack success rate before/after.
- False-positive cost.
- First useful intervention point.
- Whether detection happened before external side effect.
- Residual failure examples.
- Reopen trigger.

Acceptance criteria:

- Add `reports/control_effectiveness_scorecard.md`.
- Include at least one indirect-prompt-injection case and one connector-boundary case.
- Explicitly distinguish approval presence from approval quality.

## Priority 5: Memory, Multi-Agent, And Benchmark-Integrity Cases

Goal: cover the harder agentic surfaces that are underrepresented in the current synthetic corpus.

Add public-safe examples for:

- Poisoned memory written from untrusted retrieved context and triggered later.
- Low-privilege agent delegating to a high-privilege agent.
- Tool-result poisoning across an agent handoff.
- Eval reward hacking or benchmark-integrity failure.

Acceptance criteria:

- At least four new traces validate.
- At least two observable-agent-run fixtures trigger staged sentinel events.
- The sample brief calls out the new surfaces as watch areas.
