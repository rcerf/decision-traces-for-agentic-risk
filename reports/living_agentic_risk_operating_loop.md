# Living Agentic Risk Operating Loop

Date: 2026-07-02  
Status: concept architecture for the portfolio artifact

## Bottom Line

This project should not claim to solve agentic risk. The stronger claim is that agentic risk needs a living operating loop for intelligence, triage, testing, patching, and residual monitoring.

The field will keep moving:

- new frontier models will change capability boundaries;
- new product surfaces will add tool, connector, memory, and delegation paths;
- users, researchers, journalists, policymakers, and adversaries will expose new weak signals;
- agent-on-agent probing may discover and transfer risk motifs faster than human review cycles;
- defenders will need to ship controls fast enough to keep the defended model or product surface from being exploited at scale.

## System Shape

```text
signal sensors
  -> signal/noise triage
  -> risk ontology and delta matrix
  -> safe probe generation
  -> staged monitoring over observable runs
  -> decision trace
  -> patch object
  -> shipped control
  -> residual-risk monitor
```

## Signal Sensors

The system should ingest multiple signal classes without treating every source as equally reliable:

- public research papers and benchmark updates;
- incident databases and public postmortems;
- system cards, framework updates, and standards;
- journalism, policy concerns, and regulator focus areas;
- curated social/X weak signals reviewed before ingestion;
- local risk-monitor events with aggregate-only telemetry;
- red-team and eval findings;
- safe agent-on-agent probe summaries;
- opt-in local signal-sharing concepts that would need separate privacy, security, and utility validation before any real deployment.

The important discipline is safe abstraction. Raw jailbreak prompts or exploit recipes should not become the corpus. The corpus should preserve risk class, surface, authority, precondition, control gap, and proposed safe probe.

## Triage

Each incoming signal should be scored for:

- source credibility;
- novelty;
- affected surface;
- attacker capability required;
- blast radius;
- reversibility;
- detection latency;
- safe-probe feasibility;
- likely owner;
- whether the signal fills an empty cell in the risk matrix.

This keeps the system from confusing volume with importance.

## Patch Objects

A patch is any reviewable artifact that reduces risk or improves visibility. It may be:

- a transparent local signature;
- a small-model classifier update;
- a new eval or benchmark fixture;
- a product mitigation;
- an approval UX change;
- a tool-permission constraint;
- a connector boundary;
- a policy clarification;
- a model-behavior fix;
- a monitoring trigger that reopens the risk if behavior regresses.

The point is not to make every problem look like software antivirus. The point is to shorten the loop from credible risk signal to tested mitigation.

## Opt-In Signal-Sharing Concept

One possible public-facing concept could be a Folding@Home-style and beta-user-style risk network:

- users self-select into running an auditable local monitor;
- the monitor code, signatures, and outbound telemetry schema are inspectable;
- raw prompts, raw outputs, files, and tool arguments stay on the user's machine by default;
- volunteers can opt into local safe challenge fixtures against their own models or workflows;
- the central service receives aggregate events, hashed evidence fingerprints, uncertainty buckets, route decisions, and patch-version metadata;
- volunteers can receive early patch packs, signature updates, eval fixtures, and local mitigations.

This is the desired design constraint, not a proven result: create a useful signal loop without turning the monitor into surveillance infrastructure.

### Uncertainty-Gated Triage

Sovereign OS contains a useful prior pattern: a cheap on-device uncertainty signal routes work between local handling, stronger models, and deeper review. For agentic risk, the same pattern could become:

```text
local event
  -> deterministic signature check
  -> uncertainty / margin / disagreement measurement
  -> local route decision
  -> aggregate-only telemetry
  -> central patch prioritization
```

The hypothesis to test is whether this can reduce unnecessary human flagging while preserving expert attention for privacy exceptions, high-blast-radius ambiguous cases, novel clusters, and patch decisions.

## Agent-On-Agent Frontier

The next risk frontier is not only human users discovering jailbreaks. It is automated systems probing other systems, chaining weaknesses, and transferring motifs across models and tools.

The safe research version should avoid harmful exploit reproduction and instead preserve:

- what surface was probed;
- what authority was at stake;
- what boundary was crossed;
- what observation made the run risky;
- where the first useful intervention occurred;
- what patch object would reduce the risk;
- what residual monitor would show whether the patch held.

## Controlled Pre-Release Probe Lab

The proactive version could be a controlled internal probe lab for pre-release systems:

- adversarial agents search for vulnerable white space using abstracted historical motifs, newly patched failures, and safe strategy prompts;
- defensive agents and product controls attempt to defend the target workflow with approval gates, tool constraints, policy checks, retrieval boundaries, memory controls, and monitoring;
- the target set could include an unreleased model, a current public model, earlier patched variants, and product/workflow scaffolds;
- expert strategists review where adversarial agents are being creative, where defensive controls are brittle, and which empty cells deserve human-designed probes;
- analysts convert credible findings into traces, patch objects, release gates, and residual monitors.

The purpose would be to learn before deployment. The lab should ask whether a new model can rediscover old failures, mutate recently patched failures, or find novel combinations between known controls. It should not preserve or publish raw exploit content; the preserved artifact is the risk structure and the mitigation decision.

## What This Prototype Demonstrates

This repo demonstrates the operating shape with public-safe materials:

- public signals become safe hypotheses;
- hypotheses become a risk-delta matrix;
- high-value cells become safe probes;
- observable runs become staged sentinel events;
- events become decision traces;
- traces identify owners, mitigations, residual gaps, and patch candidates.

It does not demonstrate production precision/recall, prevalence, private telemetry performance, or robust defense against adaptive attackers. Those are next evaluation questions.

## Current Patch-Loop Case

The repo now includes one synthetic public-safe patch-loop case:

- `reports/agent_on_agent_patch_loop_case.md`
- `studies/patch-loop-case/`

It demonstrates:

```text
curated public signal
  -> risk-delta cell
  -> safe probe
  -> synthetic agent run
  -> sentinel event
  -> agentic risk trace
  -> patch object
  -> residual monitor
```

## Best Next Build

Extend that case into a constrained runnable harness: one benign probe agent creates abstract risk hypotheses, a target agent performs a synthetic workspace task, the staged sentinel identifies the first useful intervention point, and the renderer emits the patch-loop report without retaining raw exploit detail.
