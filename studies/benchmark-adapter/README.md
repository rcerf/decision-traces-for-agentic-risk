# Benchmark-to-Trace Adapter (AgentDojo)

Status: working adapter with public-safe fixtures and tests.

This module closes the open item named in `examples/ART-007-...json` under
`recommended_action`: *"Add a benchmark-to-trace adapter that converts public
indirect-injection fixtures into safe decision traces."* It takes real
[AgentDojo](https://github.com/ethz-spylab/agentdojo) run records and emits
decision traces that validate against `schema/agentic_risk_trace.schema.json`.

## Why this matters

The rest of this repo argues that agentic risk should be tracked as a corpus of
structured traces, not free-text notes. This adapter shows that the trace format
can ingest a real public benchmark's output rather than only hand-authored
examples — the difference between "here is a schema I made up" and "here is a
schema that accepts existing eval data."

## Safety design

- The adapter reads **only structural fields** from each run: suite, task ids,
  attack family, `utility`, `security`, duration, turn count. It never reads or
  copies message content, so **no raw injection text enters the trace corpus**.
  `tests/test_adapter.py::test_no_raw_message_content_leaks` enforces this.
- The bundled fixtures under `data/agentdojo_runs/` are themselves sanitized:
  they are the structural fields only, extracted from AgentDojo's public
  `runs/claude-3-5-sonnet-20241022/workspace/...` records, with all message
  bodies removed.

## Mapping (AgentDojo semantics -> trace)

AgentDojo labels each run with `utility` (was the benign task completed?) and
`security` (did the attack **fail**?). So `security == false` means the
injection **succeeded**.

| Run condition | Severity | Approval gate | mitigation_status |
|---|---|---|---|
| attack present, `security=false` (injection succeeded) | high | `before_external_side_effect` | needs_review |
| attack present, `security=true` (attack defended) | low | none (kept as benign control) | in_progress |
| no injection task (benign baseline) | — skipped, not a risk trace | — | — |

Severity is derived deterministically; there is no hidden scoring.

## Run it

```bash
# Print traces to stdout
python3 studies/benchmark-adapter/src/agentdojo_to_trace.py \
    studies/benchmark-adapter/data/agentdojo_runs --start-index 8

# Write one ART-NNN-agentdojo.json per trace
python3 studies/benchmark-adapter/src/agentdojo_to_trace.py \
    studies/benchmark-adapter/data/agentdojo_runs --start-index 8 \
    --out-dir studies/benchmark-adapter/output

# Validate the generated traces with the repo's own validator
python3 demo/validate_traces.py studies/benchmark-adapter/output

# Tests
python3 -m unittest discover -s studies/benchmark-adapter/tests
```

`output/ART-008..ART-010-agentdojo.json` are committed examples: ART-008 and
ART-009 are successful-injection runs (high severity, external-side-effect
approval gate); ART-010 is a defended run (low severity, no gate, kept as a
benign control). Both branches are shown so a reviewer does not have to run the
code to see that the defended case works.

## What this does and does not show

- **Does:** the trace schema accepts real benchmark output; the lifecycle-stage
  and trust-boundary framing survives contact with an external eval; the
  converted traces pass the same validator as the hand-authored ones.
- **Does not:** measure the benchmark, add new attacks, or claim any detection
  performance. It is a format adapter, not an evaluation.

## To extend to more runs

AgentDojo publishes runs per model under `runs/<model>/<suite>/<user_task>/<attack>/`.
To convert more, sanitize additional runs into `data/agentdojo_runs/` keeping only
the structural fields (`suite_name`, `pipeline_name`, `user_task_id`,
`injection_task_id`, `attack_type`, `utility`, `security`, `error`, `duration`),
then re-run the adapter. Do not commit files that contain message bodies.
