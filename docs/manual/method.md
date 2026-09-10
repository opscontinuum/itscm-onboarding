# The method

> **Generated file.** It is assembled from the skills, the question bank and `GETTING-STARTED.md` by `plugin/itscp_manual.py`, and an edit made here is deleted by the next regeneration. Change the source and run `python3 plugin/itscp_manual.py`.

Read this before the first session. It is the discipline every phase is run under, and it is the same file the toolkit reads: it is about how people answer, which does not change when the facilitator is a person rather than a program.

---

## Capturing what the room says

There is no file to write and nothing to install. The answer store is the stack of worksheets, holding what the toolkit's store holds: the answer, who gave it, how sure they were, and what breaks at that number. Columns instead of keys. Where the pages that follow say *write it to the store*, they mean the sheet in front of you.

Every phase page ends with its own worksheet. They all have the same five columns:

| What it records | Answer | Who said it | Sure? | What breaks at that number |
|---|---|---|---|---|
| Maximum tolerable downtime for the tier 0 processes | 8h | Head of Finance Systems | M | Overnight bank file cuts at 18:00; missing it loses a day of settlement |
| Who declares a disaster | *nobody in the room knew — **Ops Director** to confirm* |  |  | Raised in session, unowned |
| Time to rebuild from backup | 6h | Lead engineer | L | Never measured. First drill objective |

Four rules, and the first is the one that makes the other three work.

1. **Never leave a cell blank.** An answer nobody has is a name, written in the answer column. A room that leaves twelve named unknowns has done more for the organization than one that leaves twelve confident inventions.
2. Write it as it is said. A worksheet filled in from memory at the end of the day is a worksheet nobody can attribute.
3. The Sure? column is about how the answer arrived, not how plausible it sounds. "Is that something you have measured, or is it your best read?" is not a rude question. It decides whether the figure can go in front of an auditor, and people are usually relieved to be asked.
4. Two answers means two rows, with the name of whoever decides between them. Do not average them, and do not quietly keep the more senior one.

---

## The elicitation discipline

### Running this without the toolkit

The technique below is the skills' own words, and the skills assume a loaded plugin. You do not have one. These are the substitutions in effect on this page.

| Where it says | In the room you |
|---|---|
| `itscp_discover_oci` | A read-only walk for one cloud provider. Bring the equivalent from whatever your teams already use: a console export, a CMDB extract, last quarter's architecture review. What generalises is the rule, not the tool — discovery never changes anything. |
| `itscp-build` | There is no generator in a tabletop. Phase 6 is you writing the documents, and [fields.md](fields.md) is the map of which answer goes into which one. |
| `portfolio.toml` | The register is the wall: one card per system, one line per dependency. The file is only how it gets stored if somebody types it up afterwards. |
| the answer store | The stack of worksheets. It holds the same things — the answer, who gave it, how sure they were — in columns rather than in keys. |
| "the store" | The worksheet in front of you. |

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

### One question at a time

The interviewee is a busy human, often on a call, often with less context than you. Batched
questions get batched answers: the first is answered, the rest are skimmed, and you cannot
tell which is which afterwards.

Ask one. Wait. Read the answer back if it is load-bearing. Then ask the next.

The exception is a **menu** — offering three or four concrete options for a single decision is
one question, not four, and it is usually easier to answer than an open prompt. Prefer menus
whenever the answer space is genuinely small and known.

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

### Read back before you write

Before recording anything load-bearing — a tier assignment, an MTD, a declaration authority, a
named succession — say it back in one sentence and get a yes:

> "So: if Order Management is down past 6pm on a weekday you miss the bank cut-off, and that's
> the point this stops being recoverable the same day. Have I got that right?"

Read-back catches the two most common errors at the moment they are cheap: you misheard, or
they misspoke. It also creates the sentence you will quote in the generated document, which
means the plan ends up written in the business's own words rather than yours.

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

### Interviews resume; they do not restart

