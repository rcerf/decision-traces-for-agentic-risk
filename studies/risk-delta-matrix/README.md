# Risk Delta Matrix

Status: negative-space risk discovery prototype

This module pursues the first build suggested by the negative-space research direction in `studies/model-risk-sota/working_paper_outline_negative_space_risk_discovery.md`.

The idea is simple: new capabilities create new risk cells. Some cells are already evidenced by papers, incidents, benchmarks, or product reports. Other cells are structurally implied but not yet well-evidenced. Those empty cells become safe probe candidates.

This is especially important for agent-on-agent risk. If autonomous systems can probe each other, transfer exploit ideas, or discover workflow weaknesses faster than humans can manually review them, the useful artifact is not a static list of risks. It is a living matrix that turns capability deltas into safe probes, patch objects, and residual monitors.

## Run

```bash
python3 studies/risk-delta-matrix/src/generate_matrix.py --output reports/risk_delta_matrix.md
```

## Output

- `reports/risk_delta_matrix.md`

## Interpretation

This does not claim a risk is real or prevalent. It says: given a capability delta and a known risk family, this cell is plausible enough to test safely.
