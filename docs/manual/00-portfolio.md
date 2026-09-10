# Phase 0 — The portfolio and the dependency map

> **Generated file.** It is assembled from the skills, the question bank and `GETTING-STARTED.md` by `plugin/itscp_manual.py`, and an edit made here is deleted by the next regeneration. Change the source and run `python3 plugin/itscp_manual.py`.

**Who is in the room:** whoever can see the whole portfolio — enterprise architect, head of infrastructure, or the CIO. Usually two or three people together, because nobody has the complete picture alone. That gap is itself the first finding.

**How long:** half a day for a first register, plus an hour per follow-up.

Runs once for the organization, before any plan. It produces `portfolio.toml`: the register of systems, the comparative tier ranking, the recovery waves, and the dependency graph between them. Four failures live only above the level of a single plan and none of them are visible from inside one, which is why this comes first rather than after the plan that would have to be rebuilt.

**Nothing in this phase is recorded in an answer store.** A register of systems is a different shape from a set of facts about one system, so it is written by hand into `portfolio.toml` and checked with `python3 plugin/itscp_portfolio.py portfolio.toml`. The fields that file holds are listed at the end of this page.

**Do not start a per-system plan while the validator reports errors.** An inversion means two signed figures contradict each other, and a plan built on top of one bakes the contradiction in.

**Run under [the method](method.md).** No fact enters the plan unless a human said it, a read-only API returned it, or it is marked `MISSING` against a named owner.

---

## The technique — `itscp-portfolio`

*Use when an organization needs continuity plans for more than one system, when it is unclear which application to plan for first or in what order systems recover, when recovery tiers must be ranked across a portfolio rather than assigned one application at a time, or when asked how many plans an organization needs.*

Builds the register of systems, ranks them against each other, and fixes the order they
recover in. Run **before** any per-system plan.

**Read first:** `itscp-method-interview` for the elicitation discipline.

**Interviewee:** whoever can see the whole portfolio — enterprise architect, head of
infrastructure, or the CIO. Usually two or three people together, because nobody has the
complete picture alone. That gap is itself the first finding.

**Time:** half a day for a first register, plus an hour per follow-up.

---

### Why this exists

An organization does not have *a* system. It has a core product suite, the applications that
read from it, the tooling those are built and deployed with, the public interfaces clients
push data into, and the websites fronting all of it.

Planning them one at a time produces **N individually-plausible, collectively-impossible
plans.** Four failures live only above the level of a single plan, and none are visible from
inside one:

| Failure | What it looks like |
|---|---|
| **Recovery time inversion** | Order management declares 2h. The identity database it authenticates against declares 8h. Both plans are internally coherent; together they are a lie |
| **Recovery dependency** | The runbooks are in the source control server that is inside the outage. Nobody asked what a system needs in order to *be recovered*, only what it needs to run |
| **Wave ordering** | A dependency scheduled to recover after its dependant. The plan cannot execute in the order it is written |
| **Tier inflation** | Asked in isolation, forty owners declare forty Tier 0 systems. A tier means nothing without a budget to rank against |

`itscp_portfolio.py` checks all four mechanically. Your job is to elicit the register it
checks.

---

### What a register holds

One `portfolio.toml`, one row per system:

| Field | Notes |
|---|---|
| `slug`, `name` | The name the business uses, not the hostname |
| `class` | `shared-platform`, `core-data`, `dependent-app`, `supporting-infra`, `public-api`, `public-web` |
| `business_owner`, `application_owner` | **A system with neither is an error, not a gap.** Nobody can sign its recovery target |
| `tier`, `rto`, `rpo`, `mtd` | Ranked comparatively, not assigned in isolation |
| `wave` | Which recovery step it belongs to |
| `plan_repo` | Where its ISCP lives. Empty means known-about and unplanned |
| `depends_on` | Elicited by `itscp-dependencies` |

---

### Run order

#### 1. Enumerate the systems (60 min)

Do not start from a CMDB export. Start from the shape:

> "Walk me through this in five groups. What's the core system of record everything reads
> from? What reads from it? What do you build and deploy those with? What do clients push
> data into? What's publicly visible?"

That framing finds systems an inventory misses, because it asks about *roles* rather than
about servers. Then the question that finds the rest:

> "What's running that nobody in this room owns?"

**Expect the register to be incomplete after the first pass, and say so.** A register of
thirty systems where four are `MISSING` an owner is more useful than a tidy list of
twenty-six.

#### 2. Classify (20 min)

Class determines roughly where a system sits in the recovery order and which questions its
plan deserves. Two classes are routinely miscalled:

- **`supporting-infra` is not automatically last.** Source control and the artefact
  repository hold the runbooks and the deployment artefacts, which makes them recovery
  dependencies of nearly everything. In the shipped example they recover in wave 1, not
  wave 4, and that is the single most common correction this skill makes.
- **`public-api` is not just another app.** A client that has POSTed a payload considers it
  delivered. There is no upstream system holding a copy to resend, so ingest APIs often
  carry a tighter RPO than the internal systems behind them.

