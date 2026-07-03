# Opt-In Signal-Sharing Concept Assessment

Date: 2026-07-02  
Status: synthetic aggregate-only network triage output

## Bottom Line

An opt-in signal-sharing network could let users contribute to agentic-risk discovery without sending private data to a central service. This is a synthetic concept report: the local monitor stays inspectable, raw content remains local by default, and uncertainty-gated triage is a hypothesis to test, not a proven reduction in human review.

This report is generated from synthetic node events only. It does not claim production prevalence, precision/recall, or private telemetry performance.

## Sovereign OS Routing-Gate Transfer

The relevant Sovereign OS pattern is cheap local uncertainty measurement followed by route selection. In this risk version, deterministic signatures, uncertainty, top-choice margin, sample disagreement, model disagreement, challenge mode, and side-effect awareness could help decide whether an event stays in aggregate watch, enters agentic review, or becomes a patch candidate.

```text
local monitor event
  -> privacy invariant check
  -> deterministic signature and uncertainty scoring
  -> route decision
  -> aggregate-only telemetry
  -> patch prioritization
  -> signed patch distribution
```

## Network Summary

- Nodes: 4
- Aggregate events: 4
- Node modes: observer=2, patch_preview=1, red_team_volunteer=1
- Patch channels: preview=2, stable=2
- Routes: aggregate_watch=1, auto_promote_patch_candidate=3

## Routed Events

| Node | Event | Category | Score | Route | Entropy | Margin | Sample Disagreement | Model Disagreement | Patch Version |
|---|---|---|---:|---|---:|---:|---:|---:|---|
| NODE-001 | EVT-001 | connector_scope_ambiguity | 14 | auto_promote_patch_candidate | 2.30 | 0.06 | 0.62 | 0.55 | 2026.07.02-stable |
| NODE-004 | EVT-004 | approval_quality_failure | 10 | auto_promote_patch_candidate | 1.90 | 0.09 | 0.51 | 0.40 | 2026.07.02-stable |
| NODE-002 | EVT-002 | agent_on_agent_probe | 9 | auto_promote_patch_candidate | 3.10 | 0.04 | 0.74 | 0.71 | 2026.07.02-preview |
| NODE-003 | EVT-003 | benign_uncertainty | 0 | aggregate_watch | 1.40 | 0.29 | 0.18 | 0.22 | 2026.07.02-preview |

## Privacy Invariants

- No raw prompt fields are accepted.
- No raw output fields are accepted.
- No raw tool arguments, files, documents, or evidence text are accepted.
- Nodes must be aggregate-only.
- Nodes must report that private data does not leave the device.
- Events marked as containing raw content or private data are rejected before aggregation.

## Patch Distribution Model

- Stable channel receives conservative signature and mitigation updates.
- Preview channel receives early patch packs, eval fixtures, and red-team challenges.
- Patch packs should be signed, versioned, inspectable, and reversible.
- Local clients should report only patch version, route decision, risk category, uncertainty buckets, and aggregate counts.

## Best Next Build

Add a signed patch-manifest simulator and a local privacy-inspector command that verifies the outbound payload contains no raw prompts, outputs, files, or tool arguments.
