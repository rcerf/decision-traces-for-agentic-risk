# Patch Loop Case

Status: synthetic public-safe case study  
Purpose: show the living-system loop from signal to patch candidate.

This study creates one compact case for the agent-on-agent frontier:

```text
safe signal summary
  -> risk-delta cell
  -> safe probe
  -> observable run summary
  -> sentinel event
  -> decision trace summary
  -> patch object
  -> residual monitor
```

It does not include raw jailbreak text, exploit recipes, private telemetry, or production claims. The case is meant to demonstrate the operating cadence: preserve the signal, test it safely, decide what should be patched, and define how to tell whether the patch holds.

## Run

```bash
python3 studies/patch-loop-case/src/render_patch_loop.py --output reports/agent_on_agent_patch_loop_case.md
python3 -m unittest discover -s studies/patch-loop-case/tests
```

## Output

- `reports/agent_on_agent_patch_loop_case.md`

