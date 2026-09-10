# Phase 3a — The application segment

> **Generated file.** It is assembled from the skills, the question bank and `GETTING-STARTED.md` by `plugin/itscp_manual.py`, and an edit made here is deleted by the next regeneration. Change the source and run `python3 plugin/itscp_manual.py`.

**The tabletop.** Application and infrastructure teams in the room together, with the DR process owner. One exercise in segments; run it in a single long sitting or across several, but keep both teams present for all of it. The application team leads this segment; keep the infrastructure team in the room, because half the corrections come from them.

**Whose answers these are:** the application owner — whoever is accountable for the application working, not for the infrastructure under it. In an ERP context this is usually the functional lead or applications DBA rather than the cloud team.

**How long:** 90 minutes. Bring the discovery inventory; it halves the session.

Open by putting phase 1's inventory on the table. The application team corrects a list far faster than it reconstructs one from memory, and the corrections are themselves findings.

**Bring the deputies.** The backup lead engineer sitting in is the cheapest test available of whether the deputy could really do it, and it usually answers the question before you have to ask it.

**Expect a contradiction with phase 2, and do not resolve it in the room.** The business said four hours; the application owner says batch reprocessing alone takes a day. Write both on the worksheet, write the name of whose decision it is, and take it back to the business owner. A plan with a visible, owned contradiction is honest.

**Run under [the method](method.md).** Nothing enters the plan unless somebody in the room said it, an inventory shows it, or it is written down as a gap with a name against it.

---

## The technique

*From `itscp-interview-application`: Use when a continuity plan needs its system description, when the interfaces and interconnections of an application must be documented, when someone must define what proves a recovered system is actually correct, or when work recovery time and batch reprocessing after a failover need scoping.*

### Open with the inventory, not a blank page

If `itscp-discover` has run, start by showing what was found:

> "Here's what I found in the tenancy. Which of these is yours, what's each one for, and
> what's missing from this list?"

This is a far better opening than "describe your system". It is concrete, it surfaces the
resources nobody could name, and the **missing** half is where the findings live — the
instance nobody owns, the bucket that predates the current team, the standby that was
supposed to exist.

### What to elicit

#### 1. System identity (10 min)

| Field | Why |
|---|---|
| System name, and what the business calls it | Both. The ITSCP is read by both audiences |
| Version and platform | Determines which recovery procedures apply at all |
| System owner, and the authorizing official if one exists | §2.1; the reassessment decision at Reconstitution |
| Data classification / impact level, if categorized | NIST ISCP §1.2 scope in the crosswalk; drives which controls are required |
| User population — who, how many, where | Notification scope; the load a recovered system must carry |

If the system has never been formally categorized, that is a `MISSING` with the governance
owner named, not a value you assign.

#### 2. Architecture as the application sees it (20 min)

Not the cloud topology — the *application* topology. Tiers, where state lives, what is
stateless, what must be brought up in what order, and what breaks if that order is wrong.

The question that finds the real dependency:

> "If you brought this up in the wrong order, what would break, and how would you know?"

Order-of-operations knowledge is almost never written down and is almost always in one
person's head. Capture it verbatim, and record **whose** head, because that name is the
plan's dependency. Then ask the deputy question:

> "If they were on leave the week this happened, who else has actually done this?"

#### 3. Interconnections — Appendix I (25 min)

The section most likely to be incomplete, and the one that causes the most damage when it is.

**Discovery gives you nothing here.** It renders an inventory, not an interconnection list, so
unlike section 2 there is no found-in-the-tenancy list to react to and no safety net under a
partner nobody remembers. This section is elicited from a blank page. Budget the full 25
minutes and do not let it get compressed when the session overruns.

> "Who sends you files, and who's waiting on files from you?"

Per interface, record: partner, direction, transport, frequency, what breaks on their side
first, how long they tolerate silence, whether they can replay, and **a named human contact**.

Then the two questions that turn a list into a plan:

> "If we failed over and this interface pointed at the wrong place for an hour, what would
> happen?"
>
> "Who on their side would you have to call, and do you have their number outside our systems?"

**A partner contact stored only inside the system being recovered is not a contact.** This is
the single most common preventable failure in a real invocation.

#### 4. Validation — Appendix F (20 min)

