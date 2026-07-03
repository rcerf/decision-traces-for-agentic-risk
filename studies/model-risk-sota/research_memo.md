# Model and Agentic Risk SOTA Pressure Test

Date: 2026-07-02

Scope: Compare this repo's "decision traces for agentic risk" approach against current public research, standards, benchmark practice, and public OpenAI role/team signals. This memo uses public sources only.

## Bottom Line

This project is well aligned with the operational shape of current-risk intelligence work: it turns weak signals into a current operating picture with owners, mitigations, dependencies, residual risk, confidence, and review cadence. The repo is especially strong as a lightweight risk-intelligence and governance artifact.

It is not yet state of the art as a model-risk evaluation artifact. The current repo mostly demonstrates "I can structure ambiguity"; it does not yet demonstrate "I can measure agentic risk with modern evals, reproduce known benchmark failures, compare controls, or detect failures beyond regex-like patterns." That gap is fixable. The most useful next move is to make the trace schema an integration layer over existing agent-safety benchmarks and threat models rather than a standalone taxonomy.

## 1. SOTA Themes In Model And Agentic Risk Analysis

### 1. Risk Has Shifted From Outputs To Actions

Classic model-safety work emphasized harmful text, hallucination, bias, and refusal behavior. Agentic risk is broader: the system can read untrusted content, access private data, call tools, change external state, store memory, and coordinate across agents. The practical risk question is no longer only "what did the model say?" but "what did the system read, believe, decide, call, store, and change?"

OpenAI's Agentic Risk Analyst posting describes this exact operating problem: connect incidents, technical findings, abuse patterns, evals, red teaming, product launches, external research, and real-world incidents to owners, mitigations, dependencies, residual gaps, and next review points.

Source: OpenAI Agentic Risk Analyst role, https://openai.com/careers/agentic-risk-analyst-san-francisco/

### 2. Indirect Prompt Injection Is A System Security Problem, Not A Prompting Problem

The foundational security framing is that LLM-integrated apps blur the line between data and instructions. Indirect prompt injection can enter through retrieved documents, emails, web pages, code comments, support tickets, database rows, or any untrusted context the agent reads.

Modern defenses increasingly emphasize provenance, trust boundaries, least privilege, tool gating, output sanitization, user confirmation, and architecture-level isolation. The "lethal trifecta" framing is useful for product review: private data access + untrusted content exposure + external communication creates a practical exfiltration path.

Sources:
- Greshake et al., "Not what you've signed up for", https://arxiv.org/abs/2302.12173
- OWASP LLM01 Prompt Injection, https://genai.owasp.org/llmrisk/llm01-prompt-injection/
- Simon Willison, "The lethal trifecta for AI agents", https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/

### 3. Agent Evals Are Moving Toward Executable, Stateful Environments

SOTA agent evaluation is increasingly about multi-step tasks with tools, realistic state, user interaction, domain policies, and measurable outcomes. Static prompt suites are not enough.

Representative direction:
- AgentDojo tests prompt injection against tool-using agents over realistic tasks and adaptive attacks.
- AgentHarm tests whether agents comply with malicious multi-step tasks across harm categories.
- SafeArena tests deliberate misuse of autonomous web agents.
- WebArena, WorkArena, OSWorld, and tau-bench test realistic web, desktop, enterprise, and user-tool-agent workflows.
- Inspect AI and Inspect Evals are becoming a standard open eval harness layer.

The repo's synthetic examples are directionally right, but they are not yet connected to these executable environments.

### 4. The Field Cares About Utility-Security Tradeoffs

AgentDojo's framing is important: a "secure" agent that cannot perform benign tasks is not a useful product control. Modern agent-risk evals typically need at least two axes:

- Benign utility: does the agent still complete intended tasks?
- Security/safety: does it resist malicious or unintended actions?

This repo currently tracks severity and confidence but does not quantify utility retained after mitigation. That makes the risk register useful for governance but incomplete for product tradeoff decisions.

Source: AgentDojo paper and repo, https://arxiv.org/abs/2406.13352 and https://github.com/ethz-spylab/agentdojo

### 5. Autonomy Is Being Measured As Time Horizon And Environment Control

METR's work measures the length of tasks agents can complete with a given reliability. This matters because longer-horizon agents can create longer causal chains, delayed harms, and weaker human oversight.

