"""Fetch InjecAgent test cases to a local gitignored cache.

# IMPLEMENTS: injection-corpus-detonation/fetch_injecagent.py

Downloads the four base-split JSON files from the InjecAgent GitHub repo:
  data/test_cases_dh_base.json  — Direct Harm (DH) cases
  data/test_cases_ds_base.json  — Data Stealing (DS) cases
  data/test_cases_dh_enhanced.json
  data/test_cases_ds_enhanced.json

Output directory: data/injecagent/   (gitignored — contains raw attacker payloads)

PUBLIC SAFETY: This script downloads attacker instructions as research data.
The cache dir is gitignored; do NOT commit the downloaded JSON files.
The corpus runner (run_corpus.py) writes outcomes.jsonl which omits raw payloads.

Prior art:
  InjecAgent: Benchmarking Attack Deliverability of Prompt Injection Attacks on
  LLM-Integrated Applications — Zhan et al. 2024
  https://github.com/uiuc-kang-lab/InjecAgent
"""

from __future__ import annotations

import json
import logging
import time
import urllib.request
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

REPO_RAW = "https://raw.githubusercontent.com/uiuc-kang-lab/InjecAgent/main"

# Files to fetch: (remote path, local filename, split label)
SPLITS: list[tuple[str, str, str]] = [
    ("data/test_cases_dh_base.json", "dh_base.json", "direct-harm-base"),
    ("data/test_cases_ds_base.json", "ds_base.json", "data-stealing-base"),
    ("data/test_cases_dh_enhanced.json", "dh_enhanced.json", "direct-harm-enhanced"),
    ("data/test_cases_ds_enhanced.json", "ds_enhanced.json", "data-stealing-enhanced"),
]

DEFAULT_CACHE = Path(__file__).parent / "data" / "injecagent"


def fetch_split(
    remote_path: str,
    local_path: Path,
    retries: int = 3,
    delay: float = 2.0,
) -> list[dict]:
    """Fetch one split; return parsed list of case dicts.

    Uses the local cache if present and non-empty; otherwise downloads.
    """
    if local_path.exists() and local_path.stat().st_size > 0:
        logger.info("Cache hit: %s", local_path)
        with open(local_path, encoding="utf-8") as fh:
            return json.load(fh)

    url = f"{REPO_RAW}/{remote_path}"
    logger.info("Downloading %s -> %s", url, local_path)
    local_path.parent.mkdir(parents=True, exist_ok=True)

    last_exc: Optional[Exception] = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
            data: list[dict] = json.loads(raw)
            local_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            logger.info("Saved %d cases to %s", len(data), local_path)
            return data
        except Exception as exc:
            last_exc = exc
            logger.warning("Attempt %d/%d failed: %s", attempt, retries, exc)
            if attempt < retries:
                time.sleep(delay)

    raise RuntimeError(f"Failed to fetch {url} after {retries} attempts: {last_exc}")


def load_corpus(
    cache_dir: Path = DEFAULT_CACHE,
    splits: Optional[list[str]] = None,
) -> dict[str, list[dict]]:
    """Load InjecAgent corpus from cache (downloading if needed).

    Args:
        cache_dir: Local directory for cached JSON files.
        splits: Subset of split labels to load. None = all four.
                e.g. ["direct-harm-base", "data-stealing-base"]

    Returns:
        Dict mapping split label -> list of case dicts.
    """
    result: dict[str, list[dict]] = {}
    for remote_path, filename, label in SPLITS:
        if splits is not None and label not in splits:
            continue
        local_path = cache_dir / filename
        cases = fetch_split(remote_path, local_path)
        result[label] = cases
        print(f"  {label}: {len(cases)} cases")
    return result


def print_stats(corpus: dict[str, list[dict]]) -> None:
    """Print a summary of loaded corpus splits."""
    total = sum(len(v) for v in corpus.values())
    print(f"\nInjecAgent corpus loaded: {total} total cases")
    for label, cases in corpus.items():
        attack_types: dict[str, int] = {}
        for c in cases:
            t = c.get("Attack Type", "unknown")
            attack_types[t] = attack_types.get(t, 0) + 1
        breakdown = ", ".join(f"{k}:{v}" for k, v in sorted(attack_types.items()))
        print(f"  {label}: {len(cases)} cases [{breakdown}]")


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    cache = DEFAULT_CACHE
    if len(sys.argv) > 1:
        cache = Path(sys.argv[1])
    corpus = load_corpus(cache_dir=cache)
    print_stats(corpus)
