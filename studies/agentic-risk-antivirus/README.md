# Agentic Risk Signal-Sharing Loop

Status: local-first prototype  
Purpose: explore a limited antivirus-inspired operating model for agentic AI risk detection and patch-loop learning.

## Product Idea

Traditional antivirus systems combine local detection, signature updates, optional sample submission, central analysis, and shipped protections. Agentic risk may be able to borrow that loop carefully:

```text
local prompts / outputs / tool traces / telemetry
  -> local open-source risk signatures and small-model checks
  -> local risk event
  -> optional anonymized aggregate submission
  -> central corpus and analyst review
  -> new signatures, probes, evals, mitigations, approval UX changes, and model/policy updates
  -> shipped protection back to local clients
  -> residual-risk monitoring
```

This is not a production safety system. It is a portfolio prototype for the operating pattern. The point is not that risk is solved; the point is that the field will keep moving and defenders need a disciplined way to keep receiving, classifying, testing, and patching credible signals.

## Why The Analogy Is Useful

The antivirus analogy has three useful lessons for agentic risk:

1. Detection should happen locally before harm leaves the machine or workflow.
2. Signatures should be auditable, inspectable, and updateable.
3. Central intelligence improves when clients can submit suspicious signals safely.

The agentic version should be stricter about privacy because prompts, outputs, and tool traces can contain personal, enterprise, legal, medical, or credential data.

The agentic version also needs to account for a changing adversarial environment. Today many signals come from human use, research papers, red teams, journalists, policy debate, and public social channels. Over time, more signals may come from agent-on-agent pressure: automated systems probing other systems, transferring attack ideas, or discovering failures in tool, memory, connector, and approval workflows.

## Privacy Posture

Default:

- Run locally.
- Store detections locally.
- Do not upload raw prompts, raw outputs, tool arguments, files, or retrieved documents.
- Hash evidence excerpts locally.
- Share only aggregate counts, signatures, stages, severity, and coarse telemetry buckets.

Optional advanced mode:

- User-approved sample submission for sanitized cases.
- Enterprise-controlled collector.
- Differential privacy or secure aggregation for high-volume telemetry.
- Human review before any raw sample leaves a machine.

## What The Prototype Includes

- `rules/risk_signatures.json`: auditable signature pack.
- `data/sample_sessions.json`: public-safe local sessions.
- `src/local_risk_monitor.py`: local scanner for prompt, output, tool, and telemetry risk.
- `src/anonymize_events.py`: strips evidence and emits aggregate-safe telemetry.
- `tests/test_local_risk_monitor.py`: regression tests.

## Patch Objects

The central system should not only ship one kind of "patch." Depending on the signal, the patch may be:

- a transparent local signature;
- a small-model classifier update;
- a new safe probe or eval case;
- an approval-flow or tool-permission mitigation;
- a product guardrail;
- a policy update;
- a model-behavior fix;
- a residual-risk monitor that checks whether the fix actually holds.

## Run

```bash
python3 studies/agentic-risk-antivirus/src/local_risk_monitor.py \
  studies/agentic-risk-antivirus/data/sample_sessions.json \
  --signatures studies/agentic-risk-antivirus/rules/risk_signatures.json

python3 studies/agentic-risk-antivirus/src/local_risk_monitor.py \
  studies/agentic-risk-antivirus/data/sample_sessions.json \
  --signatures studies/agentic-risk-antivirus/rules/risk_signatures.json \
  --output /tmp/local-risk-events.json

python3 studies/agentic-risk-antivirus/src/anonymize_events.py \
  /tmp/local-risk-events.json \
  --output /tmp/local-risk-aggregate.json
```

## Source Anchors

- ClamAV: open-source antivirus engine with command-line scanning and automatic signature updates, https://www.clamav.net/
- YARA: pattern descriptions for identifying and classifying malware samples, https://virustotal.github.io/yara/
- Microsoft Defender cloud protection and sample submission, https://learn.microsoft.com/en-us/defender-endpoint/cloud-protection-microsoft-antivirus-sample-submission
- NIST differential privacy resources, https://www.nist.gov/blogs/cybersecurity-insights/differential-privacy-privacy-preserving-data-analysis-introduction-our

## Best Next Build

Replace the deterministic signature pack with a hybrid local engine:

- transparent signatures for high-precision known risks;
- small local classifier for ambiguous prompt/output categories;
- optional model telemetry adapter;
- user-reviewed sanitized submission queue;
- central signature/probe update pipeline;
- constrained agent-on-agent safe-probe simulator for testing how quickly new risk motifs move from discovery to mitigation.
