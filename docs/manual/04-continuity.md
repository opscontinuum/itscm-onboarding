# Phase 4 — The continuity segment

> **Generated file.** It is assembled from the skills, the question bank and `GETTING-STARTED.md` by `plugin/itscp_manual.py`, and an edit made here is deleted by the next regeneration. Change the source and run `python3 plugin/itscp_manual.py`.

**The tabletop.** Application and infrastructure teams in the room together, with the DR process owner. One exercise in segments; run it in a single long sitting or across several, but keep both teams present for all of it. The DR process owner leads this segment, with their deputy, and both technical teams still in the room.

**Whose answers these are:** the DR process owner, incident manager, or whoever would actually be running the bridge at 3am, with their deputy in the room where one is named. If nobody holds that role, you have found the most important gap in the engagement; say so before continuing.

**How long:** 90 minutes.

Runs last of the technical segments, because escalation thresholds need real recovery steps to threshold against. By now the room has the steps.

This is the segment where most organizations discover that **nobody owns the declaration decision.** That is not a failure of the exercise; it is the single most valuable thing it produces, and a tabletop surfaces it faster than an interview because everybody who assumed somebody else owned it is sitting in the room.

The succession named here and the deputy roster from phase 0 must agree. Where they do not, write both down with the decision owner named, rather than reconciling it quietly at the whiteboard.

**Run under [the method](method.md).** Nothing enters the plan unless somebody in the room said it, an inventory shows it, or it is written down as a gap with a name against it.

---

## The technique

*From `itscp-interview-continuity`: Use when a continuity plan needs its roles, teams or line of succession defined, when it must be decided who can declare a disaster and on what criteria, when a call tree or notification procedure is needed, or when there is no procedure for assessing an outage and estimating how long it will last.*

### The one question this interview exists to answer

> **At 3am, with the primary region gone, who decides to fail over — and what do they need in
> front of them to decide?**

Everything below is that question decomposed. Most organizations have some of the pieces and
have never assembled them, so the interview frequently ends with the interviewee saying they
had not realized nobody owned the decision.

### Part 1 — Roles and succession (§2.3)

#### Declaration authority

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

- **Nobody holds it.** Common. The organization believes the decision would "be made by the
  incident team", which means it would be made by whoever felt boldest, or not at all.
- **Everybody holds it.** Also common, and worse. Concurrent declarations by different people
  are how an environment ends up half failed over.

#### Separating deciding from doing

> "Is the person who decides also the person running the recovery?"

If yes, name the risk plainly: the decision gate gets compressed into whatever the recovery
work leaves time for. It is a legitimate choice for a small team — record it as a stated
choice with its consequence, not as an oversight.

#### Teams, alternates and the deputy roster

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

#### The disruption may take the people too

> "If the event that takes the environment also takes your main office — does the recovery still
> have the people it needs?"

Then: is there anyone outside that geography who can execute, and is there a contracted vendor
fallback? Usually unanswered. Record as `MISSING` with an owner; it is a legitimate finding.

### Part 2 — Activation criteria (§3.1)

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
asymmetry between an unnecessary failover and a late declaration is specific to their environment
and their failback cost, and it must be written down where the person on the bridge will see
it.

### Part 3 — Notification (§3.2)

#### The call tree

> "Walk me through who gets called, in what order, and who makes each call."

A tree, not a list: each person called is responsible for calling others. Capture primary and
alternate contact methods per person.

> "What happens when someone doesn't pick up? How long do you try before moving on?"

#### The bridge

> "Where does everyone convene, and is that dependent on anything that might also be down?"

A conference bridge hosted in the failed region, or an incident channel in a tool that
authenticates through the affected environment, is a plan with a loop in it. Ask directly.

#### What is said

Notification content is a small script, and having it prewritten is worth minutes at the worst
possible moment. Elicit: nature of the outage, known estimates, which runbook is running, where
and when to convene, and the instruction to continue the call tree.

#### External partners

> "Which of your partners needs to hear from you, and how fast?"

Cross-check against the interconnection register from the application interview. A partner in
that register with no row here is a gap; say so.

### Part 4 — Outage assessment (§3.3)

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

#### The two questions that make the assessment honest

> "If you can't produce an estimate in the time you've got — what's the answer?"

Unknown must map to a decision. Decide it here, in daylight.

> "Could the assessor be personally caught up in the event?"

