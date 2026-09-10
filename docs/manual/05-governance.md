# Phase 5 — The governance interview

> **Generated file.** It is assembled from the skills, the question bank and `GETTING-STARTED.md` by `plugin/itscp_manual.py`, and an edit made here is deleted by the next regeneration. Change the source and run `python3 plugin/itscp_manual.py`.

**Who is in the room:** governance, risk, audit, or compliance. In a smaller organization this may be the CIO. If nobody holds it, the plan can still be built; it just cannot be approved, and that should be stated rather than discovered at audit.

**How long:** 60 minutes.

**A design describes what would happen; a plan is a design somebody committed to.** The difference is a signature, a review date and a trained population, and this phase is where all three are elicited.

**Run under [the method](method.md).** No fact enters the plan unless a human said it, a read-only API returned it, or it is marked `MISSING` against a named owner.

---

## The technique — `itscp-interview-governance`

*Use when a continuity plan needs approval, a review and maintenance cadence, a risk register, or a training and exercise program, when a system's security categorization or impact level must be established for a plan, or when someone asks what evidence an auditor will want for contingency planning.*

The part that makes a design into a plan: who signs it, when it is reviewed, who is trained on
it, what evidence exists, and which risks are owned. Produces the approval statement, the
review cadence, Appendix J test/training/exercise documentation, the risk register, and the
categorization the scope statement depends on.

**Read first:** the `itscp-method-interview` skill. Run last — governance signs off on what
the other interviews produced.

**Interviewee:** governance, risk, audit, or compliance. In a smaller organization this may be
the CIO. If nobody holds it, the plan can still be built; it just cannot be approved, and that
should be stated rather than discovered at audit.

**Time:** 60 minutes.

---

### The distinction that frames the whole interview

**A design describes what would happen. A plan is a design somebody has committed to.** The
difference is a signature, a review date, and a trained population. An unsigned, unreviewed,
untrained document is a design, however good it is — and the organization will believe it has
a plan.

Open by saying this. It reframes the session from paperwork into the thing that makes the
previous three interviews count.

---

### What to elicit

#### 1. Approval (10 min)

> "Who signs this, and what are they attesting to when they do?"

Establish the signing authority — typically the system owner or designated authority — and
what the statement affirms: that the plan is complete, that it will be tested at a stated
frequency, and that it will be maintained.

> "And if they're unavailable when it needs re-approving, who signs instead?"

An alternate signatory is the same requirement as every other deputy on the Phase 0 roster.
A plan reapprovable by exactly one reachable person is a plan that goes stale during a long
absence, which is precisely when nobody notices.

> "Has anything like this been signed before? Can I see it?"

An existing signed plan, however stale, tells you the organization's real cadence and the real
signing chain. It is usually more informative than the answer to the previous question.

#### 2. Categorization and scope (10 min)

> "Has this system been formally categorized — an impact level, a data classification, a
> regulatory regime it falls under?"

This determines which controls are mandatory rather than advisable, and it belongs in the
plan's scope statement. If it has never been categorized, that is a `MISSING` with an owner
and it is worth flagging as a prerequisite: several plan requirements are conditioned on it.

Also establish any regulatory obligation with its own clock — breach notification windows,
financial reporting deadlines, sector rules. These interact with the MTD and are frequently
shorter than it.

#### 3. Review and maintenance cadence (10 min)

> "How often is this reviewed, and what else triggers a review besides the calendar?"

Elicit the triggers, not just the frequency: after every drill, after any invocation, after
material change — acquisition, re-platform, new regulation — and after a failed audit.

> "Who owns the review, and what happens if it doesn't happen?"

A cadence with no owner is not a cadence. Continuity plans decay silently, and the decay is
invisible until the invocation.

#### 4. Training — Appendix J (15 min)

**Training and exercising are different activities and auditors check for both.** A drill
exercises the plan; training makes individuals competent. A team that has participated in
drills has not necessarily been trained, and the distinction is exactly what a contingency
training control asks about.

> "Who needs to be trained, on what, and how often? And how would you evidence that to an
> auditor?"

Elicit: roles in scope, syllabus per role, the new-joiner path and its deadline, whether drill
participation counts as training and under what conditions, and how completion is recorded.

Then the one that separates real competence from attendance:

> "Could your assessment lead do their job without the document in front of them?"

#### 5. Exercises and evidence (10 min)

> "What drills do you run, how often, and what do you keep afterwards?"

Establish the exercise tiers, their cadence, and — most importantly — what evidence is
retained and where. Timing sheets, attestations, findings, and the route from a finding to a
plan change.

> "When a drill finds something wrong, what makes the plan actually change?"

If there is no route, the drills are theater. That is a finding, not a criticism, and it is
usually welcomed.

#### 6. Risk register (10 min)

Material assumptions and design risks are, by this point, scattered across the other three
interviews. Consolidate them into an owned register: each risk with an owner, likelihood,
impact and treatment.

> "Where do risks like this normally live in your organization, and who reviews them?"

