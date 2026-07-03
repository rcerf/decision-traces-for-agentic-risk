# Source Notes

This artifact is grounded in public sources and synthetic examples.

## OpenAI Preparedness Framework

Relevant concepts:

- Tracked risk categories.
- Threat models.
- Capability evaluations.
- Safeguards before deployment for high-risk capabilities.
- Research categories for emerging risks.
- Attention to risks that may not yet have realized precedents.

Source: https://cdn.openai.com/pdf/18a02b5d-6b67-4cec-ab64-68cdfbddebcd/preparedness-framework-v2.pdf

## OpenAI Computer-Using Agent And Operator System Card

Relevant concepts:

- User confirmations before external side effects.
- Active supervision on sensitive sites.
- Prompt-injection defenses.
- Monitoring and detection/human-review pipelines.
- Ongoing adaptation because adversarial threats change.

Sources:

- https://openai.com/index/computer-using-agent/
- https://openai.com/index/operator-system-card/

## OWASP Prompt Injection Guidance

Relevant concepts:

- Direct and indirect prompt injection.
- External content as an injection vector.
- Unauthorized data access or tool/API actions.
- Need for layered controls because prompt injection is not fully solved by system prompts alone.

Sources:

- https://genai.owasp.org/llmrisk/llm01-prompt-injection/
- https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html

## Sovereign OS Design Inspiration

Private repo patterns translated into this public synthetic artifact:

- Sandboxed reader for untrusted content.
- Prompt-injection pattern detection.
- Tool-call schema validation.
- Human approval states.
- Trust tiers and action tiers.
- Override and residual-risk tracking.

No private logs, personal data, proprietary Meta details, or patent-sensitive implementation details are included here.
