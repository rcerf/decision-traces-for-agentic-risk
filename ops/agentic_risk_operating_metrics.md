# Agentic Risk Operating Metrics — a straw-man

This is a proposed metric set for running an agentic-risk portfolio as an
operation, not a proposal that these exact numbers are the right ones. Each
metric names its numerator/denominator, its data source, the failure mode that
would let it be gamed or go stale, and a review cadence. The point is to show how
I would make "are we actually on top of agentic risk?" answerable rather than
rhetorical.

The design rule throughout: a metric that cannot be gamed is rare, so every
metric below is paired with the specific way it lies, and a second signal that
catches that lie.

## 1. Coverage

| | |
|---|---|
| Definition | (# material agentic-risk cells with at least one owned, evidenced trace) / (# cells in the current risk taxonomy) |
| Source | The trace corpus + the taxonomy (capability × risk-class matrix, e.g. `reports/risk_delta_matrix.md`) |
| Cadence | Weekly |
| How it lies | Coverage rises to 100% by shrinking the taxonomy or by counting thin traces. A cell can be "covered" by a stale trace. |
| Catch | Pair with **freshness** (below) and track taxonomy size as its own line; a coverage jump with a taxonomy drop is a red flag, not progress. |

## 2. Ownership

| | |
|---|---|
| Definition | (# open risks with a named accountable owner who has acknowledged) / (# open risks) |
| Source | Trace `owner` field + an acknowledgement timestamp |
| Cadence | Weekly |
| How it lies | Assigning a team name ("Safety") instead of an accountable person makes ownership look complete while nobody is on the hook. |
| Catch | Require a person, not a team, for high/critical; report unacknowledged assignments separately. |

## 3. Decision latency

| | |
|---|---|
| Definition | Median (and p90) days from trace creation to a recorded decision (mitigate / accept / escalate / close) |
| Source | Trace created-at vs decision timestamp |
| Cadence | Weekly, trended monthly |
| How it lies | Latency drops if easy items are decided fast and hard ones are left in "under review" forever (survivorship). |
| Catch | Report latency **and** the age of the oldest still-open high/critical trace; a good median with an old tail is not healthy. |

## 4. Mitigation status distribution

| | |
|---|---|
| Definition | Count of open risks by `mitigation_status` (none / proposed / in_progress / deployed / needs_review) |
| Source | Trace `mitigation_status` |
| Cadence | Weekly |
| How it lies | "deployed" can mean a control shipped, not that it works. |
| Catch | For high/critical, require an effectiveness note (measured or explicitly "not yet measured") before a mitigation counts as deployed. |

## 5. Closure rate and reopens

| | |
|---|---|
| Definition | (# risks closed in period) / (# open at period start); plus reopen rate = (# reopened) / (# closed) |
| Source | Trace status transitions |
| Cadence | Monthly |
| How it lies | Closure rate is trivially raised by closing things that should stay open; a high closure rate with a high reopen rate is churn, not progress. |
| Catch | Always report closure and reopen together; a healthy operation has high closure and low reopens. |

## 6. Freshness / staleness

| | |
|---|---|
| Definition | (# high/critical traces reviewed within their `next_review` window) / (# high/critical traces) |
| Source | Trace `next_review` vs last-reviewed date |
| Cadence | Weekly |
| How it lies | Reviews can be rubber-stamped to reset the clock without new evidence. |
| Catch | Sample-audit a few "reviewed" items each cycle for whether the review changed anything. |

## 7. Signal-to-trace conversion

| | |
|---|---|
| Definition | (# intake signals triaged within SLA) / (# intake signals received); and (# signals that became owned traces) / (# signals judged material) |
| Source | Intake log (e.g. `studies/risk-intel-intake/`) + trace corpus |
| Cadence | Weekly |
| How it lies | A fast triage SLA can be met by dismissing signals; conversion can be inflated by over-tracing noise. |
| Catch | Track dismissed-signal volume and periodically re-audit a sample of dismissals for missed material risk. |

## 8. Detection lead time (where telemetry exists)

| | |
|---|---|
| Definition | For risks with a real incident/eval signal, median time from earliest weak signal to the trace being opened |
| Source | Weak-signal timestamp vs trace created-at |
| Cadence | Monthly |
| How it lies | Only computable where a ground-truth "earliest signal" exists; easy to cherry-pick. |
| Catch | Report the denominator (how many risks had a datable earliest signal) alongside the median. |

## How these fit together

Coverage and ownership say whether the portfolio is complete and accountable.
Latency, closure, and freshness say whether it is actually moving. Conversion and
lead time say whether intake is working upstream. Each has a paired catch so a
single green number cannot hide a problem — which is the same discipline the rest
of this repo applies to individual traces: preserve the uncertainty, and never let
one summary number stand in for the thing it summarizes.

This is a starting set to argue about with the people who own the workstreams, not
a finished dashboard.
