# Routing, Detonation, and a Risk-Evaluation Dataset Factory

*A design note. It describes an architecture and a working prototype, not a solved system or a production claim. Where a component is an open hypothesis, it says so.*

## The premise: you cannot block your way out of agentic risk

Content-level detection of prompt injection does not generalize. Measured on this repo's own data, a production injection classifier lands ~41% recall out-of-distribution, a trained classifier collapses ~85 points cross-dataset, and output entropy separates attacks from benign at chance (d′≈0.07). The field's own direction confirms it: the frontier is moving from *detection* toward *architectural containment* (Google DeepMind's CaMeL, the dual-LLM/quarantine pattern, OpenAI's instruction hierarchy). See `benchmark/` and `studies/internal-signal-probe/` for the measurements.

The usual conclusion — "so detection is useless" — is wrong. Detection is useless **as a blocker**. It is genuinely useful **as a router**. This document is about building the router, and about the dataset it generates as a side effect.

## The reframe: route on blast radius, not on detection confidence

You almost never have enough precision to *block* on a detection signal. You do not need it. The routing decision should key off **what is at stake**, not off how confident a classifier is:

> A request reaching a model that holds root access or sensitive-data access is high-stakes **regardless** of whether anything was detected. Route it out to extra scrutiny because of the blast radius — not because a classifier fired.

This is why routing can be high-precision where blocking cannot: you are betting on "this context could do damage," which you know exactly, rather than on "this input is an attack," which you cannot reliably tell. Detection precision stops being the bottleneck.

Concretely, the routing gate scores an action, not a string:

```
compiled_risk = (1 − agent_trust) × sensitivity × blast_radius × (1 − purpose_alignment)
```

plus a reversibility × blast-scope matrix that maps to a deliberation level (auto-proceed → full review). Low risk proceeds; the uncertain, high-blast middle gets **detonated**; confirmed-benign or confirmed-malicious resolve at the ends.

## The loop

```
propose an agent action
  → MODEL it      compiled_risk score + reversibility×blast matrix → deliberation level
  → DISCOVER      negative-space engine flags adjacent risk cells the taxonomy implies but hasn't seen
  → DETONATE      run the uncertain / high-blast request in a QUARANTINED model with NO real access —
                  only instrumented MOCK tools — all the way to attempted action
  → OBSERVE       capture the behavioral trace: every attempted tool call, its arguments, provenance,
                  and the model's reasoning at each step
  → EVALUATE      a secondary model — or a council of models — analyzes the TRACE (not the input prompt)
                  and returns a risk PROFILE; judges that win on surface appeal but fail on substance
                  are down-weighted ("quarantine on divergence")
  → CAPTURE       the verdict is logged as a testable assessment with a falsification condition,
                  in an append-only ledger; assessments decay over time and re-surface when stale
  → ROUTE         allow / block / escalate-to-human-or-owner, with the trace attached as evidence
```

The pivot most detection work misses: **analyze what the model *did and reasoned*, not what it was *asked*.** An attempted `send_email(to=external, body=<crm rows>)` downstream of untrusted content is a far cleaner signal than any lexical property of the input — and it does not require detecting the injection at all. Containment catches what classification misses.

## The unlock: the pipeline is a dataset factory

Every request routed through detonation produces one labeled example:

```
(scenario + captured behavioral & reasoning trace)  →  (secondary-model verdict: injection? risk profile?)
```

Run the loop and it **manufactures** the corpus that internal-signal research has always lacked: paired *(model-internal-trace ↔ attack-or-benign)* data, at scale, labeled by behavior rather than by a human guessing at inputs. This is the point. A prototype lives in `studies/detonation-harness/`.

That corpus is what makes the next idea testable instead of wishful.

## Open hypothesis: an internal "under-attack" signal — and an honest account of it

The intuition: a model under attack has *some internal inkling* it is being manipulated — the same way a model can tell it is being evaluated. If so, that signal should be readable from its internal state before or independent of its output.

