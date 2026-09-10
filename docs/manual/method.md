# The method

> **Generated file.** It is assembled from the skills, the question bank and `GETTING-STARTED.md` by `plugin/itscp_manual.py`, and an edit made here is deleted by the next regeneration. Change the source and run `python3 plugin/itscp_manual.py`.

Read this before the first interview. It is the discipline every phase is run under, and it is the same file the skills read.

---

## The elicitation discipline

Every `itscp-interview-*` skill follows this file. It is the elicitation discipline, written
once. If a skill's own instructions and this file disagree, this file wins — the skills carry
the *questions*, this file carries the *method*.

The method exists because the failure mode of an AI-assisted plan is not a wrong answer. It
is a **plausible answer nobody gave**. A generated ITSCP that says "RTO: 4 hours" when no human
ever said four hours is worse than one that says "RTO: MISSING — owner: Head of Finance
Systems", because the first cannot be audited and will be believed.

---

### The Iron Rule

> **A fact enters the answer store only when a human said it, a read-only API returned it, or
> it is marked MISSING. There is no fourth source.**

Not "inferred from context". Not "a reasonable default for an organization of this size". Not
"consistent with what they said about the other tier". If nobody said it and no API returned
it, its status is `MISSING` and it names an owner.

**Violating the letter of this rule is violating the spirit of it.** The interviewee will
often be happy for you to guess — "you probably know better than me, put whatever's normal."
That is not consent to invent; it is a `MISSING` with a named owner and a reason
(`interviewee deferred to author`). Write that down and move on.

---

### Every field starts REFUTED

Borrowed directly from the compliance-audit skill in the reference repository, where
every compliance requirement starts refuted until a quoted sentence moves it.

| Status | Means | Requires |
|---|---|---|
| `MISSING` | Default. Nobody has answered. | An `owner` — the person or role who can answer |
| `ANSWERED` | A human said it, or a read-only API returned it | `value`, `provenance`, `confidence` |
| `DEFERRED` | Deliberately postponed with a date | `owner`, `due`, and the reason |
| `NOT_APPLICABLE` | Genuinely does not apply to this system | The **reason**, never the interviewer's opinion alone |

A field is never silently skipped. An interview that ends with forty `MISSING` fields has
succeeded at its real job — telling the organization what it does not know — provided every
one of them names an owner.

---

### Ask for the observable, not the abstraction

**People do not know their RTO. They know their pain.** Asking "what is your recovery time
objective for Order Management?" produces a number the interviewee reverse-engineered from
what they think you want to hear, in the meeting, under time pressure. It will be wrong and
it will be signed.

Ask instead for something they have actually experienced or can vividly imagine:

| Do not ask | Ask |
|---|---|
| "What's your RTO?" | "It's 9am Tuesday and this is down. Who calls you first, and how long before they do?" |
| "What's your RPO?" | "If we recovered to fifteen minutes before the failure, what work would people have to redo, and who would have to redo it?" |
| "Is this system critical?" | "Walk me through what stops if it's down for an hour. Then for a day." |
| "What's your MTD?" | "At what point does this stop being an IT problem and become something the CEO hears about?" |
| "Who owns this?" | "If this broke at 2am, whose phone rings? And if they don't answer?" |
| "Do you have manual workarounds?" | "Last time this was down, what did people actually do? Did anyone write it on paper?" |
| "What are your interconnections?" | "Who sends you files, and who's waiting on files from you? What breaks on their side first?" |

The abstraction is what you *record*. The observable is what you *ask*.

---

### Never accept a number without a mechanism

A number with no mechanism behind it is a guess wearing a suit. When someone gives you a
figure, ask what changes on either side of it:

> "You said four hours. What happens at hour five that doesn't happen at hour three?"

Three possible outcomes, all useful:

1. **They name the mechanism** — "the overnight bank file cuts at 6pm, if we're not up by then
   we miss a day's settlement." Record the number **and** the mechanism. The mechanism is
   what survives when the number is renegotiated.
2. **They revise the number** — "actually, thinking about it, it's really 6pm, so it depends
   what time it breaks." Excellent. That is a *time-dependent* MTD and it is more truthful
   than any constant.
3. **They cannot say** — the number is `confidence: low`, and the mechanism field is `MISSING`
   with them as owner. Do not launder a guess into a design target.

