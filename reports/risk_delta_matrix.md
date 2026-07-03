# Risk Delta Matrix

Status: generated negative-space risk discovery output

This report identifies capability/risk cells worth probing. It does not claim the risks are real-world prevalent or unknown to any specific team.

| Capability Delta | Risk Class | Score | Status | Shared Surfaces | Safe Probe |
|---|---|---:|---|---|---|
| Agent-on-agent adversarial probing | Agent-on-agent exploit discovery | 25 | probe_now | adversarial_probe, governance, multi_agent, telemetry | Create a synthetic fixture for Agent-on-agent adversarial probing x Agent-on-agent exploit discovery covering adversarial_probe, governance, multi_agent, telemetry; avoid raw exploit content and score first useful intervention point. |
| Tool-rich workspace agents | Approval quality failure | 18 | probe_now | connector, tool_calling, workflow_automation | Create a synthetic fixture for Tool-rich workspace agents x Approval quality failure covering connector, tool_calling, workflow_automation; avoid raw exploit content and score first useful intervention point. |
| Agent-on-agent adversarial probing | Telemetry privacy failure | 16 | probe_now | governance, telemetry | Create a synthetic fixture for Agent-on-agent adversarial probing x Telemetry privacy failure covering governance, telemetry; avoid raw exploit content and score first useful intervention point. |
| Local risk monitoring | Telemetry privacy failure | 16 | probe_now | endpoint, telemetry | Create a synthetic fixture for Local risk monitoring x Telemetry privacy failure covering endpoint, telemetry; avoid raw exploit content and score first useful intervention point. |
| Open-weight model release | Open-weight irreversibility | 16 | probe_now | governance, model_release | Create a synthetic fixture for Open-weight model release x Open-weight irreversibility covering governance, model_release; avoid raw exploit content and score first useful intervention point. |
| Tool-rich workspace agents | Indirect prompt injection | 15 | probe_now | connector, tool_calling | Create a synthetic fixture for Tool-rich workspace agents x Indirect prompt injection covering connector, tool_calling; avoid raw exploit content and score first useful intervention point. |
| Local risk monitoring | Agent-on-agent exploit discovery | 13 | probe_now | telemetry | Create a synthetic fixture for Local risk monitoring x Agent-on-agent exploit discovery covering telemetry; avoid raw exploit content and score first useful intervention point. |
| Open-weight model release | Agent-on-agent exploit discovery | 13 | probe_now | governance | Create a synthetic fixture for Open-weight model release x Agent-on-agent exploit discovery covering governance; avoid raw exploit content and score first useful intervention point. |
| Persistent memory | Memory integrity failure | 13 | probe_now | memory, retrieval | Create a synthetic fixture for Persistent memory x Memory integrity failure covering memory, retrieval; avoid raw exploit content and score first useful intervention point. |
| Agent-on-agent adversarial probing | Open-weight irreversibility | 12 | watchlist | governance | Create a synthetic fixture for Agent-on-agent adversarial probing x Open-weight irreversibility covering governance; avoid raw exploit content and score first useful intervention point. |
| Open-weight model release | Telemetry privacy failure | 12 | watchlist | governance | Create a synthetic fixture for Open-weight model release x Telemetry privacy failure covering governance; avoid raw exploit content and score first useful intervention point. |
| Persistent memory | Indirect prompt injection | 11 | watchlist | retrieval | Create a synthetic fixture for Persistent memory x Indirect prompt injection covering retrieval; avoid raw exploit content and score first useful intervention point. |

## Next Action

Promote `probe_now` cells into safe synthetic runs, then convert findings into structured agentic risk traces.
