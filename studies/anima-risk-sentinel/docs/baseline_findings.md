# Baseline Findings

This first baseline uses four synthetic observable agent runs:

1. Indirect prompt injection in retrieved document context.
2. Benign email summarization.
3. Connector boundary overreach from email to Drive.
4. Final-output leakage of a secret-like value.

## Initial Result

The staged sentinel catches different risks at different points:

- Ingress catches untrusted-context prompt injection before the agent acts.
- Trajectory catches connector boundary violations and missing approval gates.
- Draft review catches unsafe action proposals before final delivery.
- Final review catches leaked sensitive values that earlier stages may miss.

That is the main claim worth testing: final-output review is necessary but insufficient. Agentic risk appears across the run lifecycle, especially around retrieved content, tool calls, connector boundaries, and approval state.

## Why The Deterministic Baseline Matters

The deterministic rules are intentionally incomplete. They create a starting point for:

- Repeatable labels.
- False-positive review.
- False-negative discovery.
- Stage attribution.
- Small-model training targets.
- Human-review guidelines.

The next step is not to claim the rules are enough. The next step is to use the rule failures to generate better eval cases and a better risk model.

## Next Experiment

Run a stage ablation using `src/stage_ablation.py`:

1. Final-only review.
2. Ingress plus final review.
3. Ingress, trajectory, and final review.
4. Ingress, trajectory, draft, and final review.

For each condition, measure:

- Earliest detection stage.
- Missed risk classes.
- False positives.
- Whether the detection point leaves time to block, route, or require approval.

## Open-Model Extension

For an open-weight or locally instrumented model, add telemetry:

- Tool-choice entropy.
- Top-choice margin.
- Repeated-sample disagreement.
- Correction/retry loops.
- Refusal/comply instability.

Then test whether uncertainty near consequential tool choices is a useful review trigger when combined with deterministic tool-boundary checks.
