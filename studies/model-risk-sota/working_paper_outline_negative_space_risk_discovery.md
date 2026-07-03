# Working Paper Outline: Negative-Space Risk Discovery

Status: draftable research spine  
Date: 2026-07-02

## Tentative Title

Negative-Space Risk Discovery For Agentic AI Systems

## One-Sentence Claim

Agentic AI risk analysis can become more proactive by using a living ontology to identify structurally implied but under-evidenced risk cells, then converting those cells into safe probes, observable traces, control evidence, and reviewable operating decisions.

This is not a solved-safety claim. It is a claim about operating cadence in a live field.

## Research Question

Can a structured crosswalk of capability deltas, agentic surfaces, tool authorities, data classes, user populations, and deployment contexts generate useful risk hypotheses before those risks appear clearly in public incidents, social media, or benchmark suites?

## Contribution

The contribution is not a universal taxonomy or a production detector. It is a workflow:

```text
signal intake
  -> capability delta
  -> risk ontology crosswalk
  -> empty-cell hypothesis
  -> safe probe
  -> staged sentinel result
  -> trace
  -> owner, mitigation, residual risk, next review
  -> patch object
  -> residual-risk monitor
```

## Why This Matters

Agentic systems create risks across trajectories, tools, memory, approvals, connectors, and deployment contexts. A final-output-only risk process can miss the action path. A taxonomy-only process can miss new risks created by new capabilities. Negative-space discovery tries to make those missing cells visible.

The frontier will also become more adversarial. New risks will not only be exposed by human prompting or public utilization. Some will be exposed by agent-on-agent probing, model-vs-model comparison, and automated attempts to transfer weakness across systems. A living ontology should treat that conflict as a signal source while preserving safe-abstraction rules.

## Method

1. Build a seed ontology from public frameworks and research.
2. Track new capability and product deltas.
3. Score capability/risk intersections for shared surfaces and new authorities.
4. Promote high-scoring empty cells into safe probes.
5. Run staged sentinel analysis over synthetic or benchmark-derived traces.
6. Convert findings into decision-ready risk traces.
7. Review whether the trace created a new owner, control, metric, patch object, or residual-risk question.
8. Monitor whether the patch reduced risk without unacceptable utility loss.
9. For high-priority pre-release risks, explore a controlled role-separated probe lab where adversarial agents search for vulnerable white space, defensive agents attempt to protect workflows, and expert strategists adjudicate novelty and next probes.
10. For public deployment signals, explore opt-in local signal sharing with uncertainty-gated routing and aggregate-only telemetry.

## First Evaluation

Use public-safe materials only:

- 10-20 public source signals.
- 4-6 capability deltas.
- 5-8 risk classes.
- 5 generated risk-delta cells.
- 3 safe probes.
- 2 observable synthetic runs.
- 1 operating-picture brief.

## Success Criteria

- The generated cells are not already obvious restatements of the seed taxonomy.
- At least two cells produce actionable safe probes.
- At least one probe produces a trace with a specific owner/control/residual-risk question.
- The method avoids raw exploit reproduction.
- The method can be audited end to end from public inputs to generated output.

## Failure Modes

- The ontology creates vague speculation instead of testable hypotheses.
- The scoring rewards novelty without actionability.
- The monitor uploads private user content.
- The workflow duplicates existing benchmarks without adding operational value.
- The paper overclaims prevalence or novelty.
- The patch loop becomes a list of proposed fixes without evidence that they changed behavior.
- Agent-on-agent probes produce unsafe exploit detail rather than safe, reviewable abstractions.

## Relationship To The Signal-Sharing Concept

The signal-sharing product concept is a possible deployment layer for the paper idea:

- local monitor detects known risk motifs;
- anonymized aggregate signals identify emergent motifs;
- central analysis updates signatures and probes;
- new signatures, evals, mitigations, approval changes, and model/policy updates are shipped back;
- the ontology records both detected risks and structurally plausible empty cells.

The opt-in local signal-sharing concept is one possible version of this deployment layer. Users would run an inspectable local monitor, verify that private data stays local, contribute aggregate signals, and receive early patch packs. Uncertainty-gated routing is a hypothesis to test: deterministic rules, local models, uncertainty buckets, margin checks, and disagreement measures may help decide which events stay in aggregate watch and which become patch candidates.

## Patch Loop

The working paper should use "patch" broadly:

```text
risk signal
  -> analyst triage
  -> safe probe / eval case
  -> trace and owner
  -> patch object
  -> rollout decision
  -> residual monitor
```

A patch object might be a local signature, classifier update, system prompt rule, approval UX change, tool-permission constraint, connector boundary, policy clarification, eval case, or model-behavior change. The key research question is whether the loop lets a defended system respond faster than the risk can be exploited at scale.

## Controlled Pre-Release Probe Extension

The strongest internal version would test a model before public release by putting it in controlled conflict with itself, public models, and prior patched variants.

```text
historical patched attack motifs
  -> adversarial strategy search
  -> target model/public model workflow
  -> defensive mitigation attempt
  -> expert strategist review
  -> trace, patch object, release gate, residual monitor
```

The research question is whether stronger model capability can be used defensively: can a new model rediscover historical failures, mutate recently patched motifs, and identify adjacent vulnerable white space before those risks are exposed by public use?

## Opt-In Signal-Sharing Extension

The strongest public version would let volunteers self-select into a safety network:

```text
inspectable local monitor
  -> privacy invariant check
  -> deterministic / model / uncertainty-gated triage
  -> aggregate-only network signal
  -> central patch prioritization
  -> signed early patch distribution
```

This adapts the Sovereign OS routing-gate pattern: use a cheap local uncertainty signal to route ordinary cases locally and escalate ambiguous or high-risk cases without defaulting to human review for everything. The review-load benefit would need to be measured.

## Minimal Artifact For OpenAI Review

The portfolio version should include:

- `reports/agentic_risk_antivirus_assessment.md`
- `studies/agentic-risk-antivirus/`
- `reports/open_sentinel_network_assessment.md`
- `studies/open-sentinel-network/`
- `reports/risk_delta_matrix.md`
- `studies/risk-delta-matrix/`
- `reports/frontier_red_green_conflict_lab.md`