The pass list. Not "is the database up" but "is the business correct".

> "After a failover, what would you personally check before telling people it's safe to use?"

Push for specifics: a named transaction, a report whose total is known, a batch job whose
output can be compared. Then:

> "How long does that take, and who has to be awake to do it?"

Validation is on the critical path of the MTD and is routinely forgotten in the timings.
A validation pack requiring four people over two hours turns a 60-minute RTO into a
3-hour recovery, and the business signed for the shorter number.

#### 5. Work recovery time (15 min)

The activities between "the system is up" and "the business is working".

> "We've failed over and lost twelve minutes of transactions. Walk me through everything
> that has to happen before people can safely work again."

Typically: in-flight transaction reconciliation, interface replay in both directions, batch
and queue state, sequence and numbering repair, cache warming, and telling users what was lost.

For each, get the duration **and** whether it can run in parallel with system bring-up. The
parallel/serial distinction is usually the difference between meeting the MTD and missing it,
and nobody has ever been asked about it before.

#### 6. Concurrent processing (5 min)

NIST names it as a validation option; most systems cannot do it.

> "Could this run in two places at once during a recovery, even briefly?"

Usually no, for a good reason — a second writable copy diverges. Record the **reason**, since
NIST does not require the capability but the ISCP structure the ITSCP borrows expects the
plan to address it.

### Hand-offs

| Learned here | Belongs to | Action |
|---|---|---|
| A business impact you had not heard | `itscp-interview-business` | Record, flag as unconfirmed, let business confirm |
| Infrastructure detail contradicting discovery | `itscp-interview-infrastructure` | Record as `conflict`; do not overwrite |
| A validation step needing business sign-off | `itscp-interview-business` | Note the owner |

### Red flags

| Thought | Reality |
|---|---|
| "The architecture diagram is in the wiki, I'll use that" | Use it as the opening question, not the answer. Ask what changed |
| "They listed the interfaces, that's Appendix I done" | Not without a named external contact reachable outside the system |
| "Validation is obvious — check it's up" | Then no one has defined correct, and the declaration will be a guess |
| "WRT is roughly an hour" | Per activity, with parallelisability. "Roughly an hour" is not a plan |
| "They don't know the start order" | Then that is a MISSING with a named owner and a drill objective |
| "One engineer knows the whole bring-up, so we're fine" | You have documented a person, not a procedure. Record the deputy gap |

---

## What this segment has to come away with

19 answers, grouped by the section of the plan each one feeds. Read this before the session; the worksheet at the end is what you take into it.

Every one of them leaves the room with something written against it. An answer nobody in the room could give is a **name** — whoever can — which is a result and not a failure. A blank is neither.

### 2.1 System description

#### `system.name`

> "What is this application suite called in the systems that run it: the name on the servers, in the monitoring, in the change tickets?"

- **Records:** The system's technical name, as the plan's title and throughout
- **Answers:** application owner · **Shape:** free text
- **Note:** The name the environment uses. Where the business calls it something else, that goes in system.business_name and both appear in the plan.
- **Goes into:** docs/01-architecture.md 2
- **NIST:** 2.1 System Description (SP 800-34 Rev. 1 Appendix A.3, Sample Template for High-Impact Systems)

#### `system.component_terms`

> "You used a few words for parts of this that could mean more than one thing. Tell me what each of them means here, in your words, before I draw anything."

- **Records:** The words this organization uses for its own components, and what each one means
- **Answers:** application owner · **Shape:** several paragraphs, in their words
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** One word that means two things is the cheapest catastrophic mistake in a continuity design: a whole section gets written for the wrong layer and reads perfectly well. Ask before drawing, not after. If they cannot say, that is a MISSING with the application owner's name on it, not a guess.
- **Goes into:** docs/01-architecture.md
- **No NIST slot.** An element this toolkit carries deliberately; the answer in it is elicited like any other.

#### `system.releases`

> "What release is the application on, exactly, and what release is the database? If you are part way through an upgrade, tell me both."

- **Records:** The release of each major component, and any upgrade in flight
- **Answers:** application owner · **Shape:** free text
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** Say the numbers back. This is the fact most often carried as an assumption and it changes recovery mechanics more than almost anything else. A half-finished upgrade is the answer that matters most and the one people forget to mention.
- **Goes into:** docs/01-architecture.md, docs/11-inventory.md
- **NIST:** 2.1 System Description (SP 800-34 Rev. 1 Appendix A.3, Sample Template for High-Impact Systems)

