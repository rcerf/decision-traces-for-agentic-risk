# Ontology Crosswalk — OWASP LLM01, MITRE ATLAS, HackAPrompt

This table maps every node in the injection ontology to its source framework IDs.
**NEW** nodes have no upstream ID; they represent genuine extensions to existing taxonomies.

---

## Injection Type Crosswalk

| Ontology ID | Label | OWASP LLM01 | MITRE ATLAS | HackAPrompt | NEW? |
|---|---|---|---|---|---|
| IT-01 | Direct Prompt Injection | LLM01 — Direct | AML.T0051.000 | (all techniques) | No |
| IT-02 | Indirect Prompt Injection | LLM01 — Indirect | AML.T0051.001 | — | No |
| IT-03 | Multi-Hop / Cross-Agent Injection | LLM01 (extended) | AML.T0051.001 (extended) | — | **YES** |

---

## Delivery Vector Crosswalk

| Ontology ID | Label | OWASP LLM01 | MITRE ATLAS | HackAPrompt | NEW? |
|---|---|---|---|---|---|
| DV-01 | User Prompt | LLM01 | AML.T0051.000 | All techniques | No |
| DV-02 | Retrieved Document (RAG) | LLM01 — Indirect | AML.T0051.001 | — | No |
| DV-03 | Web Page / Fetched URL | LLM01 — Indirect (implied) | AML.T0051.001 | — | No |
| DV-04 | Tool / API Output | LLM01 (extended) | AML.T0051.001 (extended) | — | **YES** |
| DV-05 | Agent Memory / Long-Term Store | LLM01 (extended) | — | — | **YES** |
| DV-06 | Email / Messaging Content | LLM01 — Indirect | AML.T0051.001 | — | **YES** |
| DV-07 | Uploaded File | LLM01 — Indirect (implied) | — | — | **YES** |
| DV-08 | Upstream Agent Output | — | — | — | **YES** |
| DV-09 | System Prompt / Context Manipulation | LLM01 | AML.T0051 | Authority framing | No |
| DV-10 | Multimodal Content (Image / Audio / Video) | — | AML.T0043 (Craft Adversarial Data) | — | **YES** |

---

## Technique Crosswalk

| Ontology ID | Label | OWASP LLM01 | MITRE ATLAS | HackAPrompt ID | NEW? |
|---|---|---|---|---|---|
| TQ-01 | Context Ignoring | LLM01 | AML.T0051 | CI | No |
| TQ-02 | Payload Splitting / Token Smuggling | LLM01 | AML.T0051 | PS | No |
| TQ-03 | Obfuscation / Encoding | LLM01 | AML.T0043 (partial) | OB | No |
| TQ-04 | Role-Play / Persona Adoption | LLM01 | AML.T0054 (Jailbreak) | RP + PT | No |
| TQ-05 | Refusal Suppression | LLM01 | AML.T0054 (partial) | RS | No |
| TQ-06 | Few-Shot Priming | LLM01 | AML.T0043 (partial) | FS | No |
| TQ-07 | Completion Compliance | LLM01 | — | CC | No |
| TQ-08 | Distractor / Misdirection | LLM01 | — | DI | No |
| TQ-09 | Authority / System Spoofing | LLM01 | AML.T0051 | — | No |
| TQ-10 | Tool-Call Injection | LLM01 (extended) | AML.T0051.001 (extended) | — | **YES** |
| TQ-11 | Memory Poisoning | LLM01 (extended) | — | — | **YES** |
| TQ-12 | Goal / Objective Hijacking | LLM01 (extended) | — | — | **YES** |
| TQ-13 | Chain-of-Thought Manipulation | — | — | — | **YES** |
| TQ-14 | Trust-Boundary Escalation | — | AML.T0040 (extended) | — | **YES** |

---

## Goal Crosswalk

| Ontology ID | Label | OWASP LLM01 | MITRE ATLAS | HackAPrompt | NEW? |
|---|---|---|---|---|---|
| GL-01 | Data Exfiltration | LLM01 | AML.T0051 / AML.T0037 | — | No |
| GL-02 | Unauthorized Action | LLM01 | AML.T0051 | — | No |
| GL-03 | Privilege Escalation | LLM01 | AML.T0040 | — | No |
| GL-04 | Policy / Safety Evasion | LLM01 | AML.T0054 (Jailbreak) | — | No |
| GL-05 | Harmful Content Generation | LLM01 | AML.T0048 (Societal Harm) | — | No |
| GL-06 | Resource Abuse | — | — | — | **YES** |
| GL-07 | Agent Persistence / Sleeper Payload | — | — | — | **YES** |
| GL-08 | Reputation / Brand Damage | LLM01 (implied) | AML.T0048 (partial) | — | No |
| GL-09 | Supply-Chain / Downstream Poisoning | — | AML.T0043 (extended) | — | **YES** |

---

## Summary Count

| Axis | Total nodes | Borrowed / reframed | **NEW extensions** |
|---|---|---|---|
| Injection type | 3 | 2 | **1** |
| Delivery vector | 10 | 4 | **6** |
| Technique | 14 | 9 | **5** |
| Goal | 9 | 6 | **3** |
| **Total** | **36** | **21** | **15** |

---

## MITRE ATLAS Technique Reference

For convenience, the ATLAS techniques cited above:

| ATLAS ID | Name | Relevance to this ontology |
|---|---|---|
| AML.T0051 | LLM Prompt Injection | Root technique; injection_type axis |
| AML.T0051.000 | Direct Prompt Injection | IT-01, DV-01 |
| AML.T0051.001 | Indirect Prompt Injection | IT-02, DV-02/03/06/07 |
| AML.T0054 | LLM Jailbreak | TQ-04, TQ-05, GL-04 |
| AML.T0048 | Societal Harm | GL-05, GL-08 (partial) |
| AML.T0043 | Craft Adversarial Data | TQ-03, TQ-06, DV-10, GL-09 (extended) |
| AML.T0040 | ML Model Inference API Access | GL-03, TQ-14 (extended to trust boundaries) |
| AML.T0037 | Data from Information Repositories | GL-01 (data exfiltration context) |

---

## OWASP LLM01 Coverage Notes

OWASP LLM01 (2025 edition) distinguishes:
- **Direct injection:** user-controlled input manipulates model behavior
- **Indirect injection:** adversarial content in external sources processed by model

It does not currently enumerate:
- Specific delivery vectors beyond these two categories
- Specific techniques (it references the HackAPrompt paper but does not enumerate IDs)
- Goal taxonomy (it gives narrative examples but no structured classification)
- Multi-agent / tool-use / memory surfaces (noted as an emerging concern in OWASP commentary but not yet structured)

Nodes marked NEW in this ontology represent the areas where structured classification most clearly extends beyond the current OWASP enumeration.

---

## Honest Scope Statement

This crosswalk reflects a review of the three named frameworks as of mid-2025.
MITRE ATLAS and OWASP both update regularly; newer versions may add nodes that
reduce the "new" count here. The NEW designation means "not found in the reviewed
version of any of the three frameworks," not "never described anywhere in the literature."
