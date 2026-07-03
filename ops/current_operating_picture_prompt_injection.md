# Current Operating Picture: Prompt Injection In Connector-Based Agents

## Scope

This memo is a synthetic example of how weak signals about prompt injection in connector-based agents can be translated into decisions, owners, mitigations, residual gaps, and next review points.

## Key Judgments

1. Indirect prompt injection is the highest-priority current risk for agents that read untrusted content and can take external side effects.
2. The riskiest surfaces are not only browsers. Email, docs, ticketing tools, support systems, internal wikis, and retrieved documents can all carry untrusted instructions.
3. Human approval gates reduce risk, but only if the system can identify when an action is externally consequential or crosses a connector/data boundary.
4. The next useful operating metric is not just model refusal rate. It is the share of high/critical traces with named owner, deployed mitigation, human approval gate, and next review date.

## Assumptions

- The agent can read untrusted content.
- The agent can call tools or connectors.
- Some actions have external side effects.
- The model may see attacker-controlled text inside web pages, documents, emails, tickets, or retrieved content.

## Competing Hypotheses

- H1: Most risk comes from model susceptibility to malicious instructions.
- H2: Most risk comes from product design that grants excessive tool authority without clear approval boundaries.
- H3: Most risk comes from missing detection/monitoring and weak operational feedback loops after launch.

The working position is that all three matter, but H2 and H3 are often easier to mitigate operationally than fully solving H1.

## Indicators To Watch

- High/critical traces without human approval gates.
- Connector actions that combine sensitive read access with external write access.
- Repeated prompt-injection patterns in untrusted content.
- User approvals that appear uninformed or generic.
- Mitigations stuck in "proposed" without an owner.
- Increasing false negatives in injection monitors.

## Owner Matrix

| Risk Area | Primary Owner | Partner Owners | Minimum Control |
|---|---|---|---|
| Prompt injection | Product Safety / Abuse Detection | Security, Product, Evals | Untrusted-content isolation plus monitor |
| Connector boundary | Product / Platform | Privacy, Security | Data-boundary policy and explicit approval |
| External side effect | Product | Legal, Safety, UX | Human confirmation before final action |
| Memory contamination | Model Behavior / Product | Evals, Privacy | Memory write review and retrieval provenance |
| Social engineering | Trust & Safety | Policy, Investigations | Scenario evals and abuse taxonomy |

## Recommended Actions

1. Convert each weak signal into a structured trace.
2. Review high/critical traces weekly until mitigation status is deployed or risk is accepted.
3. Add a validation check: high/critical traces must have a human approval gate unless explicitly waived.
4. Create eval cases from repeated trace patterns.
5. Track closure metrics: owner named, mitigation deployed, decision latency, residual risk, next review date.

## Residual Gaps

- The taxonomy does not yet cover all cyber-adjacent abuse patterns.
- Synthetic traces need to be compared against real incidents or red-team findings.
- The current validation script only checks structural gaps, not model behavior.

## Next Review

Review after the six synthetic traces are expanded with either real sanitized traces or additional red-team probes.