#### `system.operating_systems`

> "What does each tier run on? And if any of it is a platform your recovery scripts would have to be written differently for, say so now."

- **Records:** The operating system of each tier, and what that constrains
- **Answers:** infrastructure owner · **Shape:** free text
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** Decides what language every recovery script is written in, and therefore who can run it at three in the morning. Read it back.
- **Goes into:** docs/01-architecture.md, docs/11-inventory.md
- **NIST:** 2.1 System Description (SP 800-34 Rev. 1 Appendix A.3, Sample Template for High-Impact Systems)

#### `system.instances`

> "Is this one production instance, or several? Separate ledgers, separate legal entities, anything split across sites?"

- **Records:** Whether the production environment is one instance or several, and how they are split
- **Answers:** application owner · **Shape:** several paragraphs, in their words
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** A second instance nobody mentioned changes the tier map, the recovery order and the cost. Ask it early and read the answer back.
- **Goes into:** docs/01-architecture.md, docs/02-mtd-tiers.md
- **NIST:** 2.1 System Description (SP 800-34 Rev. 1 Appendix A.3, Sample Template for High-Impact Systems)

### 1.1 Background

#### `system.business_name`

> "And what do the people who use it call it? The name that would appear in an email from Finance saying it is down."

- **Records:** The business-facing name for the same system
- **Answers:** business owner · **Shape:** free text
- **Note:** What the business calls it. The ITSCP is read by both audiences.
- **Goes into:** README.md, docs/00-plan-approval.md
- **No NIST slot.** An element this toolkit carries deliberately; the answer in it is elicited like any other.

### 1.2 Scope

#### `system.categorization`

> "Has this system ever been given an impact level or a data classification? If so, where is that recorded and what does it say?"

- **Records:** The impact level or data classification and where it is recorded
- **Answers:** governance/risk contact · **Shape:** free text
- **Note:** Impact level or data classification. Determines which controls are mandatory. If never categorized, that is itself the finding.
- **Goes into:** README.md, docs/02-mtd-tiers.md
- **NIST:** 1.2 Scope (SP 800-34 Rev. 1 Appendix A.3, Sample Template for High-Impact Systems)
- **Terminology:** ISO 22301 uses a different categorization vocabulary (practice guide; not verified)

#### `system.impact_level`

> "Of low, moderate and high, which one is this system's availability impact? Not what you would choose today: what is written down. If nothing is, say so and we record that."

- **Records:** The assigned availability impact level, which selects the template this plan is graded against
- **Answers:** governance/risk contact · **Shape:** one of `low`, `moderate`, `high`
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** Three answers are legal and 'nobody ever assigned one' is not among them: an uncategorized system leaves this MISSING with the governance contact owing it, which is the honest record and the finding an auditor wants. The answer decides which of NIST's three sample templates the plan is graded against, and therefore what letter each of its appendices carries. Uncategorized, the plan keeps the high-impact lettering, because that template is the superset and an auditor with no stated level grades against it.
- **Goes into:** README.md, docs/02-mtd-tiers.md, docs/07-standards-alignment.md
- **NIST:** 1.2 Scope (SP 800-34 Rev. 1 Appendix A.3, Sample Template for High-Impact Systems)

### 1.3 Assumptions

#### `system.assumptions`

> "What are we taking as read about this environment that I have not asked you about directly? Take them one at a time, and for each one tell me what changes if it turns out to be wrong."

- **Records:** Each stated assumption, what breaks if it is wrong, who confirms it and by when
- **Answers:** lead engineer · **Shape:** one row per item, columns `assumption` | `impact_if_wrong` | `owner` | `confirm_by`
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** An assumption is a fact nobody confirmed, so every row here is a question somebody did not get asked. Read each one back. The owner and the date are not decoration: a table of unowned assumptions is a list of things that will still be assumptions at the next review, and one of them will be the one that was wrong.
- **Goes into:** docs/01-architecture.md, checklists/risk-register.md
- **NIST:** 1.3 Assumptions (SP 800-34 Rev. 1 Appendix A.3, Sample Template for High-Impact Systems)

