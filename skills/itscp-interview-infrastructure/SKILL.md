---
name: itscp-interview-infrastructure
description: Use when a continuity plan needs its recovery strategy, replication design or alternate processing site documented, when deciding between synchronous and asynchronous replication or between hot, warm and cold standby, or when the cost of standby capacity has to be reconciled with the recovery targets the business asked for.
---

# itscp-interview-infrastructure

The recovery strategy and the machinery that implements it. Produces the architecture, the
replication matrix, Appendix C alternate site and storage, Appendix D recovery procedures, and
the cost model that decides whether the business's chosen tier is affordable.

**Read first:** `skills/_method/interview-method.md`, plus the discovery inventory and the
signed tier assignment. This interview is where the business's targets meet physics and price.

**Interviewee:** the cloud or infrastructure owner.

**Time:** 90–120 minutes.

---

## Start from the targets, not the technology

Open with the signed tiers:

> "The business has signed an MTD of two hours for order entry and cash application, RPO
> effectively zero. Here's what's in the tenancy today. Can we meet that, and what would it
> take?"

This framing does the work. It makes the conversation about a commitment already made rather
than an aspiration, and it surfaces the gap between wanted and available in the first ten
minutes instead of the last.

---

## What to elicit

### 1. Current state versus intended state (15 min)

> "Does what I found in the tenancy match what you think is there? What's missing, and what's
> there that shouldn't be?"

The gap is a finding. Undocumented resources, an absent standby, a replication policy that
covers three of five buckets — these are the plan's first real risks, and they are best found
here rather than during a drill.

### 2. Replication, mechanism by mechanism (30 min)

For every data tier — database, block, file, object, backup — establish:

| Field | Why it matters |
|---|---|
| Mechanism | Determines everything else |
| Synchronous or asynchronous | Whether an RPO 0 claim is even available |
| Measured lag today, not the target | The plan's RPO evidence |
| Behaviour on failover | Some replicas activate to a clone; some become read-only until a resource is deleted |
| **Re-baseline or resume after reversal** | The failback cost, and usually a surprise |
| One-way door? | Whether the step can be undone at all |

**The re-baseline question is the one to press.** Several cloud replication primitives copy
from zero rather than resuming after a role reversal. That turns failback from a cutover into
a multi-day project, and almost nobody has costed it. Ask explicitly:

> "After we fail over and want to come back — does this resume where it left off, or copy
> everything again? How long, at your data volume?"

If the answer is unknown, it is a `MISSING` and a Tier B test objective, not an assumption.

### 3. Latency and distance (10 min)

Synchronous replication waits for the far side to acknowledge. Beyond a certain distance that
cost lands on every commit.

> "What's the measured round-trip time between the two regions? Not the published figure —
> have you measured it?"

If unmeasured, mark it `confidence: low` and make measuring it a prerequisite, not a
follow-up. A design that assumes synchronous replication over an unmeasured link is a design
with an unexploded assumption in the middle of it.

### 4. Standby posture and the cost floor (20 min)

> "What does the standby cost today, and what's the cheapest it can be while still meeting the
> RPO the business signed?"

Every platform has a floor below which a standby stops functioning as one — a minimum node
count, a minimum OCPU allocation, a licence that bills whether running or not. Establish the
floor explicitly, because the tier the business chose may be unaffordable at it, and that is a
conversation to have now rather than at renewal.

Then: can the posture change on a schedule, and who is allowed to change it?

### 5. Naming, addressing and the biggest RTO lever (15 min)

> "When you bring the application up in the standby region, does it know it moved?"

Applications that hard-code host names, IPs or region-specific endpoints turn a 30-minute
recovery into a half-day reconfiguration. Establish what is region-locked and what resolves
locally. This is frequently the single largest RTO lever available and it is usually cheaper
to fix than any amount of extra standby capacity.

### 6. Orchestration and drills (10 min)

What exists today: orchestration service, scripts, or a document. Then the question that
decides how much of the plan is real:

> "When was the last time any of this was actually executed, end to end?"

"Never" is a common and acceptable answer. Record it plainly; it sets the drill programme's
first objective and calibrates how much the current design's timings can be trusted.

### 7. Alternate site and telecommunications — Appendix C (10 min)

For cloud estates most of NIST's Appendix C is answered by the provider. Record which parts
the provider owns, which the organisation owns, and which are genuinely not applicable —
each with a reason. Do not silently drop them; an auditor reads the omission as an oversight.

---

## The conversation where targets meet price

At some point the signed tier and the affordable design will not match. Do not resolve it
inside this interview, and do not quietly design to the cheaper one.

Produce three costed options — meet the target, meet it partially, and the cheapest defensible
design — with the standby cost and the achievable RTO/RPO for each. Hand them back to the
business owner as a decision.

**A tier silently downgraded by IT is the most dangerous artifact this toolkit could produce**,
because the business believes it has protection it is not paying for and will not find out
until the invocation.

---

## Output

Writes `infra.*`: current-versus-intended gaps, replication matrix with lag and re-baseline
behaviour, measured latency, standby posture and cost floor, region-locked naming, orchestration
state, drill history, Appendix C determinations, costed options.

Renders `docs/01-architecture.md`, `docs/03-replication-matrix.md`,
`docs/05-cost-and-teardown.md`, and seeds the runbook templates.

## Red flags

| Thought | Reality |
|---|---|
| "Replication exists, so RPO is met" | Existence is not currency. Get measured lag, or mark it unmeasured |
| "They said it resumes after failback" | Ask how they know. Untested belief about re-baselining is expensive to be wrong about |
| "Latency is fine, it's the published figure" | Published figures are not measurements. Mark it low confidence |
| "The business wants Tier 0 but can't afford it, I'll design Tier 1" | Never. Present costed options and let them choose |
| "They've never drilled, but the design is sound" | Then every duration is a target, and the plan must say so everywhere |
| "Appendix C is mostly not applicable for cloud" | Probably true, and each one still needs its reason written down |
