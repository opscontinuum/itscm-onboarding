# Building your first plan

A sequenced path from "we should probably have a DR plan" to a repository an auditor can
read. Follow it in order; the ordering encodes real dependencies, not preference.

**Expect two to three weeks of elapsed time for one application suite.** Most of that is
waiting for people, not working. The actual effort is roughly five sessions of 60–120 minutes
plus a day of assembly.

---

## Before you start

Four things, and the last is the one people skip.

1. **The plugin, loaded.** From wherever you cloned this repository:

   ```bash
   picoagent -e /path/to/itscm-onboarding/plugin
   ```

   That trusts it for the one run. For a permanent install, and for the trust fingerprint
   that will otherwise silently stop it loading after you edit a skill, see
   [Installing](README.md#installing).

2. **A repository.** Private. It will contain OCIDs, names, phone numbers, MTD figures and,
   eventually, incident narratives.
3. **The reference example.** [`oci-itscp`](https://github.com/opscontinuum/oci-itscp) is a
   complete worked plan for a hypothetical corporation. Read `README.md` and `docs/01` before
   your first interview so you know what you are aiming at. Do not copy its numbers — they
   describe a company that does not exist.
4. **Fourteen names: seven roles, and a deputy for each.**

   | Role | Deputy |
   |---|---|
   | Business owner | Business deputy, able to decide in their absence |
   | Application owner | Deputy application owner |
   | Lead engineer | Backup lead engineer, or the lead developer |
   | Infrastructure owner | Deputy infrastructure owner |
   | DR process owner | Deputy DR process owner |
   | Governance / risk contact | Deputy governance contact |
   | Signing authority | Alternate signatory |

   **If a role has no name, that is your first finding.** A system with no named business
   owner has nobody who can sign an MTD, and no amount of documentation fixes that.

   **If a role has a name but no deputy, that is a finding of the same class**, not a lesser
   one. A plan whose recovery depends on one unreachable person has a single point of failure
   written into the plan rather than into the estate. NIST SP 800-34 Rev. 1 §3.4.6 says team
   leaders "should have a designated alternate to act as the leader if the primary leader is
   unavailable", and §4.2.1 that "a successor should be clearly identified" for whoever holds
   declaration authority. The reference example carries the gap it warns about: its
   authority matrix names a deputy for the declaration and none for a planned switchover or a
   failback, the two actions with no "declare and act" path around a missing name.

   **Never substitute yourself for a missing name, and never invent a deputy.** An unfilled
   role and an unnamed deputy are both recorded as MISSING against whoever owes the answer,
   like any other fact.

---

## Phase 0 — The estate (half a day, two or three people)

Invoke `itscp-portfolio` **before** planning anything.

You are building a register of every system, not choosing one to start with. Ask for it in
five groups rather than as an inventory, because the grouping is what finds the systems a
CMDB misses:

> "What's the core system of record everything reads from? What reads from it? What do you
> build and deploy those with? What do clients push data into? What's publicly visible?"

Then three things that only make sense across an estate:

1. **Rank the tiers against a budget.** Asked alone, every owner says Tier 0. Set the budget
   from *people* — "recovering one system takes most of two engineers for the first hour, you
   have six engineers" — and force the ranking.
2. **Map recovery dependencies**, with `itscp-dependencies`. Not what a system needs to run:
   what it needs to *be recovered*. Where are the runbooks? How do you log in to the console?
   Where do the credentials come from? These find something in almost every engagement.
3. **Assign recovery waves.** Note that source control and the artefact repository usually
   belong in an early wave, not a late one, because the recovery needs them.

```bash
python3 plugin/itscp_portfolio.py portfolio.toml
```

**Do not start a per-system plan while this reports errors.** An inversion means two signed
figures contradict each other, and building a plan on top of one bakes the contradiction in.

Then, per system, in wave order, run Phases 1–7 below.

---

## Phase 0b — Scope one system (30 minutes, you alone)

Invoke `itscp-build`. It asks six questions and creates the repository skeleton and the answer
store.

Decide one thing here: **one plan per application suite, or one per system?** What you are
building is an ITSCP, an IT service continuity plan, and it borrows its structure from NIST's
ISCP, which is a system-level artefact. If your suite is genuinely one system with one
recovery, one plan.
If Finance and Manufacturing fail over independently, they are two plans that share an
inventory.

> **Getting this wrong is expensive.** A single plan covering systems with different MTDs
> ends up designed to the strictest one and priced accordingly, or — worse — to the loosest
> one and silently under-protecting the rest.

---

## Phase 1 — Discovery (60 minutes, read-only)

Invoke `itscp-discover`.

It calls the `itscp_discover_oci` tool. Show the customer the dry run first, always:

    itscp_discover_oci compartment=<ocid> regions=<primary>,<standby> dry_run=true

Then the real walk:

    itscp_discover_oci compartment=<ocid> regions=<primary>,<standby> dry_run=false

Output lands in `discovery-output/` inside your plan repository. Pass `out=<directory>` to put
it somewhere else.

Every call is a `list` or a `get`, enforced structurally rather than by convention. Verify it
yourself before pointing it at production, from your clone of this repository:

```bash
plugin/scripts/discover/test-readonly.sh
```

**You now have an inventory and, more usefully, `gaps.md`.** The gaps are interview material:
resources nobody can name, a standby that was supposed to exist, a replication policy covering
three of five buckets.

---

## Phase 2 — The business interview (90 minutes) — THE GATE

Invoke `itscp-interview-business`. Interviewee: the business or process owner.

**Do not proceed past this phase without a signed tier assignment.** Tier determines standby
capacity, replication topology and run cost. Everything after this is built to these numbers,
and all of it is expensive to change.

If the business owner is unavailable for three weeks, wait three weeks. Proceeding on assumed
tiers feels productive and is the most costly mistake available here: assumed tiers become
real architecture within a day and are never revisited.

**Output:** BIA, tiers, MTD/RTO/RPO with mechanisms, MBCO, manual workarounds, a signature.

---

## Phase 3 — The technical interviews (90–120 minutes each)

Independent of each other; run in either order or in parallel with different people.

- `itscp-interview-application` — application owner, with the lead engineer for anything
  hands-on. System description, start order, interconnections, the validation pack, work
  recovery activities.
- `itscp-interview-infrastructure` — infrastructure owner, with the lead engineer for the
  measured figures and for what has actually been executed. Replication design, standby
  posture and cost, the alternate site, recovery procedures.

**Bring the deputy to at least one of these.** The backup lead engineer sitting in is the
cheapest test available of whether the deputy could really do it, and it usually answers the
question before you have to ask it.

**Expect a contradiction here, and do not resolve it yourself.** The business says four hours;
the application owner says batch reprocessing alone takes a day. Record both, name whose
decision it is, and take it back to the business owner. A plan with a visible, owned
contradiction is honest. A plan where one side was silently dropped fails in exactly that place.

---

## Phase 4 — The continuity interview (90 minutes)

Invoke `itscp-interview-continuity`. Interviewee: the DR process owner, with their deputy.

Runs after Phase 3 because escalation thresholds need real recovery steps to threshold against.

This is where most organisations discover that **nobody owns the declaration decision.** That
is not a failure of the interview; it is the single most valuable thing it produces.

**Output:** roles and the deputy named for each, succession, activation criteria, call tree,
outage assessment, escalation thresholds, deactivation. The succession elicited here and the
Phase 0 deputy roster must agree; where they do not, that is a recorded conflict with a named
decision owner, not something to reconcile quietly.

---

## Phase 5 — The governance interview (60 minutes)

Invoke `itscp-interview-governance`. Approval, review cadence, training, exercises, evidence,
risk register.

**A design describes what would happen; a plan is a design somebody committed to.** The
difference is a signature, a review date and a trained population.

---

## Phase 6 — Generate and audit (half a day, you alone)

`itscp-build` renders the repository. Then invoke `itscp-audit`.

The audit starts every requirement REFUTED and moves it only on a quoted sentence. It reports
four things a normal audit cannot see, because it can read the answer store:

- Sections below 100% coverage
- **Every value with `confidence: low`** — the guesses inside a document about to be signed
- Unresolved contradictions
- Deferred answers past their due date

Fix what blocks approval. Leave the rest visible.

---

## Phase 7 — Approve, then drill

Get the signature. Then the sentence that has to survive into every conversation afterwards:

> **Every duration in this plan is a design target. None of them are commitments until a drill
> has measured them.**

Schedule the first drill before the approval meeting ends. A plan that has never been executed
is a hypothesis with a signature on it.

---

## What good looks like after one pass

| | Realistic first pass | What it means |
|---|---|---|
| Coverage | 70–85% | The rest are named gaps with named owners. Correct, not deficient |
| Low-confidence values | 20–40% | These are your first drill objectives |
| Sections fully complete | Roles, notification, activation, inventory | These need decisions, not measurements |
| Sections still open | Validation timings, WRT durations, re-baseline costs | These need a drill. They cannot be interviewed into existence |

**A first-pass plan at 100% coverage with high confidence throughout has almost certainly been
guessed rather than elicited.** Be suspicious of your own output if it looks finished.

---

## Common ways this goes wrong

| Mistake | Consequence |
|---|---|
| Planning one application without registering the estate | The plan's targets are unchecked against the systems it depends on, and the first invocation finds the inversion |
| Asking a single owner for their tier | In isolation the answer is always Tier 0. Tiering is comparative or it is nothing |
| Asking only what a system needs to run | You will miss what it needs to be recovered, which is where the circular plans are |
| Skipping discovery because "we know our estate" | The interview spends 40 minutes reconstructing what a read-only walk produces in 10 |
| Running the technical interviews before the tier gate | You design to assumed tiers and rebuild later |
| Letting IT answer the business questions | IT sets its own targets; the business signs something it did not choose |
| Naming a role holder and leaving the deputy blank | The plan now depends on one person being reachable. It is a finding, and it is cheapest to fix on day one |
| Putting yourself down as the deputy to fill the column | An invented deputy is the plausible-answer failure, wearing a name badge |
| Filling gaps with sensible defaults to look complete | The one failure this toolkit exists to prevent. A plausible number nobody gave is worse than a visible gap |
| Treating the generated plan as finished | It is a design. The drill makes it a plan |
| Committing the answer store | It holds names, numbers and organisational weak points. Check `.gitignore` before the first push |