**Record the mechanism in its own field.** In the reference repository, every MTD figure is a
design target that becomes a commitment only when a drill measures it. The mechanism is what
makes the target arguable rather than arbitrary.

---

### One question at a time

The interviewee is a busy human, often on a call, often with less context than you. Batched
questions get batched answers: the first is answered, the rest are skimmed, and you cannot
tell which is which afterwards.

Ask one. Wait. Read the answer back if it is load-bearing. Then ask the next.

The exception is a **menu** — offering three or four concrete options for a single decision is
one question, not four, and it is usually easier to answer than an open prompt. Prefer menus
whenever the answer space is genuinely small and known.

---

### "I don't know" is data, and it is often the most valuable answer

When an interviewee does not know, you have found something more useful than an answer: an
organizational gap with a name on it. Capture it properly.

```
status: MISSING
owner: "Head of Treasury Operations"        # who WOULD know
notes: "Business owner did not know whether the bank file has a hard cut-off.
        Raised 2026-09-02; Treasury to confirm."
```

Then **keep going**. Do not stall the interview on one unknown, and never fill it to keep
momentum. An interview that surfaces twelve named unknowns in an hour has done more for the
organization than one that produced twelve confident inventions.

---

### Separate what they know from what they are guessing

Every `ANSWERED` field carries a confidence, and you assign it from how the answer arrived,
not from how plausible it sounds:

| Confidence | Signal |
|---|---|
| `high` | They have measured it, lived it, or read it off a system while you waited |
| `medium` | They are confident from experience but have not measured it |
| `low` | They are reasoning it out in the moment, or hedged ("probably", "I'd think", "call it") |

**Ask when you cannot tell.** "Is that something you've measured, or is it your best read?" is
not a rude question — it is the question that determines whether the resulting figure can be
put in front of an auditor. Interviewees almost always answer it honestly and are usually
relieved to be asked.

Low confidence is not a failure. It is an accurate label, and it tells the drill program
what to measure first.

---

### Read back before you write

Before recording anything load-bearing — a tier assignment, an MTD, a declaration authority, a
named succession — say it back in one sentence and get a yes:

> "So: if Order Management is down past 6pm on a weekday you miss the bank cut-off, and that's
> the point this stops being recoverable the same day. Have I got that right?"

Read-back catches the two most common errors at the moment they are cheap: you misheard, or
they misspoke. It also creates the sentence you will quote in the generated document, which
means the plan ends up written in the business's own words rather than yours.

---

### Provenance on every fact

Every `ANSWERED` field records where it came from. This is the direct analog of the citation
discipline in the reference repository, where every claim about product behavior carries a
source and every untraceable claim is tagged.

| Provenance form | Use |
|---|---|
| `interview:<role>:<YYYY-MM-DD>` | A human said it. Role, not name — the store is shared |
| `oci-discovery:<operation>` | A read-only API returned it, e.g. `oci-discovery:ListVolumeGroupReplicas` |
| `document:<path-or-name>` | Taken from an existing document the organization supplied |
| `operator` | The person running the toolkit supplied it about themselves |

There is no provenance value meaning "the assistant worked it out". If you worked it out, it
is not a fact; it is either a `MISSING` or a clearly-labeled engineering judgment written
into the generated document's *Unverified statements* section — never into the answer store.

---

### Interviews resume; they do not restart

These conversations are long and the people in them are interruptible. After **every**
answered field, write to the store. Never batch the write to the end of the interview.

On entry, read the store first and skip everything already `ANSWERED`, saying so:

> "I've got 14 of 23 fields already — 9 from the infrastructure interview and 5 from
> discovery. We need about 20 minutes for the rest."

Re-asking an answered question is the fastest way to lose a busy interviewee's goodwill and
the second-fastest way to introduce a contradiction.

---

### Contradictions are surfaced, never resolved silently

Two interviewees will disagree. The business owner says four hours; the application owner says
the batch cannot be rebuilt in under a day. **Do not average them, do not pick the more
credible speaker, and do not quietly keep the first one.**

```
status: ANSWERED
value: "4h"
provenance: "interview:business-owner:2026-09-02"
confidence: low
conflict:
  value: ">=24h"
  provenance: "interview:application-owner:2026-09-03"
  notes: "Application owner states batch reprocessing alone exceeds the stated MTD.
          Unresolved. Owner: business owner. Blocks tier sign-off."
```

