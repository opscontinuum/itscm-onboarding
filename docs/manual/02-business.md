# Phase 2 — The business figures, which gate everything after them

> **Generated file.** It is assembled from the skills, the question bank and `GETTING-STARTED.md` by `plugin/itscp_manual.py`, and an edit made here is deleted by the next regeneration. Change the source and run `python3 plugin/itscp_manual.py`.

**Not the tabletop.** A separate session with the business or process owner, before the technical segments. Deliberately not in the room with the IT teams.

**Whose answers these are:** the business or process owner. Not IT. If the only person available is from IT, stop and say so: an MTD signed by IT is IT telling itself what it is allowed to fail at.

**How long:** 90 minutes for one application suite. Half a day if the suite spans several business functions with different tolerances.

**This one is not a tabletop, and holding that line is the whole point of the phase.** Tiers, maximum tolerable downtime and recovery point are the business's figures. Run in a room full of engineers they become IT's figures, and IT deciding what it is allowed to fail at is the failure this sequence is built to prevent.

**Do not start the technical segments without a signed tier assignment.** Tier determines standby capacity, replication topology and run cost. Everything after this is built to these numbers and all of it is expensive to change. With the plugin a build step holds that gate; here you hold it.

If the business owner is unavailable for three weeks, wait three weeks. Proceeding on assumed tiers feels productive and is the most costly mistake available here: assumed tiers become real architecture within a day and are never revisited.

**Run under [the method](method.md).** Nothing enters the plan unless somebody in the room said it, an inventory shows it, or it is written down as a gap with a name against it.

---

### Running this without the toolkit

The technique below is the skills' own words, and the skills assume a loaded plugin. You do not have one. These are the substitutions in effect on this page.

| Where it says | In the room you |
|---|---|
| `itscp-build` | There is no generator in a tabletop. Phase 6 is you writing the documents, and [fields.md](fields.md) is the map of which answer goes into which one. |

## The technique

*From `itscp-interview-business`: Use when a continuity plan needs its business impact analysis, when downtime tiers or MTD, RTO and RPO targets must be agreed with the business rather than assumed by IT, when someone asks how critical a system is or how long it can be down, or when manual workarounds during an outage need documenting.*

### Tiering is comparative, and this interview does not set the budget

If the organization has more than one system, the tier budget was set in `itscp-portfolio`
by ranking systems against each other. **Bring the budget into this interview and say what it
is.** Asked in isolation every owner answers Tier 0, and they are not wrong to -- the question
only has a meaningful answer relative to the others competing for the same engineers at 3am.

> "Across the environment there are four Tier 0 places and eleven candidates. Yours is currently
> third. Here is what that means for you, and here is what would have to move for it to be
> first."

If the owner disputes the ranking, that is a portfolio decision and it goes back there. Do not
re-rank inside one system's interview: the other owners are not in the room.

### Why this interview gates the others

Tier assignment determines standby capacity, replication topology, and run cost. Get it after
the build and you rebuild to numbers you could have known up front. `itscp-build` will not run
the technical interviews until the output of this one is signed.

### Run order

#### 1. Frame, without jargon (10 min)

Do not open with MTD, RTO and RPO. Open with what they do:

> "Talk me through what this system does for you on a normal Tuesday. Not the technology —
> the work."

You are listening for **business processes**, which become the rows of the BIA, and for the
**rhythms** that make timing matter: period close, payroll runs, bank cut-offs, shipping
windows, regulatory filing dates.

#### 2. Impact over time, per process (45 min)

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

#### 3. Data loss, made concrete (15 min)

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

#### 4. Minimum business continuity objective (10 min)

Not in NIST; asked because MTD alone is insufficient and an ISO 22301 auditor will ask.

> "While we're recovering, what has to work for you to keep trading at all? Not everything —
> the minimum."

The answer is usually far narrower than the full system: take orders and apply cash, defer
reporting and batch. That narrower set is what recovery sequences to first, and it is often
the difference between a Tier 0 environment and a Tier 1 one.

#### 5. Manual workarounds — Appendix E (10 min)

> "Last time this was down, what did people actually do?"

Ask about the last real outage, not the hypothetical one. You are looking for the spreadsheet,
the paper pad, the phone call to the warehouse. Then the question that matters:

> "How long can you keep doing that before it stops working?"

That duration is a real constraint on the MTD and is often shorter than anyone assumed. If the
answer is "we've never been down long enough to find out", record it as `confidence: low` and
flag it as a drill objective.

#### 6. Tiering and sign-off (10 min)

Read back the proposed tier assignment, one line per scope, with the mechanism beside each.
Then the sentence that makes it real:

> "This is what IT will build to, and what you'll be asked to sign. Is it right?"

