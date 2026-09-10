# Phase 6 — Writing it up, and auditing what you wrote

> **Generated file.** It is assembled from the skills, the question bank and `GETTING-STARTED.md` by `plugin/itscp_manual.py`, and an edit made here is deleted by the next regeneration. Change the source and run `python3 plugin/itscp_manual.py`.

**You, on your own,** with the worksheets from every session in front of you.

Half a day. There is no renderer here, so this is two jobs: write the documents from the worksheets, then audit what you wrote.

**The assembly is mechanical and the map is generated.** [fields.md](fields.md) lists every answer by the file it belongs in, which is the order to write in. The rules below for marking a missing answer, a low-confidence figure and the *Unverified statements* section are the part people skip, and skipping it is how a plan full of gaps comes out looking finished. **A cell your worksheet left open is a marked gap in the document, never a sentence you write to fill the space.**

Then audit, starting from the position that every requirement is unmet until a sentence in your own document proves otherwise. Fix what blocks approval and leave the rest visible.

**Run under [the method](method.md).** Nothing enters the plan unless somebody in the room said it, an inventory shows it, or it is written down as a gap with a name against it.

---

### Running this without the toolkit

The technique below is the skills' own words, and the skills assume a loaded plugin. You do not have one. These are the substitutions in effect on this page.

