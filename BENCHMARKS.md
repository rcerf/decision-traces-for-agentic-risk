# Benchmarks

All numbers below are copied from existing generated result files in this repo.
No raw payloads are included.

| Area | Source | Dataset / sample | Headline numbers |
|---|---|---|---|
| Content detector: regex sentinel | [benchmark](benchmark/) | `deepset/prompt-injections`, N=662 | Recall 0.8% (TP=2, FN=261), precision 100.0%, FPR 0.0%, F1 1.5%; keyword baseline recall 0.0%. |
| Behavioral detonation: provenance-only mode | [studies/detonation-harness](studies/detonation-harness/) | 14 scenarios: 7 injection, 4 benign, 3 ambiguous | Injection catch 4/7; benign FP 0/4; TP=4 FP=0 TN=4 FN=3; precision=1.00 recall=0.57 F1=0.73. |
| Behavioral detonation: precise mode | [studies/detonation-harness](studies/detonation-harness/) | Same 14-scenario harness | Injection catch 4/7; benign FP 0/4; TP=4 FP=0 TN=4 FN=3; precision=1.00 recall=0.57 F1=0.73. |
| Corpus detonation: provenance-only vs precise | [studies/injection-corpus-detonation](studies/injection-corpus-detonation/) | InjecAgent base splits, N=150, seed=42 | Tool engagement 63.3% (95/150); attack success 9.3% (14/150); provenance-only catch on successful attacks 100.0% (14/14); precise catch 35.7% (5/14); naive detector catch 0.0% (0/14). |
| Corpus detonation: attack success by goal | [studies/injection-corpus-detonation](studies/injection-corpus-detonation/) | InjecAgent base splits, 75 data-stealing + 75 direct-harm | Data-stealing attack success 14.7% (11/75); direct-harm attack success 4.0% (3/75). |
| Ontology negative space | [studies/injection-ontology](studies/injection-ontology/) | Combined public corpora, N=1508 unique items | No public data: injection type 2/3 cells (67%), delivery vector 8/10 (80%), technique 9/14 (64%), goal 5/9 (56%). UNKNOWN technique: 372 (24.7%). |
| Model capability scaling | [studies/injection-corpus-detonation](studies/injection-corpus-detonation/) | Local Qwen capability rows over InjecAgent subsets | 1.5B: tool engagement 63.3%, attack success 9.3% (n=14), provenance-only 100.0% (14/14), precise 35.7% (5/14). 3B: tool engagement 66.7%, attack success 5.0% (n=3), provenance-only 100.0% (3/3), precise 100.0% (3/3). 7B: tool engagement 55.0%, attack success 25.0% (n=5), provenance-only 100.0% (5/5), precise 100.0% (5/5). |