**Get the signature, or record explicitly that it was not given and who owes it.** The
reference repository is blunt about needing it at audit time.

### The cost conversation, once

Somewhere near the end the business will ask for everything back in fifteen minutes. Answer it
once, honestly, and without negotiating on IT's behalf:

> "That's available. It roughly doubles the standby cost, and on this platform there's a floor
> below which the standby can't be shrunk. Tier 0 for everything is a real option — it's just
> a priced one. Who signs that budget?"

Do not talk them out of Tier 0 and do not sell it. The tier is theirs to choose; the price is
IT's to state accurately. Record the tier they chose **and** whether the cost was known when
they chose it — the second one matters when the invoice arrives.

### Red flags

| Thought | Reality |
|---|---|
| "They said four hours, that's the MTD" | Not until you have the mechanism. What breaks at hour five? |
| "IT already told me the tiers" | Then IT has assigned itself its own targets. This interview has not happened |
| "They don't understand RPO, I'll explain the concept" | Explain nothing. Ask what work would have to be redone |
| "Everything is Tier 0, that's unrealistic" | It is realistic and priced. State the price; do not overrule the business |
| "We're out of time, I'll infer the rest from the pattern" | Two processes answered and eight inferred is one answered interview and eight fabrications |
| "They've never been down, so there are no workarounds" | Then the workaround duration is unknown and that is a drill objective, not a blank |

---

## What this segment has to come away with

11 answers, grouped by the section of the plan each one feeds. Read this before the session; the worksheet at the end is what you take into it.

Every one of them leaves the room with something written against it. An answer nobody in the room could give is a **name** — whoever can — which is a result and not a failure. A blank is neither.

### K. Business impact analysis

#### `business.processes`

> "Walk me through what stops if this is down for an hour. Then for a day. Then for a week. Take the processes one at a time."

- **Records:** Each business process and what its outage costs at one hour, four hours, a day and a week
- **Answers:** business owner · **Shape:** one row per item, columns `name` | `impact_1h` | `impact_4h` | `impact_1d` | `impact_1w`
- **Note:** The BIA's first step. Ask about impact at each horizon separately; people answer 'it is critical' to the general question and give you something usable when the horizon is named.
- **Goes into:** docs/02-mtd-tiers.md, checklists/tier-assignment-workshop.md
- **NIST:** 3.2.1 Determine Business Processes and Recovery Criticality (SP 800-34 Rev. 1 Chapter 3, Information System Contingency Planning Process)
- **Terminology:** ITIL calls this session a business impact analysis [glossary]

#### `business.mtd.tier0`

> "At what point does this stop being an IT problem and become something the chief executive hears about?"

- **Records:** Maximum tolerable downtime for the tier 0 processes
- **Answers:** business owner · **Shape:** a duration in hours
- **Then ask:** "What happens at that hour that does not happen at the hour before it? Name the deadline, the cut-off, the batch that has to run, or the person who picks up the phone." It goes in the **what breaks at that number** column. An empty one makes the figure a guess, and the row is marked low confidence.
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** A number without a mechanism is a guess wearing a suit.
- **Goes into:** docs/02-mtd-tiers.md
- **NIST:** 3.2.1 Determine Business Processes and Recovery Criticality (SP 800-34 Rev. 1 Appendix A.3 heading, and Appendix B Sample BIA)
- **Terminology:** ISO 22301's term is maximum tolerable period of disruption (practice guide; not verified)

#### `business.rpo.tier0`

> "If we recovered to fifteen minutes before the failure, what work would people have to redo, and who would have to redo it?"

- **Records:** Recovery point objective for the tier 0 processes
- **Answers:** business owner · **Shape:** a duration in minutes
- **Then ask:** "What is in those minutes that nobody could rebuild from anywhere else, and who finds out first that it is gone?" It goes in the **what breaks at that number** column. An empty one makes the figure a guess, and the row is marked low confidence.
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** Elicited as: if we lost 15 minutes, who redoes the work, and can they?
- **Goes into:** docs/02-mtd-tiers.md
- **NIST:** 3.2.1 Determine Business Processes and Recovery Criticality (SP 800-34 Rev. 1 Appendix A.3 heading, and Appendix B Sample BIA)

#### `business.tier_targets`

> "For each recovery tier you have: how long may it be down in total, how long may the technical recovery take, how long does the business need afterwards before it can work, and how much data may be lost? And what is the least service that still counts as trading?"