For this project, "agentic surface" and "severity" should probably be joined by explicit autonomy variables: action horizon, reversibility, state access, self-directed subtasking, human checkpoint density, and external side-effect authority.

Sources:
- METR, "Measuring AI Ability to Complete Long Tasks", https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/
- arXiv version, https://arxiv.org/abs/2503.14499
- METR public tasks, https://github.com/METR/public-tasks

### 6. Memory Is Now A First-Class Attack Surface

Persistent memory changes prompt injection from a one-shot event into a delayed-compromise problem. Recent papers study memory injection, memory poisoning, sleeper memories, and environment-injected poisoned memory. The key difference is persistence: a benign-looking interaction can corrupt what the agent later retrieves as trusted context.

This repo's taxonomy includes memory/retrieval contamination, which is good. But the repo does not yet distinguish memory write channels, trust transitions, expiry, corroboration, source authority, or belief provenance.

Sources:
- "A Practical Memory Injection Attack against LLM Agents", https://arxiv.org/html/2503.03704
- "From Untrusted Input to Trusted Memory: A Systematic Study of Memory Poisoning Attacks in LLM Agents", https://arxiv.org/html/2606.04329
- "Hidden in Memory: Sleeper Memory Poisoning in LLM Agents", https://arxiv.org/html/2605.15338

### 7. Multi-Agent And Protocol-Level Risks Are Under-Mapped In Many Lightweight Frameworks

The agentic frontier increasingly includes tool protocols, MCP-style tool invocation, agent-to-agent delegation, privilege transfer, and multi-agent workflows. A single-agent trace can miss emergent failure modes: privilege escalation through delegation, cross-agent instruction laundering, tool-result poisoning, and protocol exploits.

The schema has `multi_agent` as a surface, but examples and validators do not yet stress it.

Sources:
- "From Prompt Injections to Protocol Exploits: Threats in LLM-powered AI Agent Ecosystems", https://arxiv.org/html/2506.23260
- CSA MAESTRO framework, https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro

### 8. Monitoring Is Useful But Fragile

OpenAI's chain-of-thought monitorability work frames visible reasoning as a potentially useful but fragile control layer. The lesson for this repo: observable traces are valuable, but should not depend on hidden or non-stable reasoning access. Observable telemetry, tool calls, approvals, retrieved-context provenance, and outcome state are more robust.

Sources:
- OpenAI, "Evaluating chain-of-thought monitorability", https://openai.com/index/evaluating-chain-of-thought-monitorability/
- arXiv, "Chain of Thought Monitorability", https://arxiv.org/html/2507.11473

### 9. Benchmark Integrity Is Itself A Model-Risk Problem

Recent 2026 work argues agent benchmarks can be reward-hacked or structurally exploited. That is directly relevant if traces are turned into evals: the eval harness should be part of the threat model. Agentic systems may exploit visible tests, environment bugs, grader assumptions, or shortcuts that pass the metric without satisfying the user goal.

Sources:
- "Do Androids Dream of Breaking the Game?", https://arxiv.org/abs/2605.12673
- "Reward Hacking Benchmark: Measuring Exploits in LLM Agents with Tool Use", https://arxiv.org/abs/2605.02964
- METR, "Recent Frontier Models Are Reward Hacking", https://metr.org/blog/2025-06-05-recent-reward-hacking/

### 10. Governance Is Moving Toward Dynamic Safety Cases And Living Risk Repositories

The repo's strongest idea, traces that accumulate into a living taxonomy and operating picture, is close to the safety-case direction: structured arguments with evidence, assumptions, monitoring indicators, and update triggers.

The gap is rigor. A safety case asks: what claim are we making, what evidence supports it, what assumptions must hold, what monitoring would invalidate it, and who can accept residual risk?

Sources:
- "Safety cases for frontier AI", https://arxiv.org/abs/2410.21572
- "Dynamic safety cases for frontier AI", https://arxiv.org/abs/2412.17618
- MIT AI Risk Repository, https://airisk.mit.edu/
- AI Risk Repository paper, https://arxiv.org/abs/2408.12622

## 2. Relevant Papers, Frameworks, Benchmarks, And Docs

