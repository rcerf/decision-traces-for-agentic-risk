# State Of The Art Notes: Agentic Model Risk Analysis

Status: initial research memo  
Date: 2026-07-02  
Purpose: pressure-test this repo against current public thinking in agentic risk, model evaluation, guardrails, and strategic intelligence.

## Executive Takeaway

The repo is directionally aligned with current work. The strongest overlap is trajectory-level monitoring, staged guardrails, prompt-injection provenance, function-call/tool-use evaluation, public risk-intelligence intake, and operational follow-through.

The repo is not novel because it notices prompt injection, guardrails, or traces. Those are active areas. Its useful differentiation is the operating synthesis:

```text
public weak signals -> safe probes -> observable agent runs -> staged sentinel events -> structured risk traces -> owners, mitigations, approval gates, residual risk, next review
```

That framing fits the Agentic Risk Analyst role because it turns research/eval/security/incident signals into a current operating picture and decision backlog.

## SOTA Themes

### 1. Agent Evaluation Is Moving Beyond Final Outputs

Recent agent-evaluation surveys organize the field around both what to evaluate and how to evaluate it: behavior, capability, reliability, safety, interaction modes, datasets, metrics, tooling, and environments.

Implication for this repo:

- Keep the staged lifecycle framing.
- Explicitly distinguish final-output review from trajectory review.
- Add metrics for first detection stage, actionability, and intervention window.

Representative source:

- Evaluation and Benchmarking of LLM Agents: A Survey: https://arxiv.org/html/2507.21504v1

## 2. Trajectory-Level Safety And Diagnostics Are Central

AgentDoG and ATBench-style work emphasize trajectory-level monitoring and root-cause diagnosis, including malicious tool execution and prompt injection. This is very close to the repo's Anima Risk Sentinel idea.

Implication for this repo:

- The staged sentinel should be framed as a simple, public-safe version of trajectory diagnostics.
- Add explicit root-cause fields: source, failure mode, harm path, missing control, and mitigation owner.
- Avoid implying that deterministic checks are enough.

Representative source:

- AgentDoG: A Diagnostic Guardrail Framework for AI Agent Safety and Security: https://arxiv.org/html/2601.18491v1

## 3. Runtime Enforcement And Online Monitoring Matter

Runtime safety work argues for collecting execution traces and monitoring agents during interaction with environments, not only after completion. Monitor-red-teaming work stresses that online monitors should predict harmful outcomes before they become irreversible.

Implication for this repo:

- Emphasize "first useful intervention point."
- Add a metric for "detected before external side effect."
- Make approval gates and connector boundaries first-class controls.

Representative sources:

- Proactive Runtime Enforcement of LLM Agent Safety via Probabilistic Model Checking: https://arxiv.org/html/2508.00500v1
- Reliable Weak-to-Strong Monitoring of LLM Agents: https://arxiv.org/html/2508.19461v1

## 4. Prompt Injection Detection Is More Mature Than Function-Call Evaluation

Mozilla.ai's guardrail benchmarking found promise for indirect prompt-injection detection, especially with encoder-style guard models, but function-call malfunction detection remained unreliable for off-the-shelf judge models.

Implication for this repo:

- The current split between ingress detection and trajectory/tool-call checks is well justified.
- The next "serious" experiment should not just add another prompt-injection rule. It should test tool-call malfunction detection and connector-boundary overreach.
- A small specialized model may be valuable, but only after a deterministic baseline and labeled traces.

Representative source:

- Mozilla.ai, "Can Open-Source Guardrails Really Protect AI Agents?": https://blog.mozilla.ai/can-open-source-guardrails-really-protect-ai-agents/

## 5. Public Risk Signals Need Triage, Not Blind Collection

The role language emphasizes weak signals, external developments, investigations, and current operating picture. Social media, journalism, standards, incident databases, and research papers are all useful, but they have different reliability and safety profiles.

Implication for this repo:

- The `risk-intel-intake` layer is a good fit.
- Keep source tiers and review gates.
- Do not store raw jailbreak recipes.
- Add corroboration tracking: social signal -> research/incident corroboration -> safe probe -> reproduced result.

Representative sources:

- OWASP Top 10 for LLM Applications: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- MITRE ATLAS: https://atlas.mitre.org/
- NIST AI Risk Management Framework: https://www.nist.gov/itl/ai-risk-management-framework
- AI Incident Database: https://incidentdatabase.ai/
- MIT AI Incident Tracker: https://airisk.mit.edu/ai-incident-tracker/incident-timeline

## 6. The Strategic Intelligence Team Framing Is A Strong Match

Public role-post language describes strategic-intelligence work as connecting technical findings, investigations, external developments, and weak signals into a clear view of what matters, then turning analysis into decisions and follow-through.

That is almost exactly the repo's intended loop. The repo should use that language without sounding like it is parroting a job posting.

## Where This Repo Is Strong

- It makes weak-signal intake explicit.
- It avoids raw exploit reproduction.
- It distinguishes stages: ingress, trajectory, draft, final.
- It produces structured traces rather than free-form commentary.
- It connects technical findings to owners, mitigations, approvals, residual risk, and review cadence.
- It can be consumed as an analyst artifact, not just code.

## Where It Is Weak Or Naive

- Synthetic-only examples.
- Rule-based detection with no measured precision/recall.
- No real benchmark adapter yet for BIPIA, AgentDojo/AgentDoG/ATBench-style traces, or tool-call malfunction datasets.
- No human annotation workflow.
- No explicit false-positive/false-negative analysis beyond a benign control.
- No current integration with open models, logits/logprobs, repeated-sample disagreement, or real agent framework traces.

## Highest-Leverage Improvements

1. Add one benchmark adapter:
   - BIPIA-style safe subset for indirect prompt injection, or
   - HammerBench/function-call malfunction style data if licensing/access is clean.
2. Add an `evaluation_scorecard.md`:
   - detection stage
   - category
   - severity
   - approval gate
   - intervention window
   - false-positive note
   - mitigation status
3. Add one open-model telemetry experiment:
   - tool-choice entropy
   - top-choice margin
   - repeated-sample disagreement
   - instability before consequential action
4. Add an end-to-end run:
   - source signal from X/arXiv/AIID
   - safe probe generated
   - synthetic run emitted
   - sentinel detects events
   - trace created
   - risk brief updated

## Suggested Working-Paper Thesis

Agentic risk analysis should be treated as a current-risk intelligence system. The useful unit is not only a policy violation or final unsafe answer; it is an observable decision trace that links source signal, context provenance, agent trajectory, tool authority, approval state, output behavior, mitigation owner, and residual risk. A corpus of such traces can support both reactive incident review and proactive gap-finding.