### 4.1 Sequence of recovery activities

#### `app.start_order`

> "If everything were off and you had to bring it up from cold, what would you start first, and what would break if you started it second?"

- **Records:** The component start order and what depends on what
- **Answers:** lead engineer · **Shape:** several paragraphs, in their words
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** Rarely written down, usually in one person's head. Capture verbatim. If only one engineer holds it, that is a deputy gap as well as a documentation gap.
- **Goes into:** runbooks/RB-01-switchover.md, docs/09 3
- **NIST:** 4.1 Sequence of Recovery Activities (SP 800-34 Rev. 1 Appendix A.3, Sample Template for High-Impact Systems)

### I. System interconnections

#### `app.interconnections`

> "Who sends you files, and who is waiting on files from you? What breaks on their side first?"

- **Records:** Each interconnection, its direction, transport, contact and whether it is replayable
- **Answers:** application owner · **Shape:** one row per item, columns `partner` | `direction` | `transport` | `contact` | `replayable`
- **Note:** Appendix I. A partner contact stored only inside the system being recovered is not a contact.
- **Goes into:** docs/12-interconnections.md
- **NIST:** APPENDIX I INTERCONNECTIONS TABLE (SP 800-34 Rev. 1 Appendix A.3, Sample Template for High-Impact Systems)

### F. System validation test plan

#### `app.validation_pack`

> "Once it is back up, what do you personally check before you would tell users it is working? How long does each check take, and who does it?"

- **Records:** Each validation check, its duration and its owner
- **Answers:** application owner · **Shape:** one row per item, columns `check` | `duration` | `who`
- **Note:** Appendix F. On the MTD critical path and routinely omitted from timings.
- **Goes into:** checklists/validation-pack.md
- **NIST:** APPENDIX E SYSTEM VALIDATION TEST PLAN (SP 800-34 Rev. 1 Appendix A.3, Sample Template for High-Impact Systems)

### Minimum business continuity objective per tier

#### `app.wrt_activities`

> "After the system is technically up but before the business can use it, what has to happen? Which of those can run while we are still bringing things up?"

- **Records:** Each work-recovery activity, its duration, and whether it runs in parallel with bring-up
- **Answers:** application owner · **Shape:** one row per item, columns `activity` | `duration` | `parallel_with_bringup`
- **Note:** The parallel/serial flag decides whether the MTD is achievable.
- **Goes into:** docs/10 3
- **These words are the toolkit's, not the room's.** They render as its own and are never presented as something anybody in the room said: Maximum tolerable downtime is recovery time plus work recovery time. The toolkit decomposes it that way so that a recovery which meets its technical target and still misses what the business can tolerate is visible on paper rather than at four in the morning.

### 5.1 Concurrent processing

#### `app.concurrent_processing`

> "During recovery, would you ever run the old and the new environment at the same time? If not, why not?"

- **Records:** Whether concurrent processing is performed, and the reason either way
- **Answers:** application owner · **Shape:** several paragraphs, in their words
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** Usually NOT_APPLICABLE. NIST does not require it; the plan must still address it, with the reason.
- **Goes into:** docs/10 3
- **NIST:** 5.1 Concurrent Processing (SP 800-34 Rev. 1 Appendix A.3, Sample Template for High-Impact Systems)

### 4.2 Recovery procedures

#### `app.recovery_procedures`

> "Talk me through the recovery as if I were doing it and you were not there. Give me the commands, in order, exactly as you would type them."

- **Records:** The recovery procedure at the level of what is actually typed, in order
- **Answers:** lead engineer · **Shape:** exact text, written down as dictated or not at all
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** Reproduced byte for byte or not at all. A paraphrased command is worse than no command, because it looks runnable. Where a step is a decision rather than a keystroke, say so in the block; where a step needs a value nobody has yet, leave the placeholder visible rather than inventing one. Read the block back to them before it is written down.
- **Goes into:** runbooks/RB-02-failover.md, runbooks/RB-01-switchover.md
- **NIST:** 4.2 Recovery Procedures (SP 800-34 Rev. 1 Appendix A.3, Sample Template for High-Impact Systems)

### 5.2 Validation data testing

