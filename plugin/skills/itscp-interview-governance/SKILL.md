---
name: itscp-interview-governance
description: Use when a continuity plan needs approval, a review and maintenance cadence, a risk register, or a training and exercise program, when a system's security categorization or impact level must be established for a plan, or when someone asks what evidence an auditor will want for contingency planning.
---

# itscp-interview-governance

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

## The distinction that frames the whole interview

**A design describes what would happen. A plan is a design somebody has committed to.** The
difference is a signature, a review date, and a trained population. An unsigned, unreviewed,
untrained document is a design, however good it is — and the organization will believe it has
a plan.

Open by saying this. It reframes the session from paperwork into the thing that makes the
previous three interviews count.

---

## What to elicit

### 1. Approval (10 min)

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

### 2. Categorization and scope (10 min)

> "Has this system been formally categorized — an impact level, a data classification, a
> regulatory regime it falls under?"

This determines which controls are mandatory rather than advisable, and it belongs in the
plan's scope statement. If it has never been categorized, that is a `MISSING` with an owner
and it is worth flagging as a prerequisite: several plan requirements are conditioned on it.

Also establish any regulatory obligation with its own clock — breach notification windows,
financial reporting deadlines, sector rules. These interact with the MTD and are frequently
shorter than it.

### 3. Review and maintenance cadence (10 min)

> "How often is this reviewed, and what else triggers a review besides the calendar?"

Elicit the triggers, not just the frequency: after every drill, after any invocation, after
material change — acquisition, re-platform, new regulation — and after a failed audit.

> "Who owns the review, and what happens if it doesn't happen?"

A cadence with no owner is not a cadence. Continuity plans decay silently, and the decay is
invisible until the invocation.

### 4. Training — Appendix J (15 min)

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

### 5. Exercises and evidence (10 min)

> "What drills do you run, how often, and what do you keep afterwards?"

Establish the exercise tiers, their cadence, and — most importantly — what evidence is
retained and where. Timing sheets, attestations, findings, and the route from a finding to a
plan change.

> "When a drill finds something wrong, what makes the plan actually change?"

If there is no route, the drills are theater. That is a finding, not a criticism, and it is
usually welcomed.

### 6. Risk register (10 min)

Material assumptions and design risks are, by this point, scattered across the other three
interviews. Consolidate them into an owned register: each risk with an owner, likelihood,
impact and treatment.

> "Where do risks like this normally live in your organization, and who reviews them?"

Prefer plugging into the existing risk process over creating a parallel one. A register only
this plan reads is a register nobody reads.

### 7. Vendor agreements — Appendix L (5 min)

SLAs, support contracts and their severity paths, reciprocal agreements. Specifically: what
the cloud provider commits to in a regional event, and whether anyone has read it.

---

## Output

Writes `governance.*`: signing authority and attestation, existing approvals, categorization
and regulatory obligations, review cadence with triggers and owner, training program and
evidence method, exercise tiers and evidence retention, finding-to-change route, risk register,
vendor agreements.

Renders `docs/00-plan-approval.md`, `checklists/contingency-training.md`,
`checklists/risk-register.md`, the maintenance section of `README.md`, and Appendix J.

## Red flags

| Thought | Reality |
|---|---|
| "The CIO will sign it, that's approval covered" | Ask what they are attesting to. A signature on an unspecified claim is not approval |
| "There's one signatory and that's normal" | Then approval stalls whenever they are away. Name the alternate, or record the gap |
| "They drill annually, so training is covered" | Different activities. Drills exercise the plan; training makes individuals competent |
| "There's no formal categorization, I'll assess it as moderate" | Categorization is theirs to assign. MISSING with an owner |
| "Review cadence is annual" | And the other triggers? And who owns it? An unowned cadence does not happen |
| "They keep drill results in a folder" | Ask what makes the plan change when a drill finds something. That is the real question |
| "Risks are already in the assumptions section" | Scattered assumptions are not an owned register. Consolidate, with owners |
