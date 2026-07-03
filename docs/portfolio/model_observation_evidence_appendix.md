# Model Observation Evidence Appendix

This appendix exists to keep the portfolio honest. My independent work includes private Sovereign OS logs, benchmark runs, and model-routing experiments that are not published here because they contain working context, raw prompts, or personal/private material. This public repo therefore uses the verified source summaries below rather than raw logs.

## What Is Verified Locally

| Evidence Source | Verified Public-Safe Summary | What It Supports | What It Does Not Prove |
|---|---|---|---|
| Sovereign OS model registry snapshot | 44 model entries in a version-controlled model-behavior snapshot generated on 2026-02-22 | I built a structured registry for comparing public model behavior across providers and formats | It does not prove production-grade model profiling or safety relevance by itself |
| Capability-hubris benchmark summary | 44 models, 118 benchmark result files, 1,000 bootstrap iterations, and cluster-stability outputs | I ran structured cross-model probes and summarized format sensitivity / tool-channel behavior | It is not an industry benchmark and does not measure OpenAI internal systems |
| Prompt-injection sentinel benchmarks | 4 public datasets, 16,578 labeled samples total: 95% recall on deepset (n=116) at a high false-positive cost, 99.8% precision at 32% recall on SPML (n=16,011), and a 31.6% false-positive rate on clean NotInject content (n=339) — full table in `docs/portfolio/injection_sentinel_benchmark_results.md` | I benchmarked a local injection monitor against public datasets and recorded the recall/precision tradeoff instead of hiding it | It is not a production detector; the false-positive rate on clean content is a known open weakness, not a solved problem |
| Cross-judge generalization study | 7 Claude-family judge models over 221 transcripts, with 96 segments scored by all 7 judges: Fleiss κ = 0.947, ICC = 0.997, cross-generation κ = 0.962; the same report records a FAIL where observed group separation (3.7-3.8x) fell short of a hypothesized 6x | I tested whether a scoring method remained stable across judge models, and recorded the failed sub-claim alongside the passing ones | Agreement was measured within one model family; a separate 5-judge heterogeneous panel showed much weaker agreement (mean κ ≈ 0.20), so cross-family generalization is not established |
| Falsification discipline | 4 five-arm validation studies with pre-registered kill criteria (verdicts: one KILL, one PROCEED with a recorded confound caveat, one PROCEED, one REASSESS), plus separate recorded falsification verdicts on other private claims (two FALSIFIED, one KILL, one REJECT) — including killing a personality-fingerprinting claim when a TF-IDF baseline beat the complex method | I retire claims when simpler baselines win or confound controls erase the effect, and I record survivor verdicts too | Negative results on my own private experiments do not prove skill on OpenAI-relevant systems |
| Decision Traces for Agentic Risk repo | 7 public-safe synthetic traces, a validator, staged sentinel checks, intake adapters, risk-delta matrix, and patch-loop sketches | I can translate weak signals into structured risk records, owners, gates, mitigations, and residual monitors | It is a portfolio prototype, not a production detector |

## Count Discipline

Earlier working notes used a shorthand count of 48 models and 2,204 observations. I am not relying on that count in the public-facing application package because I cannot reconstruct the slice precisely.

A later draft also used "391 saved model-behavior measurements." I retired that count too, for the same reason: I could not reproduce it from a single command against the underlying files. Counts in this appendix are limited to ones I can regenerate on demand.

The defensible wording is:

> Built a private exploratory model-observation system inside Sovereign OS, including a 44-model behavior registry, 118 benchmark result files behind a bootstrap-validated cross-model analysis, and a separate 7 Claude-family-judge / 96-segment cross-judge agreement study.

That wording is less flashy and more credible. It shows the real shape of the work without pretending the experiments are more mature than they are.

## What A Sanitized Example Would Look Like

A public-safe row should preserve the structure of the observation without exposing raw prompts, private context, or unsafe details.

| Field | Example |
|---|---|
| Model family | Public frontier or open model, provider abstracted where needed |
| Probe class | Tool-channel format sensitivity |
| Surface | Native tool API vs text/XML tool-call representation vs Pythonic text representation |
| Observation | Model behavior changed materially when the same tool-use task was expressed through a different interface format |
| Risk interpretation | Agentic behavior cannot be evaluated only at the semantic task level; the product surface and tool-call substrate can change reliability |
| Analyst action | Add trace field for interface/provenance, require benchmark-to-trace adapter, and track first useful intervention point |
| Residual uncertainty | Need more benign controls, repeated runs, and independent review before treating this as a stable model characteristic |

## Why This Matters For Agentic Risk

The relevant skill is not the count. It is the habit of turning many messy observations into a usable operating picture:

1. Define what counts as an observation.
2. Preserve model, provider, surface, task, format, and outcome.
3. Separate raw behavior from analyst interpretation.
4. Track uncertainty and competing hypotheses.
5. Convert repeated patterns into a taxonomy.
6. Use the taxonomy to find gaps worth probing safely.

That is the same operating pattern used elsewhere in this portfolio: weak signals become hypotheses, hypotheses become safe probes, probes become decision traces, and traces become owners, mitigations, approval gates, residual risks, and next review points.

## Next Credibility Step

The best next step is not to publish raw logs. It is to add a small public fixture set:

1. Select 5-10 benign, public-safe probe tasks.
2. Run them across a smaller set of public models.
3. Publish the schema, aggregate observations, and sanitized trace examples.
4. Include benign controls and false-positive notes.
5. Add a benchmark-to-trace adapter for a public source such as AgentDojo or BIPIA.

That would make the evidence layer independently inspectable while keeping the portfolio modest and safe.
