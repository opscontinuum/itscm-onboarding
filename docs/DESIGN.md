# Design

Why the toolkit is shaped the way it is, including what was rejected. Written before
implementation and kept as the record of the decisions.

---

## Problem

An organisation needs a continuity plan for each application suite it runs. The people who
must supply the facts are spread across the business, the application team, infrastructure,
incident management and governance. None of them has read NIST SP 800-34, and the person
assembling the plan usually has not either.

The naive automation — generate a plan from a template and a few prompts — produces a document
that looks finished and is mostly invention. That document then gets signed.

## The failure mode being designed against

**A plausible answer nobody gave.** Not a wrong answer: a confident, well-formatted,
unattributable one. It is worse than a gap because it cannot be audited, it reads as complete,
and it will be believed by the people relying on it during an outage.

Every structural decision below follows from designing against that one failure.

---

## Decision 1 — Skills grouped by interviewee, not by ITSCP section

**Chosen:** one orchestrator, one discovery skill, five interview skills grouped by who holds
the knowledge, one audit skill.

**Rejected — one skill per ITSCP section (~20 skills).** Faithful to the standard and maximally
tailorable, but the elicitation method would be duplicated twenty times, and a user who does
not know the standard has no idea which to run or in what order. Sections do not cluster by
number; they cluster by who can answer them.

**Rejected — a single monolithic skill with modes.** Cheapest to discover, but one enormous
document and no way to run a single section without loading all of it.

The deciding argument: a blind user's real problem is not "which section am I on", it is "who
do I need in the room". Grouping by interviewee means you book the business owner once rather
than four times.

## Decision 2 — A separate repository from the reference example

The relationship is one-to-many: one toolkit, many generated plan repositories. A generator
cannot live inside one of its own outputs, and improvements to the interview logic must be
able to reach plans generated last quarter.

Secondary reasons: the two have different quality bars (citation discipline versus elicitation
quality) and different lifecycles (the example changes rarely; the toolkit will iterate fast).

**The split rule:** artefacts that complete the worked example belong to the example.
Elicitation, generation and discovery belong here.

## Decision 3 — Provenance on every fact

Direct analogue of the reference example's citation discipline. Every `ANSWERED` field records
`interview:<role>:<date>`, `oci-discovery:<operation>`, `document:<path>` or `operator`.

**There is deliberately no provenance value meaning "the assistant worked it out."** Removing
the representation removes the option. Reasoned conclusions go into a document's *Unverified
statements* section, labelled as judgements — never into the store as facts.

## Decision 4 — Every field starts MISSING

Borrowed from the reference example's compliance-audit skill, where every requirement starts
REFUTED until a quoted sentence moves it. Applied to elicitation: a field is `MISSING` with a
named owner until somebody answers it.

This makes the honest outcome — "we don't know, and here is who would" — a first-class result
rather than a hole to be filled. An interview producing forty named unknowns has done more for
the organisation than one producing forty confident inventions.

## Decision 5 — A single flat answer store

`.itscm/answers.yaml`, flat dotted keys, one file per plan.

Solves three problems that appear in the first hour of real use: interviews get interrupted
and must resume; the same fact has two plausible askers and must not be asked twice;
regenerating after a template fix must not require re-interviewing anyone.

Flat keys over nested structure because the store is read by humans mid-incident-planning,
diffed in review, and merged across parallel interviews. Nesting buys elegance and costs all
three.

## Decision 6 — Discovery is read-only, structurally

The reference example's Terraform is apply-locked because authoring against a hypothetical
estate is a different risk posture from touching a real one. This toolkit touches real ones.

An allowlist (`^(list|get)`) rather than a denylist, so a service shipped tomorrow with a novel
destructive verb is refused by default rather than discovered in production. Enforced by a
wrapper that fails closed, plus a static tripwire that fails the test suite if any script ever
calls the CLI outside the wrapper.

`--dry-run` exists for a social reason as much as a technical one: it converts "an AI is going
to look at our production tenancy" into a reviewable list of commands.

## Decision 7 — Coverage is always reported with confidence

Coverage alone is a misleading metric. A plan at 90% coverage where two thirds of values are
low confidence describes an organisation that has guessed comprehensively.

`itscp-build` prints the confidence distribution beside every coverage figure, and `itscp-audit`
treats low-confidence values in an approved plan as a first-class finding — they are the
numbers most likely to be wrong, in the document most likely to be believed.

---

## Decision 8 — The portfolio is a register, not an answer store

Added after the single-system assumption was challenged. Organisations have estates: a core
suite, its dependants, the tooling underneath, public ingest interfaces, public sites.

**A register of systems is a different shape from a set of facts about one system.** The
answer store holds facts with provenance, confidence and a status per field. The register
holds rows with edges between them, and the interesting questions about it are graph
questions — is anything scheduled before its dependency, does anything need itself to be
recovered. So it is a separate file (`portfolio.toml`) with a separate module, rather than a
namespace inside a store whose validation rules are about attribution.

**Rejected — one plan per organisation with system annexes.** Simplest for a small estate,
unreadable past ten systems, and an auditor asking for one system's ISCP receives the whole
portfolio. NIST's artefact is system-level and staying aligned with that is worth more than
the convenience.

**Rejected — inferring dependencies from discovery.** Network reachability is not dependency;
two systems in the same subnet may have nothing to do with each other, and the load-bearing
edges (a runbook location, a federated console login) leave no trace in a resource listing at
all. Dependencies are elicited, like everything else.

The distinction between a **runtime** and a **recovery** dependency is the part of this that
earns its place. Every toolkit asks what a system needs to run. The failure that strands a
real invocation is the runbook stored in the source control server that is inside the outage,
and only the second question finds it.

**Not yet implemented: shared-fact inheritance.** The infrastructure owner, the regions and
the provider contract are portfolio facts, and each per-system store still holds its own copy.
The register is the right home for them, but the store's validation is built around one
document per system and changing that safely is a larger change than the register itself. The
skills currently instruct the interviewer to carry the answer across with its original
provenance intact. Stated here rather than left as a surprise.

## Known limitations

| Limitation | Why it stands |
|---|---|
| Oracle EBS on OCI is the only fully-supported stack | The interview method generalises; the recovery procedures do not. Other stacks get structure without runbooks |
| Discovery is OCI-only | Other providers are a straightforward extension of the same guard pattern; not yet written |
| No import of an existing plan | An organisation with a plan in Word starts from interviews. Parsing arbitrary prose into an attributed store is a harder problem than it appears, and getting it wrong reintroduces the exact failure mode above |
| Terraform generation not attempted | Discovery emits an inventory and a resource file. Producing working infrastructure code for an arbitrary estate is where scope would explode, and it is not needed to produce a plan |
| Not yet run end to end against a real estate | The largest limitation. The first real engagement will change this design |
| Portfolio-scope facts are duplicated per system | See Decision 8. The register knows them; the stores do not read from it yet |

## Open questions

1. **Wave membership when a system spans two.** A suite whose database belongs in the core
   wave and whose reporting tier belongs in the last one is currently one row, forced into
   one wave. Splitting it into two registered systems works and may be the honest answer.
2. **Re-interviewing cadence.** The store has no notion of a fact going stale. A contact roster
   is stale in six months; an architecture decision is not.
3. **Who runs the interviews.** The skills assume an operator conducting them with an agent's
   help. Whether an interviewee could drive one directly is untested and probably unwise for
   the business interview, where the framing matters most.
