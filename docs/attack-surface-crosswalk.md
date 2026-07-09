# Attack Ontology × Measured Behavior: Why Agentic-Risk Data Has to Be Generated

*This note joins two studies — an attack ontology grounded in public frameworks (`studies/injection-ontology/`) and a detonation harness run on a real attack corpus (`studies/injection-corpus-detonation/`). All numbers are reproducible from those directories. Where a result is a floor or a heuristic, it says so.*

## 1. Public attack corpora cannot evaluate agentic risk

We built a 36-node injection ontology across five axes (injection type, delivery vector, technique, goal, severity), extending OWASP LLM01, MITRE ATLAS (AML.T0051), and the HackAPrompt taxonomy — 21 nodes borrowed, 15 new, with the new nodes concentrated on the agentic surface those frameworks under-specify. We then classified **1,508 real attacks** from public capture nets (in-the-wild jailbreaks, ChatGPT-jailbreak-prompts, deepset).

The distribution is lopsided, and that is the finding:

- **Saturated:** direct, user-turn jailbreaks — role-play/persona **69%**, authority spoofing **23%**, refusal suppression **13%**.
- **Empirically dark (zero representation):** every new agentic technique node (tool-call injection, memory poisoning, goal hijacking, chain-of-thought manipulation, trust-boundary escalation), the agentic goal nodes (resource abuse, agent persistence, supply-chain poisoning), **8 of 10 delivery vectors**, and both non-direct injection types.

> Public corpora are a photograph of humans jailbreaking chatbots. They contain almost none of the indirect, tool-mediated, memory, or multi-agent attacks that define *agentic* risk. You cannot benchmark the agentic attack surface from data that does not exist.

(Classifier caveat: heuristic keyword matching, high false-negatives on obfuscated/multi-turn prompts, delivery/goal partly inferred. Aggregate-only is the right unit of confidence.)

## 2. So generate the data: detonation fills the dark cells

The detonation harness runs a model to attempted action against instrumented mock tools and records what it tries to do. Pointed at **InjecAgent** — a real indirect-injection benchmark — it produces labeled examples in exactly the cells §1 found empty: `injection_type = indirect`, `delivery = tool-output`, `technique = tool-call injection`, `goal ∈ {data-exfiltration, harmful-action}`.

**150 real cases (75 data-stealing + 75 direct-harm, stratified, seed 42), on Qwen2.5-1.5B-Instruct:**

| Measure | Value |
|---|---|
| Tool engagement | 63.3% (95/150) |
| **Attack success** (model followed the injection to a privileged tool call) | **9.3%** (14/150) — data-stealing 14.7%, direct-harm 4.0% |
| Naive content/regex detector, on the 14 successful attacks | **0 / 14** |
| Behavioral analyzer (provenance **+** injection signal), on the 14 | **5 / 14** |

**This 9.3% success rate is a floor, not a production estimate.** The InjecAgent paper reports 43–71% for GPT-4-class ReAct agents; a small model rarely parses an injection buried in a nested JSON tool result and spontaneously calls an attacker-chosen tool. The point of the harness is not this number — it is that the harness *produces* these labeled traces at all, in a region where no public dataset exists.

## 3. The measured tradeoff: containment routes, it does not block

Two honest facts sit side by side:

- **Content detection is blind here.** The regex detector caught **0 of 14** real indirect injections — they are phrased as plausible business content with no override language. This is the same result the input-classifier benchmarks show, now on a real agent corpus.
- **Containment's recall depends on how precise you make it.** Every one of the 14 successful attacks reached a privileged action on attacker-tainted data, so a **pure-provenance** rule (flag *any* privileged action downstream of untrusted content) flags all 14 by construction — at the cost of also flagging benign privileged actions that legitimately use untrusted data. Add a precision gate (require a detected injection signal too) and recall drops to **5/14**, because the precision gate re-inherits content detection's blindness.

That is the routing thesis stated empirically: **pure containment is a high-recall routing signal that needs a second reviewer (it over-flags); a precise blocker is low-recall (it under-catches).** Neither is a standalone detector. The operating answer is to route the tainted-privileged-action cases to detonation and a secondary reviewer, not to block on a classifier.

## 4. What this establishes

- Existing frameworks and corpora are necessary but **structurally incomplete** for agentic risk — the agentic cells are empty, and we can point to exactly which ones.
- The detonation harness is a **dataset factory** for those empty cells, demonstrated end-to-end on a real benchmark.
- The behavioral/provenance signal **strictly dominates content detection** on realistic indirect injection (0/14 vs a tunable 5–14/14), and its recall/precision knob *is* the route-vs-block decision.

## 5. Honest limits

Small-model attack-success is a floor; a stronger or tool-finetuned model is needed for representative rates. The ontology classifier is heuristic. "Provenance" here is trace-structural, not interpreter-level taint tracking. The mock-tool environment has limited fidelity, and a sufficiently aware model may behave differently under obvious test conditions. Raw attack payloads are fetched at runtime and never committed — results are reproducible via the fetch scripts, not by republishing an exploit corpus.