Flag it to the orchestrator, name whose decision it is, and let the generated document carry
the conflict openly. A plan with a visible, owned contradiction is honest. A plan where one
side was silently dropped is a plan that fails in exactly that place.

---

### Red flags — stop and re-read this file

| Thought | Reality |
|---|---|
| "They said to use whatever's normal" | That is a MISSING with `interviewee deferred to author`, not permission to invent |
| "It's obvious from what they said about the other tier" | Inference is not elicitation. Ask, or mark MISSING |
| "I'll put a placeholder and we'll fix it later" | Placeholders that look like values are the failure this method exists to prevent. `{name}` is fine; `4 hours` is not |
| "They're busy, I'll batch the last five questions" | Batched answers cannot be attributed. One at a time |
| "The number seems low but they were confident" | Record it with the mechanism. If there is no mechanism, record `confidence: low` |
| "Both interviewees are roughly saying the same thing" | "Roughly" is a contradiction you have not looked at yet |
| "This field doesn't really apply here" | NOT_APPLICABLE requires a stated reason, not a judgment call |
| "I already know this from the reference repo" | The reference repo describes a hypothetical corporation. It is not evidence about this one |

---

### What a finished interview looks like

- Every field in the skill's scope has a status. None are absent.
- Every `ANSWERED` field has provenance and confidence.
- Every `MISSING` and `DEFERRED` field names an owner.
- Every number that matters has a mechanism beside it, or is explicitly `confidence: low`.
- Contradictions with other interviews are recorded, with the decision owner named.
- A closing summary was read back and confirmed: what was captured, what is outstanding, who
  owns each gap, and what happens next.

---

## Recording an answer by hand

One `answers.toml` per plan, one table per field, written as the answer arrives rather than at the end of the session. **The file is gitignored and must stay that way:** it accumulates names, telephone numbers, identifiers, downtime figures and the organization's weak points, and it is the most sensitive thing the engagement produces.

A key that is absent is unanswered. There is no null and no empty stand-in.

```toml
# Answered, with the mechanism the figure depends on.
[facts."business.mtd.tier0"]
status = "ANSWERED"
value = "8h"
mechanism = "The overnight bank file cuts at 18:00. Missing it loses a day of settlement."
provenance = "interview:business-owner:2026-09-10"
confidence = "medium"
readback = "confirmed"

# Nobody in the room knew. This is a result, not a blank.
[facts."continuity.declaration_authority"]
status = "MISSING"
owner = "business owner"
notes = "Nobody present could name who declares. Raised 2026-09-10."

# Postponed on purpose, with a date and a reason.
[facts."infra.failover_cost"]
status = "DEFERRED"
owner = "infrastructure owner"
due = "2026-10-01"
reason = "Awaiting the standby quote from the account team."

# Two people, two answers. Both are recorded and the decision is owned.
[facts."business.rto"]
status = "ANSWERED"
value = "4h"
provenance = "interview:business-owner:2026-09-10"
confidence = "low"

[facts."business.rto".conflict]
value = ">=24h"
provenance = "interview:application-owner:2026-09-11"
decision_owner = "business owner"
notes = "Application owner states batch reprocessing alone exceeds the stated target."
```

### Every field of a record

| Field | What it holds |
|---|---|
| `key` | The field being answered. One of the keys in this manual's checklists, and never anything else. |
| `status` | `MISSING`, `ANSWERED`, `DEFERRED` or `NOT_APPLICABLE`. Every field carries one; none are absent. |
| `value` | What they said. Absent on anything but `ANSWERED`. |
| `mechanism` | What changes on either side of a figure. Required on every duration, count and currency amount. |
| `provenance` | Where it came from: `interview:<role>:<YYYY-MM-DD>`, `oci-discovery:<Operation>`, `document:<path>` or `operator`. |
| `confidence` | `high`, `medium` or `low`, assigned from how the answer arrived rather than from how plausible it sounds. |
| `owner` | The role who can answer. Required on `MISSING` and `DEFERRED`; a gap with no owner is not a finding, it is a hole. |
| `due` | When a `DEFERRED` answer is expected. A deferral with no date is a `MISSING` wearing a suit. |
| `reason` | Why a field is `DEFERRED` or `NOT_APPLICABLE`. Never the interviewer's opinion on its own. |
| `notes` | Anything a later reader needs: who was in the room, what was contested, what the answer depends on. |
| `readback` | `not_required`, `confirmed` or `corrected`. A draft nobody has confirmed is not an answer and does not belong here. |
| `conflict` | The other answer, when two people gave different ones: its value, its provenance, and the named owner of the decision. |
| `superseded` | What this answer replaced, and why. Corrections are appended; nothing is overwritten in place. |

