---
name: itscp-portfolio
description: Use when an organization needs continuity plans for more than one system, when it is unclear which application to plan for first or in what order systems recover, when recovery tiers must be ranked across a portfolio rather than assigned one application at a time, or when asked how many plans an organization needs.
---

# itscp-portfolio

Builds the register of systems, ranks them against each other, and fixes the order they
recover in. Run **before** any per-system plan.

**Read first:** `itscp-method-interview` for the elicitation discipline.

**Interviewee:** whoever can see the whole portfolio — enterprise architect, head of
infrastructure, or the CIO. Usually two or three people together, because nobody has the
complete picture alone. That gap is itself the first finding.

**Time:** half a day for a first register, plus an hour per follow-up.

---

## Why this exists

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

## What a register holds

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

## Run order

### 1. Enumerate the systems (60 min)

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

### 2. Classify (20 min)

Class determines roughly where a system sits in the recovery order and which questions its
plan deserves. Two classes are routinely miscalled:

- **`supporting-infra` is not automatically last.** Source control and the artefact
  repository hold the runbooks and the deployment artefacts, which makes them recovery
  dependencies of nearly everything. In the shipped example they recover in wave 1, not
  wave 4, and that is the single most common correction this skill makes.
- **`public-api` is not just another app.** A client that has POSTed a payload considers it
  delivered. There is no upstream system holding a copy to resend, so ingest APIs often
  carry a tighter RPO than the internal systems behind them.

### 3. Rank against a budget (90 min) — the part that matters

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

### 4. Assign waves (45 min)

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

### 5. Validate, and read the findings out loud

```bash
python3 itscp_portfolio.py portfolio.toml
```

Exit 0 clean, 1 warnings, 2 errors. Errors are contradictions, not preferences — an RTO
inversion means one of two signed figures is wrong and the two business owners have to agree
which. **Take inversions back to the owners; never resolve one by editing a number yourself.**

---

## Then, per system

`itscp-build` runs once per system, in wave order, generating a plan repository each. The
register is the input: it supplies the tier, the targets and the dependencies each plan has
to honor. Re-validate after each plan is signed, because a signed plan can change a number
the register was checked against.

---

## Red flags

| Thought | Reality |
|---|---|
| "There are only two real systems, the rest are infrastructure" | The infrastructure is where the recovery dependencies live. Register it |
| "The CMDB has this already" | A CMDB lists what exists. It does not say what breaks without what |
| "Every owner said Tier 0, so most are Tier 0" | Nobody has ranked yet. Set the budget and ask again |
| "I'll fix the inversion by relaxing the app's RTO" | Two business owners signed those figures. The correction is theirs |
| "Waves are obvious, I'll assign them" | The concurrency limit is a statement about people. Ask |
| "Supporting tooling recovers last" | Not if the runbooks are in it. Ask what recovery needs, not what production needs |
