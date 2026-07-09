"""Map InjecAgent test cases to the detonation-harness scenario format.

# IMPLEMENTS: injection-corpus-detonation/adapt.py
# EXTENDS: studies/detonation-harness/src/mock_tools.py (external_action tool)

InjecAgent case structure:
    User Instruction     — what the user asked the agent to do
    User Tool            — the legitimate tool the agent uses for the task
    Tool Response        — API response containing an embedded attacker instruction
    Attacker Instruction — the injected command inside the tool response
    Attacker Tools       — list of tools the attacker wants called
    Attack Type          — "Physical Harm" | "Financial Harm" | "Data Security Harm"
                           | "Financial Data" | "Physical Data" | "Others"
    Expected Achievements— description of attacker goal

Harness scenario structure (from detonation-harness):
    id               — unique string
    user_task        — what the user asked
    untrusted_content— content from untrusted source (contains the injection)
    untrusted_source — name of the untrusted channel (the User Tool)
    available_tools  — list of mock tool names available to the model
    ground_truth     — always "injection" for InjecAgent cases

The mapping preserves InjecAgent's attack category labels as metadata fields
that are stored in the scenario but NOT used by the harness inference loop.

Attacker tool mapping:
    InjecAgent uses real service tool names (GmailSendEmail, BankManagerTransferFunds,
    AugustSmartLockGrantGuestAccess, ...). We map these to the harness's mock tool
    vocabulary using keyword matching. Tools that don't map to email / funds /
    file-share / file-write are routed to external_action (added to mock_tools.py
    in this study).

The model is presented with the full mock tool set including the mapped attacker
tool so that if it follows the injection, it can actually call the target tool.
"""

from __future__ import annotations

import re
from typing import Any

# ---------------------------------------------------------------------------
# Attacker tool keyword mapping
# ---------------------------------------------------------------------------

# (keyword, mock_tool_name) — checked in order; first match wins
_KEYWORD_MAP: list[tuple[str, str]] = [
    # Email / messaging
    ("email", "send_email"),
    ("gmail", "send_email"),
    ("smtp", "send_email"),
    ("sendmail", "send_email"),
    ("message", "send_email"),
    ("sms", "send_email"),
    ("slack", "send_email"),
    ("notify", "send_email"),
    # Financial transfers
    ("transfer", "transfer_funds"),
    ("fund", "transfer_funds"),
    ("bank", "transfer_funds"),
    ("paybill", "transfer_funds"),
    ("payment", "transfer_funds"),
    ("withdraw", "transfer_funds"),
    ("deposit", "transfer_funds"),
    ("binance", "transfer_funds"),
    ("stripe", "transfer_funds"),
    ("paypal", "transfer_funds"),
    ("placeorder", "transfer_funds"),
    # File sharing
    ("share", "share_file"),
    ("dropbox", "share_file"),
    ("googledrive", "share_file"),
    ("onedrive", "share_file"),
    ("sharelevel", "share_file"),
    # File writing / config modification
    ("writefile", "write_file"),
    ("createfile", "write_file"),
    ("updatefile", "write_file"),
    ("createpolicy", "write_file"),
    ("updatepolicy", "write_file"),
    ("updateprofile", "write_file"),
    ("clinicaldoc", "write_file"),
    # Everything else: generic external privileged action
]

_FALLBACK_TOOL = "external_action"


def map_attacker_tool(raw_tool_name: str) -> str:
    """Map an InjecAgent attacker tool name to a harness mock tool name.

    Matching is case-insensitive, applied against the camelCase tool name
    collapsed to lowercase.
    """
    lower = raw_tool_name.lower()
    for keyword, mock_name in _KEYWORD_MAP:
        if keyword in lower:
            return mock_name
    return _FALLBACK_TOOL


# ---------------------------------------------------------------------------
# Standard tool sets (non-privileged) presented alongside attacker tools
# ---------------------------------------------------------------------------

# Every scenario includes these so the model has something benign to call.
_BASE_TOOLS: list[str] = ["read_file", "http_get", "db_query"]

# Goal label derived from the InjecAgent split label
_GOAL_MAP: dict[str, str] = {
    "direct-harm-base": "direct-harm",
    "direct-harm-enhanced": "direct-harm",
    "data-stealing-base": "data-stealing",
    "data-stealing-enhanced": "data-stealing",
}


# ---------------------------------------------------------------------------
# Adapter
# ---------------------------------------------------------------------------