NIST puts personnel safety above assessment speed. In a cloud environment the safety constraint
usually binds on the people, not the equipment, and the plan needs a hand-off that does not
depend on the affected person recognizing they should hand off.

#### The closed-book form

> "If this whole plan were unreachable — it's in the region that's down — what would your
> assessor do?"

Reduce the procedure to five questions answerable from memory. NIST requires assessors to
perform without the document, and a plan stored only inside the environment it protects is a plan
with a circular dependency.

### Part 5 — Escalation thresholds (§4.3) and deactivation (§5.4)

> "The recovery is running and it's taking longer than expected. At what point does someone
> get woken up, and who?"

Thresholds must be observable at 3am by a tired person: elapsed time against a known step
duration, or elapsed total against the MTD budget. "When it feels wrong" is not a threshold.

Then the mirror of declaration:

> "Who says it's over? And who do they tell?"

Declaration and deactivation are a matched pair. An unclosed declaration leaves the
organization unsure whether it is still in a disaster, which is its own kind of outage.

### Red flags

| Thought | Reality |
|---|---|
| "The incident team would decide" | That is nobody. Get one name and an ordered succession |
| "Several senior people could declare" | Concurrent declarations half-fail-over an environment. One at a time, in order |
| "They'll assess it when it happens" | Then the activation criteria consume a number nothing produces |
| "The alternate is listed, that's covered" | Ask whether the alternate could actually do it, or only knows who to call |
| "Only one engineer has ever run the failback, but they're reliable" | Reliability is not availability. No deputy is a finding, at the same weight as no owner |
| "The on-call rota is the deputy" | A rota is not a name. Ask who is on it who could actually execute this step |
| "The roster and the succession are near enough the same" | "Near enough" is a conflict you have not looked at. Record both, name the decision owner |
| "Thresholds are a judgment call" | Judgment at 3am is not repeatable. Get an observable number |
| "The bridge is our usual incident channel" | Check what that channel depends on. A loop through the failed environment is not a bridge |
| "Safety isn't relevant, it's all cloud" | The event that takes the region may take the people. Ask |

---

## What this segment has to come away with

21 answers, grouped by the section of the plan each one feeds. Read this before the session; the worksheet at the end is what you take into it.

Every one of them leaves the room with something written against it. An answer nobody in the room could give is a **name** — whoever can — which is a result and not a failure. A blank is neither.

### 3.1 Activation criteria and procedure; who may activate

#### `continuity.declaration_authority`

> "If this broke at two in the morning and somebody had to say 'we are failing over', who says it? And if they do not answer?"

- **Records:** The single individual with declaration authority, and their named deputy
- **Answers:** DR process owner · **Shape:** free text
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** Exactly one individual, and one named deputy. Not 'the incident team', which is nobody, and not a rota, which is not a name.
- **Goes into:** runbooks/RB-02-failover.md 0, checklists/dr-authority-matrix.md
- **NIST:** 4.2.1 Activation Criteria and Procedure (SP 800-34 Rev. 1 Chapter 4, Information System Contingency Plan Development)

#### `continuity.activation_criteria`

> "What would you have to see, at three in the morning, to know this is a failover and not a bad hour?"

- **Records:** The activation criteria, each one observable
- **Answers:** DR process owner · **Shape:** several paragraphs, in their words
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** Comparisons against something knowable at 3am, not feelings.
- **Goes into:** runbooks/RB-02-failover.md 0
- **NIST:** 3.1 Activation Criteria and Procedure (SP 800-34 Rev. 1 Appendix A.3, Sample Template for High-Impact Systems)

#### `continuity.decision_time_budget`

> "How long may the decision itself take before the delay is the problem?"

- **Records:** The time budget for the declaration decision
- **Answers:** DR process owner · **Shape:** a duration in minutes
- **Then ask:** "What is happening to the outage while that decision is being taken, and what stops being recoverable once the budget is spent?" It goes in the **what breaks at that number** column. An empty one makes the figure a guess, and the row is marked low confidence.
- **Note:** Deciding is on the recovery critical path and is almost never budgeted. Whatever the number is, it comes out of the MTD.
- **Goes into:** checklists/dr-authority-matrix.md
- **No NIST slot.** An element this toolkit carries deliberately; the answer in it is elicited like any other.

#### `continuity.declaration_threshold_rule`

> "Should the point at which you stop waiting be a fixed number of hours, or should it be worked out from how much of the tolerable downtime is left at that moment?"

