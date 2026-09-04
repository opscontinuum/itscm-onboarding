# Two plans from one generator

The same toolkit, the same eighty-two questions, run twice. Once before anybody has been
interviewed, and once over a store filled by reading a real plan. Read them side by side and
the toolkit's claim is on the page rather than in a README.

| | [`day-one/`](day-one/) | [`worked-plan/`](worked-plan/) |
|---|---|---|
| Coverage | **0 of 82 (0%)** | **57 of 82 (69%)** |
| ANSWERED | 0 | 56 |
| NOT_APPLICABLE | 0 | 1 |
| MISSING, with a named owner | 82 | 25 |
| Confidence of the answers | not applicable | 35 high, 16 medium, 5 low |
| Every value's provenance | none; nothing is answered | `document:` on all 56 |
| Files generated | 35 | 35 |
| Passes all three acceptance tests | yes | yes |

Neither number is an embarrassment. Zero of eighty-two is the honest starting position of an
engagement, and every one of those eighty-two gaps names the role who can close it, so the
document doubles as a work assignment on the day it is handed over. Sixty-nine per cent is
what a careful reading of a good plan actually yields, and the missing thirty-one per cent is
the part worth reading.

---

## `day-one/`: what an engagement hands over before the first interview

Generated from the starter answer store the plugin already ships
([`plugin/answers.example.toml`](../plugin/answers.example.toml)), in which every field is
MISSING and owned. It is not a degenerate case. It is the deliverable at the end of Phase 0,
and it shows three things the populated example cannot.

**Every gap carries a named owner.** Not one line reads `[MISSING — owner: unassigned]`. Open
[`day-one/plan/docs/02-mtd-tiers.md`](day-one/plan/docs/02-mtd-tiers.md) and each unanswered
field says who owes it: the governance contact owes the impact level, the business owner owes
the tolerable downtime, the application owner owes the instance count. A reader can act on
that page before a single answer exists.

**The drawings say they have no data.** Both
[`tier-ladder.svg`](day-one/plan/docs/diagrams/tier-ladder.svg) and
[`mtd-timeline.svg`](day-one/plan/docs/diagrams/mtd-timeline.svg) render the store's MISSING
marker instead of an axis with nothing on it. A chart with an axis and no bars reads as
"nothing is at risk here", which is a plausible default wearing a graph. This behavior is
invisible in a populated plan and it is the guard that matters most.

**The coverage report reads 0 of 82.** An interview that produces forty named unknowns has
done more for an organization than one producing forty confident inventions.

---

## `worked-plan/`: the same generator over a real plan's content

Three files:

- [`worked-plan/answers.toml`](worked-plan/answers.toml), the 82-field answer store.
- [`worked-plan/plan/`](worked-plan/plan/), the 35-file plan repository generated from it.
- [`worked-plan/session.toml`](worked-plan/session.toml), the derivation, entry by entry.

### These answers came from a document, not from an interview