| Source | Type | Why It Matters For This Repo |
|---|---|---|
| OpenAI Agentic Risk Analyst role, https://openai.com/careers/agentic-risk-analyst-san-francisco/ | Role spec | Near-perfect match for current operating picture, weak-signal intake, owners, mitigations, residual gaps. |
| OpenAI Preparedness Framework v2, https://cdn.openai.com/pdf/18a02b5d-6b67-4cec-ab64-68cdfbddebcd/preparedness-framework-v2.pdf | Frontier risk framework | Anchors risk thresholds, evals, safeguards, and deployment decisions; repo should map traces to preparedness categories where relevant. |
| OpenAI Operator System Card, https://openai.com/index/operator-system-card/ | System card | Public example of CUA risks, red teaming, confirmations, monitoring, and mitigations. |
| OpenAI ChatGPT Agent System Card, https://cdn.openai.com/pdf/839e66fc-602c-48bf-81d3-b21eacc3459d/chatgpt_agent_system_card.pdf | System card | Public agentic eval/safeguard pattern, including prompt-injection testing and safety controls. |
| OpenAI Deployment Safety Hub, https://deploymentsafety.openai.com/ | Official docs | Shows model/system safety results as ongoing deployment artifact. |
| OpenAI threat intelligence reports, https://openai.com/global-affairs/disrupting-malicious-uses-of-ai-june-2025/ | Threat intel | Shows how I&I converts abuse patterns into public case studies and disruptions. |
| OWASP Top 10 for LLM Apps 2025, https://owasp.org/www-project-top-10-for-large-language-model-applications/ | Security framework | Covers prompt injection, sensitive info disclosure, supply chain, poisoning, excessive agency. |
| OWASP LLM06 Excessive Agency, https://genai.owasp.org/llmrisk/llm06-sensitive-information-disclosure/ | Security framework | Directly maps to tool overreach, excessive permissions, and approval gates. |
| MITRE ATLAS, https://atlas.mitre.org/ | Threat framework | Provides adversarial AI tactics/techniques; repo should map categories to ATLAS where possible. |
| NIST AI RMF GenAI Profile, https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence | Standard/framework | Governance, measurement, and risk-management language. |
| CSA MAESTRO, https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro | Agentic threat model | Layered agentic AI threat modeling; useful schema crosswalk candidate. |
| MIT AI Risk Repository, https://airisk.mit.edu/ | Living taxonomy | Prevents taxonomy reinvention; useful source for crosswalk and gap analysis. |
| MIT AI Risk Mitigation Taxonomy, https://arxiv.org/abs/2512.11931 | Mitigation taxonomy | Helps convert "recommended_action" into comparable mitigation classes. |
| Greshake et al. indirect prompt injection, https://arxiv.org/abs/2302.12173 | Foundational paper | Core retrieved-content attack model. |
| AgentDojo, https://arxiv.org/abs/2406.13352 | Benchmark | Dynamic prompt-injection benchmark for tool-using agents. |
| AgentDojo repo, https://github.com/ethz-spylab/agentdojo | Benchmark repo | Candidate adapter target. |
| ToolEmu, https://arxiv.org/abs/2309.15817 | Benchmark/method | LM-emulated tool sandbox for risk discovery. |
| ToolEmu repo, https://github.com/ryoungj/ToolEmu | Benchmark repo | Candidate source of trace examples. |
| AgentHarm, https://arxiv.org/abs/2410.09024 | Benchmark | Tests harmful multi-step agent requests across harm categories. |
| AgentHarm Inspect Evals, https://ukgovernmentbeis.github.io/inspect_evals/evals/safeguards/agentharm/ | Benchmark implementation | Practical integration target. |
| SafeArena, https://arxiv.org/abs/2503.04957 | Benchmark | Web-agent misuse benchmark with risk levels. |
| WebArena, https://arxiv.org/abs/2307.13854 | Benchmark | Realistic web task environment. |
| WorkArena, https://arxiv.org/abs/2403.07718 | Benchmark | Enterprise knowledge-work agent benchmark. |
| tau-bench, https://arxiv.org/abs/2406.12045 | Benchmark | Tool-agent-user interaction and rule-following reliability. |
| OS-Harm, https://arxiv.org/html/2506.14866 | Benchmark | Safety benchmark for computer-use agents. |
| OSGuard, https://arxiv.org/html/2606.15034 | Benchmark | State-based safety invariants for computer-use agents. |
| Inspect AI, https://inspect.aisi.org.uk/ | Eval framework | Strong default harness if repo adds executable evals. |
| METR long-task measurement, https://arxiv.org/abs/2503.14499 | Capability measurement | Adds autonomy/time-horizon dimension. |
| RE-Bench, https://github.com/METR/RE-Bench | Benchmark repo | AI R&D agent capability benchmark; useful for frontier risk context. |
| Anthropic Agentic Misalignment, https://www.anthropic.com/research/agentic-misalignment | Research | Insider-threat style agent behavior under stress; useful for goal/incentive traces. |
| Safety cases for frontier AI, https://arxiv.org/abs/2410.21572 | Governance research | Turns traces into structured claims and evidence. |
| Dynamic safety cases, https://arxiv.org/abs/2412.17618 | Governance research | Supports ongoing update cadence and safety performance indicators. |

