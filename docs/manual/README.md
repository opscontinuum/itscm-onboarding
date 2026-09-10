# The manual

> **Generated file.** It is assembled from the skills, the question bank and `GETTING-STARTED.md` by `plugin/itscp_manual.py`, and an edit made here is deleted by the next regeneration. Change the source and run `python3 plugin/itscp_manual.py`.

The onboarding run by hand: the same phases in the same order, for somebody working from this page rather than from a loaded plugin. Every phase carries the technique the corresponding skill carries, and every interview phase ends with the checklist of fields it records.

**Read [the method](method.md) before the first interview.** It is the discipline all of the phases are run under, and the one thing here that is not optional: a plan whose numbers nobody gave is worse than one with visible gaps, and the method is what keeps the difference legible.

## The sequence

| Phase | Who is in the room | Fields recorded |
|---|---|---|
| [Phase 0 — The portfolio and the dependency map](00-portfolio.md) | Whoever can see the whole portfolio — enterprise architect, head of infrastructure, or the CIO. Usually two or three people together, because nobody has the complete picture alone. That gap is itself the first finding. | none — see the page |
| [Phase 1 — Discovery](01-discovery.md) | You, on your own | 1 |
| [Phase 2 — The business interview, which gates the rest](02-business.md) | The business or process owner. Not IT. If the only person available is from IT, stop and say so: an MTD signed by IT is IT telling itself what it is allowed to fail at. | 11 |
| [Phase 3a — The application interview](03a-application.md) | The application owner — whoever is accountable for the application working, not for the infrastructure under it. In an ERP context this is usually the functional lead or applications DBA rather than the cloud team. | 19 |
| [Phase 3b — The infrastructure interview](03b-infrastructure.md) | The cloud or infrastructure owner, with the lead engineer. The owner holds the design and the budget; the lead engineer holds the measured figures and the answer to section 6, and those are the parts of this interview that decide how much of the plan is real. | 18 |
| [Phase 4 — The continuity interview](04-continuity.md) | The DR process owner, incident manager, or whoever would actually be running the bridge at 3am, with their deputy in the room where one is named. If nobody holds that role, you have found the most important gap in the engagement; say so before continuing. | 21 |
| [Phase 5 — The governance interview](05-governance.md) | Governance, risk, audit, or compliance. In a smaller organization this may be the CIO. If nobody holds it, the plan can still be built; it just cannot be approved, and that should be stated rather than discovered at audit. | 12 |
| [Phase 6 — Assemble and audit](06-generate-and-audit.md) | You, on your own | none — see the page |

Phase 7 is not a document. It is the signature, and then the drill: **every duration in the plan is a design target, and none of them are commitments until a drill has measured one.** Schedule the first drill before the approval meeting ends.

## Supporting pages

- [The method](method.md) — the Iron Rule, the statuses, confidence, provenance, and how to write a record by hand.
- [Every field, by the file it lands in](fields.md) — the order to write the plan in, and the full index of keys.

---

## Before you start

Working by hand, the first of the four is optional: you need a clone of this repository for the validator and the discovery script, not a loaded plugin. **The other three are not optional, and the fourth is the one people skip.**

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