- **Records:** Per tier: maximum tolerable downtime, recovery time, work recovery time, recovery point and the minimum service that counts as trading
- **Answers:** business owner · **Shape:** one row per item, columns `tier` | `mtd` | `rto` | `wrt` | `rpo` | `minimum_service` | `what_breaks_at_the_mtd`
- **Every `mtd` owes a `what_breaks_at_the_mtd`.** A target with no stated consequence is a number nobody has to meet.
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** One table, filled a row at a time, and the last column is the one that makes the rest worth having. A tier ladder of round numbers with nothing behind them is the single most common defect in a continuity plan: it reads as a measurement and it is a preference. Do not accept a figure until the row beside it says what it collides with.
- **Goes into:** docs/02-mtd-tiers.md
- **These words are the toolkit's, not the room's.** They render as its own and are never presented as something anybody in the room said: Maximum tolerable downtime is recovery time plus work recovery time. The toolkit decomposes it that way so that a recovery which meets its technical target and still misses what the business can tolerate is visible on paper rather than at four in the morning.

#### `business.tier_assignment`

> "I am going to read you back what this system does. Sort each one into the tiers we just defined, and argue with me where it does not fit."

- **Records:** Each business process, the tier it is assigned to, and the argument for it
- **Answers:** business owner · **Shape:** one row per item, columns `process` | `tier` | `rationale`
- **Note:** The impact question asks what stops. This one asks the business to commit. They are different sessions and people answer them differently: 'it is critical' survives the first and does not survive the second. Record the argument, not just the letter, because the argument is what gets re-examined when the cost lands.
- **Goes into:** docs/02-mtd-tiers.md, checklists/tier-assignment-workshop.md
- **NIST:** 3.2.3 Identify System Resource Recovery Priorities (SP 800-34 Rev. 1 Chapter 3, Information System Contingency Planning Process)
- **Terminology:** ITIL calls this session a business impact analysis [glossary]

### Minimum business continuity objective per tier

#### `business.mbco.tier0`

> "While we are recovering, what is the smallest amount of this service that keeps you trading? Not the full thing. The part you cannot do without for a day."

- **Records:** The minimum service level that must be available during work recovery
- **Answers:** business owner · **Shape:** free text
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** Not NIST. What must work to keep trading while recovery runs.
- **Goes into:** docs/02-mtd-tiers.md
- **No NIST slot.** An element this toolkit carries deliberately; the answer in it is elicited like any other.
- **Terminology:** ITIL and ISO 22301 both use minimum business continuity objective (practice guide; not verified)

#### `business.reconstruction_effort`

> "If we lost the work from the last few minutes before the failure, how long would it take to put it back, and who would be doing it?"

- **Records:** How long rebuilding the lost work takes, and who does it
- **Answers:** business owner · **Shape:** a duration in hours
- **Then ask:** "What are they rebuilding it from, and what happens if that source went down with everything else?" It goes in the **what breaks at that number** column. An empty one makes the figure a guess, and the row is marked low confidence.
- **Note:** This is the recovery point objective turned into work recovery time, which is the half of the sum that never gets costed. If the source they would rebuild from is inside the failed environment, the answer is not a duration, it is a design finding.
- **Goes into:** docs/02-mtd-tiers.md, checklists/manual-workarounds.md
- **No NIST slot.** An element this toolkit carries deliberately; the answer in it is elicited like any other.

### E. Alternate mission/business processing - manual workarounds

#### `business.workarounds`

> "Last time this was down, what did people actually do? Did anyone write anything on paper, and how long could they keep that up?"

- **Records:** Each process, the workaround used, and how long it is sustainable
- **Answers:** business owner · **Shape:** one row per item, columns `process` | `workaround` | `sustainable_for` | `what_fails_first`
- **Every `sustainable_for` owes a `what_fails_first`.** A target with no stated consequence is a number nobody has to meet.
- **Note:** Appendix E. Ask about the last real outage, not the hypothetical one.
- **Goes into:** checklists/manual-workarounds.md
- **NIST:** APPENDIX D ALTERNATE PROCESSING PROCEDURES (SP 800-34 Rev. 1 Appendix A.3, Sample Template for High-Impact Systems)

### Citation and unverified-statement discipline

#### `business.tier_signoff`

> "Have you signed off the tier assignment, or is it still with you? If it is not signed, who owes the signature and by when?"

- **Records:** Whether the tier assignment is signed, and by whom, or who owes it
- **Answers:** business owner · **Shape:** one of `signed`, `not signed`, `signed with exceptions`
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** Signed, or explicitly recorded as not signed and who owes it.
- **Goes into:** docs/02-mtd-tiers.md
- **No NIST slot.** An element this toolkit carries deliberately; the answer in it is elicited like any other.

### Periods when recovery is more expensive than the outage

#### `business.freeze_periods`

> "Are there weeks in the year when failing over would be worse than staying down? Period close, year end, a filing deadline?"