These conversations are long and the people in them are interruptible. After **every**
answered field, write to the store. Never batch the write to the end of the interview.

On entry, read the store first and skip everything already `ANSWERED`, saying so:

> "I've got 14 of 23 fields already — 9 from the infrastructure interview and 5 from
> discovery. We need about 20 minutes for the rest."

Re-asking an answered question is the fastest way to lose a busy interviewee's goodwill and
the second-fastest way to introduce a contradiction.

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

### What a finished interview looks like

- Every field in the skill's scope has a status. None are absent.
- Every `ANSWERED` field has provenance and confidence.
- Every `MISSING` and `DEFERRED` field names an owner.
- Every number that matters has a mechanism beside it, or is explicitly `confidence: low`.
- Contradictions with other interviews are recorded, with the decision owner named.
- A closing summary was read back and confirmed: what was captured, what is outstanding, who
  owns each gap, and what happens next.

---

## What a complete plan contains

The full element list, so that phase 6 is assembly rather than invention.

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

### Not yet covered

Stated so the toolkit does not imply completeness it lacks.

| Gap | Consequence |
|---|---|
| No elicitation for platform types other than Oracle EBS on OCI | The runbook templates assume Oracle Data Guard and OCI replication primitives. Other stacks get the structure but must supply their own procedures |
| No automated import of an existing plan | An organization with a plan in Word starts from interviews, not from its own document |
| Discovery covers OCI only | AWS, Azure, GCP and on-premises inventories are manual |
| Discovery does not render Appendix I | `itscp_discover_oci` writes `inventory.md`, `dr-resources.env`, `gaps.md` and `raw/`, and nothing else. The interconnection data is collected into `raw/*.json` and left unrendered, so the whole register comes from the application interview. The half discovery could have pre-filled is recalled in a meeting instead, which is where interfaces get missed |

---

## Appendix — typing the worksheets up

**Optional, and not part of the exercise.** If the organization later adopts the toolkit, the worksheets transcribe into its answer store one row per record, and the cross-system checks then run for you. The columns map like this.

| Store field | Worksheet |
|---|---|
| `key` | The field. One of the keys in this manual's checklists, and never anything else. |
| `status` | `MISSING`, `ANSWERED`, `DEFERRED` or `NOT_APPLICABLE`. Every field carries one. |
| `value` | The **Answer** column. |
| `mechanism` | The **What breaks at that number** column. |
| `provenance` | The **Who said it** column, as `interview:<role>:<YYYY-MM-DD>`. |
| `confidence` | The **Sure?** column: `high`, `medium` or `low`. |
| `owner` | The name written in an unanswered row. Required on `MISSING` and `DEFERRED`. |
| `due` | When a deferred answer is expected. A deferral with no date is a gap in disguise. |
| `reason` | Why a row was deferred or ruled out. Never the facilitator's opinion alone. |
| `notes` | Who was in the room, what was contested, what the answer depends on. |
| `readback` | `not_required`, `confirmed` or `corrected`. What happened when you said it back. |
| `conflict` | The second answer, when two people gave different ones, and whose call it is. |
| `superseded` | What an answer replaced, and why. Corrections are appended, never rubbed out. |

Statuses: `MISSING`, `ANSWERED`, `DEFERRED`, `NOT_APPLICABLE`. Confidence: `high`, `medium`, `low`. Read-back: `not_required`, `confirmed`, `corrected`.

The seven roles a name may be recorded against, each of which also owes a deputy: `business owner`, `application owner`, `lead engineer`, `infrastructure owner`, `DR process owner`, `governance/risk contact`, `signing authority`.

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

### Reading rules

- On entry, load the store and report coverage before asking anything.
- Skip `ANSWERED` fields. Re-ask only when the interviewee volunteers a correction, or when a
  `conflict` needs the owner's decision.
- `DEFERRED` fields past their `due` date are surfaced to the orchestrator, not silently
  re-asked.
