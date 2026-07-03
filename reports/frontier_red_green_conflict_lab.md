# Controlled Pre-Release Probe Lab

Date: 2026-07-02  
Status: concept architecture for internal pre-release agentic-risk discovery

## Bottom Line

The strongest proactive version of the agent-on-agent idea is a controlled internal probe lab. Instead of waiting for public users, social media, or external researchers to expose new risk motifs, the lab would run contained, public-safe conflict before release.

The lab asks:

> Can a new model, paired with structured strategy, rediscover old failures, mutate recently patched failures, and find vulnerable white space before deployment?

This is not a claim that self-play solves risk. It is a way to use frontier capability defensively while preserving analyst judgment, containment, and release discipline.

## Participants

Red side:

- adversarial agents that generate abstract risk hypotheses;
- a model under controlled evaluation;
- public models used as baselines or comparison targets;
- historical patched attack motifs as seed material;
- expert strategists who identify promising white space between known failures.

Green side:

- defended target workflows;
- approval gates;
- tool and connector constraints;
- memory and retrieval controls;
- policy checks;
- monitoring signatures and classifiers;
- release gates and residual-risk monitors.

Analyst layer:

- triages whether a finding is novel, feasible, and action-relevant;
- maps the finding to risk class, surface, authority, blast radius, reversibility, and owner;
- decides whether the output should become an eval, mitigation, product change, policy update, release gate, or residual monitor.

## Operating Loop

```text
historical patched motifs
  -> red-agent strategy search
  -> target frontier/public model workflows
  -> green-agent mitigation attempt
  -> staged sentinel and telemetry review
  -> expert strategist adjudication
  -> risk trace
  -> patch object
  -> release gate or residual monitor
```

## Target Set

The lab can compare:

- unreleased model against itself;
- unreleased model against current public model;
- current public model against earlier patched variants;
- the same model across tool, memory, connector, and approval configurations;
- a target workflow before and after a proposed mitigation.

The point is not only whether an attack succeeds. The point is where the system becomes brittle, where controls rely on luck, and where a stronger model can invent variants humans did not explicitly enumerate.

## Historical Attack Data

Historical successful attacks should be converted into safe internal motifs:

- risk class;
- affected surface;
- trust boundary crossed;
- required authority;
- control that failed;
- patch that was shipped;
- residual risk after patch;
- adjacent white-space questions.

For public portfolio materials, raw exploit detail should not be preserved. Internally, any sensitive detail should live in access-controlled systems with clear handling rules.

## White-Space Search

The strategist's role is to avoid both random fuzzing and overfitting to last week's patch. Useful prompts for the lab include:

- What adjacent capability would make this old failure reappear?
- What assumption did the patch make about user intent, tool scope, memory, or retrieval trust?
- What changes when the adversary is an agent rather than a human?
- What happens if the target model, red agent, and green agent all share partial knowledge of prior mitigations?
- Which risk cells are structurally implied but not yet evidenced?

The preserved output should be a hypothesis and a safe probe, not raw adversarial content.

## Patch Objects

Findings should become patchable artifacts:

- eval fixtures;
- system-card evidence;
- policy clarifications;
- approval UX changes;
- connector-boundary controls;
- memory provenance constraints;
- tool-permission changes;
- model-behavior fixes;
- monitoring signatures;
- residual-risk triggers;
- release-gate criteria.

## Success Criteria

The lab is useful if it:

- rediscovers old attacks before they regress;
- mutates recently patched failures into adjacent safe probes;
- identifies new high-value empty cells in the risk matrix;
- produces action-ready traces rather than vague warnings;
- reduces risky behavior without unacceptable benign utility loss;
- creates residual monitors that detect whether the patch holds.

## Failure Modes

- The red side optimizes for theatrical attacks rather than plausible product risk.
- The green side overfits to known motifs and blocks benign utility.
- The lab preserves harmful raw exploit detail instead of safe abstractions.
- Expert review becomes rubber-stamp approval rather than adversarial reasoning.
- Results do not translate into owners, patch objects, release gates, or residual monitors.

## Portfolio Positioning

For this public repo, the right artifact is a concept architecture plus synthetic patch-loop case. The credible next build is a constrained local simulator that uses public-safe historical motifs and benign workflows to demonstrate the loop without claiming production robustness.
