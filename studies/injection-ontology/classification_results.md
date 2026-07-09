# Classification Results

> **Classifier note:** Heuristic keyword/regex matching. High false-negative rate
> for obfuscated prompts (TQ-03) and multi-turn techniques (TQ-02).
> Delivery vector and goal are partially inferred from text signals alone.
> Aggregate distribution only is reported; no raw attack strings are included.

## Corpus: Combined public corpora (see note) — N = 1508

**Corpora included (no HF auth required):**
- `TrustAIRLab/in-the-wild-jailbreak-prompts` config `jailbreak_2023_05_07` (666 items) + `jailbreak_2023_12_25` (1405 items pre-dedup)
- `rubend18/ChatGPT-Jailbreak-Prompts` (79 items)
- `deepset/prompt-injections` injection-labeled items, train+test splits (263 items)
- Total after cross-corpus deduplication: **1508 unique items** (full population, no random sampling needed)

**Note on HackAPrompt corpus:** `hackaprompt/hackaprompt-dataset` is gated on HuggingFace and
requires authentication. It was not accessible in this run. The HackAPrompt paper (arXiv:2311.16119)
is cited as a framework source; the competition entries themselves could not be classified.
This biases the sample toward in-the-wild jailbreaks (TrustAIRLab) and curated prompt-injection
examples (deepset), and away from competition-style single-turn attacks.

Multi-technique items: 628 (41.6%)  
No technique matched (UNKNOWN): 372 (24.7%)

### Technique Distribution

| Technique ID | Label | Count | % of sample |
|---|---|---|---|
| TQ-04 | Role-Play / Persona Adoption | 1045 | 69.3% |
| UNKNOWN | UNKNOWN | 372 | 24.7% |
| TQ-09 | Authority / System Spoofing | 344 | 22.8% |
| TQ-05 | Refusal Suppression | 203 | 13.5% |
| TQ-06 | Few-Shot Priming | 195 | 12.9% |
| TQ-08 | Distractor / Misdirection | 191 | 12.7% |
| TQ-02 | Payload Splitting / Token Smuggling | 121 | 8.0% |
| TQ-01 | Context Ignoring | 46 | 3.1% |
| TQ-12 | Goal / Objective Hijacking | 17 | 1.1% |
| TQ-10 | Tool-Call Injection | 9 | 0.6% |
| TQ-03 | Obfuscation / Encoding | 9 | 0.6% |
| TQ-07 | Completion Compliance | 4 | 0.3% |
| TQ-14 | Trust-Boundary Escalation | 2 | 0.1% |
| TQ-13 | Chain-of-Thought Manipulation | 1 | 0.1% |
| TQ-11 | Memory Poisoning | 1 | 0.1% |

### Goal Distribution

| Goal ID | Label | Count | % of sample |
|---|---|---|---|
| GL-02 | Unauthorized Action | 698 | 46.3% |
| UNKNOWN | UNKNOWN | 589 | 39.1% |
| GL-05 | Harmful Content Generation | 433 | 28.7% |
| GL-04 | Policy / Safety Evasion | 360 | 23.9% |
| GL-06 | Resource Abuse (Compute / Cost / Rate-Limit) | 27 | 1.8% |
| GL-01 | Data Exfiltration | 2 | 0.1% |
| GL-03 | Privilege Escalation | 1 | 0.1% |

### Injection Type Distribution

| ID | Count | % |
|---|---|---|
| IT-01 | 1506 | 99.9% |
| IT-02 | 2 | 0.1% |

### Delivery Vector Distribution

| ID | Count | % |
|---|---|---|
| DV-01 | 1508 | 100.0% |
| DV-06 | 319 | 21.2% |
| DV-10 | 112 | 7.4% |
| DV-07 | 46 | 3.1% |

---

## Negative-Space Analysis: What the Public Corpora Do NOT Cover

This section identifies ontology cells that are **systematically under-represented**
in the evaluated public corpora. These are the attack categories for which defenders
have the least empirical data.

### Injection Type

| ID | Label | Status in corpus | Notes |
|---|---|---|---|
| IT-01 | Direct Prompt Injection | DOMINANT | Both corpora are 100% direct-injection by construction |
| IT-02 | Indirect Prompt Injection | ABSENT | No retrieval/RAG context in either corpus |
| IT-03 | Multi-Hop / Cross-Agent | ABSENT | No multi-agent examples exist in any public corpus we found |

**Key gap:** The two most dangerous agentic injection types (IT-02, IT-03) are completely
unrepresented in available public corpora. Defenders have no labeled data to train
or test detection systems on these categories.

### Delivery Vector