Statuses: `MISSING`, `ANSWERED`, `DEFERRED`, `NOT_APPLICABLE`. Confidence: `high`, `medium`, `low`. Read-back: `not_required`, `confirmed`, `corrected`.

The seven roles an `owner` may name, each of which also owes a deputy: `business owner`, `application owner`, `lead engineer`, `infrastructure owner`, `DR process owner`, `governance/risk contact`, `signing authority`.

---

## The store's own rules

One file per plan: `.itscm/answers.yaml` in the generated repository. Every interview reads
it, every interview appends to it, and every generated document renders from it.

**It is gitignored by default and must stay that way.** It accumulates names, phone numbers,
OCIDs, MTD figures, incident narratives and organizational weak points. It is the most
sensitive file the toolkit produces.

---

### Why a store at all

Three problems it solves, all of which appear within the first hour of real use:

1. **Interviews are interrupted.** A business owner gives you 40 minutes and leaves. Without a
   store you restart; with one you resume mid-question.
2. **The same fact has two askers.** The application owner and the infrastructure owner both
   know the database name. Without a store you ask twice, look disorganised, and create a
   contradiction you then have to reconcile.
3. **Regeneration must not require re-interviewing.** Fix a template, re-render, done. If the
   answers live only in the generated prose, every correction is archaeology.

---

### Shape

Flat, dotted keys. Greppable, diffable, mergeable, and readable by a human who has never seen
the toolkit.

```yaml
meta:
  schema_version: 1
  system_name: "EBS Production"
  created: "2026-09-02"
  last_updated: "2026-09-03"

facts:
  business.mtd.tier0:
    status: ANSWERED            # MISSING | ANSWERED | DEFERRED | NOT_APPLICABLE
    value: "2h"
    mechanism: "Bank payment file cuts at 18:00; missing it defers settlement one day."
    provenance: "interview:business-owner:2026-09-02"
    confidence: medium
    owner: null
    due: null
    notes: null

  business.mbco.tier0:
    status: MISSING
    value: null
    provenance: null
    confidence: null
    owner: "Head of Finance Systems"
    due: null
    notes: "What must be usable during work recovery, as opposed to fully restored.
            Business owner asked for time to consult Treasury."

  infra.standby.region:
    status: ANSWERED
    value: "us-phoenix-1"
    provenance: "oci-discovery:ListCloudVmClusters"
    confidence: high
    owner: null
```

#### Field rules

| Field | Rule |
|---|---|
| `status` | Always present. Never absent, never blank |
| `value` | Present only when `status: ANSWERED`. `null` otherwise |
| `mechanism` | Required for every duration, threshold or currency figure. See the method file |
| `provenance` | Required when `ANSWERED`. Never `assistant`, never `inferred` |
| `confidence` | Required when `ANSWERED`. `high`, `medium` or `low` |
| `owner` | Required when `MISSING` or `DEFERRED`. A role from the vocabulary below, not a person's name |
| `due` | Required when `DEFERRED` |
| `notes` | Free text. Where the reason for `NOT_APPLICABLE` goes |
| `conflict` | Present only when two sources disagree. Never resolved silently |

#### Owner vocabulary

`owner` names a role from the Phase 0 roster rather than a person, so the store stays shareable
and survives a leaver. The permitted values, and the deputy value for each:

| Role value | Deputy value |
|---|---|
| `business owner` | `business owner deputy` |
| `application owner` | `application owner deputy` |
| `lead engineer` | `lead engineer deputy` |
| `infrastructure owner` | `infrastructure owner deputy` |
| `DR process owner` | `DR process owner deputy` |
| `governance/risk contact` | `governance/risk contact deputy` |
| `signing authority` | `signing authority deputy` |