## 3. Where This Project Is Aligned

1. The core object is right: a structured trace. SOTA risk work needs more than a free-text incident note; it needs evidence, uncertainty, severity, ownership, mitigation status, residual risk, and review cadence.

2. The operating model matches the role. The OpenAI job asks for a current, company-wide portfolio of agentic risks mapped to workstreams, owners, mitigations, dependencies, decisions, and residual gaps. The repo's README, schema, risk register, and current operating picture all point in that direction.

3. The surfaces are directionally current: browser, connector, tool calling, memory, retrieval, computer use, multi-agent, and workflow automation are the right substrate categories.

4. The repo correctly treats human approvals as controls, not magic. The examples and unit test require high/critical traces to have approval gates, and the operating memo notes approval fatigue and boundary-detection problems.

5. The Anima Risk Sentinel study has the right staged-monitoring instinct: ingress, trajectory, draft, and final review catch different failure modes. This is aligned with modern process-level and trajectory-level agent evaluation.

6. The risk-intel intake study is smart. SOTA agent-risk work is moving quickly, and a tiered intake from research, incidents, social discovery, standards, and policy is a pragmatic way to keep the taxonomy alive.

7. The project avoids overclaiming. It says synthetic examples only and frames itself as proof of work. That restraint is good.

## 4. Where The Project Is Weak Or Naive

1. Too much taxonomy, not enough measurement. The repo structures traces but does not yet run an agent through AgentDojo, AgentHarm, SafeArena, ToolEmu, tau-bench, or Inspect AI.

2. The risk detector is a deterministic regex baseline. That is acceptable as a starting point, but the memo should admit that it is a labeling scaffold, not a serious detector. It will miss paraphrases, multilingual attacks, tool-specific attacks, stateful attacks, memory poisoning, collusion, and subtle policy violations.

3. Severity is qualitative and not calibrated. There is no mapping to likelihood, exposure, exploitability, affected population, blast radius, reversibility, or detection latency.

4. Human approval is underspecified. The repo records whether approval is required, but not approval quality: what did the user see, did they understand the connector boundary, was the prompt generic, was approval bundled with other actions, and was it logged before or after tool execution?

5. No utility-security tradeoff. Stronger controls often reduce task success. The repo needs a way to track benign task completion, false-positive cost, and user-workflow impact alongside risk reduction.

6. No formal threat model fields. Current traces do not explicitly capture attacker capability, trust boundary, authority source, data-flow path, tool permissions, exfiltration channel, preconditions, or postconditions.

7. Memory is too shallow. `memory_retrieval_contamination` is useful, but modern memory-poisoning work distinguishes memory write channels, memory selection policy, persistence, corroboration, expiry, retrieval triggers, and delayed activation.

8. Multi-agent risk is mostly a placeholder. The schema includes the surface, but there are no examples covering delegated authority, agent-to-agent instruction laundering, protocol exploits, or privilege escalation.

9. Benchmark integrity is missing. If traces become eval cases, the repo needs to consider reward hacking, visible-test overfitting, grader manipulation, environment leakage, and eval-aware behavior.

10. Weak connection to existing frameworks. The README cites OpenAI/OWASP, but the schema does not map to OWASP, MITRE ATLAS, NIST AI RMF, MIT AI Risk Repository, MAESTRO, or OpenAI Preparedness categories. Without crosswalks, the taxonomy can look reinvented.

11. No incident-to-control closure evidence. The project tracks mitigation status, but does not require evidence that a mitigation works, what eval verified it, what residual gap remains, or what monitoring indicator would reopen the trace.

