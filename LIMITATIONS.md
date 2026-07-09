# Limitations

One page, so nothing important is buried. This repo is a **portfolio prototype** — an
inspectable operating model for agentic-risk analysis, not a production system, a
benchmark leaderboard, or a claim that agentic risk is solved.

## Data: mostly synthetic, some real

- Most decision traces in `examples/` are **synthetic**, hand-authored to illustrate the
  format across failure surfaces.
- **One trace is real and cited**: `examples/real_incidents/` (the 2024 Slack AI indirect
  prompt-injection / data-exfiltration disclosure), with its genuinely open questions
  preserved rather than invented.
- **One benchmark is real and reproducible**: `benchmark/` runs the repo's detector against
  the public `deepset/prompt-injections` dataset and regenerates its numbers from committed
  code and a committed data snapshot.

## The public detector is a transparent baseline, not a detector

- The shipped sentinel (`studies/anima-risk-sentinel/`) is **deterministic regex** — six
  fixed patterns. On the real deepset set it scores **0.8% recall** (`benchmark/RESULTS.md`):
  it catches the classic "ignore previous instructions" phrasing and almost nothing else,
  and it is trivially evaded by rephrasing, encoding, or language switching.
- The synthetic sentinel ablation ("catches 3/3") uses fixtures written to match those
  patterns, so it demonstrates the **operating concept** (catch risk before final output),
  **not** a measured detection rate.

## The impressive injection numbers are private and unreproducible

- `docs/portfolio/injection_sentinel_benchmark_results.md` reports ~95% recall on deepset —
  but from a **private tiered pipeline (semantic + LLM) that is not in this repo**, at a
  ~70% false-positive cost on clean content. You cannot reproduce those numbers here.
- Read the private page and `benchmark/RESULTS.md` together: they bound the same
  recall/false-positive tradeoff. Usable recall is not free.
- No comparison against off-the-shelf tools (Lakera Guard, Meta Prompt-Guard, NeMo
  Guardrails, Rebuff), which occupy the same curve. A real evaluation would include them.

## The eval set is small and rule-scored

- `evals/` is a small, hand-authored labeled set with a **deterministic** scorer. It passes
  its calibration cases by construction; a separate set of **hard cases documents where the
  rule-based scorer fails** — exactly the cases that need human or LLM-judge review. See
  `evals/README.md`.

## Model-observation evidence is self-reported

- The 44-model behavior registry, 118 result files, and cross-judge study
  (`docs/portfolio/model_observation_evidence_appendix.md`) live in private Sovereign OS
  work; the public repo does not let you verify them. Cross-family judge agreement was
  **not** established (κ≈0.20). Earlier, non-reconstructible counts have been retired and
  are not relied on.

## Build method

- This repo was built quickly, with **AI coding assistance**. The operating model, claims,
  and honesty calls are the author's; the code runs and the tests pass, which is the
  credential — not the authorship method.

## What would raise credibility next

Real internal-eval traces improving analyst consistency; safe probes finding control gaps
faster than ad hoc review; a semantic/ML detection tier with a measured recall/FPR curve;
framework crosswalks (OWASP, MITRE ATLAS, NIST AI RMF); and human-review annotations on the
eval's hard cases.