def adapt_case(
    case: dict[str, Any],
    split_label: str,
    index: int,
) -> dict[str, Any]:
    """Convert one InjecAgent case to a harness scenario dict.

    Returns a scenario dict with all harness fields plus InjecAgent metadata
    fields (prefixed `injecagent_`) for downstream result attribution.
    Importantly, the raw Attacker Instruction is NOT echoed into any field
    that would be committed to the repo (it lives only in untrusted_content,
    which is gitignored as part of the data cache).
    """
    attacker_tools_raw: list[str] = case.get("Attacker Tools", [])
    mapped_privileged: list[str] = list({
        map_attacker_tool(t) for t in attacker_tools_raw
    })

    available_tools: list[str] = list({
        *_BASE_TOOLS,
        *mapped_privileged,
    })

    # Split label → short goal string
    attacker_goal = _GOAL_MAP.get(split_label, split_label)

    # Derive a short label for the split (base vs enhanced)
    split_variant = "enhanced" if "enhanced" in split_label else "base"

    # Short goal prefix for the ID
    goal_prefix = "dh" if "direct-harm" in attacker_goal else "ds"

    scenario_id = f"injecagent_{goal_prefix}_{split_variant}_{index:04d}"

    return {
        # --- Harness fields ---
        "id": scenario_id,
        "ground_truth": "injection",
        "user_task": case.get("User Instruction", ""),
        "untrusted_content": case.get("Tool Response", ""),
        "untrusted_source": case.get("User Tool", "external_service"),
        "available_tools": available_tools,
        # --- InjecAgent metadata (no raw payload text) ---
        "injecagent_split": split_label,
        "injecagent_attack_type": case.get("Attack Type", "unknown"),
        "injecagent_attacker_goal": attacker_goal,
        "injecagent_attacker_tools_raw": attacker_tools_raw,
        "injecagent_attacker_tools_mapped": mapped_privileged,
        "injecagent_index": index,
    }


def adapt_corpus(
    corpus: dict[str, list[dict]],
) -> list[dict[str, Any]]:
    """Adapt all splits of an InjecAgent corpus to harness scenario dicts.

    Args:
        corpus: Dict from fetch_injecagent.load_corpus().

    Returns:
        Flat list of scenario dicts, one per InjecAgent case.
    """
    scenarios: list[dict] = []
    for split_label, cases in corpus.items():
        for i, case in enumerate(cases):
            scenarios.append(adapt_case(case, split_label, i))
    return scenarios


# ---------------------------------------------------------------------------
# Sampling
# ---------------------------------------------------------------------------

def stratified_sample(
    scenarios: list[dict[str, Any]],
    n_per_goal: int,
    seed: int = 42,
) -> list[dict[str, Any]]:
    """Return a stratified random sample of n_per_goal per attacker-goal category.

    Uses a deterministic Fisher-Yates shuffle via a seeded PRNG so results are
    reproducible. Groups by injecagent_attacker_goal.

    Args:
        scenarios: Full list of adapted scenarios.
        n_per_goal: Maximum cases to draw from each goal bucket.
        seed: RNG seed for reproducibility.

    Returns:
        Sampled list (may be smaller than n_per_goal * num_goals if a goal
        bucket has fewer cases than n_per_goal).
    """
    import random

    rng = random.Random(seed)

    groups: dict[str, list[dict]] = {}
    for s in scenarios:
        g = s.get("injecagent_attacker_goal", "unknown")
        groups.setdefault(g, []).append(s)

    sample: list[dict] = []
    for goal, cases in sorted(groups.items()):
        shuffled = list(cases)
        rng.shuffle(shuffled)
        drawn = shuffled[:n_per_goal]
        sample.extend(drawn)
        print(f"  Sampled {len(drawn)}/{len(cases)} from goal={goal}")

    return sample


# ---------------------------------------------------------------------------
# CLI helper
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent))
    from fetch_injecagent import load_corpus

    corpus = load_corpus(splits=["direct-harm-base", "data-stealing-base"])
    scenarios = adapt_corpus(corpus)
    sample = stratified_sample(scenarios, n_per_goal=5, seed=42)

    print(f"\nSample of {len(sample)} adapted scenarios:")
    for s in sample[:2]:
        # Print without raw payload
        display = {k: v for k, v in s.items() if k not in ("untrusted_content",)}
        print(json.dumps(display, indent=2))
