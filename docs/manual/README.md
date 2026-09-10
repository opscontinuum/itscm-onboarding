# The tabletop

> **Generated file.** It is assembled from the skills, the question bank and `GETTING-STARTED.md` by `plugin/itscp_manual.py`, and an edit made here is deleted by the next regeneration. Change the source and run `python3 plugin/itscp_manual.py`.

This engagement, run as a facilitated exercise: the application and infrastructure teams in one room, a printed worksheet on the table, and nothing to install. The questions are the same ones the toolkit asks, because both are generated from the same files.

Two of the phases are deliberately kept out of the room. The business figures come first, on their own, because tiers agreed in front of the engineers who will have to meet them stop being the business's figures. Governance comes afterwards and needs nobody technical.

Read [the method](method.md) before the first session. It is the discipline all of this runs under, and the one part that is not optional. A plan whose numbers nobody gave is worse than one with visible gaps, and the method is what keeps the two apart.

## The running order

| Phase | Session | Answers to come away with |
|---|---|---|
| [Phase 0 — The portfolio and the dependency map](00-portfolio.md) | A workshop, before the tabletop | the register, on a wall |
| [Phase 1 — What the room brings](01-discovery.md) | The tabletop | 1 answer, plus the inventory and the gaps in it |
| [Phase 2 — The business figures, which gate everything after them](02-business.md) | Not the tabletop | 11 answers |
| [Phase 3a — The application segment](03a-application.md) | The tabletop | 19 answers |
| [Phase 3b — The infrastructure segment](03b-infrastructure.md) | The tabletop | 18 answers |
| [Phase 4 — The continuity segment](04-continuity.md) | The tabletop | 21 answers |
| [Phase 5 — Approval, review and training](05-governance.md) | Not the tabletop | 12 answers |
| [Phase 6 — Writing it up, and auditing what you wrote](06-generate-and-audit.md) | You, on your own, with the worksheets from every session in front of you | the written plan |

Phase 7 is not a document. It is the signature, and then the drill: **every duration in the plan is a design target, and none of them are commitments until a drill has measured one.** Schedule the first drill before the approval meeting ends.

## What to print

Each phase page ends with a worksheet sized for its session. Print the worksheet for the session you are running; read the rest of the page before it.

- [The method](method.md) — how an answer is captured, and the appendix for typing the worksheets up afterwards.
- [Every answer, by the document it belongs in](fields.md) — the order to write the plan in, and the full index.

---

## Before you start

Running this as a tabletop, the first of the four does not apply: there is nothing to install and nothing to load. **The other three do, and the fourth is the one people skip.**

### Running this without the toolkit

The technique below is the skills' own words, and the skills assume a loaded plugin. You do not have one. These are the substitutions in effect on this page.

| Where it says | In the room you |
|---|---|
| `picoagent -e ...` | Nothing to load. A tabletop needs the pages you are holding, a wall, and the people. |

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
   written into the plan rather than into the environment. NIST SP 800-34 Rev. 1 §3.4.6 says team
   leaders "should have a designated alternate to act as the leader if the primary leader is
   unavailable", and §4.2.1 that "a successor should be clearly identified" for whoever holds
   declaration authority. The reference example carries the gap it warns about: its
   authority matrix names a deputy for the declaration and none for a planned switchover or a
   failback, the two actions with no "declare and act" path around a missing name.

   **Never substitute yourself for a missing name, and never invent a deputy.** An unfilled
   role and an unnamed deputy are both recorded as MISSING against whoever owes the answer,
   like any other fact.

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

### Running this without the toolkit

The technique below is the skills' own words, and the skills assume a loaded plugin. You do not have one. These are the substitutions in effect on this page.

| Where it says | In the room you |
|---|---|
| the answer store | The stack of worksheets. It holds the same things — the answer, who gave it, how sure they were — in columns rather than in keys. |

| Mistake | Consequence |
|---|---|
| Planning one application without registering the portfolio | The plan's targets are unchecked against the systems it depends on, and the first invocation finds the inversion |
| Asking a single owner for their tier | In isolation the answer is always Tier 0. Tiering is comparative or it is nothing |
| Asking only what a system needs to run | You will miss what it needs to be recovered, which is where the circular plans are |
| Skipping discovery because "we know our environment" | The interview spends 40 minutes reconstructing what a read-only walk produces in 10 |
| Running the technical interviews before the tier gate | You design to assumed tiers and rebuild later |
| Letting IT answer the business questions | IT sets its own targets; the business signs something it did not choose |
| Naming a role holder and leaving the deputy blank | The plan now depends on one person being reachable. It is a finding, and it is cheapest to fix on day one |
| Putting yourself down as the deputy to fill the column | An invented deputy is the plausible-answer failure, wearing a name badge |
| Filling gaps with sensible defaults to look complete | The one failure this toolkit exists to prevent. A plausible number nobody gave is worse than a visible gap |
| Treating the generated plan as finished | It is a design. The drill makes it a plan |
| Committing the answer store | It holds names, numbers and organizational weak points. Check `.gitignore` before the first push |

---
