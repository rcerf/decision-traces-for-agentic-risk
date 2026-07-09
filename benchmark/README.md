# Injection Sentinel Benchmark

This directory contains a **fully reproducible** benchmark of the repo's deterministic
injection detector against a public labeled dataset.

## Why this exists

`docs/portfolio/injection_sentinel_benchmark_results.md` references benchmark numbers
(e.g., deepset ~95% recall / ~69.6% FPR) that were produced by a **private pipeline**
not present in this repository.  A top reviewer critique is that those numbers are
unverifiable from the public code.

This benchmark is the verifiable counterpart: it runs the **public detector**
(`studies/anima-risk-sentinel/src/risk_sentinel.py`) against the **public dataset**
(`deepset/prompt-injections`, N=662) and reports honest results.

## The numbers ARE reproducible

```bash
pip install datasets
python benchmark/fetch_data.py         # download + snapshot
python benchmark/run_injection_benchmark.py   # compute metrics + write RESULTS.md
```

Both scripts are deterministic.  The labeled snapshot
(`benchmark/data/deepset_prompt_injections.jsonl`) is committed, so the benchmark
script can run offline without re-downloading.

## See also

- `benchmark/RESULTS.md` — the reproduced numbers, methodology, and limitations
- `benchmark/fetch_data.py` — downloads and snapshots the dataset
- `benchmark/run_injection_benchmark.py` — loads snapshot, runs detector, writes RESULTS.md
