# Risk Intelligence Intake

This study turns messy external signals into structured risk hypotheses and probe backlog items.

The thesis is that agentic-risk research should use a tiered crowdsource:

- Social platforms and forums surface creative jailbreak ideas, misuse patterns, and user-discovered failures.
- Journalists and incident databases surface real-world harm, affected populations, and public accountability gaps.
- Researchers and benchmark builders stabilize those observations into methods, datasets, and evaluation claims.
- Standards and security frameworks provide durable taxonomy, controls, and governance language.
- Policy actors reveal which risks are becoming institutionally salient.

The goal is not to reproduce harmful prompts. The goal is to capture the safe abstraction: what risk pattern was observed, what surface it affects, what taxonomy cell it suggests, and what probe could test it.

## Run

```bash
python3 src/signal_triage.py data/source_signals/sample_public_signals.json
python3 src/ingest_arxiv.py --config data/config/arxiv_queries.json --max-results 2
python3 src/ingest_aiid.py --lookup-urls data/incidents/sample_aiid_lookup_urls.json
python3 src/ingest_mit_tracker.py
X_BEARER_TOKEN=... python3 src/ingest_x.py --query-config data/config/x_queries.json --max-results 10
python3 src/ingest_manual_social.py data/manual/social_capture_template.json
python3 src/merge_signals.py data/source_signals/sample_public_signals.json data/source_signals/sample_public_signals.json
python3 -m unittest tests/test_signal_triage.py
```

## Output

The triage script produces:

- Taxonomy candidates.
- Probe backlog items.
- Source-tier counts.
- Signals requiring human review.
- Signals whose raw details should not be reproduced.

These backlog items can feed `studies/anima-risk-sentinel/` as synthetic traces, red-team probes, or model-evaluation tasks.
