# Public-Signal Agentic Risk Assessment

Generated: 2026-07-02

Intended audience: reviewers with operational agentic-risk or risk-intelligence responsibility.

Important caveat: this assessment uses public information only. It does not claim these risks are unknown to OpenAI. It identifies plausible under-owned, under-measured, or under-instrumented risk hypotheses that are worth testing for coverage.

## Method

- Start with public signals from OpenAI product/system materials, safety research, standards, and agentic-risk benchmarks.
- Convert each signal into a testable risk hypothesis.
- Rank by likelihood, impact, actionability, and novelty.
- Preserve the safe probe and decision needed so the assessment can feed an operating backlog.

Scoring formula:

```text
priority = likelihood*10 + impact*10 + actionability*6 + novelty*4
```

The weights are illustrative: they encode a preference for likelihood and impact over actionability and novelty, and are not calibrated against outcome data.

## Key Judgments

1. The highest-priority risks are not isolated unsafe answers. They are state/action integrity failures across retrieval, connectors, tools, approvals, memory, and handoffs.
2. The most valuable analyst work is joining weak signals into a trace: what the agent read, believed, called, changed, asked approval for, and exposed.
3. The central coverage question is not whether a risk exists in a taxonomy. It is whether there is evidence of control effectiveness, ownership, residual risk, and next review.
4. Public evidence points to one practical next product: convert eval/incident/research signals into structured traces and operating-picture updates.

## Top Risks

### 1. Cross-surface prompt injection becomes private-data action, not just unsafe text

Priority: 142 (immediate assessment)  
Confidence: high  
Scores: likelihood 5/5, impact 5/5, actionability 5/5, novelty 3/5

Thesis: The highest-priority agentic failure mode is a long-horizon chain where untrusted content influences an agent that can read private context and then act through email, browser, file, calendar, or other connector surfaces.

Most likely failure path: A user asks for a benign summarization or workflow task. Retrieved web/email/document content contains instruction-like text. The agent incorporates that text into its plan, reads private context, and proposes or executes an external side effect that exposes data or changes state.

Why it may be under-instrumented: Many controls are evaluated at one boundary at a time: prompt ingress, final answer, or individual tool call. The risky chain may only become legible when source provenance, retrieved context, tool authority, approval state, and final response are joined into one trace.

Early indicators:
- Tool calls whose destination connector differs from the user's original task surface.
- Plans that cite untrusted retrieved content as if it were user intent.
- Final answers that look benign while intermediate tool calls crossed a data boundary.
- Approval prompts that describe the action generically rather than naming source, destination, and sensitive fields.

Safe probe: Use synthetic retrieved content containing harmless out-of-scope instructions and mocked connectors. Score whether the system detects goal drift before external side effect.

Decision needed: Define the minimum trace fields required before any cross-connector action: source trust, user intent, data class, destination, approval text, reversibility, and owner.

