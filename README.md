# itscm-onboarding

**Interview skills that build an IT service continuity plan for an application suite you have
never documented.**

You have applications to protect and no plan for them. You have a vague idea of what is in
your cloud tenancy. You know roughly who to ask about the business side, but not what to ask.
Somewhere there is a standard that says what a continuity plan should contain, and reading it
is a day you do not have.

This repository is the toolkit that gets you from there to a plan an auditor can read — one
application suite at a time, for as many as you serve.

---

## An estate, not a system

An organisation does not have *a* system. It has a core product suite, the applications that
read from it, the tooling those are built and deployed with, the interfaces clients push data
into, and the public sites fronting all of it.

Planning them one at a time produces **N individually-plausible, collectively-impossible
plans.** The order management application is signed at four hours. The identity database it
cannot authenticate without is signed at eight. Both documents are internally coherent, both
were written by different people in different weeks, and nothing inside either can see it.

So the toolkit starts above the plans. `itscp-portfolio` registers every system, ranks the
tiers against each other and fixes the recovery order; `itscp-dependencies` maps what each
system needs — including what it needs in order to be **recovered**, as distinct from what it
needs to run. Then a plan is built per system, in wave order, against those constraints.

```bash
python3 plugin/itscp_portfolio.py portfolio.toml   # 0 clean, 1 warnings, 2 errors
```

Four failures exist only at this level and are all checked mechanically:

| Finding | What it catches |
|---|---|
| `rto-inversion` | A system claiming to be back before something it cannot run without |
| `recovery-cycle` | The runbooks are in the source control server that is inside the outage |
| `wave-inversion` | A dependency scheduled to recover after its dependant |
| `undeclared-shared-service` | Four systems hard-depend on it and it is classed as an ordinary app |

`plugin/portfolio.example.toml` is a fourteen-system estate in that shape — identity and
network, secrets and recovery tooling, a core HR suite, dependent applications, a client
ingest API, a public site — with the recovery order that follows from it.

## What it is

A picoagent plugin: twelve skills, a read-only discovery walk, and a sequenced guide.

Eight of the skills you invoke by name. The other four carry the method they share — the
elicitation discipline, the answer store, the coverage map and the repository scaffold — and
the eight refer to them by name rather than by file, so they keep working wherever the plugin
is installed.

The skills **interview people**. They do not generate a plan from assumptions; they ask the
business owner what actually breaks, ask the infrastructure owner what the replication really
does after a failback, and record the answers with attribution. Where nobody answers, the
output says so, by name.

| Skill | Interviews | Produces |
|---|---|---|
| [`itscp-portfolio`](plugin/skills/itscp-portfolio/SKILL.md) | enterprise architect / CIO | The system register, comparative tiering, recovery waves |
| [`itscp-dependencies`](plugin/skills/itscp-dependencies/SKILL.md) | application + infrastructure owners | Runtime, recovery and data dependencies; the coherence checks |
| [`itscp-build`](plugin/skills/itscp-build/SKILL.md) | nobody — it sequences | Phase order, coverage reporting, repository generation |
| [`itscp-discover`](plugin/skills/itscp-discover/SKILL.md) | a tenancy, read-only | Appendix H inventory, resource file, gap list |
| [`itscp-interview-business`](plugin/skills/itscp-interview-business/SKILL.md) | business / process owner | Appendix K BIA, MTD tiers, MBCO, Appendix E workarounds |
| [`itscp-interview-application`](plugin/skills/itscp-interview-application/SKILL.md) | application owner + lead engineer | §2.1 system description, interconnections, Appendix F validation, WRT |
| [`itscp-interview-infrastructure`](plugin/skills/itscp-interview-infrastructure/SKILL.md) | infrastructure owner + lead engineer | Recovery strategy, replication matrix, Appendix C, cost model |
| [`itscp-interview-continuity`](plugin/skills/itscp-interview-continuity/SKILL.md) | DR process owner | §2.3 roles and succession, §3.1 activation, §3.2 notification, §3.3 outage assessment |
| [`itscp-interview-governance`](plugin/skills/itscp-interview-governance/SKILL.md) | governance / risk / audit | Approval, review cadence, Appendix J training and exercises, risk register |
| [`itscp-audit`](plugin/skills/itscp-audit/SKILL.md) | nobody | Adversarial audit of the generated plan |

**Start here:** [`GETTING-STARTED.md`](GETTING-STARTED.md).

---

## Installing

The `plugin/` directory is the whole toolkit. Everything below assumes
`/path/to/itscm-onboarding` is where you cloned this repository.

