# Adapter Workflow

All intake adapters emit the same `source_signal` JSON shape. That means the downstream triage script can score and prioritize signals regardless of where they came from.

## Research: arXiv

Use:

```bash
python3 src/ingest_arxiv.py --config data/config/arxiv_queries.json --max-results 5 --output data/generated/arxiv_signals.json
python3 src/signal_triage.py data/generated/arxiv_signals.json
```

Notes:

- arXiv results are Tier 1 research signals.
- The adapter marks them as `summarize_only`.
- A human should read the paper before promoting a result to a probe.
- Broad queries may return relevant agentic-evaluation work that is not directly about safety; this is expected and should be triaged.

## Incidents: AIID

Use URL lookup when you have candidate journalism or policy URLs:

```bash
python3 src/ingest_aiid.py --lookup-urls data/incidents/sample_aiid_lookup_urls.json --output data/generated/aiid_lookup_signals.json
python3 src/signal_triage.py data/generated/aiid_lookup_signals.json
```

Use snapshot mode for a local or remote JSON export:

```bash
python3 src/ingest_aiid.py --snapshot path/to/aiid_snapshot.json --output data/generated/aiid_snapshot_signals.json
```

Notes:

- The adapter currently supports AIID `lookupbyurl` plus flexible snapshot JSON.
- It does not assume a stable public bulk-feed endpoint.
- Incident signals should become harm-pathway probes, not recreations of harmful details.

## Incidents: MIT AI Incident Tracker

Use:

```bash
python3 src/ingest_mit_tracker.py --output data/generated/mit_tracker_signals.json
python3 src/signal_triage.py data/generated/mit_tracker_signals.json
```

Notes:

- The MIT tracker is useful for trend and taxonomy insight.
- Treat its classifications as indicative, especially where the site notes that labels are LLM-generated.
- Promote only the safe abstraction into probes.

## Social And Web: Manual/Curated Capture

Use:

```bash
python3 src/ingest_manual_social.py data/manual/social_capture_template.json --output data/generated/manual_social_signals.json
python3 src/signal_triage.py data/generated/manual_social_signals.json
```

Notes:

- This is the safe lane for X, Reddit, Hacker News, GitHub issues, blogs, newsletters, and one-off web observations.
- Default source tier is 3.
- Default evidence status is `unverified`.
- Default raw detail policy is `do_not_reproduce`.
- Store the safe abstraction, not the exploit string.

## X API: Recent Search Or List Timeline

Use:

```bash
export X_BEARER_TOKEN="..."
python3 src/ingest_x.py --query-config data/config/x_queries.json --output data/generated/x_signals.json
python3 src/signal_triage.py data/generated/x_signals.json
```

Optional curated-list ingestion:

```bash
python3 src/ingest_x.py --list-id "$X_LIST_ID" --max-results 25 --output data/generated/x_list_signals.json
```

Notes:

- This uses X API v2 Recent Search and, optionally, List timeline endpoints.
- Recent Search covers recent public Posts; full-archive search requires higher access.
- `X_BEARER_TOKEN` must come from an approved X developer app.
- The adapter defaults to Tier 3, `unverified`, and `do_not_reproduce` / `summarize_only` policies.
- Treat X as creative weak-signal intake, not validated evidence.

## Combining Signals

Use:

```bash
python3 src/merge_signals.py \
  data/generated/arxiv_signals.json \
  data/generated/aiid_lookup_signals.json \
  data/generated/mit_tracker_signals.json \
  data/generated/x_signals.json \
  data/generated/manual_social_signals.json \
  --output data/generated/combined_signals.json

python3 src/signal_triage.py data/generated/combined_signals.json
```

The merge script deduplicates by source URL and title, while preserving notes from duplicate records.