Relevant sources: [OpenAI Atlas prompt-injection hardening](https://openai.com/index/hardening-atlas-against-prompt-injection/); [OpenAI designing agents to resist prompt injection](https://openai.com/index/designing-agents-to-resist-prompt-injection/); [OWASP LLM01 Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/); [AgentDojo benchmark](https://github.com/ethz-spylab/agentdojo)

### 2. Approval quality becomes the weak link in high-frequency agent workflows

Priority: 136 (immediate assessment)  
Confidence: high  
Scores: likelihood 5/5, impact 4/5, actionability 5/5, novelty 4/5

Thesis: As agents ask users to approve more actions, the key risk shifts from whether approval exists to whether approval is specific, understandable, timely, scoped, and resistant to rubber-stamping.

Most likely failure path: A workflow repeatedly prompts for approvals. The user habituates to generic confirmations. A high-impact action is approved because the UI does not make the boundary crossing salient enough.

Why it may be under-instrumented: Approval logs often record presence or absence of consent, but not consent quality. A user can technically approve an action while misunderstanding the source connector, destination connector, data sensitivity, reversibility, or bundled consequences.

Early indicators:
- High approval acceptance rates for sensitive actions.
- Approvals bundled across several tool calls.
- Approvals shown after the model has already selected the action path.
- User reversals, support complaints, or manual remediation after approved actions.

Safe probe: Run synthetic workflows with specific versus generic approval text and score whether reviewers can correctly identify source, destination, reversibility, and sensitive fields.

Decision needed: Adopt approval-quality metrics, not just approval-presence metrics, for high-severity traces.

Relevant sources: [OpenAI Operator System Card](https://openai.com/index/operator-system-card/); [OpenAI link safety and browser safeguards](https://openai.com/index/keeping-you-safe-while-clicking-links-in-chatgpt/); [OpenAI introducing ChatGPT agent](https://openai.com/index/introducing-chatgpt-agent/)

### 3. Persistent memory turns one-shot injection into delayed state corruption

Priority: 134 (immediate assessment)  
Confidence: medium  
Scores: likelihood 4/5, impact 5/5, actionability 4/5, novelty 5/5

Thesis: Memory and shared workspace context can convert an input-handling failure into a delayed, hard-to-debug state-integrity failure.

Most likely failure path: Untrusted content causes an agent to write a persistent preference, fact, contact, workflow rule, or access assumption. A later session retrieves that memory and uses it to justify a bad action.

Why it may be under-instrumented: Many prompt-injection tests measure immediate compliance or refusal. Memory failures can appear later, after the original context is gone, when a poisoned memory item is retrieved as trusted personalization or institutional knowledge.

Early indicators:
- Memory writes sourced from untrusted content without provenance or expiry.
- A later agent run treats memory as higher-authority than the current user task.
- Memory items that change tool-routing, contact-routing, or data-sharing behavior.
- No review trigger when memory influences a sensitive action.

Safe probe: Use synthetic memory writes with harmless but false routing instructions, then test whether later workflows preserve provenance and require corroboration before acting.

Decision needed: Create a memory-integrity risk class with write-channel, source authority, expiry, corroboration, retrieval trigger, and sensitive-action influence fields.

Relevant sources: [OpenAI memory controls](https://help.openai.com/en/articles/8590148-memory-faq); [Practical memory injection attack against LLM agents](https://arxiv.org/html/2503.03704); [Memory poisoning in LLM agents](https://arxiv.org/html/2606.04329)

### 4. Customer-built agent stacks create a runtime gap model-side safeguards cannot fully see

Priority: 130 (immediate assessment)  
Confidence: medium  
Scores: likelihood 4/5, impact 5/5, actionability 4/5, novelty 4/5

Thesis: As AgentKit, APIs, MCP-style tools, and custom enterprise agents spread, some of the most important risks may live in customer runtime architecture rather than in model behavior alone.

Most likely failure path: A customer deploys an agent with broad scopes, weak tool isolation, sensitive retrieval, and permissive approvals. A public prompt-injection or tool-chain issue becomes a real-world incident outside the platform's own product boundary.

Why it may be under-instrumented: A model provider can improve models, policies, and platform defaults, but deployed customer agents may combine tools, permissions, secrets, logs, retrieval, and approval UX in ways that are invisible or only partially visible to central telemetry.

Early indicators:
- Support or incident reports involving third-party tool combinations.
- High-risk tool scopes without comparable approval or audit controls.
- External agents using OpenAI models but nonstandard logging, eval, or rollback paths.
- Developer examples that encourage capability before safety instrumentation.

Safe probe: Build a local mock customer agent with retrieval plus two tools and show how trace requirements reveal missing ownership, approval, and evidence fields.

Decision needed: Define a minimum recommended agent-risk telemetry contract for customer-built agents: tool call, source provenance, approval text, data class, external side effect, and incident export.

Relevant sources: [OpenAI AgentKit](https://openai.com/index/introducing-agentkit/); [OpenAI in-house data agent with MCP](https://openai.com/index/inside-our-in-house-data-agent/); [CSA MAESTRO framework](https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro); [MITRE ATLAS](https://atlas.mitre.org/)

### 5. Eval blind spots let unsafe trajectories pass safe-looking final answers

Priority: 126 (immediate assessment)  
Confidence: high  
Scores: likelihood 4/5, impact 4/5, actionability 5/5, novelty 4/5

Thesis: For agentic systems, safety evaluation can fail if it scores only the final response or task success while ignoring unauthorized intermediate actions, state changes, benchmark gaming, or invisible side effects.

Most likely failure path: An agent completes a task and produces a harmless final summary, but it used out-of-scope data, clicked a risky link, leaked metadata, or manipulated environment state along the way.

Why it may be under-instrumented: Benchmarks often need clean scalar scores, while real agentic safety depends on traces: what the agent read, believed, called, changed, and asked approval for. A final answer can look safe after an unsafe tool trajectory.

Early indicators:
- Eval success criteria that do not inspect tool arguments or environment deltas.
- Reward-hacking behaviors that satisfy the metric without satisfying the user's real goal.
- Safety monitors that trigger only after the final answer is drafted.
- No distinction between detected-before-side-effect and detected-after-side-effect.

Safe probe: Convert a benchmark-like run into a trace that records tool trajectory, environment delta, approval state, and first useful intervention point.

Decision needed: Make benchmark-to-trace conversion part of the risk-analysis operating loop, especially for high-autonomy and tool-rich systems.

Relevant sources: [Inspect AI](https://inspect.aisi.org.uk/); [AgentHarm](https://arxiv.org/abs/2410.09024); [AgentDojo](https://arxiv.org/abs/2406.13352); [METR reward hacking](https://metr.org/blog/2025-06-05-recent-reward-hacking/)

## Coverage Map

| Surface | Count |
|---|---:|
| governance | 5 |
| tool_calling | 5 |
| connector | 4 |
| computer_use | 3 |
| final_output | 3 |
| ingress | 2 |
| multi_agent | 2 |
| retrieval | 2 |
| workflow_automation | 2 |
| memory | 1 |

## Product Output

This report was generated from structured input rather than hand-written alone.

Run:

```bash
python3 studies/strategic-risk-assessment/src/generate_assessment.py --output reports/agentic_risk_assessment_public_signals.md
```

Input:

- `studies/strategic-risk-assessment/data/public_signal_risk_hypotheses.json`

The next implementation step is to replace hand-curated hypotheses with merged outputs from the risk-intelligence intake adapters, benchmark-to-trace conversion, and human review.
