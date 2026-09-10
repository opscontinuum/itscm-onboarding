# Design

Why the toolkit is shaped the way it is, including what was rejected. Written before
implementation and kept as the record of the decisions.

---

## Problem

An organization needs a continuity plan for each application suite it runs. The people who
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

Direct analog of the reference example's citation discipline. Every `ANSWERED` field records
`interview:<role>:<date>`, `oci-discovery:<operation>`, `document:<path>` or `operator`.

**There is deliberately no provenance value meaning "the assistant worked it out."** Removing
the representation removes the option. Reasoned conclusions go into a document's *Unverified
statements* section, labeled as judgments — never into the store as facts.

## Decision 4 — Every field starts MISSING

Borrowed from the reference example's compliance-audit skill, where every requirement starts
REFUTED until a quoted sentence moves it. Applied to elicitation: a field is `MISSING` with a
named owner until somebody answers it.

This makes the honest outcome — "we don't know, and here is who would" — a first-class result
rather than a hole to be filled. An interview producing forty named unknowns has done more for
the organization than one producing forty confident inventions.

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
environment is a different risk posture from touching a real one. This toolkit touches real ones.

An allowlist (`^(list|get)`) rather than a denylist, so a service shipped tomorrow with a novel
destructive verb is refused by default rather than discovered in production. Enforced by a
wrapper that fails closed, plus a static tripwire that fails the test suite if any script ever
calls the CLI outside the wrapper.

`--dry-run` exists for a social reason as much as a technical one: it converts "an AI is going
to look at our production tenancy" into a reviewable list of commands.

## Decision 7 — Coverage is always reported with confidence

Coverage alone is a misleading metric. A plan at 90% coverage where two thirds of values are
low confidence describes an organization that has guessed comprehensively.

`itscp-build` prints the confidence distribution beside every coverage figure, and `itscp-audit`
treats low-confidence values in an approved plan as a first-class finding — they are the
numbers most likely to be wrong, in the document most likely to be believed.

---

## Decision 8 — The portfolio is a register, not an answer store

Added after the single-system assumption was challenged. Organizations have environments: a core
suite, its dependants, the tooling underneath, public ingest interfaces, public sites.

**A register of systems is a different shape from a set of facts about one system.** The
answer store holds facts with provenance, confidence and a status per field. The register
holds rows with edges between them, and the interesting questions about it are graph
questions — is anything scheduled before its dependency, does anything need itself to be
recovered. So it is a separate file (`portfolio.toml`) with a separate module, rather than a
namespace inside a store whose validation rules are about attribution.

**Rejected — one plan per organization with system annexes.** Simplest for a small environment,
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

## Decision 9 — The manual is generated from the skills, never written beside them

Added when the engagement had to be runnable by somebody with no plugin loaded. The obvious
answer is to write a manual, and the obvious answer is wrong: a written manual is a second
copy of the method, and a second copy is right on the day it is written and wrong from the
first improvement to a skill that nobody remembers to mirror. What a reader would then hold is
a document that is stale in exactly the places the toolkit recently got better.

So `docs/manual/` is assembled by `plugin/itscp_manual.py` from the files that are already
authoritative: named sections of the skills for the technique, `itscp_questions` for the
questions and the worksheets, `itscp_portfolio` for the register's shape, and
`GETTING-STARTED.md` for the orientation. **Only the phase sequence, the room each phase
needs, and the by-hand procedures that replace a script are written in the generator**,
because nothing else states those in one place.

Freshness is enforced rather than remembered. `test_manual` rebuilds every page and fails on
the first differing line, so changing a skill without regenerating is a failing test — the
same guard `examples/` is held to, for the same reason.

**A manual run is a room, not a person reading a file.** The application and infrastructure
teams sit down together with a facilitator and paper, so the manual is a tabletop. Three
things follow from that, and each is enforced by a test rather than left as an intention.

It produces no TOML. The plugin's answer store is a file; the tabletop's is the stack of
worksheets, holding the same things in columns: the answer, who gave it, how sure they were,
what breaks at that number. Typing those up into the store is an appendix, for an organization
that later adopts the toolkit.

