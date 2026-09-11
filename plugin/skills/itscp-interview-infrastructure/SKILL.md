---
name: itscp-interview-infrastructure
description: Use when a continuity plan needs its recovery strategy, replication design or alternate processing site documented, when deciding between synchronous and asynchronous replication or between hot, warm and cold standby, or when the cost of standby capacity has to be reconciled with the recovery targets the business asked for.
---

# itscp-interview-infrastructure

The recovery strategy and the machinery that implements it. Produces the architecture, the
replication matrix, Appendix C alternate site and storage, Appendix D recovery procedures, and
the cost model that decides whether the business's chosen tier is affordable.

**Read first:** the `itscp-method-interview` skill, plus the discovery inventory and the
signed tier assignment. This interview is where the business's targets meet physics and price.

**Interviewee:** the cloud or infrastructure owner, with the lead engineer. The owner holds the
design and the budget; the lead engineer holds the measured figures and the answer to section 6,
and those are the parts of this interview that decide how much of the plan is real.

**Time:** 2 hours, and it runs long rather than short. The backup and restore segment is the one people underestimate, because the first answer is usually the replication design again.

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
| Behavior on failover | Some replicas activate to a clone; some become read-only until a resource is deleted |
| **Re-baseline or resume after reversal** | The failback cost, and usually a surprise |
| One-way door? | Whether the step can be undone at all |

**The re-baseline question is the one to press.** Several cloud replication primitives copy
from zero rather than resuming after a role reversal. That turns failback from a cutover into
a multi-day project, and almost nobody has costed it. Ask explicitly:

> "After we fail over and want to come back — does this resume where it left off, or copy
> everything again? How long, at your data volume?"

If the answer is unknown, it is a `MISSING` and a Tier B test objective, not an assumption.

### 3. Backups, which are not replication (20 min)

Replication answers "the region is gone". It does not answer "somebody dropped the table at
nine this morning and nobody noticed until Thursday", because it copied that faithfully and
at once. Ask both, in that order, and watch for the answer that covers one and assumes the
other:

> "Somebody deletes a table this morning and nobody notices until tomorrow. What do you reach
> for? Now the whole region is gone instead. What do you reach for then?"

Then two tables, in this order, because they answer different questions and people conflate
them. First the policies, which is how the room already thinks about it and how every backup
product models it — a schedule defined once, applied to many things:

| Column | What to press on |
|---|---|
| Policy | Its name in whatever runs it, so somebody can find it afterwards |
| Method | The mechanism, named. Not "we back it up" |
| Type | Full, differential, incremental, snapshot, log, continuous |
| Frequency | The rhythm. Compare it against the recovery point objective the business signed |
| Copy | Which copy it writes into, from the offsite storage table. How long anything is kept is asked once, there |

Expect a handful of rows. A site with one nightly policy over twenty components has one row
here, not twenty.

Then what each policy covers, going down the inventory rather than down the policy list,
because the gap is the point:

| Column | What to press on |
|---|---|
| Target | Whatever would have to come back. Go finer than the component list wherever the answers differ |
| Kind | System, application, database, filesystem, volume or drive, object store, configuration |
| What is copied | Data, configuration, both. A database with no copy of what configures it restores into nothing |
| Policy | Which one covers it, by name |
| Not covered because | The reason, where nothing covers it |

**A target nothing covers is a decision or a gap, and the difference is whether anybody has
made it.** A reason written in that last column makes it a decision with a name against it. An
empty cell beside an empty policy is the thing to go back for.

The drive-level answers are where this earns its time. A data volume on a nightly incremental
and an operating system volume nobody copies at all is an ordinary arrangement, entirely
defensible, and completely invisible if the table stops at the application.

Two questions that decide whether any of this is real:

> "When did somebody last put a copy back, for real, rather than checking the backup job
> reported success?"

> "Somebody has your administrator credentials and wants every copy gone. Which copy survives
> them, and who holds what brings it back?"

The first separates a backup from a hypothesis. The second usually has no answer, and where it
does not, that is often the most expensive finding of the engagement: a plan whose every copy
is reachable with one set of credentials is one bad afternoon from having none.

### 4. Latency and distance (10 min)

Synchronous replication waits for the far side to acknowledge. Beyond a certain distance that
cost lands on every commit.

> "What's the measured round-trip time between the two regions? Not the published figure —
> have you measured it?"

If unmeasured, mark it `confidence: low` and make measuring it a prerequisite, not a
follow-up. A design that assumes synchronous replication over an unmeasured link is a design
with an unexploded assumption in the middle of it.

### 5. Standby posture and the cost floor (20 min)

> "What does the standby cost today, and what's the cheapest it can be while still meeting the
> RPO the business signed?"

Every platform has a floor below which a standby stops functioning as one — a minimum node
count, a minimum OCPU allocation, a license that bills whether running or not. Establish the
floor explicitly, because the tier the business chose may be unaffordable at it, and that is a
conversation to have now rather than at renewal.

Then: can the posture change on a schedule, and who is allowed to change it?

### 6. Naming, addressing and the biggest RTO lever (15 min)

> "When you bring the application up in the standby region, does it know it moved?"

Applications that hard-code host names, IPs or region-specific endpoints turn a 30-minute
recovery into a half-day reconfiguration. Establish what is region-locked and what resolves
locally. This is frequently the single largest RTO lever available and it is usually cheaper
to fix than any amount of extra standby capacity.

### 7. Orchestration and drills (10 min)

What exists today: orchestration service, scripts, or a document. Then the question that
decides how much of the plan is real:

> "When was the last time any of this was actually executed, end to end?"

"Never" is a common and acceptable answer. Record it plainly; it sets the drill program's
first objective and calibrates how much the current design's timings can be trusted.

Then the question that turns drill history into a roster finding:

> "Who ran it? And who else has ever run it?"

One name is an availability requirement on a person, sitting inside a document written to
remove single points of failure. Record it against the lead engineer and their deputy.

### 8. Alternate site and telecommunications — Appendix C (10 min)

For cloud environments most of NIST's Appendix C is answered by the provider. Record which parts
the provider owns, which the organization owns, and which are genuinely not applicable —
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
behavior, measured latency, standby posture and cost floor, region-locked naming, orchestration
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
| "The lead engineer has done it, that's enough" | Once, by one person, is not a capability. Ask who else, and record the deputy gap |
| "Appendix C is mostly not applicable for cloud" | Probably true, and each one still needs its reason written down |