Prefer plugging into the existing risk process over creating a parallel one. A register only
this plan reads is a register nobody reads.

#### 7. Vendor agreements — Appendix L (5 min)

SLAs, support contracts and their severity paths, reciprocal agreements. Specifically: what
the cloud provider commits to in a regional event, and whether anyone has read it.

---

### Output

Writes `governance.*`: signing authority and attestation, existing approvals, categorization
and regulatory obligations, review cadence with triggers and owner, training program and
evidence method, exercise tiers and evidence retention, finding-to-change route, risk register,
vendor agreements.

Renders `docs/00-plan-approval.md`, `checklists/contingency-training.md`,
`checklists/risk-register.md`, the maintenance section of `README.md`, and Appendix J.

### Red flags

| Thought | Reality |
|---|---|
| "The CIO will sign it, that's approval covered" | Ask what they are attesting to. A signature on an unspecified claim is not approval |
| "There's one signatory and that's normal" | Then approval stalls whenever they are away. Name the alternate, or record the gap |
| "They drill annually, so training is covered" | Different activities. Drills exercise the plan; training makes individuals competent |
| "There's no formal categorization, I'll assess it as moderate" | Categorization is theirs to assign. MISSING with an owner |
| "Review cadence is annual" | And the other triggers? And who owns it? An unowned cadence does not happen |
| "They keep drill results in a folder" | Ask what makes the plan change when a drill finds something. That is the real question |
| "Risks are already in the assumptions section" | Scattered assumptions are not an owned register. Consolidate, with owners |

---

## The field checklist

12 fields, in the order the bank holds them, grouped by the section of the plan each one feeds. Every one of them ends the session with a status. A field nobody could answer is `MISSING` against a named owner, which is a result and not a failure; a field left absent is an error.

### Plan Approval statement

#### `governance.signing_authority`

> "Who signs this plan, and who signs it if they are away for a month?"

- **Records:** The signatory and the alternate signatory
- **Owner:** signing authority · **Answer:** free text
- **Read it back** in one sentence and get a yes before recording it.
- **Note:** The signatory and the alternate signatory. A plan that can only be approved by one reachable person cannot be reapproved after a material change while they are away.
- **Lands in:** docs/00-plan-approval.md
- **NIST:** Plan Approval (SP 800-34 Rev. 1 Appendix A.3, Sample Template for High-Impact Systems)

#### `governance.plan_custody`

> "Where will the signed copy of this plan live? And where will it live when the thing holding it is the thing that is down?"

- **Records:** Where the approved plan is held, and where it is held when the environment is unavailable
- **Owner:** signing authority · **Answer:** several paragraphs, in their words
- **Read it back** in one sentence and get a yes before recording it.
- **Note:** A plan readable only from the system it recovers is a plan nobody can read when they need it. The second half of the question is the whole question; ask it separately and wait.
- **Lands in:** docs/00-plan-approval.md
- **No NIST slot.** This element is one the toolkit carries deliberately; the answer in it is elicited like any other.

### J. Test, training and exercise documentation

#### `governance.review_cadence`

> "How often does this get reviewed, what else triggers a review, and whose job is it to start one?"

- **Records:** Review frequency, the triggers, and the owner of the review
- **Owner:** governance/risk contact · **Answer:** free text
- **Note:** Frequency AND triggers AND an owner. An unowned cadence does not happen.
- **Lands in:** README.md
- **NIST:** APPENDIX J TEST AND MAINTENANCE SCHEDULE (SP 800-34 Rev. 1 Appendix A.3, Sample Template for High-Impact Systems)

#### `governance.training_program`

> "Separately from drills: how does someone new become competent to do their part of this?"

- **Records:** The training program, distinct from the drill program
- **Owner:** governance/risk contact · **Answer:** several paragraphs, in their words
- **Read it back** in one sentence and get a yes before recording it.
- **Note:** Distinct from drills. Drills exercise the plan; training makes individuals competent. Auditors check for both.
- **Lands in:** checklists/contingency-training.md
- **NIST:** 3.5.2 Training (SP 800-34 Rev. 1 Chapter 3, Information System Contingency Planning Process)

#### `governance.drill_cadence`

> "How often will you actually exercise this? Not what the policy says: what you will fund and staff."

- **Records:** How often the plan is exercised, in practice
- **Owner:** governance/risk contact · **Answer:** a duration in months
- **Then ask:** "What would have to happen for one to be skipped, and who notices when it is?" Record the answer in `mechanism`. Without one the figure is `confidence: low`.
- **Note:** Two questions in one and the second is the real one. A stricter cadence than the organization will fund is worse than an honest looser one, because the plan then documents a control that does not run and an auditor will find the gap rather than the intention.
- **Lands in:** runbooks/RB-04-dr-drill.md
- **NIST:** 3.5 Plan Testing, Training, and Exercises (TT&E) (SP 800-34 Rev. 1 Chapter 3, Information System Contingency Planning Process)

### Plan review and maintenance cadence

#### `governance.finding_to_change_route`