#### 3. Rank against a budget (90 min) — the part that matters

**Tiering one system at a time always yields Tier 0.** Tiering is comparative, so make it
comparative:

> "You can have four Tier 0 systems. Recovering one takes most of two people for the first
> hour. Which four?"

Set the budget from **people**, not capacity. Standby infrastructure scales with money;
your six engineers do not scale at all, and they are what actually caps concurrent recovery.

Then force the ranking:

> "If the region went at 3am and you could only start three of these, which three, and what
> does the fourth owner hear in the morning?"

Record the ranking **and** the fact that it was made under a stated budget. When someone
later asks why their system is Tier 2, the answer is a decision somebody made, not an
oversight.

#### 4. Assign waves (45 min)

A wave is a step of the recovery order with a stated concurrency limit. Start from the
default five and adjust:

| Wave | Holds | Why |
|---|---|---|
| 0 Foundation | Network, identity | Nothing else can be reached or logged in to |
| 1 Secrets and recovery tooling | Vault, source control, artefacts | What the recovery itself needs |
| 2 Core systems of record | The core suite | What everything reads |
| 3 Dependent apps and public interfaces | Apps, ingest APIs | Built on the core |
| 4 Supporting and internal tooling | Ticketing, reporting, marketing site | Can wait a day |

> "How many of these can you genuinely bring up at the same time, with the people you'd
> actually have at 3am on a Sunday?"

That number is `max_concurrent`, and it is almost always smaller than the first answer.

#### 5. Validate, and read the findings out loud

```bash
python3 itscp_portfolio.py portfolio.toml
```

Exit 0 clean, 1 warnings, 2 errors. Errors are contradictions, not preferences — an RTO
inversion means one of two signed figures is wrong and the two business owners have to agree
which. **Take inversions back to the owners; never resolve one by editing a number yourself.**

---

### Then, per system

`itscp-build` runs once per system, in wave order, generating a plan repository each. The
register is the input: it supplies the tier, the targets and the dependencies each plan has
to honor. Re-validate after each plan is signed, because a signed plan can change a number
the register was checked against.

---

### Red flags

| Thought | Reality |
|---|---|
| "There are only two real systems, the rest are infrastructure" | The infrastructure is where the recovery dependencies live. Register it |
| "The CMDB has this already" | A CMDB lists what exists. It does not say what breaks without what |
| "Every owner said Tier 0, so most are Tier 0" | Nobody has ranked yet. Set the budget and ask again |
| "I'll fix the inversion by relaxing the app's RTO" | Two business owners signed those figures. The correction is theirs |
| "Waves are obvious, I'll assign them" | The concurrency limit is a statement about people. Ask |
| "Supporting tooling recovers last" | Not if the runbooks are in it. Ask what recovery needs, not what production needs |

---

## The technique — `itscp-dependencies`

*Use when mapping what one system needs from another, when the recovery order across several systems has to be established, when checking whether recovery targets are consistent between a system and the things it depends on, or when working out what is needed in order to recover a system as opposed to run it.*

Builds the dependency graph in `portfolio.toml`, and it is one question that makes it worth
doing separately from everything else:

> **What does this system need in order to be *recovered*, as distinct from what it needs in
> order to *run*?**

Every interview in every continuity toolkit asks the second. Almost none ask the first. The
gap between them is where real invocations fail.

**Read first:** `itscp-method-interview`. Run after `itscp-portfolio` has the register and
before or alongside the per-system interviews.

**Interviewee:** the application owner and the infrastructure owner for each system, together
where possible. Runtime dependencies are usually known; recovery dependencies usually are not,
and the conversation that surfaces them needs both people in it.

**Time:** 20–30 minutes per system, faster once the pattern is understood.

---

### Three kinds of edge

| Kind | Means | Found by asking |
|---|---|---|
| `runtime` | Needed for the system to function | "What does this call, read from or authenticate against?" |
| `recovery` | Needed in order to **recover** the system | "Walk me through recovering this. What do you open, log into, or pull from?" |
| `data` | Exchanges data with it; an interface, not a prerequisite | "Who sends you files, and who is waiting on yours?" |

Plus a criticality: `hard` means it does not work at all without it; `soft` means degraded but
functional. Only hard edges constrain the recovery order.

---

### Eliciting recovery dependencies

Do not ask "what are your recovery dependencies". Nobody has a list. Walk them through the
recovery and catch the tools they mention in passing:

> "It's 3am, the region is gone, and you're recovering this. Talk me through the first ten
> minutes. What do you open first?"

Then the four follow-ups that catch what the walkthrough missed:

1. **"Where is the runbook you'd be following?"** If it is in the source control server, and
   that server is in the failed region, the instructions are inside the outage.
2. **"How do you log in to the cloud console to do any of this?"** If it federates through
   the identity system, and identity is a system on the register, the first thing to recover
   is the thing you cannot authenticate to.
3. **"Where do the credentials and certificates come from?"** A secrets store is a recovery
   dependency of everything that holds a credential, which is everything.
