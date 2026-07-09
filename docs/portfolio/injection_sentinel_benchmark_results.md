# Injection Sentinel — Public-Dataset Benchmark Results

These are results from benchmarking a private, local prompt-injection monitor (part of my Sovereign OS work) against four public injection datasets on 2026-02-22. The monitor is a tiered pipeline: fast deterministic/semantic checks first, an LLM-assisted classifier only where ambiguity justifies the cost.

This page exists for the same reason as the evidence appendix: to show real numbers, including the unflattering ones, rather than describe the work in adjectives.

> **Public vs. private — read this first.** The numbers on *this* page come from a
> **private** tiered pipeline (semantic + LLM-assisted) that is **not shipped in this repo**,
> so you cannot reproduce them here. For numbers you *can* reproduce from the public code,
> see [`benchmark/RESULTS.md`](../../benchmark/RESULTS.md): the repo's **public, deterministic
> regex** detector scores **0.8% recall** on the full deepset set (N=662) — near-inert on
> paraphrased injections. Read the two together: regex alone is cheap and misses almost
> everything; the private semantic+LLM tier below reaches ~95% recall but pays a ~70%
> false-positive cost. They bound the same tradeoff — usable recall is not free.

## Results

| Dataset | Composition | N | Config | Recall (TPR) | False-positive rate | Precision | F1 | Mean latency |
|---|---|---|---|---|---|---|---|---|
| deepset prompt-injections | Mixed | 116¹ | semantic + LLM | 0.950 | 0.696 | 0.594 | 0.731 | ~9.1 s |
| Gandalf (Lakera) | All attacks, no benign samples² | 112 | semantic + LLM | 1.000 | n/a (no negatives) | 1.000 | 1.000 | ~1.5 s |
| NotInject | All benign, no attacks | 339 | semantic + LLM | n/a (no positives) | **0.316** | n/a | n/a | ~7.9 s |
| SPML chat-prompt | Mixed | 16,011 | semantic only (fast tier) | 0.322 | 0.002 | 0.998 | 0.487 | ~7 ms |

¹ This was a 116-row subset. The public reproducible benchmark (`benchmark/RESULTS.md`) uses the full 662-row train+test merge.
² All-attack sets make precision and FPR trivially perfect — the `1.000` Gandalf row measures recall on one attack family, nothing more (see reading #2).

## Honest Reading

1. **The recall/precision tradeoff is real and unresolved.** The deep configuration catches 95% of deepset attacks but flags 31.6% of clean NotInject content — roughly one false alarm per three benign inputs. The fast semantic-only tier inverts this: 99.8% precision at 32% recall. Neither point on the curve is production-grade on its own.
2. **The perfect Gandalf score is not evidence of a perfect detector.** That dataset contains only attacks, so precision and FPR are trivially perfect there; it measures recall on one well-characterized attack family, nothing more.
3. **The latency spread (7 ms vs ~9 s) is the operating insight.** A useful deployment shape is tiered: the fast tier handles volume at high precision, and only uncertain items pay for deep review — the same triage pattern this repo applies to weak signals generally.
4. **What this does not show:** robustness against adaptive attackers, performance on any production traffic, indirect-injection coverage in real agent pipelines, or results on private OpenAI-relevant systems. Datasets and their labels also embed their curators' definitions of "injection."

## Why this page exists

The false-positive number is the most useful one on this page. A monitor that flags a third of clean content is not a safety system; it is a burden generator. Knowing that — with a measured number rather than a hunch — is what turns "I built a detector" into "I know where my detector fails and what the next control-effectiveness question is."

## Prior art

This is not a new class of tool. Lakera Guard, Meta's Prompt-Guard, NVIDIA NeMo Guardrails,
and Rebuff all target prompt-injection detection and sit on points of this same
recall/false-positive curve. This page measures only my own monitors against public
datasets; it does not benchmark against those tools, and a real evaluation would.

## Provenance

Result files (private, in Sovereign OS): `benchmarks/results/injection_sentinel_{deepset_v4_llm,gandalf_v4_llm,notinject_v4_llm,spml_v2}.json`, each with per-dataset counts (TP/TN/FP/FN), config flags, and timestamps. Raw prompts and detector configuration are not published.
