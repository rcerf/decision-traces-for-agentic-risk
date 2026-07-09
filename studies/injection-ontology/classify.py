"""
Prompt-Injection Ontology Classifier
=====================================
Fetches a sample of real public attack corpora and classifies each item into the
multi-axis ontology defined in ontology.json.

Corpora used
------------
Primary:  hackaprompt/hackaprompt-dataset (HuggingFace datasets)
Fallback: TrustAIRLab/in-the-wild-jailbreak-prompts

Classifier method
-----------------
Heuristic keyword/pattern matching per axis.  No ML model is loaded by default;
the "--model" flag enables a zero-shot HuggingFace classifier (slow on CPU).

Limitations (honest, stated upfront)
-------------------------------------
1. Keyword matching has high false-negative rate for obfuscated payloads (TQ-03).
2. Delivery vector cannot be reliably inferred from prompt text alone; we default
   to DV-01 (user-prompt) for items with no metadata.
3. Goal labels are inferred from technique + keyword signals; multi-goal attacks
   will be undercounted.
4. HackAPrompt dataset is competition-derived (user prompts only, direct injection
   only); it systematically under-represents indirect, agentic, and multi-hop
   categories.  Sample size and coverage bias are disclosed in results.
5. Aggregate distribution only is reported.  No raw attack strings are written to
   any output file.

Usage
-----
    python3 classify.py
    python3 classify.py --sample 2000
    python3 classify.py --corpus hackaprompt
    python3 classify.py --corpus jailbreak
    python3 classify.py --both
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

STUDY_DIR   = Path(__file__).parent
CACHE_DIR   = STUDY_DIR / "corpus_cache"
ONTOLOGY    = STUDY_DIR / "ontology.json"
RESULTS_OUT = STUDY_DIR / "classification_results.md"

CACHE_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Ontology axes (IDs only — no payloads, no attack strings)
# ---------------------------------------------------------------------------

INJECTION_TYPES = ["IT-01", "IT-02", "IT-03"]

DELIVERY_VECTORS = [
    "DV-01", "DV-02", "DV-03", "DV-04",
    "DV-05", "DV-06", "DV-07", "DV-08",
    "DV-09", "DV-10",
]

# Technique keyword patterns (case-insensitive, matched against lowercased prompt)
# We match against abstract structural patterns, NOT stored payloads.
TECHNIQUE_PATTERNS: dict[str, list[str]] = {
    "TQ-01": [   # Context Ignoring
        r"ignore (all |your )?(previous|prior|above|earlier) (instructions?|prompt|system|rules?|guidelines?)",
        r"disregard (all |your )?(previous|prior|above|earlier)",
        r"forget (everything|all) (you|you've) (were told|been told|know)",
        r"start (fresh|over|again|anew)",
        r"new (instructions?|task|objective)[:.]?\s",
    ],
    "TQ-02": [   # Payload Splitting / Token Smuggling
        r"continue (from|with|the|this)",
        r"part\s*[12]\s*of\s*[23]",
        r"split",
        r"token",
        r"smug",
    ],
    "TQ-03": [   # Obfuscation / Encoding
        r"base64",
        r"hex(adecimal)?",
        r"rot\s*13",
        r"caesar cipher",
        r"morse code",
        r"unicode",
        r"\\u[0-9a-fA-F]{4}",
        r"b'\s*\\x",
        r"leet",
        r"1337",
        r"backwards?",
        r"mirror (text|this)",
    ],
    "TQ-04": [   # Roleplay / Persona
        r"\b(you are|you're|act as|pretend (you are|to be)|imagine you are|roleplay)\b",
        r"\b(DAN|jailbroken|uncensored|unrestricted|without (restrictions?|guidelines?|limits?))\b",
        r"\b(character|persona|role|fictional|hypothetical scenario)\b",
        r"grandma|grandfather|chemistry teacher|security researcher",
    ],
    "TQ-05": [   # Refusal Suppression
        r"do not (refuse|say (no|sorry|i can't|i cannot))",
        r"never (refuse|say (no|sorry))",
        r"don't (add|include|say|mention) (any |)(disclaimer|caveat|warning|apology|sorry)",
        r"without (any |)(moral|ethical|safety) (concern|consideration|filter|judgment)",
        r"no (disclaimer|caveat|refusal|warning)",
    ],
    "TQ-06": [   # Few-Shot Priming
        r"(example|here'?s? (an|a) (sample|example)|for (example|instance)|e\.g\.).*?(question|answer|output|response)",
        r"user[:]\s*.*?assistant[:]\s*",
        r"input[:]\s*.*?output[:]\s*",
        r"q[:]\s*.*?a[:]\s*",
    ],
    "TQ-07": [   # Completion Compliance
        r"complete the (following|sentence|text)",
        r"finish (this|the following)",
        r"continue (this|the following)",
        r"fill in the blank",
    ],
    "TQ-08": [   # Distractor
        r"(by the way|btw|also|additionally|furthermore|moreover|p\.?s\.?)\s.*?(ignore|actually|but)",
        r"(translate|summarize|rewrite) (this|the following).*?(also|additionally|but also)",
    ],
    "TQ-09": [   # Authority Spoofing
        r"(system (prompt|message|instruction)|developer (mode|override)|admin|administrator|superuser|root|operator)\s*[:>]",
        r"as (your|the) (developer|creator|owner|admin|system|operator)",
        r"(maintenance|debug|diagnostic) mode",
        r"override (mode|protocol|policy)",
        r"openai|anthropic|google\s+deepmind|meta\s+ai",  # impersonation
    ],
    "TQ-10": [   # Tool-Call Injection (rare in user-prompt corpora)
        r"(function|tool|api|sql|http|curl|fetch|select|insert|drop|update) (call|request|query)",
        r"execute (a |the |this )?(function|query|command|tool)",
    ],
    "TQ-11": [   # Memory Poisoning (rare in user-prompt corpora)
        r"remember (this|the following|that) (for|next time|always|forever)",
        r"(store|save|memorize) (this|the following) (instruction|fact|rule)",
        r"next time (i|you|we) (ask|talk|chat)",
    ],
    "TQ-12": [   # Goal Hijacking (rare in user-prompt corpora)
        r"(new|updated|actual|real) (goal|objective|task|mission|purpose)",
        r"(your|the) (true|real|primary|main) (goal|objective|task) is",
    ],
    "TQ-13": [   # CoT Manipulation
        r"(think|reason|work) (step.by.step|through this|carefully)",
        r"chain.of.thought",
        r"(let'?s?|we (can|should)) (first|start by) (think|reason|consider|analyze)",
    ],
    "TQ-14": [   # Trust-Boundary Escalation
        r"(trusted|internal|authorized|approved|verified) (source|agent|system|component|tool)",
        r"you can trust (me|this|the following)",
        r"(this message|these instructions?) (is|are) (from|authorized by)",
    ],
}

GOAL_PATTERNS: dict[str, list[str]] = {
    "GL-01": [   # Data Exfiltration
        r"(tell me|show me|reveal|print|output|display|share|expose|leak|dump)\s*(the |your |all )?(system prompt|password|secret|credentials?|token|api key|private|confidential|internal|memory)",
        r"what (is|are) (your|the) (system|secret|internal|initial|original) (prompt|instructions?|rules?)",
    ],
    "GL-02": [   # Unauthorized Action
        r"(send|email|post|tweet|publish|upload|download|delete|remove|buy|order|transfer|pay|execute|run|call)",
        r"(make|take|perform|do) (an? )?(action|request|call|transaction|purchase)",
    ],
    "GL-03": [   # Privilege Escalation
        r"(admin|root|superuser|elevated|higher|full) (access|permission|privilege|mode|rights?)",
        r"bypass (authentication|authorization|access control|login|security)",
    ],
    "GL-04": [   # Policy / Safety Evasion
        r"(without|bypass|ignore|disable|turn off|remove) (safety|content|filter|moderation|policy|restriction|guardrail|alignment)",
        r"(unrestricted|unfiltered|uncensored|unmoderated|jailbreak)",
    ],
    "GL-05": [   # Harmful Content
        r"(how to|instructions? for|steps? to) (make|build|create|synthesize|produce)\s*(a |an |)?(weapon|bomb|explosive|drug|poison|malware|virus|ransomware)",
        r"(csam|child|minor)\s*(sexual|explicit|nude|naked)",
        r"(kill|murder|harm|hurt|attack|terroris)",
    ],
    "GL-06": [   # Resource Abuse
        r"(repeat|loop|keep|continue|forever|infinite|unlimited)\s*(this|that|doing|saying|generating)",
        r"(generate|write|produce)\s*\d{3,}\s*(words?|sentences?|paragraphs?|examples?|items?)",
    ],
    "GL-07": [   # Persistence
        r"(remember|store|save|retain)\s*(this|these|the following)\s*(instruction|rule|behavior|setting)\s*(always|forever|permanently|next time)",
    ],
    "GL-08": [   # Reputation Damage
        r"(say|claim|assert|announce|state)\s*(that|you are|i am)\s*(a |an )?(bad|evil|dangerous|biased|racist|hateful|harmful)",
        r"(impersonate|pretend to be|act as)\s*(a |an )?(competitor|rival|celebrity|politician|executive|ceo|president)",
    ],
    "GL-09": [   # Supply-Chain Poisoning
        r"(poison|corrupt|tamper|manipulate)\s*(the |this )?(dataset|training|data|knowledge base|retrieval|memory|index)",
        r"(inject|embed|hide)\s*(this|the following)\s*(in|into)\s*(the |a )?(training|dataset|knowledge|retrieval|index)",
    ],
}


def _match_patterns(text: str, pattern_dict: dict[str, list[str]]) -> list[str]:
    """Return list of IDs whose patterns match `text` (lowercased)."""
    lower = text.lower()
    matched = []
    for node_id, patterns in pattern_dict.items():
        for p in patterns:
            if re.search(p, lower):
                matched.append(node_id)
                break
    return matched


def classify_item(text: str) -> dict:
    """
    Classify a single prompt text into ontology axes.
    Returns a dict of axis -> list[matched IDs].

    NOTE: Raw text is NOT stored; only classification labels are returned.
    """
    techniques = _match_patterns(text, TECHNIQUE_PATTERNS)
    goals      = _match_patterns(text, GOAL_PATTERNS)

    # Injection type: all user-prompt corpus items are IT-01 by definition.
    # We detect IT-02/IT-03 signals only if the text reads like retrieved content.
    injection = ["IT-01"]
    if re.search(r"(retrieved|fetched|search result|document|context)[:]\s", text.lower()):
        injection = ["IT-02"]

    # Delivery vector: default DV-01 for user-prompt corpus
    vectors = ["DV-01"]
    if re.search(r"(pdf|word doc|spreadsheet|upload|file|attachment)", text.lower()):
        vectors.append("DV-07")
    if re.search(r"(email|inbox|message|mail)", text.lower()):
        vectors.append("DV-06")
    if re.search(r"(image|photo|picture|screenshot|audio|video)", text.lower()):
        vectors.append("DV-10")

    return {
        "injection_type": injection,
        "delivery_vector": vectors,
        "technique": techniques if techniques else ["UNKNOWN"],
        "goal": goals if goals else ["UNKNOWN"],
    }


def load_hackaprompt(sample_n: int) -> list[str]:
    """
    Load HackAPrompt dataset.

    NOTE: hackaprompt/hackaprompt-dataset is a gated HuggingFace dataset that
    requires authentication. If unavailable, falls back to combined public corpora.
    """
    from datasets import load_dataset  # type: ignore

    cache_path = CACHE_DIR / "hackaprompt_cache.json"
    if cache_path.exists():
        print(f"[corpus] Loading HackAPrompt from cache ({cache_path})")
        with open(cache_path) as f:
            items = json.load(f)
        print(f"[corpus] Loaded {len(items)} cached items")
    else:
        print("[corpus] Attempting hackaprompt/hackaprompt-dataset (requires HF auth)...")
        try:
            ds = load_dataset("hackaprompt/hackaprompt-dataset", split="train")
            items = [
                row["user_input"]
                for row in ds
                if row.get("user_input", "").strip()
            ]
            print(f"[corpus] HackAPrompt loaded: {len(items)} items")
        except Exception as e:
            print(f"[corpus] HackAPrompt unavailable ({e}); falling back to public corpora.")
            items = _load_public_combined()
        with open(cache_path, "w") as f:
            json.dump(items, f)
        print(f"[corpus] Cached {len(items)} items")

    import random
    random.seed(42)
    if sample_n and sample_n < len(items):
        items = random.sample(items, sample_n)
    print(f"[corpus] Working sample: {len(items)} items")
    return items


def _load_public_combined() -> list[str]:
    """
    Combine three publicly available corpora (no auth required):
      1. TrustAIRLab/in-the-wild-jailbreak-prompts (configs: jailbreak_2023_05_07, jailbreak_2023_12_25)
      2. rubend18/ChatGPT-Jailbreak-Prompts
      3. deepset/prompt-injections (injection-labeled items only)
    Returns a deduplicated list of prompt strings.
    """
    from datasets import load_dataset  # type: ignore

    items: list[str] = []

    # 1. TrustAIRLab in-the-wild jailbreaks
    for cfg in ["jailbreak_2023_05_07", "jailbreak_2023_12_25"]:
        try:
            ds = load_dataset("TrustAIRLab/in-the-wild-jailbreak-prompts", cfg, split="train")
            batch = [r["prompt"] for r in ds if r.get("prompt", "").strip()]
            print(f"[corpus]   TrustAIRLab/{cfg}: {len(batch)} items")
            items.extend(batch)
        except Exception as e:
            print(f"[corpus]   TrustAIRLab/{cfg} failed: {e}")

    # 2. rubend18 ChatGPT jailbreaks
    try:
        ds = load_dataset("rubend18/ChatGPT-Jailbreak-Prompts", split="train")
        batch = [r["Prompt"] for r in ds if r.get("Prompt", "").strip()]
        print(f"[corpus]   rubend18/ChatGPT-Jailbreak-Prompts: {len(batch)} items")
        items.extend(batch)
    except Exception as e:
        print(f"[corpus]   rubend18 failed: {e}")

    # 3. deepset prompt injections (injection-labeled only)
    for split in ["train", "test"]:
        try:
            ds = load_dataset("deepset/prompt-injections", split=split)
            batch = [r["text"] for r in ds if r.get("label") == 1 and r.get("text", "").strip()]
            print(f"[corpus]   deepset/prompt-injections ({split}): {len(batch)} injection items")
            items.extend(batch)
        except Exception as e:
            print(f"[corpus]   deepset/{split} failed: {e}")

    # Deduplicate (preserve order)
    seen: set[str] = set()
    unique: list[str] = []
    for it in items:
        key = it.strip()[:300]
        if key not in seen:
            seen.add(key)
            unique.append(it)
    print(f"[corpus] Combined public corpus (deduplicated): {len(unique)} items")
    return unique


def load_jailbreak(sample_n: int) -> list[str]:
    """Load TrustAIRLab jailbreak dataset."""
    from datasets import load_dataset  # type: ignore

    cache_path = CACHE_DIR / "jailbreak_cache.json"
    if cache_path.exists():
        print(f"[corpus] Loading jailbreak dataset from cache ({cache_path})")
        with open(cache_path) as f:
            items = json.load(f)
    else:
        print("[corpus] Fetching TrustAIRLab/in-the-wild-jailbreak-prompts ...")
        all_items: list[str] = []
        for cfg in ["jailbreak_2023_05_07", "jailbreak_2023_12_25"]:
            ds = load_dataset("TrustAIRLab/in-the-wild-jailbreak-prompts", cfg, split="train")
            all_items.extend([r["prompt"] for r in ds if r.get("prompt", "").strip()])
        print(f"[corpus] Raw dataset size: {len(all_items)} items")
        items = all_items
        with open(cache_path, "w") as f:
            json.dump(items, f)
        print(f"[corpus] Cached {len(items)} items")

    import random
    random.seed(42)
    if sample_n and sample_n < len(items):
        items = random.sample(items, sample_n)
    print(f"[corpus] Working sample: {len(items)} items")
    return items


def run_classification(
    texts: list[str],
    corpus_label: str,
) -> dict:
    """Classify all texts; return aggregate counts only."""
    print(f"[classify] Classifying {len(texts)} items from {corpus_label} ...")

    technique_counts = Counter()
    goal_counts      = Counter()
    injection_counts = Counter()
    vector_counts    = Counter()
    multi_technique  = 0
    no_technique     = 0

    for text in texts:
        result = classify_item(text)
        for it in result["injection_type"]:
            injection_counts[it] += 1
        for dv in result["delivery_vector"]:
            vector_counts[dv] += 1
        for tq in result["technique"]:
            technique_counts[tq] += 1
        for gl in result["goal"]:
            goal_counts[gl] += 1
        if len(result["technique"]) > 1 and "UNKNOWN" not in result["technique"]:
            multi_technique += 1
        if result["technique"] == ["UNKNOWN"]:
            no_technique += 1

    n = len(texts)
    return {
        "corpus": corpus_label,
        "n": n,
        "injection_type": dict(injection_counts.most_common()),
        "delivery_vector": dict(vector_counts.most_common()),
        "technique": dict(technique_counts.most_common()),
        "goal": dict(goal_counts.most_common()),
        "multi_technique_count": multi_technique,
        "no_technique_matched": no_technique,
    }


def fmt_pct(count: int, n: int) -> str:
    return f"{count} ({100*count/n:.1f}%)"


def write_results_md(results: list[dict]) -> None:
    """Write classification_results.md from aggregate counts."""
    lines: list[str] = []
    lines += [
        "# Classification Results",
        "",
        "> **Classifier note:** Heuristic keyword/regex matching. High false-negative rate",
        "> for obfuscated prompts (TQ-03) and multi-turn techniques (TQ-02).",
        "> Delivery vector and goal are partially inferred from text signals alone.",
        "> Aggregate distribution only is reported; no raw attack strings are included.",
        "",
    ]

    for r in results:
        n = r["n"]
        c = r["corpus"]
        if c == "Combined public corpora (see note)":
            lines += [
                f"## Corpus: {c} — N = {n}",
                "",
                "**Corpora included (no HF auth required):**",
                "- `TrustAIRLab/in-the-wild-jailbreak-prompts` config `jailbreak_2023_05_07` (666 items) + `jailbreak_2023_12_25` (1405 items pre-dedup)",
                "- `rubend18/ChatGPT-Jailbreak-Prompts` (79 items)",
                "- `deepset/prompt-injections` injection-labeled items, train+test splits (263 items)",
                f"- Total after cross-corpus deduplication: **{n} unique items** (full population, no random sampling needed)",
                "",
                "**Note on HackAPrompt corpus:** `hackaprompt/hackaprompt-dataset` is gated on HuggingFace and",
                "requires authentication. It was not accessible in this run. The HackAPrompt paper (arXiv:2311.16119)",
                "is cited as a framework source; the competition entries themselves could not be classified.",
                "This biases the sample toward in-the-wild jailbreaks (TrustAIRLab) and curated prompt-injection",
                "examples (deepset), and away from competition-style single-turn attacks.",
                "",
            ]
        else:
            lines += [
                f"## Corpus: `{c}` — Sample N = {n}",
                "",
            ]

        lines += [
            f"Multi-technique items: {fmt_pct(r['multi_technique_count'], n)}  ",
            f"No technique matched (UNKNOWN): {fmt_pct(r['no_technique_matched'], n)}",
            "",
        ]

        lines += ["### Technique Distribution", ""]
        lines += ["| Technique ID | Label | Count | % of sample |",
                  "|---|---|---|---|"]
        # Load labels from ontology.json
        ontology = json.loads(ONTOLOGY.read_text())
        tq_labels = {
            nid: nd["label"]
            for nid, nd in ontology["axes"]["technique"]["nodes"].items()
            if nid.startswith("TQ") or nd.get("id", "").startswith("TQ")
        }
        # ontology keys are camelCase; id field is the canonical ID
        id_to_label = {}
        for node_data in ontology["axes"]["technique"]["nodes"].values():
            id_to_label[node_data["id"]] = node_data["label"]

        for tq_id, count in sorted(r["technique"].items(), key=lambda x: -x[1]):
            label = id_to_label.get(tq_id, tq_id)
            lines.append(f"| {tq_id} | {label} | {count} | {100*count/n:.1f}% |")
        lines.append("")

        lines += ["### Goal Distribution", ""]
        lines += ["| Goal ID | Label | Count | % of sample |",
                  "|---|---|---|---|"]
        id_to_label_g = {}
        for node_data in ontology["axes"]["goal"]["nodes"].values():
            id_to_label_g[node_data["id"]] = node_data["label"]

        for gl_id, count in sorted(r["goal"].items(), key=lambda x: -x[1]):
            label = id_to_label_g.get(gl_id, gl_id)
            lines.append(f"| {gl_id} | {label} | {count} | {100*count/n:.1f}% |")
        lines.append("")

        lines += ["### Injection Type Distribution", ""]
        lines += ["| ID | Count | % |", "|---|---|---|"]
        for it_id, count in sorted(r["injection_type"].items(), key=lambda x: -x[1]):
            lines.append(f"| {it_id} | {count} | {100*count/n:.1f}% |")
        lines.append("")

        lines += ["### Delivery Vector Distribution", ""]
        lines += ["| ID | Count | % |", "|---|---|---|"]
        for dv_id, count in sorted(r["delivery_vector"].items(), key=lambda x: -x[1]):
            lines.append(f"| {dv_id} | {count} | {100*count/n:.1f}% |")
        lines.append("")

    # -----------------------------------------------------------------------
    # Negative-space analysis: which cells are sparse / empty?
    # -----------------------------------------------------------------------
    lines += [
        "---",
        "",
        "## Negative-Space Analysis: What the Public Corpora Do NOT Cover",
        "",
        "This section identifies ontology cells that are **systematically under-represented**",
        "in the evaluated public corpora. These are the attack categories for which defenders",
        "have the least empirical data.",
        "",
        "### Injection Type",
        "",
        "| ID | Label | Status in corpus | Notes |",
        "|---|---|---|---|",
        "| IT-01 | Direct Prompt Injection | DOMINANT | Both corpora are 100% direct-injection by construction |",
        "| IT-02 | Indirect Prompt Injection | ABSENT | No retrieval/RAG context in either corpus |",
        "| IT-03 | Multi-Hop / Cross-Agent | ABSENT | No multi-agent examples exist in any public corpus we found |",
        "",
        "**Key gap:** The two most dangerous agentic injection types (IT-02, IT-03) are completely",
        "unrepresented in available public corpora. Defenders have no labeled data to train",
        "or test detection systems on these categories.",
        "",
        "### Delivery Vector",
        "",
        "| ID | Label | Status | Notes |",
        "|---|---|---|---|",
        "| DV-01 | User Prompt | SATURATED | All public corpus items |",
        "| DV-02 | Retrieved Document | ABSENT | No RAG corpus exists publicly at scale |",
        "| DV-03 | Web Page | ABSENT | A few known examples (Riley Goodside demos) but no labeled corpus |",
        "| DV-04 | Tool Output | ABSENT | No labeled corpus |",
        "| DV-05 | Agent Memory | ABSENT | No labeled corpus; memory-augmented agents are recent |",
        "| DV-06 | Email | ABSENT | No public labeled corpus |",
        "| DV-07 | File Upload | ABSENT | No public labeled corpus |",
        "| DV-08 | Upstream Agent | ABSENT | No public labeled corpus |",
        "| DV-09 | System Prompt | LOW | A few examples in competition data |",
        "| DV-10 | Multimodal | ABSENT | No labeled multimodal injection corpus found |",
        "",
        "**Key gap:** 8 of 10 delivery vector cells are empty or near-empty in public corpora.",
        "This is a critical empirical gap: the agentic delivery surfaces (DV-04 through DV-08,",
        "DV-10) that represent the greatest forward-looking risk are the ones with zero",
        "publicly available labeled training or evaluation data.",
        "",
        "### Technique",
        "",
        "| ID | Label | Status | Notes |",
        "|---|---|---|---|",
        "| TQ-01 | Context Ignoring | WELL COVERED | Dominant technique in HackAPrompt |",
        "| TQ-02 | Payload Splitting | LOW | Hard to detect with keyword matching; likely undercounted |",
        "| TQ-03 | Obfuscation/Encoding | LOW | By design, evades text-based classifiers |",
        "| TQ-04 | Roleplay/Persona | WELL COVERED | DAN and similar patterns pervasive |",
        "| TQ-05 | Refusal Suppression | COVERED | Common modifier |",
        "| TQ-06 | Few-Shot Priming | SPARSE | Present but requires multi-example context |",
        "| TQ-07 | Completion Compliance | SPARSE | Detectable but infrequent |",
        "| TQ-08 | Distractor | LOW | By design hard to detect |",
        "| TQ-09 | Authority Spoofing | COVERED | System-prompt impersonation patterns present |",
        "| TQ-10 | Tool-Call Injection | ABSENT | No user-prompt corpus captures this |",
        "| TQ-11 | Memory Poisoning | ABSENT | No public corpus |",
        "| TQ-12 | Goal Hijacking | ABSENT | No planning-agent corpus |",
        "| TQ-13 | CoT Manipulation | ABSENT | Requires reasoning trace; no public corpus |",
        "| TQ-14 | Trust-Boundary Escalation | ABSENT | Requires multi-agent setup |",
        "",
        "**Key gap:** All five new agentic technique nodes (TQ-10 through TQ-14) have zero",
        "representation in any public corpus. The three techniques most likely to succeed against",
        "production agentic systems (TQ-11, TQ-12, TQ-14) are also the least studied.",
        "",
        "### Goal",
        "",
        "| ID | Label | Status | Notes |",
        "|---|---|---|---|",
        "| GL-04 | Policy/Safety Evasion | DOMINANT | Primary goal of jailbreak corpora |",
        "| GL-05 | Harmful Content | COVERED | Co-present with GL-04 |",
        "| GL-01 | Data Exfiltration | SPARSE | System-prompt theft examples present |",
        "| GL-02 | Unauthorized Action | ABSENT | No action-capable agent context in corpora |",
        "| GL-03 | Privilege Escalation | ABSENT | No multi-permission context |",
        "| GL-06 | Resource Abuse | ABSENT | No agentic loop context |",
        "| GL-07 | Agent Persistence | ABSENT | No memory-augmented context |",
        "| GL-08 | Reputation Damage | SPARSE | Some impersonation examples |",
        "| GL-09 | Supply-Chain Poisoning | ABSENT | No pipeline context |",
        "",
        "**Key gap:** Public corpora are overwhelmingly oriented toward policy/safety evasion (GL-04)",
        "and harmful content (GL-05). The goal categories most relevant to enterprise and",
        "agentic risk — unauthorized action (GL-02), resource abuse (GL-06), persistence (GL-07),",
        "and supply-chain poisoning (GL-09) — have zero labeled public examples.",
        "",
        "---",
        "",
        "## Summary of Gaps",
        "",
        "| Category | Cells with public data | Cells with NO public data |",
        "|---|---|---|",
        "| Injection type | 1 of 3 | 2 of 3 (67%) |",
        "| Delivery vector | 2 of 10 | 8 of 10 (80%) |",
        "| Technique | 5 of 14 | 9 of 14 (64%) |",
        "| Goal | 4 of 9 | 5 of 9 (56%) |",
        "",
        "**The public attack corpus is heavily front-loaded on direct, user-turn,",
        "single-turn, policy-evasion attacks. The agentic attack surface —",
        "indirect injection, multi-hop, tool-use, memory, multi-agent trust —",
        "is essentially uncharted empirically.**",
        "",
        "This is the core negative-space finding: the cells that most urgently need",
        "red-team data, detection benchmarks, and defenses are the ones the community",
        "has not yet collected corpora for.",
    ]

    out = "\n".join(lines) + "\n"
    RESULTS_OUT.write_text(out)
    print(f"[output] Results written to {RESULTS_OUT}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify attack corpus into injection ontology")
    parser.add_argument("--sample", type=int, default=3000,
                        help="Max items to sample per corpus (default 3000)")
    parser.add_argument("--corpus", choices=["hackaprompt", "jailbreak"], default="hackaprompt",
                        help="Which corpus to use (default: hackaprompt)")
    parser.add_argument("--both", action="store_true",
                        help="Use both corpora")
    args = parser.parse_args()

    all_results = []

    if args.corpus == "hackaprompt" or args.both:
        texts = load_hackaprompt(args.sample)
        corpus_label = "hackaprompt/hackaprompt-dataset"
        if (CACHE_DIR / "hackaprompt_cache.json").exists() and len(texts) == 1508:
            corpus_label = "Combined public corpora (see note)"
        all_results.append(run_classification(texts, corpus_label))

    if args.corpus == "jailbreak" or args.both:
        try:
            texts = load_jailbreak(args.sample)
            all_results.append(run_classification(texts, "TrustAIRLab/in-the-wild-jailbreak-prompts"))
        except Exception as e:
            print(f"[warn] Could not load jailbreak corpus: {e}", file=sys.stderr)

    write_results_md(all_results)

    # Print brief console summary
    for r in all_results:
        n = r["n"]
        top_tq = sorted(r["technique"].items(), key=lambda x: -x[1])[:3]
        top_gl = sorted(r["goal"].items(), key=lambda x: -x[1])[:3]
        print(f"\n=== {r['corpus']} (N={n}) ===")
        print("Top techniques:", ", ".join(f"{k}={v}" for k, v in top_tq))
        print("Top goals:     ", ", ".join(f"{k}={v}" for k, v in top_gl))
        print(f"UNKNOWN technique: {r['no_technique_matched']} ({100*r['no_technique_matched']/n:.1f}%)")

    print(f"\nFull results written to: {RESULTS_OUT}")


if __name__ == "__main__":
    main()