#### `app.validation_data_tests`

> "Once it is back up, how would you satisfy yourself that the data is right, as opposed to the system being up? Who is the person whose word settles it?"

- **Records:** Each data validation check, what it proves and who signs it off
- **Answers:** application owner · **Shape:** one row per item, columns `check` | `what_it_proves` | `who_signs`
- **Note:** Not the same as the functional pack, and the difference is the point. A database opening read-write proves the system is up. Only somebody who runs the process can say the data is right, so the signature column names a person's role and never the infrastructure team.
- **Goes into:** checklists/validation-pack.md, docs/10-phase-reconstitution.md
- **NIST:** 5.2 Validation Data Testing (SP 800-34 Rev. 1 Appendix A.3, Sample Template for High-Impact Systems)

### Interface landing and replication of inbound data

#### `app.interface_landing`

> "Today, before we change anything: where do inbound files from other systems land, and does anything read them from somewhere that is not replicated?"

- **Records:** Where inbound interface data lands today and whether that location is replicated
- **Answers:** lead engineer · **Shape:** several paragraphs, in their words
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** Ask what it is, not what it should be. The recommended pattern is easy to write and useless without the current state beside it, and a design proposal in a description's clothes is how a plan ends up recovering an environment nobody has.
- **Goes into:** docs/12-interconnections.md
- **No NIST slot.** An element this toolkit carries deliberately; the answer in it is elicited like any other.

#### `app.unsafe_reruns`

> "After a failover, which scheduled jobs would be dangerous to run again, and which are safe to just resubmit?"

- **Records:** Each scheduled job, whether it is safe to resubmit, and what a second run does
- **Answers:** application owner · **Shape:** one row per item, columns `job` | `safe_to_resubmit` | `what_happens_if_it_runs_twice`
- **`safe_to_resubmit` is one of:** `safe`, `unsafe`, `nobody knows`
- **Note:** 'Nobody knows' is a legal answer and a useful one: it is the list somebody has to work through before the next drill. A job that pays suppliers twice is a worse outage than the one that caused the failover.
- **Goes into:** runbooks/RB-02-failover.md, docs/10-phase-reconstitution.md
- **No NIST slot.** An element this toolkit carries deliberately; the answer in it is elicited like any other.

### Measured durations on the recovery critical path

#### `app.reconfiguration_duration`

> "Has anyone ever timed the full reconfiguration of the application tier after a move, start to finish? What did it come out at?"

- **Records:** How long a full application-tier reconfiguration takes, measured
- **Answers:** lead engineer · **Shape:** a duration in hours
- **Then ask:** "Was that timed on a rehearsal or estimated from experience? And what is the longest it has ever taken?" It goes in the **what breaks at that number** column. An empty one makes the figure a guess, and the row is marked low confidence.
- **Note:** This figure usually carries the plan's whole design argument and usually arrives as a range somebody remembers. If it has never been timed, record that: an untimed step on the critical path is the reason the recovery misses its target by an afternoon.
- **Goes into:** docs/09-phase-recovery.md, runbooks/RB-01-switchover.md
- **No NIST slot.** An element this toolkit carries deliberately; the answer in it is elicited like any other.

---

## The worksheet

Print this. One line per answer, filled in as it is said rather than afterwards.

- **Never leave a cell blank.** No answer means write the name of who can give one.
- **Sure?** is how the answer arrived, not how plausible it sounds. H: they have measured it or read it off a screen while you waited. M: confident from experience, never measured. L: worked out in the room just now. Ask when you cannot tell.
- **What breaks at that number** is what makes a figure arguable rather than arbitrary. A duration with an empty cell beside it is a guess, and is marked L.
- Two people, two answers: **write both**, and write whose decision it is.

### 2.1 System description

| What it records | Answer | Who said it | Sure? | What breaks at that number |
|---|---|---|---|---|
| The system's technical name, as the plan's title and throughout (`system.name`) |  |  | H / M / L |  |
| The words this organization uses for its own components, and what each one means (`system.component_terms`) |  |  | H / M / L |  |
| The release of each major component, and any upgrade in flight (`system.releases`) |  |  | H / M / L |  |
| The operating system of each tier, and what that constrains (`system.operating_systems`) |  |  | H / M / L |  |
| Whether the production environment is one instance or several, and how they are split (`system.instances`) |  |  | H / M / L |  |

