# Three-Minute Brief

## What This Is

This is a compact, public-safe prototype for thinking about agentic AI risk.

It is not a production detector, a benchmark, or a claim that agentic risk is solved. It is a small artifact meant to make an operating model visible: how weak signals can become safe probes, structured decision traces, mitigation decisions, owners, and residual-risk follow-up.

The intended reaction is modest:

> This is an interesting way to organize the work. It is concrete enough to inspect, humble enough not to overclaim, and relevant enough to discuss.

## The Core Idea

Agentic risk will not stay still. New models, tools, connectors, memories, user behaviors, public jailbreaks, and agent-on-agent attacks will keep changing the risk landscape.

The useful operating question is:

> How do we keep a current picture of emerging risk, turn credible signals into safe tests, assign ownership, ship mitigations, and keep checking whether the residual risk changed?

This prototype sketches that loop.

```text
weak signal
  -> safe risk hypothesis
  -> safe probe
  -> observable run
  -> structured trace
  -> owner, mitigation, approval gate, residual risk
  -> patch or monitor
  -> next review
```

## Why This Maps To My Background

At Meta, my work was not only interpreting individual product-risk questions. It was turning repeated ambiguous judgments into a legible corpus: facts, rationale, mitigations, owners, unresolved risk, and review triggers.

This repo applies the same operating pattern to a new substrate:

- model behavior;
- tool use;
- memory and retrieval;
- connector boundaries;
- prompt injection;
- approval gates;
- public weak signals;
- future agent-on-agent pressure.

The artifact is small, but it shows how I think: make ambiguity legible, preserve evidence and uncertainty, organize repeated cases into a taxonomy, and use empty cells in the framework to ask what risk should be present but has not yet been found.

## What To Read

Start with:

1. `README.md`
2. `reports/sample_agentic_risk_brief.md`
3. `examples/ART-007-public-benchmark-indirect-injection.json`
4. `docs/portfolio/model_observation_evidence_appendix.md`

For a deeper review, continue to:

1. `docs/portfolio/hiring_manager_tour.md`
2. `docs/portfolio/working_paper_preview.md`
3. `docs/portfolio/end_to_end_case_study.md`
4. `reports/living_agentic_risk_operating_loop.md`
5. `reports/frontier_red_green_conflict_lab.md`
6. `reports/open_sentinel_network_assessment.md`

## What This Does Not Prove

This prototype does not prove production precision, real-world prevalence, robustness against adaptive attackers, or suitability for any specific deployed model.

Those are exactly the next questions a serious team would test.