- **Records:** How the point of no return is calculated rather than what it is today
- **Answers:** DR process owner · **Shape:** several paragraphs, in their words
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** The default action when nobody can estimate is a separate field and this is the rule behind it. A fixed threshold ages badly; one computed from what is left of the budget survives a change to the tier. Ask which they want and write down why.
- **Goes into:** checklists/dr-authority-matrix.md
- **No NIST slot.** An element this toolkit carries deliberately; the answer in it is elicited like any other.

#### `continuity.data_loss_gate`

> "If you came up having lost more data than the tier allows, does downstream processing stay stopped until somebody clears it, or does it run?"

- **Records:** What happens to downstream processing when the recovery point was missed
- **Answers:** DR process owner · **Shape:** several paragraphs, in their words
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** Decide it in daylight. In the event this is asked of whoever is nearest, at speed, and the wrong answer pays somebody twice or fails to pay them at all. Name who clears it.
- **Goes into:** checklists/dr-authority-matrix.md
- **No NIST slot.** An element this toolkit carries deliberately; the answer in it is elicited like any other.

### 2.3 Roles and responsibilities

#### `continuity.succession`

> "If the first person does not answer, who is next? And after them? Keep going until you reach someone who is always reachable."

- **Records:** The ordered line of succession and what each hand-off waits for
- **Answers:** DR process owner · **Shape:** one row per item, columns `order` | `role` | `passes_after`
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** Must terminate in someone always reachable. Must agree with the Phase 0 deputy roster; a disagreement is a conflict with a named decision owner, never a silent preference for one list.
- **Goes into:** checklists/roles-and-responsibilities.md
- **NIST:** 2.3 Roles and Responsibilities (SP 800-34 Rev. 1 Appendix A.3, Sample Template for High-Impact Systems)

#### `continuity.decision_and_recovery_roles`

> "Who decides to declare, who runs the recovery, who authorizes spending, and who says it is over? Take them one at a time, and tell me where the same person appears twice."

- **Records:** Each duty in a recovery, the role that holds it and the deputy behind them
- **Answers:** DR process owner · **Shape:** one row per item, columns `duty` | `held_by` | `deputy`
- **`duty` is one of:** `decides to declare`, `runs the recovery`, `authorizes the spending`, `says it is over`
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** Four duties, asked separately, because asking for one job title gets you one name and hides the overlap. Where the same role holds two of them, say so out loud and ask what they put down to do the other. Deciding whether the repair estimate beats the remaining budget and running the storage sequence are not the same work and cannot be done at the same minute.
- **Goes into:** checklists/roles-and-responsibilities.md
- **These words are the toolkit's, not the room's.** They render as its own and are never presented as something anybody in the room said: The toolkit names duties, not posts. It asks who decides to declare, who runs the recovery, who authorizes the spending and who says it is over, and it maps those answers onto the roles this plan already uses. A standard's own post names are supplied by the standard and never by the person being interviewed, because a question that names a post supplies the answer it was asked to elicit.

#### `continuity.people_unavailable`

> "If whatever caused this also took your people, one office or one time zone, who is left who could execute this, and where are they?"

- **Records:** Who could execute the plan if the disruption also removed the primary team
- **Answers:** DR process owner · **Shape:** several paragraphs, in their words
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** Almost never asked and almost never has an answer. 'Nobody' is the correct answer where it is true, and it belongs in the plan as a named hole rather than being filled in by whoever is drafting.
- **Goes into:** checklists/roles-and-responsibilities.md
- **NIST:** 3.4.6 Roles and Responsibilities (SP 800-34 Rev. 1 Chapter 3, Information System Contingency Planning Process)

### 3.3 Outage assessment

#### `continuity.unknown_estimate_default`

> "If nobody can say how long the repair will take, do you declare or do you wait?"

- **Records:** The default action when the repair estimate is unknown
- **Answers:** DR process owner · **Shape:** one of `declare`, `wait`
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** Declare, or wait? Nobody has answered this. Decide it in daylight.
- **Goes into:** checklists/outage-assessment.md
- **No NIST slot.** An element this toolkit carries deliberately; the answer in it is elicited like any other.

#### `continuity.assessment_procedure`

> "Who works out how bad it is, and how do they produce a repair estimate the person declaring can act on?"

