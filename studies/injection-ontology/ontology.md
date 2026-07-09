# Agentic Prompt-Injection Ontology

> **Honesty note:** This ontology deliberately builds on existing public work rather than reinventing it.
> The borrowed structure comes from OWASP LLM01, MITRE ATLAS AML.T0051, and the HackAPrompt taxonomy
> (Schulhoff et al., EMNLP 2023, arXiv:2311.16119). Nodes marked **[NEW]** represent genuine
> extensions; everything else is a restatement or minor reframing of prior work.
> The ontology schema lives in `ontology.json`; this document is the human-readable companion.

---

## 1. Source Frameworks

| Framework | Version / Entry | What it provides | What it leaves open |
|-----------|-----------------|-----------------|---------------------|
| **OWASP LLM Top 10** | LLM01 — Prompt Injection (2025) | Direct vs. indirect distinction; high-level risk framing | No technique or goal taxonomy; delivery vectors are two ("user input", "retrieved content") |
| **MITRE ATLAS** | AML.T0051 (LLM Prompt Injection); AML.T0051.000 (Direct); AML.T0051.001 (Indirect); related: AML.T0054, AML.T0048, AML.T0043 | Attacker-perspective TTP IDs; integrates with ATT&CK navigator | Delivery vector and goal dimensions under-specified; multi-agent / tool-use not addressed |
| **HackAPrompt Taxonomy** | Schulhoff et al., EMNLP 2023, arXiv:2311.16119 | Empirically derived technique taxonomy from 600K+ competition entries: CI, PS, OB, RP, RS, FS, CC, PT, DI | Single-turn, user-prompt-only scope; no agentic, indirect, or multi-hop coverage |

This ontology adds a **delivery vector axis**, extends the **technique axis** into agentic territory, expands the **goal axis**, and adds **severity dimensions** not present in any of the above.

---

## 2. Axes at a Glance

| Axis | Nodes | New nodes | Primary source |
|------|-------|-----------|----------------|
| Injection type | 3 | 1 | OWASP LLM01, MITRE AML.T0051 |
| Delivery vector | 10 | 5 | OWASP LLM01 (partial); rest NEW |
| Technique | 14 | 5 | HackAPrompt (9 borrowed); rest NEW |
| Goal | 9 | 3 | OWASP/ATLAS (6 borrowed); rest NEW |
| Severity dimensions | 4 | 2 | Composite; 2 NEW |

**Total nodes: 36. New nodes: 16. Borrowed/reframed: 20.**

---

## 3. Axis 1 — Injection Type

Controls how injected instructions reach the model relative to attacker/victim boundaries.

| ID | Label | Description | Source |
|----|-------|-------------|--------|
| IT-01 | Direct Prompt Injection | Attacker controls the user turn directly | OWASP LLM01; AML.T0051.000 |
| IT-02 | Indirect Prompt Injection | Injection embedded in content the model retrieves or processes | OWASP LLM01; AML.T0051.001 |
| **IT-03** | **Multi-Hop / Cross-Agent Injection** | Injection propagates across two or more agents in the same pipeline | **NEW** |

**IT-03 extension rationale:** Existing frameworks treat injection as a single-hop event between attacker and target model. Multi-agent orchestration (LangGraph, AutoGen, OpenAI Swarm, AWS Bedrock multi-agent) creates transitive trust chains. A compromised upstream agent becomes a delivery vehicle for downstream agents without the attacker needing continued access.

---

## 4. Axis 2 — Delivery Vector

The channel through which injection reaches the model's context window. This axis is the most significant extension: OWASP LLM01 names two vectors; this ontology enumerates ten.