4. **"If you had to rebuild rather than fail over, where do the artefacts come from?"** The
   artefact repository becomes a hard recovery dependency the moment the answer is "rebuild".

**These four find something in almost every engagement.** They are not exotic; they are the
ordinary consequence of tooling being used to build the systems it also has to recover.

#### The trap they exist to catch

Two systems each needing the other to be recovered first is a deadlock, and neither plan can
see it because each is separately reasonable. The validator raises `recovery-cycle` as an
error. **The fix is never to reorder the pair** — it is to put what one of them needs (a
runbook copy, a break-glass credential, console access that does not federate) somewhere
outside the cycle.

---

### Checking the graph

```bash
python3 itscp_portfolio.py portfolio.toml
```

| Finding | Severity | Means |
|---|---|---|
| `rto-inversion` | ERROR | A system claims to be back before something it cannot run without |
| `recovery-cycle` | ERROR | Systems that each need the other recovered first. Nothing can start |
| `wave-inversion` | ERROR | A hard dependency scheduled after its dependant |
| `unknown-dependency` | ERROR | An edge pointing at a system not in the register |
| `runtime-cycle` | WARNING | Mutually dependent at runtime. Recoverable together, not in an order |
| `wave-concurrency` | WARNING | A hard dependency in the same wave. Ordering inside a wave is unspecified |
| `undeclared-shared-service` | WARNING | Four or more systems hard-depend on it, but it is classed as an ordinary app |

#### Handling an inversion

An RTO inversion is a contradiction between two signed figures, so it is **not yours to
resolve.** Take it back:

> "Order management is signed at four hours. It cannot log in without the identity database,
> which is signed at eight. One of those two numbers has to move. Which, and who signs it?"

Three legitimate outcomes: the dependency's target tightens, the dependant's relaxes, or the
dependency is broken (a cached credential, a read-only mode, a queue that absorbs the gap).
The third is the best answer and the one nobody reaches for unaided — offer it.

**Never resolve an inversion by editing a number.** The register would validate and the plan
would still be impossible; you would have deleted the finding rather than the problem.

---

### What to record

Per edge: `on`, `kind`, `criticality`, and a note saying *what breaks* without it. The note is
what survives a re-organization; the slug is just a pointer.

Keep `soft` honest. "Degraded but functional" must mean somebody can still do their job, not
that the system technically starts. If the answer is "it comes up but nobody can use it",
that edge is `hard`.

---

### Red flags

| Thought | Reality |
|---|---|
| "They listed their integrations, the graph is done" | Integrations are `data` edges. You have not asked what recovery needs |
| "The runbook location is a documentation detail" | It is a hard recovery dependency. It decides whether the plan is readable during the outage |
| "Everything depends on identity, that's not worth recording" | Recording it is what puts identity in wave 0 and catches the login circularity |
| "This dependency is soft, they can work around it" | Ask whether anyone can do their job. If not, it is hard |
| "I'll relax the RTO to clear the inversion" | Two owners signed those figures. Deleting the finding is not fixing the problem |
| "A recovery cycle just means recover them together" | If each needs the other *first*, together does not help. Break it from outside |

---

## What `portfolio.toml` holds

Written by hand and checked with `python3 plugin/itscp_portfolio.py portfolio.toml`. `plugin/portfolio.example.toml` is a fourteen-system register in this shape.

**Once for the organization**

| Field | What it holds |
|---|---|
| `organization` | The organization's name |
| `tier_budget` | How many systems each tier may hold. The budget is what makes the ranking comparative; without one every owner answers tier 0, and is not wrong to |
| `wave` | One block per step of the recovery order: `id`, `name`, `purpose`, and `max_concurrent` — how many of that wave's systems can genuinely be recovered at once, which is a statement about people far more often than about capacity |

**Once per system**

| Field | What it holds |
|---|---|
| `slug`, `name` | The name the business uses, not the hostname |
| `class` | One of `shared-platform`, `core-data`, `dependent-app`, `supporting-infra`, `public-api`, `public-web` |
| `business_owner`, `application_owner` | A system with neither is an error, not a gap: nobody can sign its recovery target |
| `tier`, `rto`, `rpo`, `mtd` | Ranked against the other systems, never in isolation. Durations as people write them: `0`, `30m`, `4h`, `2d` |
| `wave` | Which step of the recovery order it belongs to |
| `plan_repo` | Where its plan lives. Empty means known about and unplanned |
| `notes` | Anything the register would otherwise lose |

**Once per dependency, under the system that has it**

| Field | What it holds |
|---|---|
| `on` | The slug of the system depended on. A slug not in the register is an error |
| `kind` | One of `runtime`, `recovery`, `data`. `recovery` is the one almost nobody asks for, and the one that finds the circular plans |
| `criticality` | `hard` or `soft`. Only hard edges constrain the recovery order |
| `notes` | What breaks without it. This is what survives a reorganization; the slug is only a pointer |

A system with 4 or more hard dependants is a shared service in practice, whatever its declared class, and the validator says so.