- **Records:** The outage assessment procedure and where the repair estimate comes from
- **Answers:** DR process owner · **Shape:** several paragraphs, in their words
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** Where the repair estimate the activation criteria consume comes from.
- **Goes into:** checklists/outage-assessment.md
- **NIST:** 3.3 Outage Assessment (SP 800-34 Rev. 1 Appendix A.3, Sample Template for High-Impact Systems)

#### `continuity.assessment_calibration`

> "Last time something broke badly, how long was it before anyone could say how long it would take to fix?"

- **Records:** How long this organization actually takes to produce a repair estimate
- **Answers:** DR process owner · **Shape:** a duration in minutes
- **Then ask:** "What were they waiting on for that long, and is that thing any faster now?" It goes in the **what breaks at that number** column. An empty one makes the figure a guess, and the row is marked low confidence.
- **Note:** Calibrates the assessment budget against what this organization can do rather than against what the plan would like. If the honest answer is two hours, a ten-minute assessment step is fiction and the plan should say so.
- **Goes into:** checklists/outage-assessment.md
- **No NIST slot.** An element this toolkit carries deliberately; the answer in it is elicited like any other.

### 3.2 Notification

#### `continuity.call_tree`

> "Once it is declared, who gets told, in what order, and by whom? What happens when one of them does not pick up?"

- **Records:** The call tree, its order, and the unreachable procedure
- **Answers:** DR process owner · **Shape:** several paragraphs, in their words
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** The unreachable branch is the half that gets skipped and the half that gets used.
- **Goes into:** checklists/contact-roster.md
- **NIST:** 3.2 Notification (SP 800-34 Rev. 1 Appendix A.3, Sample Template for High-Impact Systems)

#### `continuity.bridge`

> "Where does everyone gather to work the incident, and what does joining it depend on?"

- **Records:** The incident bridge and its dependencies
- **Answers:** DR process owner · **Shape:** free text
- **Note:** Check what it depends on. A bridge that authenticates through the failed environment is a plan with a loop in it.
- **Goes into:** checklists/contact-roster.md
- **No NIST slot.** An element this toolkit carries deliberately; the answer in it is elicited like any other.

### 4.3 Recovery escalation and notification

#### `continuity.escalation_thresholds`

> "Once recovery is running, what would tell a tired person at 4am that it is going badly enough to wake someone more senior?"

- **Records:** The escalation thresholds, each observable
- **Answers:** DR process owner · **Shape:** several paragraphs, in their words
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** Observable at 3am by a tired person. 'When it feels wrong' is not one.
- **Goes into:** docs/09 5
- **NIST:** 4.3 Recovery Escalation Notices/Awareness (SP 800-34 Rev. 1 Appendix A.3, Sample Template for High-Impact Systems)

### 5.10 Deactivation

#### `continuity.deactivation_authority`

> "Who says it is over, and what do they have to see before they can say it?"

- **Records:** Who may deactivate the plan and on what evidence
- **Answers:** DR process owner · **Shape:** free text
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** Declaration and deactivation are a matched pair.
- **Goes into:** docs/10 4.2
- **NIST:** 5.10 Deactivation (SP 800-34 Rev. 1 Appendix A.3, Sample Template for High-Impact Systems)

### A. Personnel contact list

#### `continuity.contact_roster`

> "For every role we have named: who holds it, how do I reach them out of hours, and when did anyone last ring that number and get an answer?"

- **Records:** Each role, who holds it, how they are reached and when that was last verified
- **Answers:** DR process owner · **Shape:** one row per item, columns `role` | `held_by` | `reached_by` | `last_verified`
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** The one file that must never be committed to a shared repository, and the one that is useless if it is out of date. Press on the last column: a roster nobody has rung is a list of numbers, not a call tree. A role with no holder is a gap with a name on it and belongs here as MISSING rather than being quietly left out.
- **Goes into:** checklists/contact-roster.md
- **NIST:** APPENDIX A PERSONNEL CONTACT LIST (SP 800-34 Rev. 1 Appendix A.3, Sample Template for High-Impact Systems)

### B. Vendor contact list

#### `continuity.vendor_contacts`

> "Which outside organizations would you have to call during this, how do you reach them out of hours, and what reference do they need you to quote before they will help?"