| ID | Label | Description | Source |
|----|-------|-------------|--------|
| DV-01 | User Prompt | Human-turn message | OWASP LLM01; AML.T0051.000 |
| DV-02 | Retrieved Document (RAG) | Injected content in fetched chunk | OWASP LLM01; AML.T0051.001 |
| DV-03 | Web Page / Fetched URL | Injected content in page visited by agent | OWASP LLM01 (implied) |
| **DV-04** | **Tool / API Output** | Injection in structured/unstructured response from tool call | **NEW** |
| **DV-05** | **Agent Memory / Long-Term Store** | Injection written to memory, retrieved in future sessions | **NEW** |
| **DV-06** | **Email / Messaging Content** | Injection in email/chat read by an agent with mailbox access | **NEW** |
| **DV-07** | **Uploaded File** | Injection in PDF/Word/image EXIF/spreadsheet parsed by agent | **NEW** |
| **DV-08** | **Upstream Agent Output** | Output of a compromised/spoofed agent feeds downstream agent | **NEW** |
| DV-09 | System Prompt / Context Manipulation | Attacker manipulates or forges the system prompt | OWASP LLM01; AML.T0051 |
| **DV-10** | **Multimodal Content** | Injection in image pixels, audio, or video frames | **NEW** |

**Illustrative (sanitized) examples — no working payloads included:**
- *DV-04:* A search-API wrapper returns a result containing text that, when inserted into the agent's context, reads as a new instruction rather than a search result.
- *DV-05:* A user asks an agent to remember a preference; the preference field is crafted to include instruction-like text that fires on the next session.
- *DV-08:* In a document-summarization pipeline, Agent A (summarizer) is injected through DV-02; its summary output then carries the injection into Agent B (reviewer) via DV-08.

---

## 5. Axis 3 — Technique

The rhetorical or structural mechanism used to make the model follow injected instructions. Nine nodes are drawn directly from the HackAPrompt taxonomy; five are extensions.

| ID | Label | HackAPrompt ID | Source |
|----|-------|----------------|--------|
| TQ-01 | Context Ignoring | CI | HackAPrompt |
| TQ-02 | Payload Splitting / Token Smuggling | PS | HackAPrompt |
| TQ-03 | Obfuscation / Encoding | OB | HackAPrompt |
| TQ-04 | Role-Play / Persona Adoption | RP + PT | HackAPrompt |
| TQ-05 | Refusal Suppression | RS | HackAPrompt |
| TQ-06 | Few-Shot Priming | FS | HackAPrompt |
| TQ-07 | Completion Compliance | CC | HackAPrompt |
| TQ-08 | Distractor / Misdirection | DI | HackAPrompt |
| TQ-09 | Authority / System Spoofing | — | OWASP LLM01; AML.T0051 |
| **TQ-10** | **Tool-Call Injection** | — | **NEW** |
| **TQ-11** | **Memory Poisoning** | — | **NEW** |
| **TQ-12** | **Goal / Objective Hijacking** | — | **NEW** |
| **TQ-13** | **Chain-of-Thought Manipulation** | — | **NEW** |
| **TQ-14** | **Trust-Boundary Escalation** | — | **NEW** |

**Extension rationale summaries:**
- **TQ-10 (Tool-Call Injection):** Tool-using agents generate structured tool calls from natural language. Injected instructions can exploit this to produce dangerous downstream calls (SQL injection via the LLM layer, SSRF via an HTTP tool). Not covered by HackAPrompt (single-turn, no tool context) or OWASP LLM01 at this granularity.
- **TQ-11 (Memory Poisoning):** Persistent memory stores (vector DB, episodic memory) can be written by one session and read by another. A stored injection fires automatically without further attacker access — analogous to stored XSS.
- **TQ-12 (Goal Hijacking):** Planning-capable agents maintain a task objective that can be overwritten mid-run by injected content. Differs from context-ignoring (TQ-01) which operates at the instruction level; this operates at the goal/plan level.
- **TQ-13 (Chain-of-Thought Manipulation):** Models with visible or hidden reasoning traces (o1, Claude extended thinking, ReAct steps) can have those traces steered by injected "reasoning" steps, exploiting the model's tendency to follow its own prior logic.
- **TQ-14 (Trust-Boundary Escalation):** Multi-agent and tool-use architectures establish implicit trust hierarchies. This technique exploits those boundaries — e.g., content arriving from a "trusted" internal tool is treated as a system-level instruction.

---

## 6. Axis 4 — Goal

The attacker's intended outcome.