Use the deputy value when the primary is unreachable and the deputy now owes the answer. A role
whose deputy has no name does not block the field, but the missing deputy is itself a finding,
raised by `itscp-build` at Phase 0 and reconciled against the line of succession by
`itscp-interview-continuity`. Anything genuinely outside this list means the
roster is wrong, so fix the roster rather than inventing an eighth owner.

#### Key namespaces

| Prefix | Owned by | Feeds |
|---|---|---|
| `system.*` | `itscp-interview-application` | §1 Introduction, §2.1 System description |
| `business.*` | `itscp-interview-business` | Appendix K BIA, MTD tiers, Appendix E workarounds |
| `app.*` | `itscp-interview-application` | §2.1, Appendix F validation, Appendix I interconnections |
| `infra.*` | `itscp-interview-infrastructure` + `itscp-discover` | Architecture, replication, Appendix C, Appendix H |
| `continuity.*` | `itscp-interview-continuity` | §2.3 roles, §3.1 activation, §3.2 notification, §3.3 assessment, §4.3 escalation |
| `governance.*` | `itscp-interview-governance` | Approval, categorization, review cadence, Appendix J TT&E |
| `discovery.*` | `itscp-discover` only | Raw inventory; never written by an interview |

Section and appendix numbers in the *Feeds* column are NIST ISCP crosswalk references, not
numbering the ITSCP owns. The `itscp-method-coverage-map` skill carries the crosswalk and states
the relationship.

A skill writes only within its own prefix. If an interview learns something outside its
prefix — and it will — it records the fact **and** notes which interview owns the key, so the
owning skill confirms it rather than inheriting it unread.

---

### Writing rules

**Write after every answer, not at the end.** An interview that ends unexpectedly must leave
the store consistent.

**Never delete a fact to change it.** Supersede in place and keep the prior value:

```yaml
  business.mtd.tier0:
    status: ANSWERED
    value: "6h"
    provenance: "interview:business-owner:2026-09-10"
    confidence: high
    superseded:
      - value: "2h"
        provenance: "interview:business-owner:2026-09-02"
        reason: "Revised after Treasury confirmed the file cut-off is 22:00, not 18:00."
```

The reference repository keeps an append-only record of changes for the same reason: a
continuity plan whose numbers move without a trail cannot be audited, and the question
"when did this become six hours, and who said so?" is asked exactly once, in the worst week.

**Never write a value the toolkit produced.** Engineering judgments belong in the generated
document's *Unverified statements* section, attributed as judgments. The store holds only
what humans and read-only APIs said.

---

### Reading rules

- On entry, load the store and report coverage before asking anything.
- Skip `ANSWERED` fields. Re-ask only when the interviewee volunteers a correction, or when a
  `conflict` needs the owner's decision.
- `DEFERRED` fields past their `due` date are surfaced to the orchestrator, not silently
  re-asked.

---

### Coverage

Coverage is `ANSWERED + NOT_APPLICABLE` over total fields in scope. `itscp-build` reports it
per section and refuses to claim a section complete below 100%.

**Coverage is not quality.** A store at 100% coverage where two thirds of the fields are
`confidence: low` describes an organization that has guessed comprehensively. Report the
confidence distribution alongside coverage, always, and let the drill program aim at the
low-confidence figures first.

---

## What a complete plan contains

The authoritative list of what a complete plan contains. `itscp-build` reports against this
table and `itscp-audit` checks it. If a row has no skill, the toolkit does not yet cover it
and says so rather than quietly producing an incomplete plan.

Structure follows NIST SP 800-34 Rev. 1 Appendix A (Sample ISCP Templates) and §4.1–§4.5.

**What the toolkit produces is an ITSCP: an IT service continuity plan, the service-level
artefact of the ITIL service continuity management practice.** NIST SP 800-34 specifies an
Information System Contingency Plan (ISCP), a system-level artefact under a different
instrument. The ITSCP aligns *to* the ISCP structure; it is not one. The reference example
makes the same borrowing explicit through the crosswalk at `oci-itscp/docs/07-itil4-alignment.md`
§1a, and this map follows that crosswalk: the left-hand column of every table below names a
**NIST ISCP element**, and the right-hand column names the file in **our ITSCP** that carries
it. Write "the ITSCP" or "the plan" for what the toolkit produces, and "ISCP" only when
naming NIST's or FedRAMP's own artefact. Conflating the two inherits the wrong requirement
set in both directions: the plan acquires requirements it does not have and misses the ones
it does.

