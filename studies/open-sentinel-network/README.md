# Opt-In Signal-Sharing Concept

Status: synthetic public-safe prototype  
Purpose: model an opt-in, open-source local signal-sharing concept for agentic-risk discovery.

The idea combines three patterns:

- local detection and patch distribution inspired by antivirus systems;
- Folding@Home-style voluntary participation in a shared safety network;
- beta-user-style self-selection into early monitoring and patch preview.

The local monitor must be inspectable. Users should be able to see the local rules, local classifiers, outbound telemetry schema, and patch manifests. By default, raw prompts, raw outputs, files, tool arguments, and private data do not leave the machine.

## Sovereign OS Routing-Gate Transfer

This study adapts my prior Sovereign OS routing-gate pattern:

```text
cheap local uncertainty signal
  -> route locally when confident
  -> escalate when uncertainty rises
  -> preserve only compact structured telemetry
```

In Sovereign OS, routing gates route computation across local and stronger models. Here, uncertainty gates are modeled as a hypothesis for routing risk events across aggregate watch, agentic review, patch candidate, and privacy exception.

## Run

```bash
python3 studies/open-sentinel-network/src/network_triage.py --output reports/open_sentinel_network_assessment.md
python3 -m unittest discover -s studies/open-sentinel-network/tests
```

## Output

- `reports/open_sentinel_network_assessment.md`