Every value was read out of [`oci-itscp`](https://github.com/opscontinuum/oci-itscp) at
commit `d475ee6`, a public repository documenting a **hypothetical corporation's** DR plan for
Oracle E-Business Suite on Exadata. Nothing in it is real: no environment, no person, no
identifier. Its own contact roster carries a warning banner saying every name and number in it
is fictitious placeholder data, and this store treats it that way.

So every provenance in the store is `document:oci-itscp/<path>`, naming the file the fact came
from. **A real engagement produces `interview:<role>:<date>` provenance instead**, and a
reader comparing the two can see at a glance which kind of plan they are holding. The store
refuses a provenance value meaning "the assistant worked it out", by name, so there was no
third option: read it out of the reference plan, or leave it MISSING.

Nothing was invented. Filling eighty-two fields with plausible prose and recording it as
elicited is precisely the failure this toolkit exists to prevent, and an example that did it
would discredit the tool it demonstrates.

### What the reference plan could not answer

Twenty-five fields stayed MISSING. They are not oversights in the derivation; they are what a
careful reader finds when they hold a good plan up against a complete question set.

| Field | Owed by | Why |
|---|---|---|
| `system.impact_level` | governance/risk contact | **No availability impact level is assigned anywhere.** FIPS 199 appears only structurally, in the observation that a plan-approval statement is required at every level. |
| `system.categorization` | governance/risk contact | No classification is recorded and no place one is held is named. |
| `system.business_name` | business owner | The corporation is hypothetical and never named. |
| `business.mtd.tier0` | business owner | The two-hour figure is stated in three places and has no mechanism. |
| `business.rpo.tier0` | business owner | Same: a figure, and nothing about what is in those seconds. |
| `business.mbco.tier0` | business owner | The plan records this against itself as gap G1. |
| `business.workarounds` | business owner | No manual workaround appears anywhere. |
| `business.tier_signoff` | business owner | The workshop output table is empty; no signature exists. |
| `business.reconstruction_effort` | business owner | Never asked, never costed. |
| `app.interconnections` | application owner | No interconnections table; one named partner and an empty row. |
| `app.unsafe_reruns` | application owner | The plan points at an idempotency register that does not exist. |
| `infra.measured_rtt_ms` | lead engineer | The 60 to 70 millisecond figure is explicitly an estimate; the plan says to measure your own and directs it to a file that is not there. |
| `infra.standby_cost_floor` | infrastructure owner | The cost model is an empty template; even the currency is a blank. |
| `infra.warned_posture_time` | infrastructure owner | "Takes minutes", never quantified, never measured. |
| `continuity.bridge` | DR process owner | The bridge is a placeholder; only its dependency is stated. |
| `continuity.contact_roster` | DR process owner | A roster file with no verified contact in it. |
| `continuity.vendor_obligations` | governance/risk contact | Marked "to be resolved" by the plan itself. |
| `continuity.people_unavailable` | DR process owner | The plan asks this of itself and records it unanswered. |
| `continuity.assessment_calibration` | DR process owner | No incident and no drill, so nothing to calibrate against. |
| `governance.risk_register` | governance/risk contact | The plan records this against itself as gap G2. The file does not exist. |
| `governance.associated_plans` | governance/risk contact | No list of plans this one leans on, and no owners. |
| `governance.drill_cadence` | governance/risk contact | Quarterly is stated; nothing says what would cause a skip or who notices. |
| `governance.availability_boundary` | governance/risk contact | The plan records this against itself as gap G4. |
| `governance.breach_disclosure_clock` | governance/risk contact | The plan disclaims authority over it and leaves the holder blank. |
| `discovery.completed` | infrastructure owner | No read-only walk has run; there is no tenancy. |

Five of those are gaps the reference plan already names against itself, which is to its
credit: G1 the minimum continuity objective, G2 the risk register, G4 the availability
boundary, and the two roles-and-responsibilities questions it marks "to be resolved". The
derivation did not discover them. It records them where an auditor would look, instead of in
a crosswalk table near the back. Its fourth self-named gap, G3 the review cadence, comes back
answered at medium confidence, because the plan does state an annual cadence with six
re-approval triggers and an owner and then says the wider maintenance section is still open.

### The impact level, and what it costs

`system.impact_level` is the one gap with a structural consequence. It selects which of NIST
SP 800-34's three sample templates the plan is graded against, and therefore what letter each
appendix carries. Uncategorized, the generated plan keeps the high-impact Appendix A.3
lettering, because that template is the superset and an auditor with no stated level grades
against it. So
[`worked-plan/plan/checklists/manual-workarounds.md`](worked-plan/plan/checklists/manual-workarounds.md)
is headed `APPENDIX D ALTERNATE PROCESSING PROCEDURES` and
[`validation-pack.md`](worked-plan/plan/checklists/validation-pack.md) is headed
`APPENDIX E SYSTEM VALIDATION TEST PLAN`. On a low-impact system both would letter one lower.
The plan is graded strictly because nobody said it need not be.

### Sixteen figures with nothing behind them

The store refuses an answered figure that arrives without a mechanism, because a number with
no mechanism behind it is a guess wearing a suit. Ten questions carry that requirement.
**Eight of the ten could not be satisfied** and stayed MISSING; only the application-tier
reconfiguration estimate and the ten-minute decision budget arrived with an explanation
attached.

The tier table is the clearer demonstration, because there the figures survive into the
document with the refusal beside them. Four tiers, each with a tolerable downtime, a recovery
time, a work recovery time and a recovery point: **sixteen figures, and not one mechanism**.
Open [`worked-plan/plan/docs/02-mtd-tiers.md`](worked-plan/plan/docs/02-mtd-tiers.md) and the
`what_breaks_at_the_mtd` column says so in every row. The reference plan is candid about it
itself, at `README.md:157`:

> The figures are this plan's own design targets for the hypothetical corporation; they are
> not derived from any source.

That is why the whole row carries low confidence. Confidence here is assigned from how the
answer arrived and not from how plausible it sounds: 35 high where the plan states something
plainly, 16 medium where it states it as an assumption it asks the reader to confirm, and 5
low where it hedges or marks a figure unverified.

### The five files that do not exist

The reference plan links five files it never wrote:
`checklists/manual-workarounds.md`, `checklists/validation-pack.md`, `docs/11-inventory.md`,
`docs/12-interconnections.md` and `checklists/risk-register.md`. The derivation found a
sixth, `evidence/latency-baseline.md`, which is where the plan tells the reader to record the
measurement its whole replication design rests on.

The generator writes all of them, because the document set and the field map are the same
data and a document cannot point at a file nobody wrote. So the contrast is visible: open
[`worked-plan/plan/docs/12-interconnections.md`](worked-plan/plan/docs/12-interconnections.md)
and it exists, is headed correctly, and says the interconnection table is MISSING and owed by
the application owner. That is the point. A structural guarantee is not the same as content,
and the toolkit only claims the first.

### Where the derivation ran out of source

Two markers, used consistently, so a reader can grep for the edges of what was actually
stated. The phrase **"not stated in the reference plan"** appears 175 times in the generated
plan and marks a cell the reference does not fill. The phrase **"a fictitious placeholder in
the reference plan"** marks a cell the reference fills with data its own banner says is
invented, which is a different thing and not an answer either.

The rule applied throughout: a table field is answered when its identifying column and at
least one substantive column are stated, and the rest of the cells say what they are. A field
where nothing substantive is stated stays MISSING. That is why `continuity.vendor_contacts` is
answered with placeholder contact details marked as such, and `continuity.contact_roster` is
MISSING outright.

---

## Where the toolkit's vocabulary had to bend

An honest example has to report where it did not fit. Three places, all recorded in the files
themselves.

**Read-backs.** Forty-eight questions require the answer to be read back to the interviewee
and confirmed before it may be written down. Thirty-eight of them are answered here, and
nobody was read anything back to. Those records carry `readback = "confirmed"` because the
store will not accept them otherwise, and each one also carries a note saying that no
interview took place and that the value is quoted from the cited file rather than drafted on
anyone's behalf. The read-back exists so that words attributed to a source are the source's
own; a committed, citable file is a different form of that guarantee and not the one the field
was designed for. The note is the honest record. It is not a substitute for the rule.

**The session vocabulary has no value meaning "derived from a document".** The transcript's
closed event list runs asked, answered, unanswered, deferred, not applicable, drafted, three
read-back outcomes, conflict raised and superseded. Every one presumes a person. Every entry
also has to name who was in the room, by role, from the roster. So
[`worked-plan/session.toml`](worked-plan/session.toml) uses `answered` and `unanswered` for
what the reference plan states and does not state, names the role that owns the field rather
than anybody who was present, leaves the interviewee unnamed because there was none, and says
all of this in its own `[meta]` block. That is the least distorting reading available; it is
still a bend, and it is the clearest candidate for a new event value.

**A closed option list could not carry a stated condition.**
`continuity.unknown_estimate_default` offers `declare` or `wait`. The reference plan answers
"declare", conditioned on the blast radius being regional. The condition is recorded as the
mechanism beside the value so that it renders in the document's References section rather than
being dropped, and a reader is not told to declare unconditionally.

**Neither drawing has data behind it.** The tier ladder needs each tier's posture and relative
run cost; the timeline needs five activity strings. No question in the bank asks for any of
them, so even a fully derived store draws both as MISSING. That is a finding about the
toolkit, not about the reference plan, which states all six of those values.

---

## Why an answer store is committed here, once

[`worked-plan/answers.toml`](worked-plan/answers.toml) is the only answer store that should
ever be committed anywhere. The file's own header states the terms and so does this: every
value in it was read out of a public repository about a hypothetical corporation. There is no
real environment, no real person, no real organization and no real identifier in it, so there is
nothing to leak.

**Your store is not this store.** A populated store accumulates roles, telephone numbers,
resource identifiers, tolerable-downtime figures and the places an organization is weak. It
is the most sensitive file the toolkit produces, `.itscm/` is gitignored wholesale so that a
new artefact is private by default rather than private if somebody remembers, and none of that
changes because of this file. The exception exists so that the toolkit can be judged by
reading its output instead of by running it, and it does not generalise.

`day-one/` needs no such argument. It contains no organizational detail at all, because
nothing has been answered.

---

## Reproducing this

Both trees are regenerated and compared byte for byte by section 9 of the test suite, so
neither can silently rot when the renderer or the question bank changes:

```bash
plugin/tests/run-tests.sh          # nine sections; 9 is the examples
cd plugin/tests && python3 test_examples.py
```

The section rebuilds `worked-plan/plan/` from `worked-plan/answers.toml` and `day-one/plan/`
from the shipped starter store, compares every path and every byte, and additionally holds the
committed store to the terms of its exception: canonical emitter output, no shape that looks
like a real identifier, a header saying why it is here, and no provenance claiming an
interview that never happened.
