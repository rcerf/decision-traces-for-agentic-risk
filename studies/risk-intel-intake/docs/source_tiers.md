# Source Tiers

The intake layer deliberately separates signal creativity from signal reliability.

## Tier 0: Authoritative Frameworks And Standards

Examples:

- OWASP Top 10 for LLM Applications.
- MITRE ATLAS.
- NIST AI RMF and Generative AI Profile.
- OpenAI, Anthropic, Google, Meta, and other system cards or safety documentation.

Use for:

- Stable taxonomy terms.
- Control language.
- Governance framing.
- Mitigation patterns.

Do not use for:

- Fast discovery of new exploit motifs.

## Tier 1: Research, Benchmarks, And Datasets

Examples:

- arXiv papers.
- Peer-reviewed papers.
- Benchmark repos such as BIPIA or InjecAgent.
- Guardrail evaluations.
- Public datasets with labels.

Use for:

- Evaluation design.
- Probe construction.
- Baseline comparisons.
- Failure-mode definitions.

Do not use without review when:

- The source contains harmful prompt strings or exploit instructions.
- The dataset licenses or safety norms restrict redistribution.

## Tier 2: Incident Databases, Journalism, And Policy Sources

Examples:

- AI Incident Database.
- MIT AI Incident Tracker.
- Reporting by credible journalists.
- Regulator, legislative, or public-hearing materials.
- Policy papers and civil-society reports.

Use for:

- Real-world harm mapping.
- Stakeholder impact.
- Public salience.
- Trend discovery.

Do not use for:

- Direct technical exploit details unless corroborated by research or technical reports.

## Tier 3: Social Media, Forums, And Community Reports

Examples:

- X.
- Bluesky.
- Mastodon.
- Reddit.
- Hacker News.
- Discord/Slack communities if accessible and permitted.
- GitHub issues.

Use for:

- Early weak signals.
- Creative adversarial motifs.
- User-discovered edge cases.
- Candidate taxonomy gaps.

Handle carefully:

- Capture abstractions, not copy-paste jailbreak recipes.
- Preserve source URL and timestamp.
- Mark evidence as unverified until reproduced safely.
- Route high-risk exploit details to human review.