It names no tool at all. The skills are written for an agent with the plugin loaded, so they
name scripts, modules and files a room does not have. An earlier version answered each of
those with a translation table on the page, which was honest and still wrong: a facilitator
does not want to be told what the sentence would have meant to somebody else. So sections that
only drive the toolkit are excluded by name, the handful of sentences elsewhere that name
something runnable are replaced one at a time with a recorded reason, and cross-references
between skills become the phase that carries them, derived from the phase list so a phase that
moves takes its references with it. A test scans every page for command-shaped text using a
pattern written independently of those replacements, so anything runnable that reappears fails
the build. Where a script did real work, as the validator does for the register's five
cross-system checks, the manual carries the procedure by hand; a further test asserts each
check still names a finding the validator actually raises.

It assumes no particular cloud. Phase 1 is whatever the teams already use to see their
environment. The read-only walk is one provider's shortcut, and what generalizes out of it is
the rule that discovery never changes anything.

**Rejected — a manual that links to the skills instead of embedding them.** It is trivially
drift-free and it is an index, not a manual. Somebody facilitating from a printed page needs
the technique on that page.

**Rejected — embedding the skills whole.** The first version did, and it shipped a document
that told a room to run a discovery script and hand-write `answers.toml`. Verbatim is the right
instinct for drift and the wrong unit: the unit is the section, and which sections belong is a
decision that has to be recorded and tested, not assumed.

**Rejected — extracting the questions from the skill prose.** The bank already is the schema,
and the skills carry the conversational probes around it. The manual takes each from where it
lives rather than parsing one out of the other.

The extractors refuse rather than guess: a missing heading, frontmatter field or `**Label:**`
line raises. A skill that grows a section fails the build too, until somebody says whether the
manual carries it.

## Decision 10 — Discovery is one directory per environment

Discovery is the only part of the toolkit that has to know what it is looking at. Everything
else is a conversation, and a conversation about an outage runs the same whether the workload
is on OCI, on VMware or in somebody's colo. So the environment-specific part is isolated
rather than spread: `plugin/scripts/discover/<environment>/`, with the contract in a README
beside it and `oci/` the only implementation today.

**Named, not implied.** AWS, Azure, VMware and Kubernetes have directories in nobody's future
until somebody writes them, and the README says so. A toolkit that implies broader coverage
than it has costs an engagement more than one that states its limit: the first is discovered
at the customer site.

The proof of read-only-ness is what makes this a contract rather than a convention. Each
environment carries its own `test-readonly.sh`, and the runner one level up finds them by
looking rather than by list, so a new environment is covered by the suite the moment its
directory exists and an environment whose proof is missing fails loudly instead of being
skipped.

**Rejected — one script with a `--provider` flag.** The guard is the load-bearing part, and a
guard that has to know every provider's read verbs is one edit from allowing a write on the
provider whose verbs somebody got wrong. One guard per environment keeps the blast radius
readable: a reviewer opens one file.

**Rejected — dropping the scripts and making discovery manual everywhere.** Tempting after the
manual was rewritten around what teams already have, and wrong. A read-only walk of a tenancy
takes ten minutes and produces a gap list nobody assembles by hand. The manual treats it as an
accelerator where it exists, which is exactly what it is.

## Known limitations

| Limitation | Why it stands |
|---|---|
| Oracle EBS on OCI is the only fully-supported stack | The interview method generalises; the recovery procedures do not. Other stacks get structure without runbooks |
| Discovery is OCI-only | Other providers are a straightforward extension of the same guard pattern; not yet written |
| No import of an existing plan | An organization with a plan in Word starts from interviews. Parsing arbitrary prose into an attributed store is a harder problem than it appears, and getting it wrong reintroduces the exact failure mode above |
| Terraform generation not attempted | Discovery emits an inventory and a resource file. Producing working infrastructure code for an arbitrary environment is where scope would explode, and it is not needed to produce a plan |
| Not yet run end to end against a real environment | The largest limitation. The first real engagement will change this design |
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