### 1.1 Background

| What it records | Answer | Who said it | Sure? | What breaks at that number |
|---|---|---|---|---|
| The business-facing name for the same system (`system.business_name`) |  |  | H / M / L |  |

### 1.2 Scope

| What it records | Answer | Who said it | Sure? | What breaks at that number |
|---|---|---|---|---|
| The impact level or data classification and where it is recorded (`system.categorization`) |  |  | H / M / L |  |
| The assigned availability impact level, which selects the template this plan is graded against (`system.impact_level`) |  |  | H / M / L |  |

### 1.3 Assumptions

**Each stated assumption, what breaks if it is wrong, who confirms it and by when** (`system.assumptions`) — one row each, add as many as the room needs

| assumption | impact_if_wrong | owner | confirm_by | Who said it | Sure? |
|---|---|---|---|---|---|
|   |   |   |   |  | H / M / L |
|   |   |   |   |  | H / M / L |
|   |   |   |   |  | H / M / L |

### 4.1 Sequence of recovery activities

| What it records | Answer | Who said it | Sure? | What breaks at that number |
|---|---|---|---|---|
| The component start order and what depends on what (`app.start_order`) |  |  | H / M / L |  |

### I. System interconnections

**Each interconnection, its direction, transport, contact and whether it is replayable** (`app.interconnections`) — one row each, add as many as the room needs

| partner | direction | transport | contact | replayable | Who said it | Sure? |
|---|---|---|---|---|---|---|
|   |   |   |   |   |  | H / M / L |
|   |   |   |   |   |  | H / M / L |
|   |   |   |   |   |  | H / M / L |

### F. System validation test plan

**Each validation check, its duration and its owner** (`app.validation_pack`) — one row each, add as many as the room needs

| check | duration | who | Who said it | Sure? |
|---|---|---|---|---|
|   |   |   |  | H / M / L |
|   |   |   |  | H / M / L |
|   |   |   |  | H / M / L |

### Minimum business continuity objective per tier

**Each work-recovery activity, its duration, and whether it runs in parallel with bring-up** (`app.wrt_activities`) — one row each, add as many as the room needs

| activity | duration | parallel_with_bringup | Who said it | Sure? |
|---|---|---|---|---|
|   |   |   |  | H / M / L |
|   |   |   |  | H / M / L |
|   |   |   |  | H / M / L |

### 5.1 Concurrent processing

| What it records | Answer | Who said it | Sure? | What breaks at that number |
|---|---|---|---|---|
| Whether concurrent processing is performed, and the reason either way (`app.concurrent_processing`) |  |  | H / M / L |  |

### 4.2 Recovery procedures

| What it records | Answer | Who said it | Sure? | What breaks at that number |
|---|---|---|---|---|
| The recovery procedure at the level of what is actually typed, in order (`app.recovery_procedures`) |  |  | H / M / L |  |

### 5.2 Validation data testing

**Each data validation check, what it proves and who signs it off** (`app.validation_data_tests`) — one row each, add as many as the room needs

| check | what_it_proves | who_signs | Who said it | Sure? |
|---|---|---|---|---|
|   |   |   |  | H / M / L |
|   |   |   |  | H / M / L |
|   |   |   |  | H / M / L |

### Interface landing and replication of inbound data

| What it records | Answer | Who said it | Sure? | What breaks at that number |
|---|---|---|---|---|
| Where inbound interface data lands today and whether that location is replicated (`app.interface_landing`) |  |  | H / M / L |  |

**Each scheduled job, whether it is safe to resubmit, and what a second run does** (`app.unsafe_reruns`) — one row each, add as many as the room needs

| job | safe_to_resubmit | what_happens_if_it_runs_twice | Who said it | Sure? |
|---|---|---|---|---|
|   |   |   |  | H / M / L |
|   |   |   |  | H / M / L |
|   |   |   |  | H / M / L |

### Measured durations on the recovery critical path

| What it records | Answer | Who said it | Sure? | What breaks at that number |
|---|---|---|---|---|
| How long a full application-tier reconfiguration takes, measured (`app.reconfiguration_duration`) |  |  | H / M / L |  |
