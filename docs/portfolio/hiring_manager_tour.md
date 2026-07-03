# Hiring Manager Tour

This repo is intended to be read as a working-hypothesis prototype for agentic risk analysis.

It is not a production detector. It is a compact demonstration of how weak signals can become structured risk traces, eval probes, staged monitoring checks, and mitigation decisions. It treats agentic risk as a living field where new models, public discoveries, product deltas, and agent-on-agent pressure continuously update the operating picture.

## 10-Minute Read

Read these in order:

1. `README.md`
2. `docs/portfolio/three_minute_brief.md`
3. `reports/sample_agentic_risk_brief.md`
4. `examples/ART-007-public-benchmark-indirect-injection.json`
5. `docs/portfolio/model_observation_evidence_appendix.md`
6. `docs/portfolio/working_paper_preview.md`
7. `docs/portfolio/end_to_end_case_study.md`
8. `reports/living_agentic_risk_operating_loop.md`
9. `reports/risk_delta_matrix.md`

What to look for:

- Does the thesis make sense?
- Does the three-minute brief make the artifact legible without technical setup?
- Does the sample brief look like a current-risk analyst work product?
- Does the public-benchmark-inspired trace show how public research can become a safe trace without preserving exploit detail?
- Does the evidence appendix separate verified local evidence from claims that remain private or unresolved?
- Does the working-paper preview frame the idea as useful and provisional rather than solved?
- Does the end-to-end case study show how a public signal becomes a safe probe, trace, and mitigation decision?
- Does the living-system report explain how the project would monitor a moving frontier without claiming to solve it?
- Does the risk-delta matrix surface plausible empty cells that can be safely probed?
- Is the risk trace legible?
- Are evidence, uncertainty, severity, owner, mitigation, approval gate, and next review explicit?

## 20-Minute Review

Add:

1. `reports/frontier_red_green_conflict_lab.md`
2. `reports/open_sentinel_network_assessment.md`
3. `reports/agent_on_agent_patch_loop_case.md`
4. `reports/agentic_risk_assessment_public_signals.md`
5. `reports/agentic_risk_antivirus_assessment.md`
6. `studies/anima-risk-sentinel/README.md`
7. `studies/risk-intel-intake/README.md`
8. `studies/model-risk-sota/working_paper_outline_negative_space_risk_discovery.md`

What to look for:

- The controlled pre-release probe concept shows how an internal team could separate adversarial discovery, defensive controls, and analyst adjudication before release.
- The opt-in signal-sharing concept shows how users might contribute aggregate risk signals while keeping private data local, pending real privacy/security validation.
- The patch-loop case turns agent-on-agent risk into a concrete but public-safe workflow.
- The public-signal risk assessment identifies testable hypotheses rather than merely restating a taxonomy.
- The signal-sharing assessment makes the product metaphor concrete without creating a surveillance product.
- The sentinel evaluates observable agent runs at ingress, trajectory, draft, and final output.
- The intake layer turns public signals into safe probe backlog items.
- The strategic assessment module turns structured hypotheses into a ranked report with safe probes and decisions needed.
- The local monitor module demonstrates transparent signatures, local detection, and aggregate-only export.
- The risk-delta matrix turns capability changes into safe probe candidates.
- The ablation shows why final-output review is insufficient for agentic systems.
- The SOTA backlog shows the next credibility jump: benchmark-to-trace ingestion, framework crosswalks, threat-model fields, and control-effectiveness metrics.

## 45-Minute Review

Run:

```bash
python3 demo/validate_traces.py examples
python3 studies/anima-risk-sentinel/src/stage_ablation.py studies/anima-risk-sentinel/data/runs
python3 studies/risk-intel-intake/src/signal_triage.py studies/risk-intel-intake/data/source_signals/sample_public_signals.json
python3 studies/strategic-risk-assessment/src/generate_assessment.py --output reports/agentic_risk_assessment_public_signals.md
python3 studies/agentic-risk-antivirus/src/local_risk_monitor.py studies/agentic-risk-antivirus/data/sample_sessions.json --signatures studies/agentic-risk-antivirus/rules/risk_signatures.json
python3 studies/risk-delta-matrix/src/generate_matrix.py --output reports/risk_delta_matrix.md
python3 studies/patch-loop-case/src/render_patch_loop.py --output reports/agent_on_agent_patch_loop_case.md
python3 studies/open-sentinel-network/src/network_triage.py --output reports/open_sentinel_network_assessment.md
python3 -m unittest discover -s tests
python3 -m unittest discover -s studies/anima-risk-sentinel/tests
python3 -m unittest discover -s studies/risk-intel-intake/tests
python3 -m unittest discover -s studies/strategic-risk-assessment/tests
python3 -m unittest discover -s studies/agentic-risk-antivirus/tests
python3 -m unittest discover -s studies/risk-delta-matrix/tests
python3 -m unittest discover -s studies/patch-loop-case/tests
python3 -m unittest discover -s studies/open-sentinel-network/tests
```

What to look for:

- Trace validation catches missing approval gates.
- The stage ablation detects more risk when trajectory monitoring is included.
- The intake triage prioritizes research/standards-backed probes while routing social weak signals to review.
- The strategic assessment can be regenerated from the structured hypothesis file.
- The local monitor detects prompt-injection, approval, connector-boundary, telemetry, and social-engineering motifs.
- The risk-delta matrix can be regenerated from capability-delta and risk-class inputs.
- The patch-loop case can be regenerated from a structured public-safe case file.
- The opt-in signal-sharing report can be regenerated from aggregate-only synthetic volunteer node events.

## What This Demonstrates

- I can structure ambiguous risk signals into decision-ready artifacts.
- Rick understands that agentic risk lives across the run lifecycle, not only in final output.
- I can connect public research, incidents, journalism, and social weak signals into a safe probe backlog.
- I can build a small runnable system rather than only write a memo.
- I can pressure-test my own artifact against current public research and name the missing pieces without overclaiming.
- I can produce a ranked risk assessment and expose the product logic behind it.
- I can translate a familiar security operating model into an auditable, privacy-aware agentic-risk concept without presenting it as proven.
- I can reason about future agent-on-agent pressure as an operating challenge, not a speculative claim of solved safety.
- I can sketch pre-release role-separated probing as an analyst workflow that joins capability change, historical failures, expert strategy, mitigations, and residual monitoring.
- I can adapt prior routing-gate work into a hypothesis for privacy-preserving agentic-risk triage.

## What This Does Not Yet Prove

- Production precision/recall.
- Real-world prevalence.
- Robustness against adaptive attackers.
- Performance on private OpenAI telemetry.
- Safety of any specific deployed model.

Those are next evaluation questions, not claims made by this prototype.