> "A drill finds something wrong. What happens to that finding, and who closes it?"

- **Records:** The route from a drill finding to a change in the plan
- **Owner:** governance/risk contact · **Answer:** several paragraphs, in their words
- **Read it back** in one sentence and get a yes before recording it.
- **Note:** If there is no route, the drills are theater.
- **Lands in:** README.md
- **No NIST slot.** This element is one the toolkit carries deliberately; the answer in it is elicited like any other.

#### `governance.availability_boundary`

> "Who owns keeping this available day to day, and who owns getting it back after a disaster? Same person, or different?"

- **Records:** Where day-to-day availability ends and continuity begins, and who owns each side
- **Owner:** governance/risk contact · **Answer:** several paragraphs, in their words
- **Read it back** in one sentence and get a yes before recording it.
- **Note:** The boundary most plans raise against themselves and never close. Where it is the same person, ask what they stop doing during a recovery; where it is two, ask who decides which one a given incident is.
- **Lands in:** docs/07-standards-alignment.md
- **No NIST slot.** This element is one the toolkit carries deliberately; the answer in it is elicited like any other.

### Risk register

#### `governance.risk_register`

> "What are you assuming for this to work, that you would not want to discover was wrong during an outage? Take them one at a time."

- **Records:** Each material assumption or design risk, its owner and its review date
- **Owner:** governance/risk contact · **Answer:** one row per item, columns `risk` | `owner` | `review_date` | `mitigation`
- **Note:** Material assumptions and design risks, owned and reviewed rather than scattered.
- **Lands in:** checklists/risk-register.md
- **No NIST slot.** This element is one the toolkit carries deliberately; the answer in it is elicited like any other.

#### `governance.breach_disclosure_clock`

> "If the cause turns out to be an attack rather than a failure, who has to be told, how fast, and whose job is that clock? Name the role, not the department."

- **Records:** Who owns the disclosure clock when the cause is an attack, and how fast it runs
- **Owner:** governance/risk contact · **Answer:** several paragraphs, in their words
- **Read it back** in one sentence and get a yes before recording it.
- **Note:** A recovery driven by an attack is not only a continuity event, and this plan has no authority over the disclosure clock. Record who does. An unowned regulatory clock is the one gap in a continuity plan that costs money after the service is back.
- **Lands in:** checklists/roles-and-responsibilities.md, docs/08-phase-activation.md
- **No NIST slot.** This element is one the toolkit carries deliberately; the answer in it is elicited like any other.

### 5.9 Event documentation

#### `governance.event_documentation`

> "After a real event, who writes down what happened, what goes in it, and where does it end up? And has that ever actually been done here?"

- **Records:** How a real event is written up, by whom, and where the record goes
- **Owner:** governance/risk contact · **Answer:** several paragraphs, in their words
- **Read it back** in one sentence and get a yes before recording it.
- **Note:** A drill report and an event report are different documents and most organizations have neither. Ask the last part plainly: if it has never been done, the answer is what the plan should say, not an intention dressed as a procedure.
- **Lands in:** docs/00-record-of-changes.md, runbooks/RB-04-dr-drill.md
- **NIST:** 5.9 Event Documentation (SP 800-34 Rev. 1 Appendix A.3, Sample Template for High-Impact Systems)

### K. Associated plans and procedures

#### `governance.associated_plans`

> "What other plans does this one lean on or feed into? Anything for the building, for a security incident, for the wider business?"

- **Records:** Each related plan, who owns it and how it relates to this one
- **Owner:** governance/risk contact · **Answer:** one row per item, columns `plan` | `owner` | `how_it_relates`
- **Note:** A continuity plan that assumes a facilities plan exists, and a facilities plan that assumes this one does, is a pair of documents each waiting for the other. Naming the owner is what makes the assumption checkable.
- **Lands in:** docs/07-standards-alignment.md, README.md
- **NIST:** APPENDIX K ASSOCIATED PLANS AND PROCEDURES (SP 800-34 Rev. 1 Appendix A.3, Sample Template for High-Impact Systems)

### Drill levels and what each proves

#### `governance.drill_levels`

> "For each exercise you run: does it prove the plan reads correctly, that the steps run, or that the business can work afterwards? And what does it leave unproven?"

- **Records:** Each exercise level, what it proves and what it does not
- **Owner:** governance/risk contact · **Answer:** one row per item, columns `level` | `what_it_proves` | `what_it_does_not_prove`
- **Note:** The last column is the one that gets argued about, which is why it is a column. An organization whose only evidence is a reading has a plan nobody has run, and it will believe otherwise until this table is filled in.
- **Lands in:** docs/06-test-environments.md, runbooks/RB-04-dr-drill.md
- **The toolkit supplies this element's words, not the customer.** They render as the toolkit's own and are never presented as something anybody said: An exercise proves one of three things and rarely all three: that the plan reads correctly, that the steps run, or that the business can work afterwards. The toolkit asks which level each exercise reaches and what it therefore leaves unproven, because a plan whose only evidence is a reading has never been shown to work.