Being honest about where this stands:

- **Output entropy is dead.** We measured it — chance-level. A jailbroken model is *confidently* wrong, so the signal is not in the output distribution.
- **A naive activation probe was inconclusive.** On a 0.5B model, last-token, no reasoning trace, a linear probe separated injection from benign in-distribution but was largely *lexical* — it matched a bag-of-words baseline cross-dataset. It did not demonstrate a transferable "the model knows" signal. (`studies/internal-signal-probe/`.)
- **But the refined version is a real, open research direction, not hand-waving.** Three published lines make it credible: refusal is mediated by a **single activation direction** that jailbreaks suppress (Arditi et al., 2024); models show **emergent introspective awareness** of their own internal states (Anthropic, 2025); and models can **detect that they are being evaluated** (evaluation-awareness). "A model senses it is being jailbroken, the way it senses it is being tested" is the evaluation-awareness result pointed at injection.

The reason the signal has not been found by hand is not that it is impossible — it is that no one had the labeled *(internal-trace ↔ jailbreak)* dataset. The detonation factory produces exactly that. The honest claim here is therefore modest and specific: **this is an apparatus to generate the dataset and a testbed to look for the signal — not a working internal-state detector.** If a probe trained on the growing corpus recovers a transferable signal, that is a finding; if it does not, that is also a finding. Both get reported.

## The flywheel

```
routing → detonation → labeled traces → train internal-signal decoder →
decoder becomes a better first-pass router → more/better detonation → …
```

The system bootstraps its own risk understanding. It does not depend on any single component working perfectly; each rung only has to be good enough to *route*, and the routing generates the data that improves the next rung.

## What is built vs. what is hypothesis

- **Prototyped (runnable), with a first result:** the compiled-risk scoring and the detonation harness — instrumented mock tools, behavioral-trace capture, secondary analysis, labeled-dataset output (`studies/detonation-harness/`). In its first run (Qwen2.5-1.5B, 14 scenarios), a **content/regex detector caught 0 of 7 realistic indirect injections** (plausible business framing, no jailbreak language), while the **behavioral provenance signal caught every attack the model actually followed to a privileged action — 4/4 successful attacks, zero false positives on benign.** The model *resisted* 2 of the 7 and didn't act on 1 — the harness records those too, so the factory produced both successful-attack and resisted-attack labeled examples in a single run.
- **Prototyped, honestly bounded:** the injection benchmarks and the internal-signal probe — both shipped with their negative and null results intact.
- **Hypothesis with a testbed, not a result:** the learned internal-state "under-attack" signal. The factory exists to test it; the result is not claimed.

## Honesty guardrails

Load-bearing, because the credibility of the whole thing depends on them:

- "Quarantine" here means an **isolated, no-real-access execution context with mock tools** — and, for judges, a *classification/down-weighting* rule. It is **not** live-compute privilege separation at the hardware layer.
- Multi-model judge trust weights are **seeded priors** unless and until the calibration runs behind them are made reproducible; they are not represented as empirically calibrated otherwise.
- Small-model tool-use is unreliable; where the harness's model fails to attempt valid actions, that failure rate is reported, not hidden.
- Mock-tool environments have limited fidelity, and a sufficiently aware model may behave differently because it senses a test. Detonation catches the naive-to-moderate case, not necessarily the adaptive adversary.
- Boundary-first / null-set framings (define the prohibited region, harden its perimeter) are used here as **design principles with prototypes**, not as formally proven properties.

## Prior art this builds on

CaMeL / "defeat prompt injection by design" (DeepMind); the dual-LLM/quarantine pattern; OpenAI's instruction hierarchy; AgentDojo (instrument the tools, measure whether the attack's objective completed); refusal-direction probing (Arditi et al., 2024); model introspection and evaluation-awareness. The contribution is not any single one of these — it is composing them into a routing-and-detonation loop that *generates its own evaluation dataset*, and using that dataset to make the internal-signal question empirically testable.