- **Records:** Each vendor, what they supply, how they are reached and the reference they need
- **Answers:** DR process owner · **Shape:** one row per item, columns `organization` | `what_they_supply` | `reached_by` | `reference_to_quote`
- **Note:** The reference column is the one that saves an hour. A support contract number stored only inside the system being recovered is not a contract number. Ask where a printed copy lives.
- **Goes into:** checklists/contact-roster.md
- **NIST:** APPENDIX B VENDOR CONTACT LIST (SP 800-34 Rev. 1 Appendix A.3, Sample Template for High-Impact Systems)

### Vendor obligations during a recovery

#### `continuity.vendor_obligations`

> "Is anyone outside this organization contracted to do part of this if you cannot? What does the contract actually oblige them to do, and how fast?"

- **Records:** Each external party, what their contract obliges, how fast, and where the contract is held
- **Answers:** governance/risk contact · **Shape:** one row per item, columns `organization` | `what_the_contract_obliges` | `response_time` | `where_the_contract_is_held`
- **Note:** Not a NIST appendix: the templates have no heading for this and the coverage map invented one. It is still worth asking, because a recovery that assumes a vendor will help is a recovery resting on goodwill. If the answer is that nobody has read the contract, record that.
- **Goes into:** checklists/contact-roster.md, checklists/risk-register.md
- **No NIST slot.** An element this toolkit carries deliberately; the answer in it is elicited like any other.

### 5.4 Recovery declaration

#### `continuity.recovery_declaration`

> "Who tells the business it is recovered, and what do they have to have seen before they are allowed to say it?"

- **Records:** Who declares recovery complete and the evidence they need first
- **Answers:** DR process owner · **Shape:** several paragraphs, in their words
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** Distinct from standing the plan down. This is the moment users are told they may work, and the evidence for it is the validation pack rather than the infrastructure being green.
- **Goes into:** docs/10-phase-reconstitution.md
- **NIST:** 5.4 Recovery Declaration (SP 800-34 Rev. 1 Appendix A.3, Sample Template for High-Impact Systems)

### 5.5 Notification (users)

#### `continuity.user_notification`

> "How do users find out they can work again? Who sends it, through what, and what does it have to tell them?"

- **Records:** How users are told service is restored, by whom and what the message must carry
- **Answers:** DR process owner · **Shape:** several paragraphs, in their words
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** Ask what the message has to say, not just who sends it. Users coming back to a system that lost fifteen minutes of work need to be told that, and a channel that runs through the recovered environment is a channel with a loop in it.
- **Goes into:** checklists/contact-roster.md, docs/10-phase-reconstitution.md
- **NIST:** 5.5 Notifications (users) (SP 800-34 Rev. 1 Appendix A.3, Sample Template for High-Impact Systems)

### 5.6 Cleanup

#### `continuity.cleanup`

> "Once it is over, what has to be taken down or put back? And what is the thing you would most regret leaving running?"

- **Records:** What is dismantled after the event, and who is responsible for each of it
- **Answers:** DR process owner · **Shape:** several paragraphs, in their words
- **Say it back** in one sentence and get a yes before you write it.
- **Note:** The second half of the question finds the expensive one. Ask also what must deliberately not be torn down: the replication that was rebuilt is the thing most often cleaned up by somebody tidying.
- **Goes into:** docs/10-phase-reconstitution.md
- **NIST:** 5.6 Cleanup (SP 800-34 Rev. 1 Appendix A.3, Sample Template for High-Impact Systems)

---

## The worksheet

Print this. One line per answer, filled in as it is said rather than afterwards.

- **Never leave a cell blank.** No answer means write the name of who can give one.
- **Sure?** is how the answer arrived, not how plausible it sounds. H: they have measured it or read it off a screen while you waited. M: confident from experience, never measured. L: worked out in the room just now. Ask when you cannot tell.
- **What breaks at that number** is what makes a figure arguable rather than arbitrary. A duration with an empty cell beside it is a guess, and is marked L.
- Two people, two answers: **write both**, and write whose decision it is.

### 3.1 Activation criteria and procedure; who may activate

| What it records | Answer | Who said it | Sure? | What breaks at that number |
|---|---|---|---|---|
| The single individual with declaration authority, and their named deputy (`continuity.declaration_authority`) |  |  | H / M / L |  |
| The activation criteria, each one observable (`continuity.activation_criteria`) |  |  | H / M / L |  |
| The time budget for the declaration decision (`continuity.decision_time_budget`) |  |  | H / M / L |  |
| How the point of no return is calculated rather than what it is today (`continuity.declaration_threshold_rule`) |  |  | H / M / L |  |
| What happens to downstream processing when the recovery point was missed (`continuity.data_loss_gate`) |  |  | H / M / L |  |

