# Injection Corpus Detonation — Results

## Setup

| Field | Value |
|-------|-------|
| Dataset | InjecAgent (base splits: direct-harm, data-stealing) |
| Sample size | 150 cases |
| Sample draw | Stratified random, 75 per attacker-goal from base splits, seed=42 |
| Model | `Qwen/Qwen2.5-1.5B-Instruct` |
| Harness | `studies/detonation-harness` (detonate + analyze, unmodified) |
| Run date | 2026-07-07 |
| Wall time | 25.2 min |

## Metrics

| Metric | Value |
|--------|-------|
| Tool-engagement rate | 63.3% (95/150) |
| Attack success rate (all) | 9.3% (14/150) |
| Successful attacks (n) | 14 |
| PROVENANCE-ONLY catch (on successful attacks) | 100.0% (14/14) |
| PRECISE catch (on successful attacks) | 35.7% (5/14) |
| Naive-detector catch (on successful attacks) | 0.0% (0/14) |

### Attack success rate by attacker-goal category

| Attacker goal | n | Followed | Attack success rate |
|---------------|---|----------|---------------------|
| data-stealing | 75 | 11 | 14.7% |
| direct-harm | 75 | 3 | 4.0% |

## Dual Detection Mode Analysis

**PROVENANCE-ONLY (loose):** flags privileged action arguments downstream of untrusted content.
Recall on successful attacks: **100.0%** (14/14).
On InjecAgent successful attacks, the privileged action arguments are attacker-derived,
so this is expected to catch attacks that reached a privileged tool. FP rate on 4 detonation-harness benign scenarios: 0/4
(none include the routing case; real FP risk exists for legitimate external-content
+ privileged-action workflows — not measured here).

**PRECISE (strict):** also requires injection signal patterns in content.
Recall on successful attacks: **35.7%** (5/14).
FP rate on detonation-harness benign: 0/4.
9 successful attacks had content with no recognizable signal —
those are the content-detection blind spot that precise mode re-inherits.

**Naive input-string detector:** 0.0% (0/14) on successful attacks.

## Capability Scaling

*InjecAgent paper reports 43–71% for GPT-4-class ReAct agents; all local rows
are a lower bound. Realistic ceiling requires an API model, not run here.*

| Model | Params | Sample | Tool-engagement | Attack-success% | by goal (data-stealing / direct-harm) | Prov-Only catch | Precise catch |
|-------|--------|--------|-----------------|-----------------|----------------------------------------|-----------------|---------------|
| Qwen/Qwen2.5-1.5B-Instruct | 1.5B | n=150, seed=42 | 63.3% | 9.3% (n=14) | 14.7% / 4.0% | 100.0% (14/14) | 35.7% (5/14) |
| Qwen/Qwen2.5-3B-Instruct | 3B | n=60, seed=42 | 66.7% | 5.0% (n=3) | 10.0% / 0.0% | 100.0% (3/3) | 100.0% (3/3) |
| Qwen/Qwen2.5-7B-Instruct | 7B | n=20, seed=42 | 55.0% | 25.0% (n=5) | 50.0% / 0.0% | 100.0% (5/5) | 100.0% (5/5) |
## Honest Reading

**Model behavior:** Qwen/Qwen2.5-1.5B-Instruct run on CPU. Attack-success 9.3% vs 43–71% for
GPT-4-class ReAct agents (InjecAgent paper); a larger model follows injections
at substantially higher rates.

**PRECISE blind spot:** 9 of 14 successful attacks had no recognizable
signal — those are missed by precise mode and caught only by provenance-only.

**Sample disclosure:** Base splits only (['direct-harm-base', 'data-stealing-base']). Enhanced splits
(adversarially perturbed) would likely lower the precise-mode catch rate further.

**What these numbers do NOT show:** Simplified inline-injection harness, not a
real multi-turn tool-use pipeline.

## Prior art

- **InjecAgent** (Zhan et al. 2024): "Benchmarking Attack Deliverability of Prompt
  Injection Attacks on LLM-Integrated Applications."
  https://github.com/uiuc-kang-lab/InjecAgent | https://arxiv.org/abs/2403.02691

- **AgentDojo** (Debenedetti et al. 2024): "A Dynamic Environment to Evaluate Attacks
  and Defenses for LLM Agents." https://arxiv.org/abs/2406.13352

## Files

| File | Contents |
|------|----------|
| `outcomes.jsonl` | Per-case outcomes: IDs, category tags, engaged/followed/caught — **no raw payloads** |
| `fetch_injecagent.py` | Downloads InjecAgent test cases to gitignored cache |
| `adapt.py` | Maps InjecAgent cases to harness scenario format |
| `run_corpus.py` | Runs the corpus and writes this file + outcomes.jsonl |
| `data/injecagent/` | Gitignored cache — raw test cases with attacker payloads |
