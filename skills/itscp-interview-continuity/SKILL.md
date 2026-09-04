---
name: itscp-interview-continuity
description: Use when a continuity plan needs its roles, teams or line of succession defined, when it must be decided who can declare a disaster and on what criteria, when a call tree or notification procedure is needed, or when there is no procedure for assessing an outage and estimating how long it will last.
---

# itscp-interview-continuity

Who decides, who is told, and how anyone knows what they are deciding about. Produces §2.3
roles and succession, §3.1 activation criteria, §3.2 notification, §3.3 outage assessment,
§4.3 escalation thresholds, and §5.4 deactivation.

**Read first:** `skills/_method/interview-method.md`. Run **after** the application and
infrastructure interviews — escalation thresholds are meaningless until there are real
recovery steps to threshold, and a call tree is meaningless until you know who does the work.

**Interviewee:** the DR process owner, incident manager, or whoever would actually be running
the bridge at 3am, with their deputy in the room where one is named. If nobody holds that role,
you have found the most important gap in the engagement; say so before continuing.

**Bring the Phase 0 role roster.** The deputies named there and the succession elicited here are
two views of one fact, and this interview is where they get reconciled.

**Time:** 90 minutes.

---

## The one question this interview exists to answer

> **At 3am, with the primary region gone, who decides to fail over — and what do they need in
> front of them to decide?**

Everything below is that question decomposed. Most organisations have some of the pieces and
have never assembled them, so the interview frequently ends with the interviewee saying they
had not realised nobody owned the decision.

---

## Part 1 — Roles and succession (§2.3)

### Declaration authority

> "Right now, today, if this had to fail over — whose call is it?"

Then, immediately, the question that finds the real gap:

> "And if they're on a plane? And if the person after them is also unreachable?"

NIST is unambiguous: exactly one individual holds declaration authority, and a successor is
clearly identified. Elicit an **ordered** list with the interval after which authority passes,
and press until it terminates in someone who is always reachable.

Then check it against the Phase 0 roster. If the roster names one deputy and the succession
names a different person first, you have not found a wording difference; you have found two
groups with different beliefs about who takes over, which is exactly the disagreement that
surfaces at 3am. Record a `conflict`, name whose decision it is, and move on. Do not pick the
more credible list.

**Two failure modes to name explicitly if you see them:**

- **Nobody holds it.** Common. The organisation believes the decision would "be made by the
  incident team", which means it would be made by whoever felt boldest, or not at all.
- **Everybody holds it.** Also common, and worse. Concurrent declarations by different people
  are how an estate ends up half failed over.

### Separating deciding from doing

> "Is the person who decides also the person running the recovery?"

If yes, name the risk plainly: the decision gate gets compressed into whatever the recovery
work leaves time for. It is a legitimate choice for a small team — record it as a stated
choice with its consequence, not as an oversight.

### Teams, alternates and the deputy roster

Walk the candidate team list and, for each, ask who does it here. Expect several to collapse
into the same three people. That is normal and worth recording accurately rather than
flattering.

For every team: leader, alternate, second alternate.

> "Is the alternate someone who could actually do it, or someone who'd know who to call?"

Both are valid answers and they are very different plans. Record which.

Cover the technical roles explicitly, because they are the ones usually left with a single
name: the lead engineer running the recovery, and the backup lead engineer or lead developer
behind them. A runbook with one person who has executed it is a runbook with an availability
requirement on that person.

> "Which of these actions has exactly one person who has ever done it?"

That question finds the real gap faster than walking the roster does. **A role with no named
deputy is a finding, not an acceptable state.** NIST SP 800-34 Rev. 1 §3.4.6 says team leaders
"should have a designated alternate to act as the leader if the primary leader is unavailable".
Record it MISSING against the role holder. Do not
name a deputy on their behalf, and do not accept "whoever is on call" as one: an unnamed
deputy is the plausible-answer failure with a rota in front of it.

### The disruption may take the people too

> "If the event that takes the estate also takes your main office — does the recovery still
> have the people it needs?"

Then: is there anyone outside that geography who can execute, and is there a contracted vendor
fallback? Usually unanswered. Record as `MISSING` with an owner; it is a legitimate finding.

---

## Part 2 — Activation criteria (§3.1)

> "What would have to be true for you to declare? Not what you'd feel — what you'd be able to
> point at."

Push from feeling to criterion. Usable criteria are comparisons against something knowable at
3am: expected outage duration against remaining MTD budget, extent of damage, criticality of
the affected scope.

Then the two questions that make the criteria operable:

> "How long are you allowed to spend deciding?"
>
> "What's the default if you can't tell? Do you declare, or do you wait?"

**The second question is the one nobody has answered.** It is the difference between a gate
that works at 3am and one that stalls. Whichever way they answer, record the reasoning — the
asymmetry between an unnecessary failover and a late declaration is specific to their estate
and their failback cost, and it must be written down where the person on the bridge will see
it.