### 2.3 Roles and responsibilities

| What it records | Answer | Who said it | Sure? | What breaks at that number |
|---|---|---|---|---|
| Who could execute the plan if the disruption also removed the primary team (`continuity.people_unavailable`) |  |  | H / M / L |  |

**The ordered line of succession and what each hand-off waits for** (`continuity.succession`) — one row each, add as many as the room needs

| order | role | passes_after | Who said it | Sure? |
|---|---|---|---|---|
|   |   |   |  | H / M / L |
|   |   |   |  | H / M / L |
|   |   |   |  | H / M / L |

**Each duty in a recovery, the role that holds it and the deputy behind them** (`continuity.decision_and_recovery_roles`) — one row each, add as many as the room needs

| duty | held_by | deputy | Who said it | Sure? |
|---|---|---|---|---|
|   |   |   |  | H / M / L |
|   |   |   |  | H / M / L |
|   |   |   |  | H / M / L |

### 3.3 Outage assessment

| What it records | Answer | Who said it | Sure? | What breaks at that number |
|---|---|---|---|---|
| The default action when the repair estimate is unknown (`continuity.unknown_estimate_default`) |  |  | H / M / L |  |
| The outage assessment procedure and where the repair estimate comes from (`continuity.assessment_procedure`) |  |  | H / M / L |  |
| How long this organization actually takes to produce a repair estimate (`continuity.assessment_calibration`) |  |  | H / M / L |  |

### 3.2 Notification

| What it records | Answer | Who said it | Sure? | What breaks at that number |
|---|---|---|---|---|
| The call tree, its order, and the unreachable procedure (`continuity.call_tree`) |  |  | H / M / L |  |
| The incident bridge and its dependencies (`continuity.bridge`) |  |  | H / M / L |  |

### 4.3 Recovery escalation and notification

| What it records | Answer | Who said it | Sure? | What breaks at that number |
|---|---|---|---|---|
| The escalation thresholds, each observable (`continuity.escalation_thresholds`) |  |  | H / M / L |  |

### 5.10 Deactivation

| What it records | Answer | Who said it | Sure? | What breaks at that number |
|---|---|---|---|---|
| Who may deactivate the plan and on what evidence (`continuity.deactivation_authority`) |  |  | H / M / L |  |

### A. Personnel contact list

**Each role, who holds it, how they are reached and when that was last verified** (`continuity.contact_roster`) — one row each, add as many as the room needs

| role | held_by | reached_by | last_verified | Who said it | Sure? |
|---|---|---|---|---|---|
|   |   |   |   |  | H / M / L |
|   |   |   |   |  | H / M / L |
|   |   |   |   |  | H / M / L |

### B. Vendor contact list

**Each vendor, what they supply, how they are reached and the reference they need** (`continuity.vendor_contacts`) — one row each, add as many as the room needs

| organization | what_they_supply | reached_by | reference_to_quote | Who said it | Sure? |
|---|---|---|---|---|---|
|   |   |   |   |  | H / M / L |
|   |   |   |   |  | H / M / L |
|   |   |   |   |  | H / M / L |

### Vendor obligations during a recovery

**Each external party, what their contract obliges, how fast, and where the contract is held** (`continuity.vendor_obligations`) — one row each, add as many as the room needs

| organization | what_the_contract_obliges | response_time | where_the_contract_is_held | Who said it | Sure? |
|---|---|---|---|---|---|
|   |   |   |   |  | H / M / L |
|   |   |   |   |  | H / M / L |
|   |   |   |   |  | H / M / L |

### 5.4 Recovery declaration

| What it records | Answer | Who said it | Sure? | What breaks at that number |
|---|---|---|---|---|
| Who declares recovery complete and the evidence they need first (`continuity.recovery_declaration`) |  |  | H / M / L |  |

### 5.5 Notification (users)

| What it records | Answer | Who said it | Sure? | What breaks at that number |
|---|---|---|---|---|
| How users are told service is restored, by whom and what the message must carry (`continuity.user_notification`) |  |  | H / M / L |  |

### 5.6 Cleanup

| What it records | Answer | Who said it | Sure? | What breaks at that number |
|---|---|---|---|---|
| What is dismantled after the event, and who is responsible for each of it (`continuity.cleanup`) |  |  | H / M / L |  |
