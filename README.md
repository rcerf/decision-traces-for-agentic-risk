# Decision Traces for Agentic Risk

This is a compact, public-safe prototype for agentic risk analysis.

The point of the repo is not to claim that I solved agentic risk. I have not. The point is to make an operating model inspectable: how weak signals can become safe probes, how probe outcomes can become structured decision traces, and how repeated traces can become a taxonomy that points to owners, mitigations, approval gates, residual risk, and gaps worth investigating.

This README is the primary artifact. A reader should be able to scroll this page and understand the idea without opening a dozen files. The supporting files are included for verification, examples, and deeper inspection.

This repo uses synthetic examples only. It does not contain private Meta, JUUL, OpenAI, or personal data.

## Table Of Contents

- [Bottom Line](#bottom-line)
- [Reviewer Start Here](#reviewer-start-here)
- [What This Is And Is Not](#what-this-is-and-is-not)
- [Thought Traces, Not Claims](#thought-traces-not-claims)
- [The Working Hypothesis](#the-working-hypothesis)
- [Why Agentic Risk Needs A Living Operating Picture](#why-agentic-risk-needs-a-living-operating-picture)
- [The Operating Loop](#the-operating-loop)
- [Decision Traces](#decision-traces)
- [Lifecycle Monitoring](#lifecycle-monitoring)
- [Negative-Space Risk Discovery](#negative-space-risk-discovery)
- [Sample Current-Risk Brief](#sample-current-risk-brief)
- [Signal Sharing And Patch-Loop Analogy](#signal-sharing-and-patch-loop-analogy)
- [Controlled Pre-Release Probe Lab](#controlled-pre-release-probe-lab)
- [How The Prototype Is Structured](#how-the-prototype-is-structured)
- [What This Demonstrates](#what-this-demonstrates)
- [What This Does Not Prove](#what-this-does-not-prove)
- [Next Evaluation Questions](#next-evaluation-questions)
- [Author Context](#author-context)
- [Evidence Appendix](#evidence-appendix)
- [How To Run The Prototype](#how-to-run-the-prototype)
- [Public Source Anchors](#public-source-anchors)
- [Repository Map](#repository-map)

## Bottom Line

Agentic AI risk work should not stop at one-off incident review or final-output scanning. The risk often begins earlier: in the prompt, retrieved content, connector context, memory, tool permissions, planning steps, approval state, or downstream action.

The operating question is:

> How do we keep a current picture of emerging risk, turn credible signals into safe tests, assign ownership, ship mitigations, and keep checking whether the residual risk changed?

This prototype sketches one answer:

```text
weak signal
  -> safe risk hypothesis
  -> safe probe
  -> observable run
  -> structured decision trace
  -> owner, mitigation, approval gate, residual risk
  -> patch or monitor
  -> next review
```

The intended reaction is modest:

> This is an interesting way to organize the work. It is concrete enough to inspect, humble enough not to overclaim, and relevant enough to discuss.

## Reviewer Start Here

If you only have a few minutes, read this README and skim these anchors:

| Question | Where To Look |
|---|---|
| What is the idea? | `docs/portfolio/three_minute_brief.md` |
| How would a hiring manager inspect it? | `docs/portfolio/hiring_manager_tour.md` |
| What is the strongest synthetic analyst output? | `reports/sample_agentic_risk_brief.md` |
| What is the public-safe trace format? | `examples/ART-007-public-benchmark-indirect-injection.json` and `schema/agentic_risk_trace.schema.json` |
| How should I interpret the independent AI work? | `docs/portfolio/thought_traces_not_claims.md` |
| What evidence exists behind the independent model-observation work? | `docs/portfolio/model_observation_evidence_appendix.md` |
| What are the limits? | [What This Does Not Prove](#what-this-does-not-prove) |

The most important caveat: this is a portfolio prototype. It is meant to show how I reason, structure risk, preserve uncertainty, and turn weak signals into reviewable operating artifacts. It is not a production detector or a claim that I have solved agentic risk.

## What This Is And Is Not

This is:

- A working-hypothesis prototype for agentic risk analysis.
- A public-safe synthetic corpus of traces, probes, and staged sentinel checks.
- A demonstration of operating judgment: evidence, confidence, severity, owner, mitigation, approval gate, residual risk, and next review.
- A small runnable system that validates traces and shows how analyst reasoning could be made more legible.
- A portfolio artifact showing how I think about current-risk intelligence and product-risk operations.

This is not:

- A production detector.
- A benchmark.
- A claim of measured real-world prevalence.
- A claim of novel academic research.
- A replacement for internal telemetry, evals, red teaming, policy review, or human investigation.
- A repository of raw jailbreak prompts or exploit recipes.
- A claim that a small model, regex layer, or volunteer network can solve agentic risk.

The claim is narrower:

> Agentic risk analysis benefits from a living operating loop that turns signals into safe probes, probes into traces, traces into taxonomies, and taxonomies into mitigation decisions.

## Thought Traces, Not Claims

The repo is also meant to show how I think. Some of the underlying Sovereign OS work is exploratory, private, or unfinished, so I do not present it here as academic proof, a production safety system, or a claim of novelty. I use it as thought trace evidence: how I move from messy signals to structure, how I separate hypotheses from measurements, how I preserve residual uncertainty, and how I back away from ideas when the evidence is marginal or negative.

The short version is in `docs/portfolio/thought_traces_not_claims.md`.

## The Working Hypothesis

Provisional title:

> Negative-Space Risk Discovery for Agentic Systems: Turning Weak Signals Into Safe Probes, Decision Traces, and Patch Loops

One-sentence thesis:

> Agentic AI risk analysis should be treated as a living intelligence and operating system: weak signals become safe probes, probes become structured traces, repeated traces become a taxonomy, and gaps in the taxonomy become prompts for proactive investigation.

Agentic systems create risk across a lifecycle rather than only at final output. Risk can enter through prompts, retrieved content, memory, connectors, tool permissions, planning steps, approval states, and downstream actions. As models become more capable and agentic products become more widely deployed, risk discovery will increasingly depend on connecting heterogeneous signals: public jailbreaks, incident reports, eval failures, product changes, red-team findings, research papers, policy concerns, and agent-on-agent probes.

This prototype proposes a practical operating model for current-risk intelligence:

1. Public and internal signals are translated into safe hypotheses.
2. Hypotheses become safe probes.
3. Probe outcomes become structured decision traces.
4. Traces are organized into a risk taxonomy.
5. The taxonomy is used to identify missing controls, unresolved owners, mitigation gaps, residual risks, and empty cells that may deserve investigation before they appear as incidents.

The contribution is not a claim of solved safety or a new production detector. It is a legible framework for organizing agentic risk work so analysts can move from reactive review toward proactive discovery and faster mitigation loops.

## Why Agentic Risk Needs A Living Operating Picture

Static taxonomies are necessary, but insufficient. The field will keep moving:

- New frontier models will change capability boundaries.
- New product surfaces will add tool, connector, memory, and delegation paths.
- Users, researchers, journalists, policymakers, and adversaries will expose new weak signals.
- Agent-on-agent probing may discover and transfer risk motifs faster than human review cycles.
- Defenders will need to ship controls fast enough to reduce exposure before risky behavior scales.

That means the core artifact for an agentic risk team is not only a policy, model card, eval report, or incident postmortem. It is a current operating picture:

- What signals have we seen?
- Which are credible?
- Which risk surfaces do they implicate?
- Which controls already exist?
- Which owners are responsible?
- Which mitigations are deployed, proposed, or missing?
- Which residual risks remain?
- Which gaps in the taxonomy suggest risks we have not yet observed?
- When should the issue be reviewed again?

This framing comes from practical product-risk operations. At Meta, my strongest work was not only interpreting individual product-risk questions. It was turning repeated ambiguous judgments into a legible corpus: facts, rationale, mitigations, owners, unresolved risk, escalation triggers, and review dates. Once the corpus exists, the work can move from reactive case handling toward pattern recognition, reusable precedent, and proactive gap-finding.

This repo applies that same operating pattern to agentic AI.

## The Operating Loop

The prototype is organized around a loop:

```text
signal sensors
  -> signal/noise triage
  -> risk ontology and delta matrix
  -> safe probe generation
  -> staged monitoring over observable runs
  -> decision trace
  -> patch object
  -> shipped control
  -> residual-risk monitor
```

### 1. Signal Sensors

The system should ingest multiple signal classes without treating every source as equally reliable:

- research papers and benchmark updates;
- incident databases and public postmortems;
- system cards, framework updates, and standards;
- journalism, policy concerns, and regulator focus areas;
- curated social/X weak signals reviewed before ingestion;
- local risk-monitor events with aggregate-only telemetry;
- red-team and eval findings;
- safe agent-on-agent probe summaries;
- opt-in local sentinel concepts that would need separate privacy, security, and utility validation before any real deployment.

The important discipline is safe abstraction. Raw exploit details should not become the corpus. The corpus should preserve risk class, surface, authority, precondition, control gap, and proposed safe probe.

### 2. Triage

Each incoming signal should be scored for:

- source credibility;
- novelty;
- affected surface;
- attacker capability required;
- blast radius;
- reversibility;
- detection latency;
- safe-probe feasibility;
- likely owner;
- whether the signal fills an empty cell in the risk matrix.

This keeps the system from confusing volume with importance.

### 3. Safe Probes

The probe should preserve the risk structure without preserving or reproducing harmful detail.

For example, instead of storing a raw prompt-injection string, the safe abstraction might be:

> External content contains instruction-like text. Test whether an agent treats untrusted retrieved content as evidence or as an instruction.

That abstraction is enough to create benign fixtures, monitor the model trajectory, and identify the first useful intervention point.

### 4. Decision Traces

The trace is the core record. It captures:

- what happened;
- why it matters;
- what evidence exists;
- what is uncertain;
- how severe the risk appears;
- how confident the analyst is;
- which competing hypotheses remain;
- who owns the mitigation;
- what approval gate is required;
- what residual risk remains;
- when the issue should be reviewed again.

The trace is meant to make analyst judgment legible and reusable.

### 5. Patch Objects

A patch is any reviewable artifact that reduces risk or improves visibility. It may be:

- a transparent local signature;
- a small-model classifier update;
- a new eval or benchmark fixture;
- a product mitigation;
- an approval UX change;
- a tool-permission constraint;
- a connector boundary;
- a policy clarification;
- a model-behavior fix;
- a monitoring trigger that reopens the risk if behavior regresses.

The point is not to make every problem look like software antivirus. The point is to shorten the loop from credible risk signal to tested mitigation.

## Decision Traces

A decision trace is a structured risk record, not just a note. It is designed to preserve the reasoning needed for review, escalation, and reuse.

The synthetic trace schema includes fields for:

- trace ID;
- risk category;
- severity;
- confidence;
- evidence;
- open questions;
- competing hypotheses;
- affected surfaces;
- mitigation status;
- owner;
- approval gate;
- residual risk;
- next review date.

The repository includes seven synthetic traces:

| Trace | Risk Category | Severity |
|---|---|---|
| ART-001 | Prompt injection | High |
| ART-002 | Connector data boundary | High |
| ART-003 | Tool overreach | High |
| ART-004 | Social engineering | High |
| ART-005 | Policy evasion | Medium |
| ART-006 | Memory/retrieval contamination | Medium |
| ART-007 | Public-benchmark-inspired indirect prompt injection | High |

The validator checks schema shape and flags high or critical traces that lack deployed mitigation. That is intentionally simple. It is not a judge model. It is a small demonstration of how structured risk work can become inspectable and enforceable.

## Lifecycle Monitoring

Final-output review is too late for many agentic risks.

By the time an answer is written, the model may already have:

- trusted untrusted retrieved content;
- planned an unsafe action;
- crossed a connector boundary;
- selected an unstable tool path;
- prepared to expose private data;
- skipped a human approval gate;
- stored contaminated memory;
- created a downstream obligation for another system or person.

This prototype therefore evaluates risk across four stages:

| Stage | What It Watches | Why It Matters |
|---|---|---|
| Ingress | Prompt, retrieved content, connector context, permissions | Many risks enter before the model plans or writes |
| Trajectory | Plans, tool calls, tool arguments, approvals, connector crossings | Agentic failures often show up as unsafe intermediate actions |
| Draft | Emerging answer, unsafe action proposals, sensitive content, confidence language | Some failures become visible before final response |
| Final | Completed response before it reaches the next consumer | Final review is still useful, but should not be the only control |

In the current synthetic ablation, final-only review detects 1 of 3 risky runs. Adding ingress and trajectory monitoring detects all 3 risky runs. This is not a production measurement; it is a demonstration of the operating point: the first useful intervention often happens before final output.

## Negative-Space Risk Discovery

The most interesting part of the framework is not only cataloging known risks. It is asking what the current taxonomy implies should be present but has not yet been seen.

Examples:

- If agents can use external tools and read untrusted content, where can instruction hierarchy fail?
- If agents can remember prior interactions, where can memory become contaminated or socially engineered?
- If agents can delegate work to other agents, where can agent-on-agent manipulation emerge?
- If models are patched against known attacks, what adjacent variants remain untested?
- If one risk class appears under one connector, which similar connector surfaces have not been probed?

The repo includes a generated risk-delta matrix. It does not claim that these risks are novel, prevalent, or unknown to any specific team. It identifies capability/risk cells worth safe probing.

Current top safe-probe candidates:

| Capability Delta | Risk Class | Status |
|---|---|---|
| Agent-on-agent adversarial probing | Agent-on-agent exploit discovery | Probe now |
| Tool-rich workspace agents | Approval quality failure | Probe now |
| Agent-on-agent adversarial probing | Telemetry privacy failure | Probe now |
| Local risk monitoring | Telemetry privacy failure | Probe now |
| Open-weight model release | Open-weight irreversibility | Probe now |
| Tool-rich workspace agents | Indirect prompt injection | Probe now |
| Persistent memory | Memory integrity failure | Probe now |

This is the move from reactive incident cataloging to proactive risk search.

## Sample Current-Risk Brief

The sample brief is meant to look like analyst output: concise judgments, current evidence, mitigation backlog, and next review.

Key judgments from the synthetic brief:

1. Final-output review is insufficient for agentic systems.
2. Indirect prompt injection and connector-boundary overreach are best caught before final response generation.
3. Human approval gates are central controls for high-impact or connector-crossing actions, but they need to avoid generic confirmation fatigue.
4. Public weak signals should feed a probe backlog, not be treated as validated evidence.
5. Agentic risk should be treated as a living operating picture.
6. A possible next-build concept is a controlled pre-release probe lab where adversarial discovery, defensive controls, and analyst adjudication are separated and measured safely.
7. A possible deployment concept is opt-in local signal sharing, where inspectable monitors contribute aggregate-only events after explicit privacy and security review.

Current synthetic evidence:

| Evidence Area | Current Prototype State |
|---|---|
| Trace corpus | 7 synthetic traces across prompt injection, connector boundaries, tool overreach, social engineering, policy evasion, memory/retrieval contamination, and public-benchmark-inspired indirect injection |
| Sentinel study | 4 observable runs, including 3 risky runs and 1 benign negative control |
| Risk-intelligence intake | 7 sample public signals across standards, research, incidents, journalism, policy, and social weak signals |
| Risk-delta matrix | Capability/risk cells ranked for safe probing |
| Opt-in signal-sharing concept | 4 synthetic volunteer nodes with aggregate-only events; concept only, not a deployed client |

Open mitigation backlog:

| Risk Area | Current Control | Gap | Next Action |
|---|---|---|---|
| Indirect prompt injection | Deterministic ingress patterns | No measured false-positive/false-negative rate | Add BIPIA-style safe fixtures and benign controls |
| Connector boundary crossing | Tool-call scope and approval checks | Connector intent is inferred crudely | Add explicit task-scope model and cross-connector policy |
| Function-call malfunction | Deterministic trajectory checks | No specialized judge model yet | Evaluate small judge or rubric-based classifier |
| Data leakage | Secret-like final-output regex | Limited secret patterns | Add draft-stage and tool-output provenance tests |
| Social weak signals | Manual review gate | Limited source credibility scoring | Add source profiles and corroboration tracking |
| Agent-on-agent probing | Safe-abstraction requirement | No runnable multi-agent probe harness yet | Explore a constrained simulator preserving risk class and first useful intervention point |
| Opt-in signal sharing | Aggregate-only synthetic events | No real opt-in client, privacy inspector, or signed patch channel | Treat as a future product concept requiring separate privacy, security, and utility review |

The decision in the sample brief is deliberately modest:

> Continue development as a portfolio-grade prototype. The current artifact is useful because it demonstrates the operating shape: weak signals become probes, probes become traces, traces become patch candidates, and patch candidates become reviewable operating decisions with residual monitoring.

## Signal Sharing And Patch-Loop Analogy

One product metaphor, used carefully, is signal sharing and patch-loop distribution.

The useful part of the analogy:

- local detection of known risky motifs;
- fast signature or policy updates;
- central aggregation of new weak signals;
- reviewable patch distribution;
- a feedback loop between user-side observations and central analysis.

The dangerous part of the analogy:

- surveillance;
- raw prompt or file exfiltration;
- opaque local monitors;
- overbroad flagging;
- privacy-invasive telemetry.

A possible future version is opt-in local signal sharing:

- users self-select into running an auditable local monitor;
- code, signatures, and outbound telemetry schema are inspectable;
- raw prompts, raw outputs, files, and tool arguments stay local by default;
- volunteers could opt into local challenge fixtures against their own workflows;
- the central service would receive aggregate events, hashed evidence fingerprints, uncertainty buckets, route decisions, and patch-version metadata;
- volunteers can receive early patch packs, signature updates, eval fixtures, and local mitigations.

The Sovereign OS connection is an uncertainty-gated routing hypothesis: cheap local uncertainty signals might help decide whether work stays local, routes to a stronger model, or goes to human review.

For agentic risk, that becomes:

```text
local event
  -> deterministic signature check
  -> uncertainty / margin / disagreement measurement
  -> local route decision
  -> aggregate-only telemetry
  -> central patch prioritization
```

The hypothesis to test is whether this can reduce unnecessary human review while preserving expert attention for privacy exceptions, high-blast-radius ambiguous cases, novel clusters, and patch decisions. That is a research/product question, not something this prototype proves.

## Controlled Pre-Release Probe Lab

The next risk frontier is not only human users discovering jailbreaks. It is automated systems probing other systems, chaining weaknesses, and transferring motifs across models and tools.

A proactive internal version could be a controlled pre-release probe lab:

- adversarial agents search for vulnerable white space using abstracted historical motifs, newly patched failures, and safe strategy prompts;
- defensive agents and product controls defend the target workflow with approval gates, tool constraints, policy checks, retrieval boundaries, memory controls, and monitoring;
- the target set could include an unreleased model, a current public model, earlier patched variants, and product/workflow scaffolds;
- expert strategists review where adversarial agents are being creative, where defensive controls are brittle, and which empty cells deserve human-designed probes;
- analysts convert credible findings into traces, patch objects, release gates, and residual monitors.

The purpose would be to learn before deployment. A mature version should ask whether a new model can rediscover old failures, mutate recently patched failures, or find novel combinations between known controls.

The public artifact should not preserve or publish raw exploit content. The preserved artifact is the risk structure and the mitigation decision.

## How The Prototype Is Structured

The prototype has several layers.

| Layer | Purpose | Example Files |
|---|---|---|
| Schema and traces | Make risk records structured and reviewable | `schema/agentic_risk_trace.schema.json`, `examples/*.json` |
| Validator | Check trace shape and missing mitigation patterns | `demo/validate_traces.py`, `tests/` |
| Sentinel study | Watch observable runs across ingress, trajectory, draft, final | `studies/anima-risk-sentinel/` |
| Risk-intel intake | Convert public signals into review-gated safe hypotheses | `studies/risk-intel-intake/` |
| Strategic assessment | Generate a ranked public-signal risk assessment | `studies/strategic-risk-assessment/` |
| Risk-delta matrix | Identify capability/risk cells worth probing | `studies/risk-delta-matrix/`, `reports/risk_delta_matrix.md` |
| Patch-loop case | Show signal -> probe -> trace -> patch -> residual monitor | `studies/patch-loop-case/`, `reports/agent_on_agent_patch_loop_case.md` |
| Opt-in signal-sharing concept | Sketch local monitors and aggregate-only signals | `studies/open-sentinel-network/` |
| Local signature monitor concept | Demonstrate transparent signatures and privacy-aware aggregate telemetry | `studies/agentic-risk-antivirus/` |
| Evidence appendix | State what independent model-observation evidence is verified and what remains private or unresolved | `docs/portfolio/model_observation_evidence_appendix.md` |
| Portfolio docs | Explain the artifact for hiring and review | `docs/portfolio/` |

The small amount of code is intentionally simple. The code is there to make the operating model concrete, not to pretend this is a complete safety platform.

## What This Demonstrates

This artifact demonstrates several things at once.

### Current-Risk Intelligence

Weak signals become evidence, confidence, severity, owners, mitigations, and next review points. The artifact is oriented toward the question a risk team actually needs to answer:

> What is changing, why does it matter, who owns the control, and what should happen next?

### Agentic Substrate Fluency

The traces cover risks that matter more when models become agents:

- prompt injection;
- connector data boundaries;
- tool overreach;
- social engineering;
- policy evasion;
- memory/retrieval contamination;
- approval quality failure;
- agent-on-agent probing.

### Operational Governance

High-impact traces need owners, approval controls, and residual-risk follow-up. The point is not only to detect risk, but to route it into a decision workflow.

### Technical Fluency

The repo includes runnable validators, unit tests, synthetic fixtures, generated reports, and small pipeline scripts. The technical work is intentionally modest, but it makes the artifact inspectable.

### SOTA Self-Awareness

The model-risk review names where this prototype aligns with public agentic-risk work and where it needs stronger adapters: benchmark ingestion, framework crosswalks, threat-model fields, and control-effectiveness metrics.

### Strategic Output

The generated public-signal assessment ranks plausible under-owned or under-instrumented agentic risks and turns them into safe probes and decisions.

### Living-System Posture

The artifact treats agentic risk as a moving frontier where new models, public discoveries, adversarial probes, and agent-on-agent attacks update the operating picture.

### Product Translation

The artifact translates a familiar security operating model into an auditable, privacy-aware agentic-risk prototype without pretending the analogy is perfect.

### Personal Fit

This is also a sample of how I work: make ambiguity legible, preserve evidence and uncertainty, organize repeated cases into a taxonomy, and use empty cells in the framework to ask what risk should be present but has not yet been found.

## What This Does Not Prove

This prototype does not prove:

- production precision or recall;
- real-world prevalence;
- robustness against adaptive attackers;
- performance on private telemetry;
- safety of any specific deployed model;
- quality of a small-model classifier;
- feasibility of opt-in local signal sharing at scale;
- that agent-on-agent attacks are already the dominant risk;
- that the listed risk cells are unknown to any internal team.

Those are next evaluation questions, not claims made by this prototype.

## Next Evaluation Questions

The next credibility jump would be to test:

- Can traces generated from real internal evals improve analyst consistency?
- Can safe probes derived from public signals find control gaps faster than ad hoc review?
- Which lifecycle stage catches each risk class earliest?
- Which signals are noisy but useful, and which are distracting?
- Which mitigations actually reduce residual risk after deployment?
- How should human review be routed so scarce expert attention goes to high-value uncertainty?
- Can benchmark outputs be converted into decision traces without losing nuance?
- Can control-effectiveness metrics track attack success reduction, benign utility, false-positive burden, and first useful intervention point?
- Can local telemetry be useful while preserving strong privacy boundaries?

Recommended near-term build:

1. Add one integrated run that starts from a risk-intel signal and automatically generates a safe sentinel fixture.
2. Add a scorecard: detected stage, severity, control, owner, residual risk, and false-positive note.
3. Extend the patch-loop case into a constrained runnable harness.
4. Explore controlled role separation so adversarial discovery, defensive patching, and analyst adjudication are explicit.
5. Sketch signed patch-pack simulation for an opt-in local signal-sharing concept.

Recommended two-week build:

1. Add an open benchmark-to-trace adapter, ideally Inspect AI plus AgentHarm or AgentDojo.
2. Add framework crosswalks for OWASP, MITRE ATLAS, NIST AI RMF, MIT AI Risk Repository, MAESTRO, and OpenAI Preparedness categories where relevant.
3. Add control-effectiveness metrics.
4. Add an open-model telemetry experiment using entropy, margin, and repeated-sample disagreement around tool choice.
5. Add human-review annotations for false positives and false negatives.

## Author Context

I built this as a portfolio artifact while exploring agentic risk, current-risk intelligence, and AI deployment governance roles.

My background is product-risk systems at Meta, regulated connected-device launch work at JUUL, ML/product evaluation work at Grand Rounds, and software engineering training at Hack Reactor. The repo is intended to make my current thinking inspectable, not to present a production safety system.

LinkedIn: https://www.linkedin.com/in/rcerf

Sanitized resume: `docs/portfolio/rick_cerf_resume.md`

## Evidence Appendix

The model-observation evidence behind my independent Sovereign OS work is deliberately not dumped into this public repo. Some source material contains private working context, raw prompts, or personal material. Instead, I added a public-safe appendix that separates verified local counts from claims I am not relying on yet.

The current verified summary is modest:

- a 44-model behavior registry;
- 118 benchmark result files behind that registry;
- a separate 7-model / 96-segment cross-judge generalization study;
- this repo's 7 public-safe synthetic decision traces.

See `docs/portfolio/model_observation_evidence_appendix.md`.

## How To Run The Prototype

Basic validation:

```bash
python3 demo/validate_traces.py examples
python3 -m unittest tests/test_critical_actions_require_approval.py
```

Selected study runs:

```bash
python3 studies/anima-risk-sentinel/src/risk_sentinel.py studies/anima-risk-sentinel/data/runs
python3 studies/anima-risk-sentinel/src/stage_ablation.py studies/anima-risk-sentinel/data/runs
python3 -m unittest studies/anima-risk-sentinel/tests/test_risk_sentinel.py

python3 studies/risk-intel-intake/src/signal_triage.py studies/risk-intel-intake/data/source_signals/sample_public_signals.json
python3 -m unittest studies/risk-intel-intake/tests/test_signal_triage.py

python3 studies/strategic-risk-assessment/src/generate_assessment.py --output reports/agentic_risk_assessment_public_signals.md
python3 -m unittest discover -s studies/strategic-risk-assessment/tests

python3 studies/risk-delta-matrix/src/generate_matrix.py --output reports/risk_delta_matrix.md
python3 -m unittest discover -s studies/risk-delta-matrix/tests

python3 studies/patch-loop-case/src/render_patch_loop.py --output reports/agent_on_agent_patch_loop_case.md
python3 -m unittest discover -s studies/patch-loop-case/tests

python3 studies/open-sentinel-network/src/network_triage.py --output reports/open_sentinel_network_assessment.md
python3 -m unittest discover -s studies/open-sentinel-network/tests
```

Optional ingestion adapters:

```bash
python3 studies/risk-intel-intake/src/ingest_arxiv.py --config studies/risk-intel-intake/data/config/arxiv_queries.json --max-results 2
python3 studies/risk-intel-intake/src/ingest_aiid.py --lookup-urls studies/risk-intel-intake/data/incidents/sample_aiid_lookup_urls.json
python3 studies/risk-intel-intake/src/ingest_mit_tracker.py
X_BEARER_TOKEN=... python3 studies/risk-intel-intake/src/ingest_x.py --query-config studies/risk-intel-intake/data/config/x_queries.json --max-results 10
python3 studies/risk-intel-intake/src/ingest_manual_social.py studies/risk-intel-intake/data/manual/social_capture_template.json
```

## Public Source Anchors

OpenAI's Preparedness Framework emphasizes tracked risk categories, threat models, evaluations, safeguards, and the need to identify risks that may not yet have precedent. OpenAI's computer-using-agent materials emphasize user confirmations, active supervision for sensitive sites, prompt-injection defenses, monitoring, and detection/human-review pipelines. OWASP frames prompt injection as a top LLM risk, including indirect injection through external content and unauthorized actions through connected tools/APIs.

Sources:

- OpenAI Preparedness Framework v2: https://cdn.openai.com/pdf/18a02b5d-6b67-4cec-ab64-68cdfbddebcd/preparedness-framework-v2.pdf
- OpenAI Computer-Using Agent: https://openai.com/index/computer-using-agent/
- OpenAI Operator System Card: https://openai.com/index/operator-system-card/
- OWASP LLM01 Prompt Injection: https://genai.owasp.org/llmrisk/llm01-prompt-injection/
- OWASP LLM Prompt Injection Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html
- AgentDojo: https://github.com/ethz-spylab/agentdojo
- BIPIA: https://github.com/microsoft/BIPIA

## Repository Map

The README is designed to stand alone. The files below are available for deeper inspection.

```text
README.md
schema/agentic_risk_trace.schema.json
examples/*.json
evals/rubric.md
demo/validate_traces.py
tests/test_critical_actions_require_approval.py

reports/sample_agentic_risk_brief.md
reports/agentic_risk_assessment_public_signals.md
reports/agentic_risk_antivirus_assessment.md
reports/risk_delta_matrix.md
reports/living_agentic_risk_operating_loop.md
reports/agent_on_agent_patch_loop_case.md
reports/frontier_red_green_conflict_lab.md
reports/open_sentinel_network_assessment.md

studies/anima-risk-sentinel/
studies/risk-intel-intake/
studies/strategic-risk-assessment/
studies/risk-delta-matrix/
studies/patch-loop-case/
studies/open-sentinel-network/
studies/agentic-risk-antivirus/
studies/model-risk-sota/

docs/from_product_risk_to_agentic_risk.md
docs/source_notes.md
docs/portfolio/
docs/portfolio/model_observation_evidence_appendix.md
docs/portfolio/rick_cerf_resume.md
ops/current_operating_picture_prompt_injection.md
ops/risk_register_template.csv
```
