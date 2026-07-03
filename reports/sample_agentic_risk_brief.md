# Sample Agentic Risk Brief

Date: 2026-07-02  
Scope: Synthetic traces and staged sentinel runs in this repo  
Status: Working-paper prototype, not production measurement

## Key Judgments

1. Final-output review is insufficient for agentic systems. In the current synthetic ablation, final-only review detects 1 of 3 risky runs; adding ingress and trajectory monitoring detects all 3 risky runs.
2. Indirect prompt injection and connector-boundary overreach are best caught before final response generation. The useful intervention points are ingress and trajectory.
3. Human approval gates are central controls for high-impact or connector-crossing actions, but they need to be specific enough to avoid generic confirmation fatigue.
4. Public weak signals should feed a probe backlog, not be treated as validated evidence. Social-media signals are useful for creativity but should stay review-gated until corroborated or safely reproduced.
5. Agentic risk should be treated as a living operating picture. New models, product surfaces, and agent-on-agent probing can change the risk landscape faster than a static taxonomy can absorb.
6. A possible next-build concept is a controlled pre-release probe lab: separate adversarial discovery, defensive controls, and analyst adjudication in a public-safe harness before treating the idea as operationally useful.
7. A possible deployment concept is opt-in local signal sharing: users would run inspectable local monitors and contribute aggregate-only risk signals only after explicit privacy, security, and utility review.

## Current Evidence

Trace corpus:

- 7 synthetic agentic risk traces.
- 5 high-severity traces.
- 2 medium-severity traces.
- Categories include prompt injection, connector boundary ambiguity, tool overreach, social engineering, policy evasion, memory/retrieval contamination, and public-benchmark-inspired indirect injection.

Sentinel study:

- 4 observable agent runs.
- 3 risky runs.
- 1 benign negative-control run.
- First detection stages: ingress, trajectory, final, and none for the benign run.

Risk-intelligence intake:

- 7 sample public signals.
- Source tiers include standards, research/benchmarks, incident/journalism/policy, and social weak signals.
- Social/journalism weak signals route to review.
- Jailbreak-style raw details are marked `do_not_reproduce`.

Risk-delta matrix:

- Agent-on-agent adversarial probing is now a top safe-probe candidate.
- The matrix does not claim prevalence. It identifies capability/risk cells worth testing safely.
- The output is intended to feed patch objects: signatures, evals, approval changes, product mitigations, policy updates, model-behavior fixes, or residual monitors.

Controlled pre-release probe lab concept:

- A constrained public-safe harness could test adversarial discovery against defensive controls and analyst adjudication.
- This repo does not include a pre-release model probe harness.
- Expert strategists would still need to adjudicate novelty, feasibility, likely blast radius, and next probes.

Opt-in signal-sharing concept:

- 4 synthetic volunteer nodes.
- Privacy audit rejects raw prompt/output fields by design.
- Uncertainty-gated routing is a hypothesis for reducing unnecessary review, not a proven result.
- Patch-preview nodes are a concept for future signed update experiments, not a deployed channel.

## Open Mitigation Backlog

| Risk Area | Current Control | Gap | Next Action |
|---|---|---|---|
| Indirect prompt injection | Deterministic ingress patterns | No measured false-positive/false-negative rate | Add BIPIA-style safe fixtures and benign controls |
| Connector boundary crossing | Tool-call scope and approval checks | Connector intent is inferred crudely | Add explicit task-scope model and cross-connector policy |
| Function-call malfunction | Deterministic trajectory checks | No specialized judge model yet | Evaluate small judge or rubric-based classifier |
| Data leakage | Secret-like final-output regex | Limited secret patterns | Add draft-stage and tool-output provenance tests |
| Social weak signals | Manual review gate | No automated source credibility scoring beyond simple priority | Add source profiles and corroboration tracking |
| Agent-on-agent probing | Safe-abstraction requirement | No runnable multi-agent probe harness yet | Explore constrained simulator that preserves risk class, surface, authority, and first useful intervention point without raw exploit detail |
| Controlled pre-release probing | Concept report and patch-loop case | No executable pre-release probe harness | Prototype synthetic role separation with public-safe historical motifs and benign target workflows |
| Opt-in signal sharing | Aggregate-only synthetic node events | No real opt-in client, privacy inspector, or signed patch channel | Treat as future product concept requiring privacy, security, and utility validation |

## Recommended Next Review

Within 72 hours:

- Add one integrated run that starts from a risk-intel signal and automatically generates a safe sentinel fixture.
- Add a small scorecard: detected stage, severity, control, owner, residual risk, and false-positive note.
- Add a README diagram showing the operating loop.
- Extend the patch-loop case into a constrained runnable harness.
- Explore controlled role separation so adversarial discovery, defensive patching, and analyst adjudication are explicit.
- Sketch signed patch-pack simulation for an opt-in local signal-sharing concept.

Within two weeks:

- Add an open benchmark-to-trace adapter, ideally Inspect AI plus AgentHarm or AgentDojo.
- Add framework crosswalks for OWASP, MITRE ATLAS, NIST AI RMF, MIT AI Risk Repository, MAESTRO, and OpenAI Preparedness categories where relevant.
- Add control-effectiveness metrics that track benign utility, attack success reduction, false-positive burden, first useful intervention point, and whether detection happened before external side effect.
- Add an open-model telemetry experiment using entropy, margin, and repeated-sample disagreement around tool choice.
- Add human-review annotations for false positives and false negatives.

## Decision

Continue development as a portfolio-grade prototype. The current artifact is useful because it demonstrates the operating shape: weak signals become probes, probes become traces, traces become patch candidates, and patch candidates become reviewable operating decisions with residual monitoring.