| ID | Label | Description | Source |
|----|-------|-------------|--------|
| GL-01 | Data Exfiltration | Extract system prompt, user data, credentials, memory | OWASP LLM01; AML.T0051 |
| GL-02 | Unauthorized Action | Cause unsanctioned agent action (email, code exec, API call) | OWASP LLM01; AML.T0051 |
| GL-03 | Privilege Escalation | Access capabilities beyond attacker's authorization | OWASP LLM01; AML.T0040 |
| GL-04 | Policy / Safety Evasion | Bypass content filters or safety guardrails | OWASP LLM01; AML.T0054 |
| GL-05 | Harmful Content Generation | Produce CSAM, extremist content, bioweapon instructions | OWASP LLM01; AML.T0048 |
| GL-08 | Reputation / Brand Damage | Produce defamatory or embarrassing output attributed to operator | OWASP LLM01 (implied) |
| **GL-06** | **Resource Abuse** | Excessive tool calls, API cost inflation, rate-limit exhaustion | **NEW** |
| **GL-07** | **Agent Persistence / Sleeper Payload** | Foothold in memory/config that re-activates without attacker | **NEW** |
| **GL-09** | **Supply-Chain / Downstream Poisoning** | Compromise one pipeline component to poison downstream agents or fine-tuning data | **NEW** |

---

## 7. Axis 5 — Severity Dimensions

Severity is assessed per incident, not per ontology node. Four dimensions are identified; two are extensions.

| Dimension | Values | Source |
|-----------|--------|--------|
| Impact scope | single-user / multi-user / system-wide / cross-organization | Standard security practice |
| Reversibility | reversible / partially-reversible / irreversible | Standard security practice |
| **Detection difficulty** | low / medium / high | **NEW** |
| **Effect latency** | immediate / deferred / persistent | **NEW** |

**Extension rationale:**
- **Detection difficulty** matters more in agentic contexts because attacks may occur inside reasoning traces, memory stores, or tool call chains that are not surfaced to human reviewers.
- **Effect latency** is needed because memory-poisoning and sleeper attacks have a time gap between injection and activation that existing severity models (which assume immediate impact) do not capture.

---

## 8. Taxonomy Graph (Abbreviated)

```
injection_type
  IT-01 (direct)
    delivery_vector: DV-01, DV-09
  IT-02 (indirect)
    delivery_vector: DV-02, DV-03, DV-06, DV-07, DV-10
  IT-03* (multi-hop)
    delivery_vector: DV-04*, DV-05*, DV-08*

technique (operates across all injection types)
  HackAPrompt-derived: TQ-01 through TQ-09
  Agentic extensions*: TQ-10 through TQ-14

goal (independent of injection type or technique)
  Borrowed: GL-01 through GL-05, GL-08
  Agentic extensions*: GL-06, GL-07, GL-09

* = new extension
```

---

## 9. What This Ontology Does NOT Claim

- Completeness. The agentic attack surface is evolving rapidly; new techniques will require new nodes.
- Mutual exclusivity. Real attacks combine multiple techniques and may pursue multiple goals simultaneously.
- Precision. The delivery vector and technique axes can be ambiguous; the boundary between TQ-01 (context ignoring) and TQ-09 (authority spoofing) is fuzzy in practice.
- The "new" nodes are truly unprecedented in the literature; they may have informal precedents not found in the three reviewed frameworks.

See `classification_results.md` for empirical coverage of the technique axis against a real corpus.

---

## References

1. OWASP LLM Top 10 2025 — LLM01. https://owasp.org/www-project-top-10-for-large-language-model-applications/
2. MITRE ATLAS AML.T0051 — LLM Prompt Injection. https://atlas.mitre.org/techniques/AML.T0051
3. Schulhoff, S., et al. "Ignore This Title and HackAPrompt: Exposing Systemic Vulnerabilities of LLMs through a Global Scale Prompt Hacking Competition." EMNLP 2023. arXiv:2311.16119
4. Greshake, K., et al. "Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection." arXiv:2302.12173 (2023)
5. Perez, F., & Ribeiro, I. "Prompt Injection Attacks and Defenses in LLM-Integrated Applications." arXiv:2310.12815 (2023)