---

## Part 3 — Notification (§3.2)

### The call tree

> "Walk me through who gets called, in what order, and who makes each call."

A tree, not a list: each person called is responsible for calling others. Capture primary and
alternate contact methods per person.

> "What happens when someone doesn't pick up? How long do you try before moving on?"

### The bridge

> "Where does everyone convene, and is that dependent on anything that might also be down?"

A conference bridge hosted in the failed region, or an incident channel in a tool that
authenticates through the affected estate, is a plan with a loop in it. Ask directly.

### What is said

Notification content is a small script, and having it prewritten is worth minutes at the worst
possible moment. Elicit: nature of the outage, known estimates, which runbook is running, where
and when to convene, and the instruction to continue the call tree.

### External partners

> "Which of your partners needs to hear from you, and how fast?"

Cross-check against the interconnection register from the application interview. A partner in
that register with no row here is a gap; say so.

---

## Part 4 — Outage assessment (§3.3)

**The section almost every real plan is missing**, because the activation criteria assume an
estimate that no procedure produces.

> "Your criteria compare expected outage duration against your MTD budget. Where does that
> duration number come from? Who works it out, and how?"

The usual answer is a pause. That pause is the finding.

Elicit, in order:

| Question | Produces |
|---|---|
| "Who does the assessing, and are they the same people doing the recovery?" | The assessment team, or the fact that there isn't one |
| "How long do they get?" | The time budget, which must fit inside the decision window |
| "What do they look at first?" | The concrete signal list, in order |
| "Who owns the infrastructure you can't see?" | For cloud: the provider's status page and support channel |
| "How do you get an estimate from the provider, and how fast?" | The support path, severity, and who holds the account identifier |
| "What if the cause looks deliberate?" | The branch where this stops being only a continuity event |

### The two questions that make the assessment honest

> "If you can't produce an estimate in the time you've got — what's the answer?"

Unknown must map to a decision. Decide it here, in daylight.

> "Could the assessor be personally caught up in the event?"

NIST puts personnel safety above assessment speed. In a cloud estate the safety constraint
usually binds on the people, not the equipment, and the plan needs a hand-off that does not
depend on the affected person recognising they should hand off.

### The closed-book form

> "If this whole plan were unreachable — it's in the region that's down — what would your
> assessor do?"

Reduce the procedure to five questions answerable from memory. NIST requires assessors to
perform without the document, and a plan stored only inside the estate it protects is a plan
with a circular dependency.

---

## Part 5 — Escalation thresholds (§4.3) and deactivation (§5.4)

> "The recovery is running and it's taking longer than expected. At what point does someone
> get woken up, and who?"

Thresholds must be observable at 3am by a tired person: elapsed time against a known step
duration, or elapsed total against the MTD budget. "When it feels wrong" is not a threshold.

Then the mirror of declaration:

> "Who says it's over? And who do they tell?"

Declaration and deactivation are a matched pair. An unclosed declaration leaves the
organisation unsure whether it is still in a disaster, which is its own kind of outage.

---

## Output

Writes `continuity.*`: leadership roles and the deputy named for each, ordered succession with
intervals reconciled against the Phase 0 roster, team structure with alternates and their
capability, geographic and vendor fallback, activation criteria and the
unknown-case default, decision time budget, call tree, bridge and its dependencies,
notification script, external notification list, assessment team, time budget, signal list,
provider escalation path, unknown-estimate rule, closed-book form, escalation thresholds,
deactivation authority.

Renders `checklists/roles-and-responsibilities.md`, `checklists/contact-roster.md`,
`checklists/outage-assessment.md`, `checklists/dr-authority-matrix.md`, and the decision gate
in `runbooks/RB-02`.

## Red flags

| Thought | Reality |
|---|---|
| "The incident team would decide" | That is nobody. Get one name and an ordered succession |
| "Several senior people could declare" | Concurrent declarations half-fail-over an estate. One at a time, in order |
| "They'll assess it when it happens" | Then the activation criteria consume a number nothing produces |
| "The alternate is listed, that's covered" | Ask whether the alternate could actually do it, or only knows who to call |
| "Only one engineer has ever run the failback, but they're reliable" | Reliability is not availability. No deputy is a finding, at the same weight as no owner |
| "The on-call rota is the deputy" | A rota is not a name. Ask who is on it who could actually execute this step |
| "The roster and the succession are near enough the same" | "Near enough" is a conflict you have not looked at. Record both, name the decision owner |
| "Thresholds are a judgement call" | Judgement at 3am is not repeatable. Get an observable number |
| "The bridge is our usual incident channel" | Check what that channel depends on. A loop through the failed estate is not a bridge |
| "Safety isn't relevant, it's all cloud" | The event that takes the region may take the people. Ask |
