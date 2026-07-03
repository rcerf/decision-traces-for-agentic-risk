# Agentic Risk Signal-Sharing Assessment

Date: 2026-07-02  
Status: product concept and local-first prototype

## Bottom Line

The antivirus analogy is useful only as a limited product metaphor: local detection, optional submission, central triage, and shipped updates.

The idea is not that agentic risk is identical to malware, and it is not that any local monitor has "solved" agentic risk. The useful analogy is the operating loop:

```text
local detection and public weak signals
  -> signature / classifier / adversarial-probe event
  -> optional privacy-preserving submission
  -> central analysis and signal/noise triage
  -> updated signatures, probes, evals, mitigations, and policy/model patches
  -> shipped protection
  -> residual-risk monitoring
```

For OpenAI Strategic Intelligence & Analysis, this is a concrete way to connect public weak signals, local user-facing risk events, model/product telemetry, and central risk intelligence.

## Proposed Product

An open-source, auditable local monitor that users or enterprises can run near their AI usage. It watches prompts, retrieved context, tool calls, approvals, outputs, and limited model telemetry for high-risk patterns.

The monitor should start with transparent signatures and deterministic rules, then add a small local classifier only where ambiguity justifies it.

The long-term concept is a living risk-signal loop, not a static endpoint scanner. It would need to learn from new model capabilities, new product surfaces, newly public jailbreak ideas, research papers, incident databases, policy concerns, and eventually carefully bounded agent-on-agent probing where one system searches for weaknesses in another.

## What It Detects First

1. Prompt injection and instruction-confusion markers.
2. Secret-like values in outputs.
3. Social-engineering pressure patterns.
4. Sensitive external-side-effect tool calls without approval.
5. Cross-connector sensitive actions.
6. Unstable consequential tool selection from available telemetry.
7. Agent-on-agent probing patterns where a model or agent appears to test, transfer, or chain vulnerability ideas across systems.

## Privacy Guardrails

Default behavior:

- No raw prompt upload.
- No raw output upload.
- No raw retrieved document upload.
- No raw tool-argument upload.
- Local evidence excerpts may be shown to the user.
- Submitted telemetry is aggregate-only and evidence-hashed.

Optional behavior:

- User-approved sanitized sample submission.
- Enterprise-controlled collector.
- Differential privacy or secure aggregation for high-volume signals.
- Human review before any raw sample leaves a device.

## Strategic Value

This suggests a flywheel similar to antivirus but adapted to AI:

- Users get local protection.
- Analysts get aggregate weak signals.
- New risk motifs can be categorized quickly.
- New signatures and safe probes can be shipped back.
- The ontology improves from real usage while preserving privacy.
- Product, policy, and model teams receive patchable artifacts: eval cases, mitigations, approval changes, classifier/signature updates, and residual-risk monitors.
- Opt-in users could act like a beta network: they inspect the local monitor, contribute aggregate signals, test safe challenge fixtures against their own workflows, and receive early patch distribution.

## Opt-In Signal-Sharing Network

The open-source version should be inspectable end to end:

- local code and rules are auditable;
- outbound telemetry schema is public;
- default submissions are aggregate-only;
- raw prompt/output upload is off by default;
- volunteer red-team mode uses safe challenges and simulated external actions;
- patch packs are signed, versioned, and reviewable before local application.

To reduce human burden, the local monitor could rely on deterministic signatures, small local classifiers, model disagreement, uncertainty buckets, top-choice margin, sample disagreement, and side-effect awareness. Whether that actually reduces review load without losing important cases is a key evaluation question.

## No Solved Claim

Agentic risk is a live field. New model releases, tool permissions, connectors, memory systems, and delegation patterns will create new risk surfaces. Human users will expose some risks through ordinary use and public experimentation. Over time, adversarial agents may expose others by probing models and workflows at machine speed.

The right claim is therefore modest: this prototype shows a public-safe operating pattern for turning noisy signals into reviewable events, safe probes, and patch candidates. It does not prove prevalence, precision/recall, or production robustness.

## Key Risk In The Product Itself

The monitor must not become a surveillance layer. If it uploads raw user prompts or outputs by default, it creates its own trust and privacy problem. The right posture is local-first, auditable, opt-in, and aggregate-first.

## Prototype Location

- `studies/agentic-risk-antivirus/README.md`
- `studies/agentic-risk-antivirus/rules/risk_signatures.json`
- `studies/agentic-risk-antivirus/src/local_risk_monitor.py`
- `studies/agentic-risk-antivirus/src/anonymize_events.py`

## Best Next Experiment

Run the local monitor against synthetic agent traces, then convert the resulting local events into `Agentic Risk Trace` JSON. That would connect endpoint-style detection to the repo's operating-picture layer.

The next version should add a constrained agent-on-agent simulation: one benign challenge agent generates safe abstract vulnerability hypotheses, a target agent produces an observable run, and the monitor scores where the first useful intervention should occur without reproducing harmful exploit details.