12. Synthetic-only examples limit credibility. For a hiring artifact, synthetic is fine if the project clearly says so. To be research-useful, it needs sanitized public case studies or benchmark-derived traces.

## 5. What Would Make It More Novel And Useful

### A. Reposition The Repo As A Trace Layer Over Existing Evals

Do not compete with AgentDojo, AgentHarm, SafeArena, ToolEmu, Inspect, or METR. Instead, make this repo answer:

> After an eval, red-team run, incident, or external signal fires, how does the organization preserve the finding, connect it to risk ownership, choose controls, track residual gaps, and decide what to review next?

That is a useful niche and closely matches the role.

### B. Add A Framework Crosswalk

Add fields or a generated report mapping each trace to:

- OWASP LLM Top 10 category.
- MITRE ATLAS tactic/technique.
- MIT AI Risk Repository domain/subdomain.
- NIST AI RMF function/category.
- MAESTRO layer.
- OpenAI Preparedness category where relevant.
- Benchmark source, if the trace came from an eval.

This would reduce "reinventing the wheel" risk.

### C. Add Threat Model Fields To The Schema

Suggested additions:

- `attacker_capability`
- `trust_boundary`
- `authority_source`
- `data_flow`
- `tool_permissions`
- `external_side_effect`
- `reversibility`
- `exfiltration_channel`
- `autonomy_horizon`
- `human_checkpoint_density`
- `preconditions`
- `postconditions`
- `control_evidence`
- `benchmark_source`
- `framework_mappings`

### D. Build One Inspect AI Adapter

A strong proof point would be:

1. Run or mock a small AgentDojo or AgentHarm eval through Inspect.
2. Convert failures into `Agentic Risk Trace` JSON.
3. Generate an operating-picture summary: top categories, owners, residual gaps, missing controls, and next review dates.

That would turn the repo from a hand-authored portfolio into an eval-to-risk pipeline.

### E. Add Control Effectiveness, Not Just Control Presence

For each mitigation, record:

- What changed?
- What eval or incident replay tested it?
- Benign utility before/after.
- Attack success rate before/after.
- False-positive rate or review burden.
- Residual failure examples.
- Reopen trigger.

### F. Add Approval-Quality Metrics

Approval should be treated as a UX/security control with measurable quality:

- Was the approval specific to the action?
- Did it name the source connector and destination connector?
- Did it show sensitive fields or summaries?
- Could the user edit scope?
- Was approval required before execution?
- Was the action reversible?
- Did users rubber-stamp it?

### G. Add Memory And Multi-Agent Trace Examples

Add public/synthetic cases for:

- Poisoned memory written from a retrieved document and triggered a week later.
- Agent A with low privilege delegates to Agent B with high privilege.
- Tool output injects a cross-agent instruction.
- Multi-agent workflow loses the original user intent after handoff.

### H. Add Benchmark-Integrity Risk To The Taxonomy

New category candidate: `eval_reward_hacking` or `benchmark_integrity_failure`.

Rationale: current research shows agent benchmark scores can be gamed. A risk analyst should track not only product failures, but also failures in the measurement apparatus that leadership relies on.

### I. Turn Traces Into Dynamic Safety Case Fragments

Each trace can become a mini safety-case node:

- Claim: "Connector-based agent cannot exfiltrate private docs through untrusted retrieved instructions without explicit user approval."
- Evidence: eval runs, red-team results, production telemetry, incident absence with exposure denominator.
- Assumptions: connector scopes are enforced; approvals are pre-action; untrusted content is labeled.
- Defeaters: new tool with external send permission; memory enabled; approval UI changed.
- Monitoring indicator: cross-connector actions without approval, injection detections in retrieved context, user approval reversal rate.

This would make the project feel more like frontier safety assurance than a risk spreadsheet.

## Suggested Positioning

The strongest positioning is not "I invented a new model-risk taxonomy." The stronger claim is:

> I built a compact operating layer for agentic risk intelligence: it ingests weak signals and eval findings, preserves evidence and uncertainty, maps them to owners and controls, tracks residual risk, and turns repeated patterns into eval cases and safety-case fragments.

That is both honest and differentiated. The novelty is the connective tissue between research/evals and cross-functional risk operations, not a new benchmark or a universal detector.