---

### Portfolio scope (above any single plan)

Elicited once for the organization, not once per system. Held in `portfolio.toml` rather than
in an answer store, because a register of systems is a different shape from a set of facts
about one.

| Element | Elicited by | Written to |
|---|---|---|
| System register: every system, its class and owners | `itscp-portfolio` | `portfolio.toml` |
| Comparative tier ranking and the budget it was ranked against | `itscp-portfolio` | `portfolio.toml` |
| Recovery waves and their concurrency limits | `itscp-portfolio` | `portfolio.toml` |
| Runtime, recovery and data dependencies between systems | `itscp-dependencies` | `portfolio.toml` |
| Cross-system coherence: inversions, cycles, wave order | `itscp_portfolio.validate` | audit report |

**A plan for one system in a portfolio of many is incomplete even at 100% coverage of the rows
below**, because none of them can see the system's neighbours.

### Front matter

| NIST ISCP element | Elicited by | Written to |
|---|---|---|
| Plan Approval statement | `itscp-interview-governance` | `docs/00-plan-approval.md` |
| Record of Changes | `itscp-build` (from git log) | `docs/00-record-of-changes.md` |

### 1. Introduction

| NIST ISCP element | Elicited by | Written to |
|---|---|---|
| 1.1 Background — why the plan exists, its objectives | `itscp-interview-governance` | `README.md`, `docs/00-plan-approval.md` |
| 1.2 Scope — FIPS 199 impact level, RTOs, alternate site and storage | `itscp-interview-governance` + `itscp-interview-business` | `README.md`, `docs/02-mtd-tiers.md` |
| 1.3 Assumptions — including what is explicitly *not* covered | `itscp-interview-infrastructure` | `docs/01-architecture.md` §1 |

### 2. Concept of Operations

| NIST ISCP element | Elicited by | Written to |
|---|---|---|
| 2.1 System description — architecture, locations, I/O and architecture diagrams | `itscp-interview-application` + `itscp-discover` | `docs/01-architecture.md` §2 |
| 2.2 Overview of the three phases | `itscp-build` (renders from the runbook set) | `docs/08`, `docs/09`, `docs/10` |
| 2.3 Roles and responsibilities — team structure, hierarchy, coordination, and a named deputy for every role | `itscp-build` (Phase 0 roster) + `itscp-interview-continuity` | `checklists/roles-and-responsibilities.md` |

### 3. Activation and Notification

| NIST ISCP element | Elicited by | Written to |
|---|---|---|
| 3.1 Activation criteria and procedure; who may activate | `itscp-interview-continuity` | `runbooks/RB-02-failover.md` §0, `checklists/dr-authority-matrix.md` |
| 3.2 Notification — call tree, methods, unreachable procedure | `itscp-interview-continuity` | `checklists/contact-roster.md` |
| 3.3 Outage assessment — procedure and the repair estimate | `itscp-interview-continuity` | `checklists/outage-assessment.md` |

### 4. Recovery

| NIST ISCP element | Elicited by | Written to |
|---|---|---|
| 4.1 Sequence of recovery activities, ordered by BIA priority | `itscp-interview-infrastructure` | `runbooks/RB-01`, `RB-02`, `docs/09` §3 |
| 4.2 Recovery procedures — step by step, nothing assumed | `itscp-interview-infrastructure` + `itscp-interview-application` | `runbooks/`, `scripts/` |
| 4.3 Recovery escalation and notification — triggers and thresholds | `itscp-interview-continuity` | `docs/09` §5 |

### 5. Reconstitution