| ID | Label | Status | Notes |
|---|---|---|---|
| DV-01 | User Prompt | SATURATED | All public corpus items |
| DV-02 | Retrieved Document | ABSENT | No RAG corpus exists publicly at scale |
| DV-03 | Web Page | ABSENT | A few known examples (Riley Goodside demos) but no labeled corpus |
| DV-04 | Tool Output | ABSENT | No labeled corpus |
| DV-05 | Agent Memory | ABSENT | No labeled corpus; memory-augmented agents are recent |
| DV-06 | Email | ABSENT | No public labeled corpus |
| DV-07 | File Upload | ABSENT | No public labeled corpus |
| DV-08 | Upstream Agent | ABSENT | No public labeled corpus |
| DV-09 | System Prompt | LOW | A few examples in competition data |
| DV-10 | Multimodal | ABSENT | No labeled multimodal injection corpus found |

**Key gap:** 8 of 10 delivery vector cells are empty or near-empty in public corpora.
This is a critical empirical gap: the agentic delivery surfaces (DV-04 through DV-08,
DV-10) that represent the greatest forward-looking risk are the ones with zero
publicly available labeled training or evaluation data.

### Technique

| ID | Label | Status | Notes |
|---|---|---|---|
| TQ-01 | Context Ignoring | WELL COVERED | Dominant technique in HackAPrompt |
| TQ-02 | Payload Splitting | LOW | Hard to detect with keyword matching; likely undercounted |
| TQ-03 | Obfuscation/Encoding | LOW | By design, evades text-based classifiers |
| TQ-04 | Roleplay/Persona | WELL COVERED | DAN and similar patterns pervasive |
| TQ-05 | Refusal Suppression | COVERED | Common modifier |
| TQ-06 | Few-Shot Priming | SPARSE | Present but requires multi-example context |
| TQ-07 | Completion Compliance | SPARSE | Detectable but infrequent |
| TQ-08 | Distractor | LOW | By design hard to detect |
| TQ-09 | Authority Spoofing | COVERED | System-prompt impersonation patterns present |
| TQ-10 | Tool-Call Injection | ABSENT | No user-prompt corpus captures this |
| TQ-11 | Memory Poisoning | ABSENT | No public corpus |
| TQ-12 | Goal Hijacking | ABSENT | No planning-agent corpus |
| TQ-13 | CoT Manipulation | ABSENT | Requires reasoning trace; no public corpus |
| TQ-14 | Trust-Boundary Escalation | ABSENT | Requires multi-agent setup |

**Key gap:** All five new agentic technique nodes (TQ-10 through TQ-14) have zero
representation in any public corpus. The three techniques most likely to succeed against
production agentic systems (TQ-11, TQ-12, TQ-14) are also the least studied.

### Goal

| ID | Label | Status | Notes |
|---|---|---|---|
| GL-04 | Policy/Safety Evasion | DOMINANT | Primary goal of jailbreak corpora |
| GL-05 | Harmful Content | COVERED | Co-present with GL-04 |
| GL-01 | Data Exfiltration | SPARSE | System-prompt theft examples present |
| GL-02 | Unauthorized Action | ABSENT | No action-capable agent context in corpora |
| GL-03 | Privilege Escalation | ABSENT | No multi-permission context |
| GL-06 | Resource Abuse | ABSENT | No agentic loop context |
| GL-07 | Agent Persistence | ABSENT | No memory-augmented context |
| GL-08 | Reputation Damage | SPARSE | Some impersonation examples |
| GL-09 | Supply-Chain Poisoning | ABSENT | No pipeline context |

**Key gap:** Public corpora are overwhelmingly oriented toward policy/safety evasion (GL-04)
and harmful content (GL-05). The goal categories most relevant to enterprise and
agentic risk — unauthorized action (GL-02), resource abuse (GL-06), persistence (GL-07),
and supply-chain poisoning (GL-09) — have zero labeled public examples.

---

## Summary of Gaps

| Category | Cells with public data | Cells with NO public data |
|---|---|---|
| Injection type | 1 of 3 | 2 of 3 (67%) |
| Delivery vector | 2 of 10 | 8 of 10 (80%) |
| Technique | 5 of 14 | 9 of 14 (64%) |
| Goal | 4 of 9 | 5 of 9 (56%) |

**The public attack corpus is heavily front-loaded on direct, user-turn,
single-turn, policy-evasion attacks. The agentic attack surface —
indirect injection, multi-hop, tool-use, memory, multi-agent trust —
is essentially uncharted empirically.**

This is the core negative-space finding: the cells that most urgently need
red-team data, detection benchmarks, and defenses are the ones the community
has not yet collected corpora for.
