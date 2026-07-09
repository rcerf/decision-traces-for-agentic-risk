# Real Incident Traces

This directory contains decision traces based on real, publicly-documented agentic AI incidents. These complement the synthetic examples in `../` by proving the trace format generalizes to material the author did not invent.

---

## ART-R01 — Slack AI Indirect Prompt Injection (August 2024)

**File:** `ART-R01-slack-ai-prompt-injection.json` (internal trace_id: `ART-R01`)

### Incident

In August 2024, security researchers at PromptArmor disclosed a live vulnerability in Slack AI — Salesforce's LLM-powered workspace assistant. An attacker with access to any public Slack workspace channel could plant adversarial instructions in that channel. When a legitimate user later queried Slack AI (e.g., "What API key did the dev team share?"), Slack AI's RAG-style retrieval ingested the poisoned content alongside private-channel context in the same prompt window. The model then followed the injected instructions, rendering fabricated Markdown links that exfiltrated private-channel content (including API keys) as URL query parameters to an attacker-controlled server.

### Primary Sources

| Role | URL | Date |
|------|-----|------|
| Primary disclosure | https://promptarmor.substack.com/p/data-exfiltration-from-slack-ai-via | 2024-08-19 |
| Secondary analysis | https://simonwillison.net/2024/Aug/20/data-exfiltration-from-slack-ai/ | 2024-08-20 |
| News coverage | https://www.theregister.com/2024/08/21/slack_ai_prompt_injection/ | 2024-08-21 |
| Incident registry | https://oecd.ai/en/incidents/2024-08-19-ef40 | 2024-08-19 |

### Why This Is Public-Safe

- The trace describes the attack class and mechanism, not a working exploit string.
- No private individual is named; the researcher (PromptArmor) published voluntarily.
- No reproduction payload or attacker-controlled URL is included.
- All facts are drawn from published security disclosures and news coverage.

### What Is Known vs. Genuinely Open

**Known from public record:**
- Attack mechanism: indirect prompt injection via RAG retrieval mixing untrusted public-channel content with private-channel data in a single context window.
- Exfiltration channel: Markdown link rendering in AI-generated output.
- Vendor response: Slack initially declined to classify as a vulnerability; after public disclosure stated a patch was deployed.
- Researcher: PromptArmor; disclosure date: 2024-08-19.
- No CVE or CVSS was assigned.

**Genuinely unresolved (preserved in `open_questions`):**
1. Whether any real-world exploitation occurred before or after disclosure — Slack's "no evidence" statement was not independently verified.
2. What the patch actually changed — Slack confirmed a fix but published no technical detail of the remediation.
3. Whether the same vector applies in Slack Connect (cross-organization) deployments.
4. The systematic blast radius when third-party file connectors (Google Drive, Dropbox) are active.
5. Whether Enterprise Key Management (EKM) provides any runtime isolation against this attack.

### How This Differs from the Synthetic Examples

The synthetic examples (`ART-001` through `ART-007`) demonstrate the trace format on author-constructed scenarios. This trace is grounded in:

- **External signal** — the vulnerability was discovered by independent researchers, not constructed for the repo.
- **Real vendor response data** — Slack's initial dismissal and subsequent patch are documented facts, not hypothetical framings.
- **Genuinely unresolved questions** — the open questions above cannot be answered from public sources; they are structurally open, not pre-resolved gaps dressed up as questions.
- **No CVE** — the absence of formal vulnerability classification is itself a finding worth preserving in the trace, as it illustrates how vendor disagreement about severity creates governance gaps.

The trace uses `mitigation_status: "needs_review"` rather than `"deployed"` because the patch's scope is unknown, meaning the residual risk cannot be confidently assessed from public information alone.