| NIST ISCP element | Elicited by | Written to |
|---|---|---|
| 5.1 Concurrent processing (or a stated reason it is not performed) | `itscp-interview-application` | `docs/10` §3 |
| 5.2 Validation data testing | `itscp-interview-application` | `docs/10` §3, `runbooks/RB-01` §5 |
| 5.3 Validation functionality testing — the business's own pass list | `itscp-interview-business` | `docs/10` §3, validation pack |
| 5.4 Recovery declaration | `itscp-interview-continuity` | `docs/10` §4.2 |
| 5.5 User notification | `itscp-interview-continuity` | `checklists/contact-roster.md` |
| 5.6 Cleanup | `itscp-interview-infrastructure` | `docs/10` §4, `runbooks/RB-05` |
| 5.7 Offsite data storage (or stated not applicable) | `itscp-interview-infrastructure` | `docs/10` §4 |
| 5.8 Data backup after reconstitution | `itscp-interview-infrastructure` | `docs/10` §4.1 |
| 5.9 Event documentation and after-action report | `itscp-interview-governance` | `evidence/`, after-action template |
| 5.10 Deactivation | `itscp-interview-continuity` | `docs/10` §4.2 |

### Appendices

| NIST ISCP appendix | Elicited by | Written to |
|---|---|---|
| A. Personnel contact information, primary and deputy for every role | `itscp-build` (Phase 0 roster) + `itscp-interview-continuity` | `checklists/contact-roster.md` §2 |
| B. Vendor contacts, offsite storage and alternate site POCs | `itscp-interview-infrastructure` | `checklists/contact-roster.md` §5 |
| C. Alternate site, storage and telecommunications | `itscp-interview-infrastructure` | `docs/01` §5, `docs/03` |
| D. Detailed recovery procedures and checklists | `itscp-interview-infrastructure` | `runbooks/`, `checklists/pre-failover-precheck.md` |
| E. Alternate mission/business processing — manual workarounds | `itscp-interview-business` | `checklists/manual-workarounds.md` |
| F. System validation test plan | `itscp-interview-application` | `checklists/validation-pack.md` |
| G. Diagrams — architecture and I/O | `itscp-discover` + `itscp-interview-infrastructure` | `docs/01` §2, `docs/diagrams/` |
| H. Hardware, software and firmware inventory | `itscp-discover` | `docs/11-inventory.md` |
| I. System interconnections | `itscp-interview-application` only. `itscp-discover` collects the raw data but does not render it, see *Not yet covered* | `docs/12-interconnections.md` |
| J. Test, training and exercise documentation | `itscp-interview-governance` | `checklists/contingency-training.md`, `runbooks/RB-04` |
| K. Business impact analysis | `itscp-interview-business` | `docs/02-mtd-tiers.md`, `checklists/tier-assignment-workshop.md` |
| L. Vendor SLAs and reciprocal agreements | `itscp-interview-governance` | `checklists/contact-roster.md` §5 |

---

### Beyond NIST

Not required by SP 800-34, included because the reference repository demonstrates their value
and because auditors working to ISO 22301 ask for them.

| Element | Elicited by | Written to | Why |
|---|---|---|---|
| Minimum business continuity objective per tier | `itscp-interview-business` | `docs/02-mtd-tiers.md` | MTD says *when* service returns; MBCO says *how much of it* is acceptable meanwhile |
| Risk register | `itscp-interview-governance` | `checklists/risk-register.md` | Material assumptions and design risks, owned and reviewed rather than scattered |
| Plan review and maintenance cadence | `itscp-interview-governance` | `README.md` | Continuity plans decay; nothing else states when this one is reviewed |
| Cost model and posture economics | `itscp-interview-infrastructure` | `docs/05-cost-and-teardown.md` | Standby cost drives the tier the business can actually have |
| Citation and unverified-statement discipline | every skill | every document | The property that makes a generated plan auditable |

---

### Not yet covered

Stated so the toolkit does not imply completeness it lacks.

| Gap | Consequence |
|---|---|
| No elicitation for platform types other than Oracle EBS on OCI | The runbook templates assume Oracle Data Guard and OCI replication primitives. Other stacks get the structure but must supply their own procedures |
| No automated import of an existing plan | An organization with a plan in Word starts from interviews, not from its own document |
| Discovery covers OCI only | AWS, Azure, GCP and on-premises inventories are manual |
| Discovery does not render Appendix I | `itscp_discover_oci` writes `inventory.md`, `dr-resources.env`, `gaps.md` and `raw/`, and nothing else. The interconnection data is collected into `raw/*.json` and left unrendered, so the whole register comes from the application interview. The half discovery could have pre-filled is recalled in a meeting instead, which is where interfaces get missed |
