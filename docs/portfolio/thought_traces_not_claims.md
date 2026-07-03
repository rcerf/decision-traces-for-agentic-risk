# Thought Traces, Not Claims

This page is a framing note for reviewers.

The repo is not trying to prove that I solved agentic risk, invented a new alignment method, or built a production detector. I have not. It is trying to make my operating style inspectable: how I turn ambiguous risk into structure, how I preserve uncertainty, how I decide what deserves deeper review, and how I update the system when evidence does not fit the taxonomy.

## What This Shows

### 1. Case-to-corpus thinking

My strongest product-risk work treated individual decisions as reusable evidence. A review was not only "approve or block this launch." It became facts, rationale, mitigation, owner, unresolved risk, dependency, and next-review date.

This repo applies the same pattern to agentic AI risk: weak signals become safe hypotheses, hypotheses become probes, probes become traces, and traces become an operating picture.

### 2. Residual discovery

If a new case does not fit the existing taxonomy, that is not just a classification failure. It is information. It may reveal a missing category, a missing owner, a missing control, or a risk surface that has not been instrumented yet.

That is the practical idea behind the artifact-routing / residual-review language in my private Sovereign OS work. I would not present that work as a solved theory. I would present it as a useful operating instinct: look for the thing that does not fit, then decide whether the structure needs to change.

### 3. AI-assisted risk governance

The governance idea I am most comfortable defending is operational, not grand: log the decision, observe the override, record the precedent, update the taxonomy, and route the next ambiguous case through a better review path.

That shows up here as decision traces, approval gates, residual-risk monitors, and patch-loop objects. It also shows up in my private prototypes around human override tracking, novelty-based routing, and memory/retrieval boundary controls.

### 4. Evidence humility

Some of my independent model-observation work produced promising signals. Some produced marginal results. Some should be killed or softened because simpler baselines were competitive.

That is useful to show because risk work gets dangerous when every idea becomes a claim. The discipline is to keep counts separate, name uncertainty, distinguish prototypes from measurements, and retire language that the evidence cannot carry.

### 5. Current operating picture

Agentic risk will keep changing as models, tools, connectors, memory, delegation patterns, public jailbreaks, red-team findings, incidents, policy concerns, and product surfaces change.

The artifact I would want on a risk team is therefore not only a policy or a static taxonomy. It is a current operating picture: what signals exist, what they imply, who owns the mitigation, what uncertainty remains, what needs review, and what gaps should be investigated before they appear as incidents.

## How To Read The Repo

Read the README as the main artifact. It is intentionally long so a reviewer can understand the operating model without opening many files.

Then inspect:

- `reports/sample_agentic_risk_brief.md` for a compact analyst-style output.
- `examples/ART-007-public-benchmark-indirect-injection.json` for the structured trace shape.
- `schema/agentic_risk_trace.schema.json` for what the trace requires.
- `docs/portfolio/model_observation_evidence_appendix.md` for count discipline and caveats around the independent model-observation work.
- `studies/model-risk-sota/working_paper_outline_negative_space_risk_discovery.md` for the more speculative working-paper framing.

## What Not To Infer

Do not infer that this repo is:

- a production detector;
- a benchmark;
- a claim of measured real-world prevalence;
- a claim of novel academic research;
- a repo of raw jailbreak prompts or exploit recipes;
- evidence that I have validated a cognitive-fingerprint method;
- a replacement for internal telemetry, evals, red teaming, policy review, or human investigation.

The narrower claim is enough:

> I can take ambiguous risk signals, turn them into inspectable structure, preserve uncertainty, identify owners and mitigations, and keep the system honest as new evidence arrives.