| Where it says | In the room you |
|---|---|
| `python3 itscp_portfolio.py` | Check the register by hand. [Five passes over the wall](00-portfolio.md#checking-the-register-by-hand), each one a question you can answer from the cards in front of you. |
| `itscp-build` | There is no generator in a tabletop. Phase 6 is you writing the documents, and [fields.md](fields.md) is the map of which answer goes into which one. |
| `portfolio.toml` | The register is the wall: one card per system, one line per dependency. The file is only how it gets stored if somebody types it up afterwards. |
| the answer store | The stack of worksheets. It holds the same things — the answer, who gave it, how sure they were — in columns rather than in keys. |
| `answers.yaml` in the tree | The worksheets. Nothing to create; the stack of paper is the store. |
| "the store" | The worksheet in front of you. |

## The technique

*From `itscp-method-repo-scaffold`: The directory tree itscp-build generates, which skill fills each file, and the rendering rules for MISSING fields, low-confidence values and the References and Unverified statements sections. Read before creating or filling a plan repository.*

The tree `itscp-build` creates, and which skill fills each file. Structure follows the
reference example so that anyone who has read one plan can navigate any other.

```
<your-org>-itscp-<suite>/
├── README.md                          scope, how to read, plan maintenance
├── .gitignore                         answer store, evidence, resource files
├── .itscm/
│   └── answers.yaml                   the answer store (gitignored)
├── docs/
│   ├── 00-plan-approval.md            governance      signature, attestation
│   ├── 00-record-of-changes.md        build           derived from git log
│   ├── 01-architecture.md             infrastructure  design, assumptions, diagrams
│   ├── 02-mtd-tiers.md                business        BIA output, tiers, MBCO
│   ├── 03-replication-matrix.md       infrastructure  mechanisms, one-way doors
│   ├── 04-monitoring.md               infrastructure  alarms, RPO attestation
│   ├── 05-cost-and-teardown.md        infrastructure  posture economics
│   ├── 06-test-environments.md        infrastructure  what each test tier proves
│   ├── 07-standards-alignment.md      governance      NIST / ITIL / ISO crosswalk
│   ├── 08-phase-activation.md         build           ITSCP phase 1 routing
│   ├── 09-phase-recovery.md           build           ITSCP phase 2 routing
│   ├── 10-phase-reconstitution.md     build           ITSCP phase 3 routing
│   ├── 11-inventory.md                discovery       Appendix H
│   ├── 12-interconnections.md         application     Appendix I (discovery does not render it)
│   ├── references.md                  build           consolidated citation index
│   └── compliance-audit.md            audit           adversarial audit output
├── runbooks/
│   ├── RB-01-switchover.md            infrastructure  planned role transition
│   ├── RB-02-failover.md              infra + continuity  unplanned, with the gate
│   ├── RB-03-failback.md              infrastructure  the return trip
│   ├── RB-04-dr-drill.md              governance      exercise procedure
│   └── RB-05-replication-lifecycle.md infrastructure  build, posture, teardown
├── checklists/
│   ├── roles-and-responsibilities.md  continuity      §2.3, teams, succession
│   ├── contact-roster.md              continuity      Appendix A + B, call tree
│   ├── outage-assessment.md           continuity      §3.3, the repair estimate
│   ├── dr-authority-matrix.md         continuity      decision rights
│   ├── tier-assignment-workshop.md    business        the BIA session
│   ├── manual-workarounds.md          business        Appendix E
│   ├── validation-pack.md             application     Appendix F
│   ├── pre-failover-precheck.md       infrastructure  Appendix D
│   ├── drill-timing-sheet.md          governance      evidence capture
│   ├── contingency-training.md        governance      Appendix J
│   └── risk-register.md               governance      owned risks
├── scripts/                           infrastructure  recovery automation
├── evidence/                          governance      drill results, attestations
└── terraform/                         infrastructure  environment as code (apply-locked)
```

### Rendering rules

Applied by `itscp-build` when it writes any of the above.

| Answer-store state | Renders as |
|---|---|
| `ANSWERED`, confidence high or medium | The value, plainly |
| `ANSWERED`, confidence low | `4 hours *(low confidence; not measured)*` |
| `MISSING` | `**[MISSING — owner: Head of Finance Systems]**` |
| `DEFERRED` | `**[DEFERRED to 2026-10-01 — owner: Treasury]**` |
| `NOT_APPLICABLE` | `Not applicable — <the recorded reason>` |
| `conflict` present | Both values, both sources, and the named decision owner |

**A missing value never renders as blank, and never as a plausible default.** The whole point
of the toolkit is that a reader can tell, at a glance, which parts of the plan are known and
which are outstanding.

### Sections every generated document carries

- `## References` — sources for any claim about product behavior or a standard.
- `### Unverified statements` — engineering judgments the toolkit or the author made,
  labeled as judgments. This is where anything not traceable to a person or an API goes.

The second section is not optional. It is what keeps a generated document honest about the
difference between what was elicited and what was reasoned.

*From `itscp-audit`: Use when an IT service continuity plan (ITSCP) needs checking against NIST SP 800-34 or the SP 800-53 contingency planning controls, when someone asks whether their plan is complete or audit-ready, or before submitting a plan for approval or external review.*

### The rule that makes this an audit rather than a review

> **A requirement PASSES only when the report quotes the sentence that satisfies it, with file
> path and section heading.**

"The runbooks cover this" is not evidence. "The plan clearly intends" is not evidence. If you
cannot paste the sentence, the verdict is not PASS.

### Verdicts

Exactly one per requirement, from this list:

| Verdict | Means | The row must carry |
|---|---|---|
| PASS | A sentence in the plan satisfies the whole requirement | Path, section, verbatim quote |
| PARTIAL | Part is satisfied, or the artefact exists but is a blank template | Path, section, quote, and the missing part named |
| REFUTED | Nothing in the plan satisfies it | Where you looked, and the closest thing found (or "nothing") |
| NOT APPLICABLE | The standard or the plan's stated scope excludes it | The sentence that excludes it — never the auditor's opinion |
| INACCESSIBLE | The requirement text could not be read | Source, wall type, date attempted, and the fallback used |

**There is no "not assessed".** A requirement you did not reach is a requirement the audit did
not cover, and the summary must say so by count so the reader can reject the audit.

### Coverage-derived findings

Because the plan was generated from an answer store, the audit has evidence a normal audit
does not. Report all four:

| Finding class | Source |
|---|---|
| Sections below 100% coverage | Answer store status counts |
| Values with `confidence: low` | These are guesses in a signed document. List every one |
| Unresolved `conflict` entries | Two sources disagreed and nobody decided |
| `DEFERRED` fields past their due date | Someone promised an answer and the date passed |

**Low-confidence values in an approved plan are the highest-value finding this audit
produces.** They are the numbers most likely to be wrong, in the document most likely to be
believed, and they are invisible to any auditor without the store.

### Portfolio findings

A plan can pass every requirement in the standard and still be impossible, because the
standard is written for one system and the failure is between systems. When a
`portfolio.toml` exists, run it and fold the result into the report:

```bash
python3 itscp_portfolio.py portfolio.toml
```

| Finding | Why it belongs in an audit |
|---|---|
| `rto-inversion` | The plan states a recovery target it cannot meet, because something it hard-depends on is signed slower. Two signed documents contradict each other |
| `recovery-cycle` | Systems that each need the other recovered first. Neither plan can execute |
| `wave-inversion` | A dependency scheduled to recover after its dependant |
| `undeclared-shared-service` | A concentration of risk the register's classing hides |
| `no-plan` | A system the organization knows it has and has not planned for |

**Report an inversion against both plans, not one.** Naming only the faster of the two reads
as a defect in that plan; it is a disagreement between two owners, and the finding is only
actionable when both are named.

If there is no `portfolio.toml`, say so as a finding in its own right: an audit of one plan
in a portfolio of many has verified that plan against the standard and nothing against its
neighbours.

### Scope

Audit the plan repository: every document, runbook and checklist. Scripts and configuration
are evidence only where a document points at them.

State which standard editions you read and which you could not. If a source is paywalled or
login-gated, say so with the date attempted and what you used instead. **Never paraphrase a
standard from memory** — an audit whose requirements are remembered rather than read is an
opinion with a table around it.

### Output

`docs/compliance-audit.md`, containing:

1. Method, and the rule above, stated explicitly.
2. Sources read, with access status per instrument.
3. Per-requirement table with verdicts and quotes.
4. Summary counts by verdict, including anything not covered.
5. The four coverage-derived finding classes.
6. Remediation list, ordered by what blocks approval.

### Red flags

| Thought | Reality |
|---|---|
| "The intent is clearly met" | Then quote the sentence. If you cannot, it is not PASS |
| "This section is thorough, PASS" | Thorough is not a verdict. Which requirement, which sentence |
| "Not applicable — it's a cloud environment" | Quote the scope statement that excludes it, or ask for one |
| "I know what SP 800-53 CP-2 says" | Read it. Remembered requirements are how audits go wrong quietly |
| "I ran out of time, I'll report what I checked" | Report the uncovered count too, so the reader can judge the audit |
| "Coverage is high so the plan is good" | Print the confidence split. Comprehensive guessing is still guessing |
