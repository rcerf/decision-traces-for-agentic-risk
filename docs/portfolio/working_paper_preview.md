# Working Paper Preview

## Provisional Title

Negative-Space Risk Discovery for Agentic Systems: Turning Weak Signals Into Safe Probes, Decision Traces, and Patch Loops

## One-Sentence Thesis

Agentic AI risk analysis should be treated as a living intelligence and operating system: weak signals become safe probes, probes become structured traces, repeated traces become a taxonomy, and gaps in the taxonomy become prompts for proactive investigation.

## Abstract

Agentic AI systems create risk across a lifecycle rather than only at final output. Risk can enter through prompts, retrieved content, memory, connectors, tool permissions, planning steps, approval states, and downstream actions. As models become more capable and agentic products become more widely deployed, risk discovery will increasingly depend on connecting heterogeneous signals: public jailbreaks, incident reports, eval failures, product changes, red-team findings, research papers, policy concerns, and agent-on-agent probes.

This working-hypothesis concept proposes a practical operating model for current-risk intelligence. Public and internal signals are translated into safe hypotheses; hypotheses become safe probes; probe outcomes become structured decision traces; traces are organized into a risk taxonomy; and the taxonomy is used to identify missing controls, unresolved owners, mitigation gaps, residual risks, and negative-space cells that may deserve investigation before they appear as incidents.

The contribution is not a claim of solved safety or a new production detector. It is a legible framework for organizing agentic risk work so that analysts can move from reactive review toward proactive discovery and faster mitigation loops.

## The Problem

Final-output review is too late for many agentic risks.

By the time an answer is written, the model may already have:

- trusted untrusted retrieved content;
- planned an unsafe action;
- crossed a connector boundary;
- selected an unstable tool path;
- prepared to expose private data;
- skipped a human approval gate;
- stored contaminated memory;
- created a downstream obligation for another system or person.

Risk analysis therefore needs to inspect the run as a sequence of decision points, not only as a completed answer.

## The Proposed Operating Model

1. Collect weak signals from research, incidents, public reports, product changes, red teams, eval failures, and reviewed social sources.
2. Convert credible signals into safe risk hypotheses without preserving exploit recipes.
3. Generate safe probes that test the risk class without creating real-world harm.
4. Observe agent runs across ingress, trajectory, draft, and final-response stages.
5. Convert observations into structured decision traces.
6. Record evidence, confidence, severity, competing hypotheses, owner, mitigation, approval gate, residual risk, and next review.
7. Aggregate repeated traces into a taxonomy.
8. Use the taxonomy to find empty cells: risks that should exist given the capability surface but have not yet been observed.
9. Route high-confidence findings into patches, evals, product controls, approval UX, monitoring, or policy review.
10. Monitor the residual risk after mitigation.

## Negative-Space Risk Discovery

The most interesting part of the framework is not only cataloging known risks. It is asking what the current taxonomy implies should be present but has not yet been seen.

For example:

- If agents can use external tools and read untrusted content, where can instruction hierarchy fail?
- If agents can remember prior interactions, where can memory become contaminated or socially engineered?
- If agents can delegate work to other agents, where can agent-on-agent manipulation emerge?
- If models are patched against known attacks, what adjacent variants remain untested?
- If one risk class appears only under a specific connector, which similar connector surfaces have not been probed?

This is the move from reactive incident cataloging to proactive risk search.

## Why This Might Be Useful To An Internal Risk Team

A team could use this operating model to:

- keep a current risk picture across many moving signals;
- turn public weak signals into safe internal probes;
- preserve analyst reasoning in a reusable format;
- identify owners and residual risk rather than only issues;
- compare risk classes across products, models, and tool surfaces;
- spot holes in the framework before they become incidents;
- coordinate evaluation, product, policy, and mitigation work.

## What This Prototype Demonstrates

This repo includes a small synthetic version of the loop:

- synthetic risk traces;
- schema validation;
- a staged sentinel concept;
- public-signal intake sketches;
- risk-delta matrix generation;
- a sample analyst brief;
- a patch-loop case study;
- an opt-in signal-sharing concept;
- a controlled pre-release probe-lab concept.

The prototype is intentionally small. The point is not scale. The point is to make the reasoning inspectable.

## What This Does Not Claim

This does not claim:

- production readiness;
- measured real-world prevalence;
- precision or recall;
- access to private telemetry;
- novelty over all current research;
- that a small model can solve agentic risk;
- that open volunteer telemetry is easy to govern;
- that agent-on-agent risk is already the dominant threat.

The claim is narrower:

> This is a useful operating lens for organizing agentic risk intelligence, making analyst judgment legible, and identifying the next safe thing to test.

## Next Evaluation Questions

The next credibility jump would be to test:

- Can traces generated from real internal evals improve analyst consistency?
- Can safe probes derived from public signals find control gaps faster than ad hoc review?
- Which lifecycle stage catches each risk class earliest?
- Which signals are noisy but useful, and which are distracting?
- Which mitigations actually reduce residual risk after deployment?
- How should human review be routed so scarce expert attention goes to high-value uncertainty?

## Reader Takeaway

If this artifact works, a reader should not think:

> This person solved agentic risk.

They should think:

> This person has a concrete, systems-minded way to make emerging risk legible, operational, and worth discussing.