- **Records:** Each period when failing over costs more than the outage, and who decides during it
- **Answers:** business owner · **Shape:** one row per item, columns `period` | `why` | `who_decides`
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** Nobody volunteers this and everybody has one. It changes the activation criteria for a fortnight a quarter, which is when the plan is most likely to be used and least likely to have been read.
- **Goes into:** checklists/dr-authority-matrix.md, docs/08-phase-activation.md
- **No NIST slot.** An element this toolkit carries deliberately; the answer in it is elicited like any other.

#### `business.freeze_override_authority`

> "If we were inside one of those periods and had to fail over anyway, who is allowed to say yes, and what do they need in front of them first?"

- **Records:** Who may authorize a failover inside a freeze period, and on what evidence
- **Answers:** business owner · **Shape:** free text
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** A freeze with no override is a plan that stops working four weeks a year. Name one individual and what they need to see; 'the board' is nobody at two in the morning.
- **Goes into:** checklists/dr-authority-matrix.md
- **No NIST slot.** An element this toolkit carries deliberately; the answer in it is elicited like any other.

---

## The worksheet

Print this. One line per answer, filled in as it is said rather than afterwards.

- **Never leave a cell blank.** No answer means write the name of who can give one.
- **Sure?** is how the answer arrived, not how plausible it sounds. H: they have measured it or read it off a screen while you waited. M: confident from experience, never measured. L: worked out in the room just now. Ask when you cannot tell.
- **What breaks at that number** is what makes a figure arguable rather than arbitrary. A duration with an empty cell beside it is a guess, and is marked L.
- Two people, two answers: **write both**, and write whose decision it is.

### K. Business impact analysis

| What it records | Answer | Who said it | Sure? | What breaks at that number |
|---|---|---|---|---|
| Maximum tolerable downtime for the tier 0 processes (`business.mtd.tier0`) |  |  | H / M / L |  |
| Recovery point objective for the tier 0 processes (`business.rpo.tier0`) |  |  | H / M / L |  |

**Each business process and what its outage costs at one hour, four hours, a day and a week** (`business.processes`) — one row each, add as many as the room needs

| name | impact_1h | impact_4h | impact_1d | impact_1w | Who said it | Sure? |
|---|---|---|---|---|---|---|
|   |   |   |   |   |  | H / M / L |
|   |   |   |   |   |  | H / M / L |
|   |   |   |   |   |  | H / M / L |

**Per tier: maximum tolerable downtime, recovery time, work recovery time, recovery point and the minimum service that counts as trading** (`business.tier_targets`) — one row each, add as many as the room needs

| tier | mtd | rto | wrt | rpo | minimum_service | what_breaks_at_the_mtd | Who said it | Sure? |
|---|---|---|---|---|---|---|---|---|
|   |   |   |   |   |   |   |  | H / M / L |
|   |   |   |   |   |   |   |  | H / M / L |
|   |   |   |   |   |   |   |  | H / M / L |

**Each business process, the tier it is assigned to, and the argument for it** (`business.tier_assignment`) — one row each, add as many as the room needs

| process | tier | rationale | Who said it | Sure? |
|---|---|---|---|---|
|   |   |   |  | H / M / L |
|   |   |   |  | H / M / L |
|   |   |   |  | H / M / L |

### Minimum business continuity objective per tier

| What it records | Answer | Who said it | Sure? | What breaks at that number |
|---|---|---|---|---|
| The minimum service level that must be available during work recovery (`business.mbco.tier0`) |  |  | H / M / L |  |
| How long rebuilding the lost work takes, and who does it (`business.reconstruction_effort`) |  |  | H / M / L |  |

### E. Alternate mission/business processing - manual workarounds

**Each process, the workaround used, and how long it is sustainable** (`business.workarounds`) — one row each, add as many as the room needs

| process | workaround | sustainable_for | what_fails_first | Who said it | Sure? |
|---|---|---|---|---|---|
|   |   |   |   |  | H / M / L |
|   |   |   |   |  | H / M / L |
|   |   |   |   |  | H / M / L |

### Citation and unverified-statement discipline

| What it records | Answer | Who said it | Sure? | What breaks at that number |
|---|---|---|---|---|
| Whether the tier assignment is signed, and by whom, or who owes it (`business.tier_signoff`) |  |  | H / M / L |  |

### Periods when recovery is more expensive than the outage

| What it records | Answer | Who said it | Sure? | What breaks at that number |
|---|---|---|---|---|
| Who may authorize a failover inside a freeze period, and on what evidence (`business.freeze_override_authority`) |  |  | H / M / L |  |

**Each period when failing over costs more than the outage, and who decides during it** (`business.freeze_periods`) — one row each, add as many as the room needs

| period | why | who_decides | Who said it | Sure? |
|---|---|---|---|---|
|   |   |   |  | H / M / L |
|   |   |   |  | H / M / L |
|   |   |   |  | H / M / L |
