#!/usr/bin/env python3
"""Ingest public X posts into review-gated source signals.

Requires an X API bearer token in X_BEARER_TOKEN or --bearer-token.
The adapter stores safe summaries and metadata, not raw exploit recipes.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from ingest_common import clean_text, source_signal, stable_id, today, write_json


RECENT_SEARCH_URL = "https://api.x.com/2/tweets/search/recent"
LIST_TWEETS_URL = "https://api.x.com/2/lists/{list_id}/tweets"


def request_json(url: str, bearer_token: str) -> dict[str, Any]:
    req = Request(url, headers={"Authorization": f"Bearer {bearer_token}"})
    with urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_recent_search(query: str, bearer_token: str, max_results: int = 10) -> dict[str, Any]:
    params = {
        "query": query,
        "max_results": max(10, min(max_results, 100)),
        "tweet.fields": "created_at,author_id,public_metrics,possibly_sensitive,lang,entities",
        "expansions": "author_id",
        "user.fields": "username,name,verified",
    }
    return request_json(f"{RECENT_SEARCH_URL}?{urlencode(params)}", bearer_token)


def fetch_list_tweets(list_id: str, bearer_token: str, max_results: int = 10) -> dict[str, Any]:
    params = {
        "max_results": max(5, min(max_results, 100)),
        "tweet.fields": "created_at,author_id,public_metrics,possibly_sensitive,lang,entities",
        "expansions": "author_id",
        "user.fields": "username,name,verified",
    }
    return request_json(f"{LIST_TWEETS_URL.format(list_id=list_id)}?{urlencode(params)}", bearer_token)


def author_lookup(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    users = payload.get("includes", {}).get("users", [])
    return {str(user.get("id")): user for user in users}


def post_url(post: dict[str, Any], users_by_id: dict[str, dict[str, Any]]) -> str:
    author = users_by_id.get(str(post.get("author_id")), {})
    username = author.get("username")
    if username and post.get("id"):
        return f"https://x.com/{username}/status/{post['id']}"
    if post.get("id"):
        return f"https://x.com/i/web/status/{post['id']}"
    return "manual-x-intake"


def safe_summary(text: str) -> str:
    """Keep enough detail for triage while avoiding exploit-recipe storage."""
    text = clean_text(text)
    if len(text) <= 220:
        return text
    return text[:217].rstrip() + "..."


def payload_to_signals(
    payload: dict[str, Any],
    *,
    source_name: str,
    default_categories: list[str],
    default_surfaces: list[str],
    raw_detail_policy: str,
) -> list[dict[str, Any]]:
    users = author_lookup(payload)
    signals = []
    for post in payload.get("data", []) or []:
        url = post_url(post, users)
        text = post.get("text", "")
        created_at = str(post.get("created_at", today()))[:10]
        signal_id = stable_id("SIG-X", url, text)
        probe_id = stable_id("PROBE-X", url, text)
        author = users.get(str(post.get("author_id")), {})
        author_label = f"@{author.get('username')}" if author.get("username") else "X post"
        signals.append(
            source_signal(
                signal_id=signal_id,
                title=f"X weak signal from {author_label}",
                source_tier=3,
                source_type="social",
                source_name=source_name,
                source_url=url,
                observed_at=created_at,
                summary=safe_summary(text),
                risk_hypothesis="This public X post may describe a jailbreak motif, agent failure, guardrail gap, or socially salient risk worth abstracting into a safe probe.",
                affected_surfaces=default_surfaces,
                risk_categories=default_categories,
                evidence_status="unverified",
                novelty=4,
                actionability=3,
                source_reliability=2,
                raw_detail_policy=raw_detail_policy,
                probe_id=probe_id,
                probe_description="Human-review the post, abstract the failure pattern, and create a harmless probe without reproducing exploit text.",
                expected_detection_stage="ingress",
                safe_reproduction="Use benign placeholders and avoid copying jailbreak strings or operational misuse instructions.",
                notes="Generated from X API; review required before promotion.",
            )
        )
    return signals


def query_config_to_signals(config_path: Path, bearer_token: str, max_results_override: int | None) -> list[dict[str, Any]]:
    query_configs = json.loads(config_path.read_text())
    signals: list[dict[str, Any]] = []
    for query_cfg in query_configs:
        max_results = max_results_override or int(query_cfg.get("max_results", 10))
        payload = fetch_recent_search(query_cfg["query"], bearer_token, max_results=max_results)
        signals.extend(
            payload_to_signals(
                payload,
                source_name=f"X recent search: {query_cfg['name']}",
                default_categories=query_cfg["risk_categories"],
                default_surfaces=query_cfg["affected_surfaces"],
                raw_detail_policy=query_cfg.get("raw_detail_policy", "do_not_reproduce"),
            )
        )
    return signals


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query-config", default="data/config/x_queries.json")
    parser.add_argument("--list-id", help="Optional X List ID to ingest instead of/in addition to recent search")
    parser.add_argument("--max-results", type=int)
    parser.add_argument("--bearer-token", default=os.environ.get("X_BEARER_TOKEN"))
    parser.add_argument("--input-json", help="Use saved X API JSON payload instead of making a live request")
    parser.add_argument("--output")
    args = parser.parse_args()

    signals: list[dict[str, Any]] = []
    if args.input_json:
        payload = json.loads(Path(args.input_json).read_text())
        signals.extend(
            payload_to_signals(
                payload,
                source_name="X saved payload",
                default_categories=["jailbreak_motif", "guardrail_gap"],
                default_surfaces=["ingress", "final_output"],
                raw_detail_policy="do_not_reproduce",
            )
        )
    else:
        if not args.bearer_token:
            raise SystemExit("X_BEARER_TOKEN is required for live X API ingestion")
        signals.extend(query_config_to_signals(Path(args.query_config), args.bearer_token, args.max_results))
        if args.list_id:
            payload = fetch_list_tweets(args.list_id, args.bearer_token, max_results=args.max_results or 10)
            signals.extend(
                payload_to_signals(
                    payload,
                    source_name=f"X list timeline: {args.list_id}",
                    default_categories=["jailbreak_motif", "guardrail_gap", "public_salience"],
                    default_surfaces=["ingress", "final_output"],
                    raw_detail_policy="do_not_reproduce",
                )
            )

    write_json(signals, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
