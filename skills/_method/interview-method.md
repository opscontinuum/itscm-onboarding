# The interview method

Every `itscp-interview-*` skill follows this file. It is the elicitation discipline, written
once. If a skill's own instructions and this file disagree, this file wins — the skills carry
the *questions*, this file carries the *method*.

The method exists because the failure mode of an AI-assisted plan is not a wrong answer. It
is a **plausible answer nobody gave**. A generated ISCP that says "RTO: 4 hours" when no human
ever said four hours is worse than one that says "RTO: MISSING — owner: Head of Finance
Systems", because the first cannot be audited and will be believed.

---

## The Iron Rule

> **A fact enters the answer store only when a human said it, a read-only API returned it, or
> it is marked MISSING. There is no fourth source.**

Not "inferred from context". Not "a reasonable default for an organisation of this size". Not
"consistent with what they said about the other tier". If nobody said it and no API returned
it, its status is `MISSING` and it names an owner.

**Violating the letter of this rule is violating the spirit of it.** The interviewee will
often be happy for you to guess — "you probably know better than me, put whatever's normal."
That is not consent to invent; it is a `MISSING` with a named owner and a reason
(`interviewee deferred to author`). Write that down and move on.

---

## Every field starts REFUTED

Borrowed directly from `skills/itscp-compliance-audit` in the reference repository, where
every compliance requirement starts refuted until a quoted sentence moves it.

| Status | Means | Requires |
|---|---|---|
| `MISSING` | Default. Nobody has answered. | An `owner` — the person or role who can answer |
| `ANSWERED` | A human said it, or a read-only API returned it | `value`, `provenance`, `confidence` |
| `DEFERRED` | Deliberately postponed with a date | `owner`, `due`, and the reason |
| `NOT_APPLICABLE` | Genuinely does not apply to this system | The **reason**, never the interviewer's opinion alone |

A field is never silently skipped. An interview that ends with forty `MISSING` fields has
succeeded at its real job — telling the organisation what it does not know — provided every
one of them names an owner.

---

## Ask for the observable, not the abstraction

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

## Never accept a number without a mechanism

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

## One question at a time

The interviewee is a busy human, often on a call, often with less context than you. Batched
questions get batched answers: the first is answered, the rest are skimmed, and you cannot
tell which is which afterwards.

Ask one. Wait. Read the answer back if it is load-bearing. Then ask the next.

The exception is a **menu** — offering three or four concrete options for a single decision is
one question, not four, and it is usually easier to answer than an open prompt. Prefer menus
whenever the answer space is genuinely small and known.

---

## "I don't know" is data, and it is often the most valuable answer

When an interviewee does not know, you have found something more useful than an answer: an
organisational gap with a name on it. Capture it properly.

```
status: MISSING
owner: "Head of Treasury Operations"        # who WOULD know
notes: "Business owner did not know whether the bank file has a hard cut-off.
        Raised 2026-09-02; Treasury to confirm."
```

Then **keep going**. Do not stall the interview on one unknown, and never fill it to keep
momentum. An interview that surfaces twelve named unknowns in an hour has done more for the
organisation than one that produced twelve confident inventions.

---

## Separate what they know from what they are guessing

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

Low confidence is not a failure. It is an accurate label, and it tells the drill programme
what to measure first.

---

## Read back before you write

Before recording anything load-bearing — a tier assignment, an MTD, a declaration authority, a
named succession — say it back in one sentence and get a yes:

> "So: if Order Management is down past 6pm on a weekday you miss the bank cut-off, and that's
> the point this stops being recoverable the same day. Have I got that right?"

Read-back catches the two most common errors at the moment they are cheap: you misheard, or
they misspoke. It also creates the sentence you will quote in the generated document, which
means the plan ends up written in the business's own words rather than yours.

---

## Provenance on every fact

Every `ANSWERED` field records where it came from. This is the direct analogue of the citation
discipline in the reference repository, where every claim about product behaviour carries a
source and every untraceable claim is tagged.

| Provenance form | Use |
|---|---|
| `interview:<role>:<YYYY-MM-DD>` | A human said it. Role, not name — the store is shared |
| `oci-discovery:<operation>` | A read-only API returned it, e.g. `oci-discovery:ListVolumeGroupReplicas` |
| `document:<path-or-name>` | Taken from an existing document the organisation supplied |
| `operator` | The person running the toolkit supplied it about themselves |

There is no provenance value meaning "the assistant worked it out". If you worked it out, it
is not a fact; it is either a `MISSING` or a clearly-labelled engineering judgement written
into the generated document's *Unverified statements* section — never into the answer store.

---

## Interviews resume; they do not restart

These conversations are long and the people in them are interruptible. After **every**
answered field, write to the store. Never batch the write to the end of the interview.

On entry, read the store first and skip everything already `ANSWERED`, saying so:

> "I've got 14 of 23 fields already — 9 from the infrastructure interview and 5 from
> discovery. We need about 20 minutes for the rest."

Re-asking an answered question is the fastest way to lose a busy interviewee's goodwill and
the second-fastest way to introduce a contradiction.

---

## Contradictions are surfaced, never resolved silently

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

## Red flags — stop and re-read this file

| Thought | Reality |
|---|---|
| "They said to use whatever's normal" | That is a MISSING with `interviewee deferred to author`, not permission to invent |
| "It's obvious from what they said about the other tier" | Inference is not elicitation. Ask, or mark MISSING |
| "I'll put a placeholder and we'll fix it later" | Placeholders that look like values are the failure this method exists to prevent. `{name}` is fine; `4 hours` is not |
| "They're busy, I'll batch the last five questions" | Batched answers cannot be attributed. One at a time |
| "The number seems low but they were confident" | Record it with the mechanism. If there is no mechanism, record `confidence: low` |
| "Both interviewees are roughly saying the same thing" | "Roughly" is a contradiction you have not looked at yet |
| "This field doesn't really apply here" | NOT_APPLICABLE requires a stated reason, not a judgement call |
| "I already know this from the reference repo" | The reference repo describes a hypothetical corporation. It is not evidence about this one |

---

## What a finished interview looks like

- Every field in the skill's scope has a status. None are absent.
- Every `ANSWERED` field has provenance and confidence.
- Every `MISSING` and `DEFERRED` field names an owner.
- Every number that matters has a mechanism beside it, or is explicitly `confidence: low`.
- Contradictions with other interviews are recorded, with the decision owner named.
- A closing summary was read back and confirmed: what was captured, what is outstanding, who
  owns each gap, and what happens next.
