# Open-Model Observability Plan

We cannot rely on private production stack traces, internal model weights, or hidden chain-of-thought. We can still study the sentinel architecture using models and frameworks that expose observable telemetry.

## Trace Levels

### Level 0: Black-Box Trace

Available from almost any model or API:

- Prompt.
- Retrieved context.
- Tool calls, if the agent framework logs them.
- Draft/final response.
- Refusals.
- Latency and retry counts.

Useful for:

- Input and output guardrails.
- Tool-call policy checks.
- Connector boundary checks.
- Data leakage checks.

### Level 1: Agent Framework Trace

Available when running the agent in a local framework or instrumented harness:

- Plan text if explicitly emitted.
- Tool call order.
- Tool arguments.
- Tool outputs.
- Handoffs.
- Approval state.
- Error/retry/correction loops.

Useful for:

- Trajectory monitoring.
- Goal drift.
- Tool overreach.
- High-impact action gating.
- Comparing ingress-only, trajectory, draft, and final review.

### Level 2: Open-Weight Model Telemetry

Available when running open-weight models locally or in an environment that exposes model internals:

- Token logprobs.
- Entropy over candidate next tokens.
- Margin between top candidate tokens.
- Hidden states or activations, if available.
- Attention patterns, if exposed.
- Repeated-sample disagreement across temperature or seeds.

Useful for:

- Uncertainty around tool choice.
- Instability around refusal/comply decisions.
- Detecting brittle transitions before external side effects.
- Building risk features for a small specialized classifier.

## Candidate Experiments

### Experiment 1: Stage Ablation

Run the same traces through four detector sets:

1. Final-only.
2. Ingress plus final.
3. Ingress plus trajectory plus final.
4. Ingress plus trajectory plus draft plus final.

Measure which risks are detected earlier, which are missed, and which false positives are introduced by each stage.

### Experiment 2: Tool-Call Entropy

For an open-weight model that exposes logits/logprobs, ask it to select among safe, irrelevant, and unsafe tool calls. Record:

- Entropy of tool choice.
- Top-token margin for tool name and high-risk arguments.
- Whether repeated samples disagree on action.
- Whether uncertainty spikes before unsafe action selection.

The hypothesis is not that entropy is a complete safety signal. It is that high uncertainty near consequential tool choice is useful as a review trigger.

### Experiment 3: Prompt Injection Provenance

Compare prompt-injection detection across:

- User prompt.
- Retrieved document.
- Tool output.
- Connector content.

The hypothesis is that the same text should carry different risk depending on provenance. A suspicious instruction in user text, untrusted retrieval, or tool output should not be treated identically.

### Experiment 4: Small Risk Model

Use deterministic sentinel labels as weak labels. Human-review a subset. Train or prompt a small classifier to classify:

- Risk source.
- Failure mode.
- Real-world harm.
- Required control.

Compare the small model against the deterministic baseline on precision, recall, latency, and explainability.

## Study Output

Each run should produce:

- Risk events by stage.
- First detection stage.
- Severity and confidence.
- Required approval gate.
- Suggested mitigation.
- Reusable eval case.
- False-positive / false-negative notes after review.