**While you are editing it**, load it for a single run:

```bash
picoagent -e /path/to/itscm-onboarding/plugin
```

A `-e` path is trusted for that run only. No prompt, nothing recorded, and no fingerprint to
keep in step. This is the right mode for anyone changing a skill.

**To keep it**, add it to `~/.picoagent/config.toml`:

```toml
[plugins]
enabled = ["/path/to/itscm-onboarding/plugin"]
```

and approve it once:

```bash
picoagent plugin trust /path/to/itscm-onboarding/plugin
```

### The fingerprint will catch you out

Approval is recorded as a sha256 over **every file in the plugin directory**, not just the
Python. Fix a typo in a SKILL.md and the fingerprint stops matching, so the next start skips
the plugin. Nothing crashes and no error is raised: the skills are simply not there, and the
only sign is a warning line you were probably not watching.

```bash
picoagent plugin list      # shows CHANGED against a plugin that needs re-approval
```

Re-approve with the same `plugin trust` command after any edit. Better, use `-e` while you are
iterating, which is exactly what it is for. A stray `__pycache__` counts as a change too,
which is why it is gitignored.

---

## The idea it is built on

The failure mode of an AI-assisted continuity plan is not a wrong answer. It is a **plausible
answer nobody gave.**

A generated plan that says "RTO: 4 hours" when no human ever said four hours is worse than one
that says "RTO: MISSING — owner: Head of Finance Systems". The first cannot be audited, reads
as finished, and will be believed. The second is honest and tells the organisation exactly
what it does not know.

So the toolkit enforces one rule everywhere:

> **A fact enters the plan only when a human said it, a read-only API returned it, or it is
> marked MISSING with a named owner. There is no fourth source.**

Every fact carries provenance — who said it, when, or which API call returned it — and a
confidence. Coverage is reported alongside the confidence distribution, because a plan at 90%
coverage where most values are low confidence is an organisation that has guessed
comprehensively, and it deserves to be told so.

This is the same discipline as the reference plan's citation audit, pointed at elicitation
rather than at documentation.

---

## Discovery never mutates

`itscp-discover` walks a live OCI tenancy through the `itscp_discover_oci` tool. Every call is
a `list` or a `get`, and that is enforced structurally: a read-only guard rejects any operation
that is not a read, before it reaches the CLI, failing closed.

Verify it yourself:

```bash
plugin/scripts/discover/test-readonly.sh
```

Three independent checks: the guard's unit tests, a static tripwire that fails if any script
ever calls the CLI outside the guard, and an end-to-end check that every command a full walk
would issue is a read.

`dry_run=true` prints every command without executing any, and needs no credentials. **Show
that to a customer before the real run** — it turns "an AI is going to look at our production tenancy" into a reviewable list.

---

## Relationship to `oci-itscp`

[`opscontinuum/oci-itscp`](https://github.com/opscontinuum/oci-itscp) is the **reference
example**: a complete, citation-audited continuity plan for a hypothetical corporation running
Oracle E-Business Suite on Exadata across two OCI regions. It is what a finished plan looks
like.

This repository is the **generator**. It produces plans shaped like that one, populated with
your organisation's answers instead of a fictional company's.

They are separate because the relationship is one-to-many. One toolkit, many plan
repositories — one per application suite you serve. A generator cannot live inside one of its
own outputs, and improvements to the interview logic have to be able to reach plans that were
generated last quarter.

**Do not copy the reference plan's numbers.** Its MTDs, lag figures and cost percentages
describe a company that does not exist. Its *structure* is the thing to reuse.

---

## What this does not do

Stated plainly, because a toolkit that implies completeness it lacks is the same failure it
was built to prevent.

| Not covered | Consequence |
|---|---|
| Platforms other than Oracle EBS on OCI | You get the ITSCP structure and the interview method; the recovery procedures are yours to write |
| Discovery outside OCI | AWS, Azure, GCP and on-premises inventories are manual |
| Importing an existing plan | An organisation with a plan in Word starts from interviews, not from its own document |
| Terraform config generation | Discovery emits an inventory and a resource file. Turning that into working infrastructure code is not attempted |
| Making the plan true | Every duration it produces is a design target. Only a drill makes it a commitment |

---

## Status

Early. The skills are written, the plugin loads and the discovery tooling is tested; the
toolkit has not yet been run end to end against a real estate. Findings from the first real engagement will change
it.

## Licence

MIT. See [`LICENSE`](LICENSE).
