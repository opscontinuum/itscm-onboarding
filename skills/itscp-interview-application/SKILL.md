---
name: itscp-interview-application
description: Use when a continuity plan needs its system description, when the interfaces and interconnections of an application must be documented, when someone must define what proves a recovered system is actually correct, or when work recovery time and batch reprocessing after a failover need scoping.
---

# itscp-interview-application

The system as the people who run it understand it. Produces §2.1 System Description, Appendix I
interconnections, Appendix F the validation test plan, and the work recovery time activities
that decide whether the MTD is achievable at all.

**Read first:** `skills/_method/interview-method.md`.

**Interviewee:** the application owner — whoever is accountable for the application working,
not for the infrastructure under it. In an ERP context this is usually the functional lead or
applications DBA rather than the cloud team.

**Bring the lead engineer, and the backup lead engineer if there is one.** Sections 2 and 5
below ask what actually happens when the system is brought up, and the owner is accountable for
that rather than practised at it. If the only person who can answer section 2 is one engineer,
say so: that is a deputy gap as well as an undocumented start order, and it belongs in the
roster finding rather than only in the notes.

**Time:** 90 minutes. Bring the discovery inventory; it halves the session.

---

## Open with the inventory, not a blank page

If `itscp-discover` has run, start by showing what was found:

> "Here's what I found in the tenancy. Which of these is yours, what's each one for, and
> what's missing from this list?"

This is a far better opening than "describe your system". It is concrete, it surfaces the
resources nobody could name, and the **missing** half is where the findings live — the
instance nobody owns, the bucket that predates the current team, the standby that was
supposed to exist.

---

## What to elicit

### 1. System identity (10 min)

| Field | Why |
|---|---|
| System name, and what the business calls it | Both. The ITSCP is read by both audiences |
| Version and platform | Determines which recovery procedures apply at all |
| System owner, and the authorising official if one exists | §2.1; the reassessment decision at Reconstitution |
| Data classification / impact level, if categorised | NIST ISCP §1.2 scope in the crosswalk; drives which controls are required |
| User population — who, how many, where | Notification scope; the load a recovered system must carry |

If the system has never been formally categorised, that is a `MISSING` with the governance
owner named, not a value you assign.

### 2. Architecture as the application sees it (20 min)

Not the cloud topology — the *application* topology. Tiers, where state lives, what is
stateless, what must be brought up in what order, and what breaks if that order is wrong.

The question that finds the real dependency:

> "If you brought this up in the wrong order, what would break, and how would you know?"

Order-of-operations knowledge is almost never written down and is almost always in one
person's head. Capture it verbatim, and record **whose** head, because that name is the
plan's dependency. Then ask the deputy question:

> "If they were on leave the week this happened, who else has actually done this?"

### 3. Interconnections — Appendix I (25 min)

The section most likely to be incomplete, and the one that causes the most damage when it is.

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

### 4. Validation — Appendix F (20 min)

The pass list. Not "is the database up" but "is the business correct".

> "After a failover, what would you personally check before telling people it's safe to use?"

Push for specifics: a named transaction, a report whose total is known, a batch job whose
output can be compared. Then:

> "How long does that take, and who has to be awake to do it?"

Validation is on the critical path of the MTD and is routinely forgotten in the timings.
A validation pack requiring four people over two hours turns a 60-minute RTO into a
3-hour recovery, and the business signed for the shorter number.

### 5. Work recovery time (15 min)

The activities between "the system is up" and "the business is working".

> "We've failed over and lost twelve minutes of transactions. Walk me through everything
> that has to happen before people can safely work again."

Typically: in-flight transaction reconciliation, interface replay in both directions, batch
and queue state, sequence and numbering repair, cache warming, and telling users what was lost.

For each, get the duration **and** whether it can run in parallel with system bring-up. The
parallel/serial distinction is usually the difference between meeting the MTD and missing it,
and nobody has ever been asked about it before.

### 6. Concurrent processing (5 min)

NIST names it as a validation option; most systems cannot do it.

> "Could this run in two places at once during a recovery, even briefly?"

Usually no, for a good reason — a second writable copy diverges. Record the **reason**, since
NIST does not require the capability but the ISCP structure the ITSCP borrows expects the
plan to address it.

---

## Output

Writes `system.*` and `app.*`: identity, categorization, architecture and start order,
interconnection register, validation pack with durations and owners, WRT activities with
parallelisability, concurrent-processing determination.

Renders `docs/01-architecture.md` §2, `docs/12-interconnections.md`,
`checklists/validation-pack.md`.

## Hand-offs

| Learned here | Belongs to | Action |
|---|---|---|
| A business impact you had not heard | `itscp-interview-business` | Record, flag as unconfirmed, let business confirm |
| Infrastructure detail contradicting discovery | `itscp-interview-infrastructure` | Record as `conflict`; do not overwrite |
| A validation step needing business sign-off | `itscp-interview-business` | Note the owner |

## Red flags

| Thought | Reality |
|---|---|
| "The architecture diagram is in the wiki, I'll use that" | Use it as the opening question, not the answer. Ask what changed |
| "They listed the interfaces, that's Appendix I done" | Not without a named external contact reachable outside the system |
| "Validation is obvious — check it's up" | Then no one has defined correct, and the declaration will be a guess |
| "WRT is roughly an hour" | Per activity, with parallelisability. "Roughly an hour" is not a plan |
| "They don't know the start order" | Then that is a MISSING with a named owner and a drill objective |
| "One engineer knows the whole bring-up, so we're fine" | You have documented a person, not a procedure. Record the deputy gap |
