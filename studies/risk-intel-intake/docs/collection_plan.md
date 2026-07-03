# Collection Plan

This layer should collect weak signals without turning the repo into an exploit cookbook.

## Intake Loop

1. Monitor source streams.
2. Capture a safe summary of the observed risk pattern.
3. Assign source tier, evidence status, affected surfaces, and candidate risk categories.
4. Decide whether raw details are safe to store.
5. Convert the signal into one or more safe probes.
6. Run probes in a sandboxed study harness.
7. Promote confirmed patterns into taxonomy, eval cases, and sentinel rules.

See `adapter_workflow.md` for the current runnable adapters.

## Candidate Streams

### Research

- arXiv searches for agentic risk, prompt injection, jailbreaking, guardrails, function-call safety, and AI incident taxonomies.
- OpenReview and conference proceedings.
- Benchmark repos and datasets.
- Safety system cards and preparedness documents.

### Security And Standards

- OWASP GenAI Security Project.
- MITRE ATLAS.
- NIST AI RMF and Generative AI Profile.
- Vendor security blogs with technical detail.

### Incidents And Journalism

- AI Incident Database.
- MIT AI Incident Tracker.
- Credible technology and policy journalism.
- Regulator statements, legislative hearings, and policy reports.

### Social And Community

- X lists for jailbreak researchers, AI security researchers, eval builders, and product-safety observers.
- Hacker News, Reddit, GitHub issues, and public Discord/Slack communities when access and reuse are appropriate.
- Community reports of model failures, jailbreak motifs, and tool-use failures.

## Safety Handling

Do:

- Store safe abstractions.
- Store URLs and metadata.
- Store risk hypothesis, affected surfaces, and proposed probe.
- Mark exploit details as `do_not_reproduce` when appropriate.

Do not:

- Store complete harmful jailbreak prompts when not necessary.
- Publish exploit strings that lower the barrier to misuse.
- Run probes against real accounts, real people, production systems, or third-party services.
- Confuse virality with validity.

## Promotion Criteria

A weak signal can become a probe when it has:

- Clear affected surface.
- Plausible harm path.
- Safe reproduction plan.
- Expected detector stage.
- Observable success/failure criteria.

A probe can become a taxonomy update when:

- It reproduces across more than one fixture, model, or agent setup.
- It maps to a source/failure/harm dimension.
- It suggests a reusable mitigation or approval rule.
