# Anima Risk Sentinel Study

This study explores a staged risk-analysis sub-agent for agentic systems.

The core idea is that a model or agent run should be evaluated at multiple points, not only after the final answer is written. Each stage exposes different signals:

1. Ingress: prompt, retrieved context, connector context, permissions.
2. Trajectory: plans, tool calls, tool arguments, approvals, connector crossings, telemetry.
3. Draft: partial answer, claims, proposed actions, sensitive content, confidence language.
4. Final: completed response before it is sent to the next consumer.

The first implementation is a deterministic baseline. That is deliberate. A deterministic baseline creates labels, false positives, false negatives, and evaluation discipline before adding a trained classifier or small risk model.

## What This Can Study Now

- Prompt injection in user input or untrusted retrieved context.
- Connector boundary crossing.
- Tool overreach and high-impact actions without approval.
- Data leakage in drafts or final output.
- High-entropy or unstable telemetry around risky action selection.
- Whether staged monitoring catches different risk classes at different points.

## What This Does Not Need

This does not require OpenAI internal weights, hidden chain-of-thought, or private stack traces. The study uses observable traces:

- Prompt text.
- Retrieved content provenance.
- Tool choices.
- Tool arguments.
- Tool outputs.
- Approval states.
- Drafts and final outputs.
- Optional model telemetry when available, such as token logprobs, entropy, margins, or repeated-sample disagreement.

## Run

```bash
python3 src/risk_sentinel.py data/runs
python3 src/stage_ablation.py data/runs
python3 -m unittest tests/test_risk_sentinel.py
```

## Current Baseline

See `docs/baseline_findings.md` for the first synthetic-run result and the next stage-ablation experiment.

## Next Adapter Targets

The deterministic baseline can later be paired with:

- Encoder classifier for prompt injection or social-engineering detection.
- Small judge model for tool-call correctness and policy fit.
- Open-weight model telemetry adapter for logits, entropy, uncertainty, and repeated-sample disagreement.
- Agent-framework trace adapter for tool calls, approvals, connector boundaries, and handoffs.

## Research Question

Can a staged sentinel pipeline identify agentic risk earlier and more precisely than final-output review alone?

The useful comparison is not only accuracy. It is operational value:

- Which stage detected the risk first?
- Did the detection point leave time to block, route, or require approval?
- Did the event produce a reusable trace, eval case, or mitigation rule?
- What was the false-positive cost?
- What new taxonomy cell did the case reveal?
