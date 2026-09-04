---
name: itscp-interview-business
description: Use when a continuity plan needs its business impact analysis, when downtime tiers or MTD, RTO and RPO targets must be agreed with the business rather than assumed by IT, when someone asks how critical a system is or how long it can be down, or when manual workarounds during an outage need documenting.
---

# itscp-interview-business

The business impact analysis, run as a conversation rather than a form. Produces Appendix K,
the MTD tiers, the minimum business continuity objective, and Appendix E manual workarounds.

**Read first:** `skills/_method/interview-method.md`. The method is not optional here — this
is the interview where invented numbers do the most damage, because everything downstream is
built to them.

**Interviewee:** the business or process owner. Not IT. If the only person available is from
IT, stop and say so: an MTD signed by IT is IT telling itself what it is allowed to fail at.

**Time:** 90 minutes for one application suite. Half a day if the suite spans several business
functions with different tolerances.

---

## Why this interview gates the others

Tier assignment determines standby capacity, replication topology, and run cost. Get it after
the build and you rebuild to numbers you could have known up front. `itscp-build` will not run
the technical interviews until the output of this one is signed.

---

## Run order

### 1. Frame, without jargon (10 min)

Do not open with MTD, RTO and RPO. Open with what they do:

> "Talk me through what this system does for you on a normal Tuesday. Not the technology —
> the work."

You are listening for **business processes**, which become the rows of the BIA, and for the
**rhythms** that make timing matter: period close, payroll runs, bank cut-offs, shipping
windows, regulatory filing dates.

### 2. Impact over time, per process (45 min)

For each process, walk the clock. This is the core of the interview and the part that cannot
be rushed:

> "It's down at 9am on a Tuesday. What happens in the first hour? By lunchtime? By close of
> business? Tomorrow morning? By Friday?"

Listen for the **step change** — the point where consequences stop being linear. That point is
the MTD, and it is nearly always a mechanism rather than a preference: a file that cuts, a
contract that penalises, a regulator that must be told, a customer who orders elsewhere.

Record per process:

| Field | Notes |
|---|---|
| Process name | The business's own words, not the module name |
| Impact at 1h / 4h / 1 day / 1 week | Their description, not your summary |
| The step change, and its mechanism | **Required.** A number without a mechanism is a guess |
| Time dependence | Does breaking during close, payroll, or quarter end change the answer? |
| Data loss tolerance | "If we lost 15 minutes of work, who redoes it, and can they?" |
| Peak / seasonal exposure | When would this hurt most? |

**Ask about the worst week, not the average one.** Continuity plans are bought for the worst
week and are almost always specified against the average one.

### 3. Data loss, made concrete (15 min)

RPO is the hardest concept to elicit honestly, because "zero" is always the instinctive
answer and is rarely worth what it costs.

> "Suppose we get you back in twenty minutes, but the last fifteen minutes of work is gone.
> Walk me through what that actually means. Who finds out? Can they redo it? How would they
> even know what was lost?"

The three outcomes that matter:

- **Reconstructable** — it is on paper, in email, in a partner's system. RPO can be relaxed;
  the cost moves into work recovery time instead.
- **Not reconstructable** — a customer commitment nobody else recorded. This is the real
  Tier 0 test, far more so than transaction volume.
- **Nobody would notice** — genuinely acceptable loss. Rare, and worth writing down when true,
  because it is the cheapest tier decision available.

### 4. Minimum business continuity objective (10 min)

Not in NIST; asked because MTD alone is insufficient and an ISO 22301 auditor will ask.

> "While we're recovering, what has to work for you to keep trading at all? Not everything —
> the minimum."

The answer is usually far narrower than the full system: take orders and apply cash, defer
reporting and batch. That narrower set is what recovery sequences to first, and it is often
the difference between a Tier 0 estate and a Tier 1 one.

### 5. Manual workarounds — Appendix E (10 min)

> "Last time this was down, what did people actually do?"

Ask about the last real outage, not the hypothetical one. You are looking for the spreadsheet,
the paper pad, the phone call to the warehouse. Then the question that matters:

> "How long can you keep doing that before it stops working?"

That duration is a real constraint on the MTD and is often shorter than anyone assumed. If the
answer is "we've never been down long enough to find out", record it as `confidence: low` and
flag it as a drill objective.

### 6. Tiering and sign-off (10 min)

Read back the proposed tier assignment, one line per scope, with the mechanism beside each.
Then the sentence that makes it real:

> "This is what IT will build to, and what you'll be asked to sign. Is it right?"

**Get the signature, or record explicitly that it was not given and who owes it.** The
reference repository is blunt about needing it at audit time.

---

## The cost conversation, once

Somewhere near the end the business will ask for everything back in fifteen minutes. Answer it
once, honestly, and without negotiating on IT's behalf:

> "That's available. It roughly doubles the standby cost, and on this platform there's a floor
> below which the standby can't be shrunk. Tier 0 for everything is a real option — it's just
> a priced one. Who signs that budget?"

Do not talk them out of Tier 0 and do not sell it. The tier is theirs to choose; the price is
IT's to state accurately. Record the tier they chose **and** whether the cost was known when
they chose it — the second one matters when the invoice arrives.

---

## Output

Writes `business.*` in the answer store: process inventory, per-process impact curves,
step-change mechanisms, tier assignments, MTD/RTO/RPO/WRT targets, MBCO, manual workarounds
and their durations, sign-off status.

Renders `docs/02-mtd-tiers.md`, `checklists/tier-assignment-workshop.md`,
`checklists/manual-workarounds.md`.

## Red flags

| Thought | Reality |
|---|---|
| "They said four hours, that's the MTD" | Not until you have the mechanism. What breaks at hour five? |
| "IT already told me the tiers" | Then IT has assigned itself its own targets. This interview has not happened |
| "They don't understand RPO, I'll explain the concept" | Explain nothing. Ask what work would have to be redone |
| "Everything is Tier 0, that's unrealistic" | It is realistic and priced. State the price; do not overrule the business |
| "We're out of time, I'll infer the rest from the pattern" | Two processes answered and eight inferred is one answered interview and eight fabrications |
| "They've never been down, so there are no workarounds" | Then the workaround duration is unknown and that is a drill objective, not a blank |
