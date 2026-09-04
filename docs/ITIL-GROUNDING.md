# ITIL grounding

What instrument this toolkit produces, where it sits against ITIL 4 service continuity
management, what evidentiary standard it has to meet, and the one guarantee it cannot make.

This document is a grounding document, not a conformance claim. It does three things:

1. **§1** names the instrument the toolkit produces and adopts the naming rule that keeps it
   distinct from the two neighbouring instruments it is routinely confused with.
2. **§2** maps ITIL 4 practices to the skills that elicit them and the coverage-map rows that
   carry them, and reports what the ITIL citation the mapping rests on actually is.
3. **§3** to **§5** state the evidentiary bar the picoagent continuity tooling meets, state
   plainly why one part of that bar is unavailable here, recommend the substitute, and list
   what has to change.

> **Source honesty.** Nothing in this document was fetched over the network. Every external
> claim is second hand: it rests either on the citation record in `oci-itscp/docs/citation-audit.md`
> [2], which recorded an adversarial fetch of each source on 2026-09-01, or on the fetch record
> transcribed into `picoagent/examples/plugins/iscp-author/iscp_template.py` [7] and its README
> [6], dated 2026-09-02. Where a claim rests only on one of those records and not on the primary
> text, this document says so. The ITIL 4 *Service Continuity Management* practice guide and the
> text of ISO 22301:2019 are paywalled and were not read by anyone at any point in this chain.

---

## 1. Which instrument this toolkit produces

**The toolkit produces an ITSCP: an IT Service Continuity Plan, a service-level artefact under
ITIL.** It does not produce an ISCP, and it must never say that it does.

`picoagent/docs/engineering/continuity-tooling.md` §3 [5] separates three families and states
why the separation is load bearing: getting it wrong "inherits the wrong requirement set in
both directions", so that a plan modelled as another family's plan "plus extras" acquires
requirements it does not have and misses the ones it does.

| Family | Term | Level | Governing instrument |
|---|---|---|---|
| ISCP | Information System Contingency Plan | system | NIST SP 800-34 Rev. 1; FedRAMP SSP Appendix G |
| ITSCP | IT Service Continuity Plan | service | ITIL 4 / ITSCM |
| COOP | Continuity of Operations Plan | organisation | HSPD-20/NSPD-51, FCD 1 |

Reproduced from [5] §3.

### The naming rule, adopted

[5] §3 states it directly, and this repository adopts it without modification:

> ... call its plan "the ITSCP" or "the plan", never "the ISCP". An ITSCP may *align to* NIST's
> ISCP structure - that repo does, through its `docs/07-itil4-alignment.md` §1a crosswalk -
> without being one. Keep NIST's own "ISCP" inside quotations and when naming NIST artefacts
> ("NIST's ISCP template", "Table 3-5: ISCP TT&E Activities").

Quoted verbatim, including its hyphen dashes.

`oci-itscp/skills/itscp-compliance-audit/SKILL.md` §1 [10] already operates this rule and
states the consequence for an auditor: every row assesses an ISCP requirement against the
ITSCP by way of the crosswalk, and "an auditor who conflates the two will cite the wrong
instrument for the finding."

The toolkit currently does not operate the rule. `ISCP` appears 26 times across eleven files in
this repository, and the occurrences fall into three classes. §5.1 lists them by file.

| Class | Example | Correct? |
|---|---|---|
| Naming NIST's own artefact | `coverage-map.md` line 7, "NIST SP 800-34 Rev. 1 Appendix A (Sample ISCP Templates)" | Yes, keep |
| Naming a NIST section number in a crosswalk sense | `answer-store.md` line 85, "ISCP §1 Introduction" | Yes if marked as a crosswalk, no if read as our own numbering |
| Naming our own output | `coverage-map.md` line 1, "every ISCP section"; `interview-method.md` line 8, "A generated ISCP that says"; `itscp-build` description, "an ISCP for an application suite" | No, must become ITSCP |

The word `ITIL` appears nowhere in any skill, in `README.md`, in `GETTING-STARTED.md` or in
`docs/DESIGN.md`. `ISO 22301` appears twice: `itscp-interview-business/SKILL.md` line 90 and
`skills/_method/coverage-map.md` line 87, both as a reason to ask for the minimum business
continuity objective. So the toolkit sits on both sides of the line that [5] §3 draws, and
says nothing about it in either direction.

### What that means for the coverage map

`skills/_method/coverage-map.md` line 7 states its own structure: "Structure follows NIST SP
800-34 Rev. 1 Appendix A (Sample ISCP Templates) and §4.1 to §4.5." That is the ISCP skeleton,
used to organise an ITSCP.

**This is not wrong. It is undeclared.** `oci-itscp` does the same thing and it is defensible
there because `docs/07-itil4-alignment.md` §1a [1] carries the crosswalk that makes the
borrowing visible, and because the compliance-audit skill [10] states in its scope paragraph
that the plan "aligns *to* the ISCP structure; it is not one." Neither statement exists in
this repository. A reader of `coverage-map.md` today has no way to tell whether the NIST
structure is a deliberate borrowing or a category error.

Three consequences follow, and they are the substance of §5:

- The map's title and framing sentence describe the artefact as an ISCP and must not.
- The map has no column recording where each element's structure comes from, so its 36
  NIST-derived rows and its 5 "Beyond NIST" rows are typographically identical to a reader.
- The map has no row for anything an ITSCP needs that an ISCP does not, which is why §2.2
  finds ITIL practices with no elicitation behind them at all.

---

## 2. Mapping to ITIL practice

### 2.1 What reference [1] in `oci-itscp/docs/07` actually is

The instruction was to verify this before relying on it. The finding matters, so it is stated
before the mapping rather than after.

Reference [1] in `oci-itscp/docs/07-itil4-alignment.md` is:

> *Glossary, ITIL 4 Foundation Official Training Materials.* PeopleCert (copy hosted by a
> training provider), undated, accessed 2026-09-01.
> `https://igen.nl/wp-content/uploads/2024/10/ITIL-4-Foundation_Glossary_Digital.pdf`

Six findings about it.

| # | Finding | Evidence |
|---|---|---|
| F1 | It is the **ITIL 4 Foundation glossary**, not the ITSCM practice guide. | The entry says so, and doc/07's own source-honesty note says the practice guide "could not be read for this revision" [1] |
| F2 | It is a **third-party-hosted copy** of copyrighted PeopleCert training material, on a Dutch training provider's WordPress uploads directory. It is not a PeopleCert or AXELOS canonical URL. | The URL itself; the entry's own parenthetical "copy hosted by a training provider" |
| F3 | It is **undated**, so the edition of the glossary cannot be pinned. | The entry says "undated" |
| F4 | Its **content was independently verified**. The citation audit [2] fetched it, got HTTP 200, extracted the page text, and found the definition sentences present. Verdict VERIFIED, 14 markers checked in the body, body verdict "Supported", remediation "none". | [2] `docs/07-itil4-alignment.md` table, row 1 |
| F5 | The audit reproduced only the **RTO and RPO** definition sentences in its quote column. The other definitions doc/07 attributes to [1], service continuity management practice, business impact analysis, disaster, disaster recovery plans, rest on the audit's body check of all 14 markers rather than on a quote reproduced in the audit table. | [2] row 1 quote column, compared with the marker positions in [1] §1, §3 and §4 |
| F6 | The **practice names in doc/07 §4 are not individually cited to it.** §4 carries `[1]` on the service continuity management row only, and its own preamble says "Purposes are paraphrased where the glossary does not define the practice; only the service continuity management practice definition is quoted [1]." | [1] §4 preamble and table |

**What this means for reliance.** [1] is good enough to quote for exactly six terms, and it is
not good enough for anything else.

| Quotable from [1], verified | Not verifiable, practice guide only |
|---|---|
| service continuity management practice | vital business function |
| business impact analysis | maximum tolerable period of disruption (MTPD) |
| recovery time objective | minimum business continuity objective (MBCO) |
| recovery point objective | invocation |
| disaster | recovery options |
| disaster recovery plans | the ITSCM practice's own activity list |

The last row of the right-hand column is the one that constrains §2.3 below. **There is no
verified source anywhere in this chain for the ITSCM practice's activity set.** The single
verified anchor connecting an activity to the practice is the glossary's BIA definition, which
calls the BIA "a key activity in the practice of service continuity management" [1]. Everything
else in the activity list is either paraphrase from general usage, which is what doc/07 says it
is doing, or unverified.

Two further consequences that only appear once F2 is taken seriously:

- **Persistence.** A PDF on a training provider's uploads directory is not a stable citation
  target. A generated plan that cites it will, eventually, cite a 404.
- **Copyability.** F2 puts the glossary text outside the class of material this toolkit can bake
  into a template corpus. §4 turns on this.

### 2.2 The practice map

Practice list taken from `oci-itscp/docs/07-itil4-alignment.md` §4 [1], unchanged. No practice
has been added, renamed or given a definition it does not carry there. Coverage-map row
references are to `skills/_method/coverage-map.md` in this repository.

| ITIL 4 practice | Toolkit skill that elicits it | Coverage-map rows that carry it | Verdict |
|---|---|---|---|
| **Service continuity management** (definition quoted [1]) | `itscp-interview-business` (BIA, tiers, MBCO), `itscp-interview-infrastructure` (recovery options), `itscp-interview-continuity` (activation, roles), `itscp-interview-governance` (exercising, review) | App. K; §4.1, §4.2, App. C, App. D; §3.1, §3.2, §3.3; App. J; Beyond-NIST MBCO and review-cadence rows | **Covered** |
| **Availability management** (purpose paraphrased in [1]) | none | none | **Absent** |
| **Change enablement** (paraphrased) | `itscp-interview-continuity` (declaration authority), `itscp-interview-governance` (approval) | §3.1, front-matter Plan Approval | **Partial** |
| **Incident management** (paraphrased) | `itscp-interview-continuity` (activation criteria, outage assessment, escalation) | §3.1, §3.3, §4.3, §5.9 | **Partial** |
| **Monitoring and event management** (paraphrased) | `itscp-discover` only, as an inventory of alarms that already exist | none | **Absent** |
| **Risk management** (paraphrased) | `itscp-interview-governance` §6 | Beyond-NIST risk-register row | **Covered** |
| **Service level management** (paraphrased) | `itscp-interview-business` (tiers as the target set) | App. K, §1.2 | **Partial** |
| **Information security management** (paraphrased) | `itscp-interview-governance` §2 (categorisation, regulatory regime) | §1.2 | **Partial** |

The four verdicts that are not "Covered" are the substance of this section.

**Availability management, absent.** The string `availabilit` appears once in the entire skills
directory, in `itscp-discover/SKILL.md` line 70, where it means "availability domains". No
skill asks for an availability target, and no skill asks the question doc/07 T8 and T13 exist
to force: which parts of this design are availability controls and which are continuity
controls. This is gap G4 reproduced, and §2.4 treats it as such.

**Monitoring and event management, absent.** `itscp-discover/SKILL.md` line 82 inventories
"Monitoring alarms: what currently pages, versus what the plan will need", so the toolkit knows
the gap exists. Nothing closes it. `itscp-interview-infrastructure` has seven elicitation
sections and none of them is monitoring, its output list does not include `docs/04-monitoring.md`,
and no coverage-map row mentions alarms, signals or an alert catalogue. `templates/repo-scaffold.md`
line 18 nevertheless lists `docs/04-monitoring.md` as an infrastructure-owned file. **A scaffold
file with no eliciting question renders empty or renders invented.** This is also the artefact
that [5] §2 calls the sharpest constraint on the design: "If you dont define what alerts the app
team needs the SRE to see you have no way to be successful in 3 9's or 4 9's."

**Change enablement, partial.** The toolkit elicits who may declare a disaster and who signs the
plan. It does not elicit who the change authority is for a planned switchover, and it does not
elicit whether invocation is a pre-authorised emergency change recorded after the fact, which is
the specific point doc/07 §4 raises against the reference plan. `runbooks/RB-01-switchover.md`
and `RB-03-failback.md` are in the scaffold with `itscp-interview-infrastructure` as their owner,
and that interview asks nothing about approval.

**Incident management, partial.** The continuity interview is strong on activation criteria,
outage assessment and escalation thresholds, and `docs/DESIGN.md` is right that §3.3 is the
section most real plans lack. What is missing is the interface: doc/07 T10 recommends "major
incident declared" as the entry condition to the decision gate, on the ground that invocation is
a decision taken *within* a major incident. The toolkit never asks what the organisation's
existing major-incident process is, so the generated gate hangs off nothing.

**Service level management, partial.** The tier table is the business-facing target set and the
business interview elicits it well. Neither an availability target nor a link to an existing SLA
document is asked for anywhere, which is the same hole doc/07 §4 records against the reference
plan ("Targets are not yet in an SLA document").

**Information security management, partial.** `itscp-interview-governance` §2 elicits
categorisation and regulatory regime, which is the part that gates other requirements. Backup
immutability and retention lock, and the sensitivity of the `evidence/` directory, both of which
doc/07 §4 names as this practice's contribution to the reference plan, are elicited nowhere.

### 2.3 The ITSCM practice activities against the seven phases

**Caveat, and it is the important part of this subsection.** The six activities below, business
impact analysis, risk assessment, continuity strategy and recovery options, plan development,
exercising and testing, review and improvement, are the activity set commonly attributed to
service continuity management. Per finding F6 in §2.1, **only the first is verifiable against a
source this chain has read.** The other five are not quoted from ITIL 4 and must not be
presented as ITIL 4's own wording.

They are nevertheless assessable, because each has a NIST SP 800-34 Rev. 1 process step that
`oci-itscp/docs/07` §1a already cites and that the citation audit verified [2]. The table below
therefore assesses against the NIST step, which is citable, and names the ITIL activity as the
unverified label it is.

| Activity (unverified label) | Citable anchor | Toolkit phase | Elicited by | Verdict |
|---|---|---|---|---|
| Business impact analysis | Glossary BIA definition [1]; NIST Step 2 [4] | Phase 2, the gate | `itscp-interview-business` §§1 to 6 | **Covered.** Strongest part of the toolkit. Impact curves, step-change mechanism required, MBCO, workarounds, sign-off |
| Risk assessment | NIST Step 3, "identify preventive controls" [4] | none | none | **Largely absent.** See below |
| Continuity strategy and recovery options | NIST Step 4, "create contingency strategies" [4] | Phase 4 | `itscp-interview-infrastructure` §§2 to 5, plus the three costed options | **Covered** |
| Plan development | NIST Step 5, "develop an information system contingency plan" [4] | Phase 7 | `itscp-build` | **Covered as sequencing.** No renderer exists yet; see §5.3 |
| Exercising and testing | NIST Step 6 [4] | Phase 5, plus Phase 7 | `itscp-interview-governance` §5; drill history in `itscp-interview-infrastructure` §6 | **Covered as elicitation.** The toolkit elicits the exercise programme and the finding-to-change route |
| Review and improvement | NIST Step 7, "ensure plan maintenance" [4] | Phase 5 | `itscp-interview-governance` §3 | **Covered** |

**Risk assessment is the hole.** The strings `threat` and `preventive` appear nowhere in the
skills directory. The governance interview §6 builds a risk register by consolidating material
assumptions and design risks that surfaced in the other interviews, which closes doc/07 gap G2,
but a register of assumptions is not a risk assessment: nothing in the toolkit asks what this
plan is protecting the service *against*. There is no scenario set, no threat elicitation, and
no preventive-control question. The nearest fragments are two questions in
`itscp-interview-continuity`: "What if the cause looks deliberate?" and "If the event that takes
the estate also takes your main office, does the recovery still have the people it needs?" Both
are branch conditions inside an assessment procedure, not a threat basis for the plan.

The consequence is concrete. A plan with tiers, replication and runbooks but no stated threat
basis cannot answer the first question a risk reviewer asks, which is why the standby is in
that region and not another one, and it cannot tell an auditor which of NIST Step 3's preventive
controls were considered and rejected.

### 2.4 Gaps G1 to G4, carried across

| Gap in `oci-itscp/docs/07` §3 | Status in this toolkit | Evidence |
|---|---|---|
| **G1** No minimum business continuity objective per tier | **Closed by construction** | `itscp-interview-business` §4 elicits it with a scripted question; coverage-map "Beyond NIST" row 1; `answer-store.md` line 40 uses `business.mbco.tier0` as its worked example of a MISSING field; scaffold routes it to `docs/02-mtd-tiers.md` |
| **G2** No risk register | **Closed by construction** | `itscp-interview-governance` §6 with owner, likelihood, impact, treatment; coverage-map "Beyond NIST" row 2; `checklists/risk-register.md` in the scaffold. Note the §2.3 caveat: this closes the register gap, not the risk-assessment gap |
| **G3** No review and maintenance cadence | **Closed by construction** | `itscp-interview-governance` §3 elicits frequency, triggers and owner, and asks "what happens if it doesn't happen"; coverage-map "Beyond NIST" row 3; renders the maintenance section of the generated `README.md` |
| **G4** No explicit availability-versus-continuity boundary | **Reproduced** | No question, no coverage-map row, no scaffold section. See §2.2 |

Three of four closed by construction is the toolkit's strongest claim against the reference
plan, and it is worth stating precisely why: G1, G2 and G3 were closed by *adding a question to
an interview*, which is the cheapest possible fix and the one a generator is uniquely good at.
G4 was not, because G4 is not a missing answer. It is a missing distinction, and the toolkit
has no place to put a distinction that is not also a field.

---

## 3. The rigour bar, stated concretely

`iscp-author` makes one guarantee and enforces it mechanically. This section describes how,
with file and line citations, so that §3.4 can state the equivalent bar without hand-waving.

### 3.1 Verbatim template sourcing

`iscp_template.py` [7] opens with the words `DATA ONLY: the verbatim text of the two source
templates this plugin renders` (line 1) and states the reason at lines 3 to 6: "a generated
document that *looks* like a FedRAMP ISCP but carries a structure of our own making fails
assessor review and costs the reader more time than shipping nothing would."

| What | Which source | Recorded where |
|---|---|---|
| `ISCP_BLOCKS` (line 912) | FedRAMP SSP Appendix G ISCP Template, **version 5.0, dated 12/06/2024**, downloaded 2026-09-02, HTTP 200, **153865 bytes, md5 `298f6b1392ee21b1cded5164c2523b86`**, read out of `word/document.xml` with `zipfile` and `xml.etree`, keeping paragraph styles so instructional text stayed distinguishable | [7] lines 9 to 17; [6] lines 132 to 138 |
| `BIA_BLOCKS` (line 813) | NIST SP 800-34 Rev. 1 Appendix B, "Sample Business Impact Analysis (BIA) and BIA Template", pages B-1 to B-4, May 2010 with errata 2010-11-11 | [7] lines 18 to 24 |

What is copied: headings, table titles, column headers, and boilerplate the template supplies
as *final* text, named explicitly at [7] lines 30 to 33 (the Three Phases description, the role
duty lists, Table 2.1 Backup Types, Table 2.4 Alternative Site Types, the eight role headings).

What is not copied, and the rule that decides: two editorial rules at [7] lines 26 to 38.
Instructional text is dropped, because every FedRAMP "Instructions:" box ends with "Delete this
and all other instructional text from your final version of this document". NIST's worked
examples are dropped, because "emitting them into a real plan would put a fictional business
process in front of an assessor".

Version currency is itself evidenced: [6] line 137 records that v5.0 "is confirmed current: it
is the newest row of the template's own revision history", and [6] lines 160 to 166 record that
FedRAMP now files the Rev 5 templates under a `LEGACY` prefix and that the plugin "does not
produce 20x output and does not claim 20x coverage."

### 3.2 The byte-level provenance invariant

`iscp_render.py` [8] lines 3 to 21 state the invariant. Every byte of `ISCP.md` is one of
exactly three things and "the renderer is built so that it *cannot* produce a fourth":

| Kind | Meaning | Mechanism |
|---|---|---|
| `template` | Text from `iscp_template` or a `Question.placeholder`, which is to say from FedRAMP or NIST | `_Writer.template`, [8] line 83 |
| `answer` | A value recorded through `iscp_answer`, stringified and nothing more | `_Writer.answer`, [8] line 87 |
| `markup` | Markdown structure containing no letters or digits at all | `_Writer.markup`, [8] line 79, constrained by the `MARKUP_ONLY` regex at [8] line 50, which admits only whitespace and the structural characters |

Every append goes through one of those three methods; the class docstring at [8] line 74 says
so. `Segment` is a frozen dataclass carrying `kind` and `text` ([8] lines 53 to 57).
`render_iscp` ([8] line 141) returns the document, the segment list and the unfilled question
ids together, so provenance cannot be dropped by a caller that only wants the text.

Two details worth naming because they are where a weaker implementation would leak:

- `_Writer.answer_value` ([8] lines 91 to 100) emits a list as **one segment per item** with a
  markup separator, and its docstring gives the reason: joining them "would produce a sentence
  that is in neither the template nor the answers, which is exactly what must not happen."
- `_Writer._slot` ([8] lines 111 to 120) renders the *source's own placeholder* when a question
  is unanswered, never a plausible default, and leaves braces that name no known question id
  literal, which is what keeps NIST's own `{insert}` and `{system name}` intact ([8] line 44).

`ProvenanceTests` ([9] line 408, "The load-bearing test: every byte of ISCP.md is template
text, an answer, or markup") asserts four properties in `assert_provenance` ([9] lines 411 to
422):

1. `"".join(segment.text for segment in segments) == document`. The segments reassemble into
   exactly the document, so nothing is unattributed by omission.
2. Every `template` segment is `assertIn`-checked against `source_corpus()` ([9] lines 51 to
   54), which is `iscp_template.template_corpus()` ([7] line 997) joined with every question
   placeholder. A template segment that is not a substring of the two sources fails with "not
   from either source".
3. Every `answer` segment is `assertIn`-checked against `answer_values(answers)` ([9] line 34),
   which walks the answers structure and stringifies through the renderer's own `_scalar`.
4. Every `markup` segment is `assertRegex`-checked against `MARKUP_ONLY`, failing with "markup
   segment contains content".

Six further tests pin the surrounding behaviour: headings equal `EXPECTED_HEADINGS` in the
template's order ([9] line 432); every table title appears with its column header row ([9] line
438); instructional text is absent ([9] line 449); NIST's worked examples never appear ([9] line
454, "NIST's sample {example!r} leaked into the plan"); unanswered items render the template's
own placeholders and the unfilled count equals the whole question bank ([9] line 460); rendering
is deterministic ([9] line 468).

The README states the consequence in one sentence, at [6] line 57: "This is not a claim, it is a
checked invariant... If someone adds a helpful sentence to the renderer, that test fails."

### 3.3 Refusal to emit what has no authoritative template

[6] lines 27 to 40, the DRP argument, is the part of the design most relevant to this repository.

FedRAMP asks a cloud service provider for exactly one contingency-planning document, SSP
Appendix G, and publishes no DRP template. NIST SP 800-34 Rev. 1 §2.2 defines a Disaster
Recovery Plan as a plan *type* but publishes no DRP template either: its Appendix A is ISCP
templates and its Appendix B is the BIA template. So:

> A generated document titled "Disaster Recovery Plan" with a structure of our own invention
> would look authoritative, fail assessor review, and cost the reader more time than shipping
> nothing.

The refusal is not a refusal to do the work. The work is done, under a name that claims nothing:
the runbook set fills the appendix slot ISCP §4.2 explicitly allows, and the emit table at [6]
line 24 labels the runbooks **"This project's own structure"**, in bold, in the same table as
the two rows that say "verbatim". The generator will not even write the §4.2 cross-reference
pointing at them; the user answers `recovery.procedures` to say so themselves ([6] lines 42 to
46).

Note also the scope refusal at [6] line 47: a Business Continuity Plan, COOP, Occupant Emergency
Plan and crisis-communications plan are not emitted, because the template's own Table 1.4 lists
them as "Plans Outside of ISCP Scope". The exclusion is sourced to the template rather than to a
judgement.

### 3.4 The equivalent bar for this toolkit

The checklist. Each item names the `iscp-author` mechanism it is the analogue of.

- [ ] **1. Declare the instrument.** Every generated repository states in its `README.md` that
      it is an ITSCP, that it aligns to NIST SP 800-34 Rev. 1 structure, and that it is not an
      ISCP. Analogue: [6] line 22, the emit table's first column.
- [ ] **2. Declare structural provenance per element.** Every heading in a generated document
      is traceable to exactly one of a fixed set of structural sources. Analogue: [6] lines 22
      to 25.
- [ ] **3. Transcribe, do not paraphrase.** Where an element's structure comes from NIST, the
      heading text is the transcribed NIST text, held in a data-only module that says where each
      block came from and when it was read. Analogue: [7] lines 1 to 24.
- [ ] **4. Record the fetch.** Source version, date, and a byte count or hash where the source
      is a file. Analogue: [7] lines 12 to 14, `153865 bytes, md5 298f6b...`.
- [ ] **5. Enforce content provenance mechanically.** Every non-markup byte of a generated
      document is template text, a value from the answer store, or a status marker. A test
      asserts it. Analogue: [8] lines 3 to 21 and [9] `ProvenanceTests`.
- [ ] **6. Segments must reassemble.** The provenance record covers the whole document, not a
      sample of it. Analogue: [9] line 413.
- [ ] **7. Unanswered renders the marker, never a default.** Already the toolkit's stated rule
      in `templates/repo-scaffold.md` lines 56 to 63 and `itscp-build/SKILL.md`. Not yet
      enforced by anything. Analogue: [8] `_slot` and [9] line 460.
- [ ] **8. The reference example's numbers never leak.** No value from `oci-itscp` may appear in
      a generated plan as a default. A test asserts it, using the reference plan's own figures as
      the tripwire list. Analogue: [9] line 454, which uses NIST's sample business process the
      same way.
- [ ] **9. Determinism.** Same answer store, same bytes out. Analogue: [9] line 468.
- [ ] **10. Refuse what has no template.** The toolkit does not emit a document whose title
      asserts conformance to an instrument it has not read. Analogue: [6] lines 27 to 40.
- [ ] **11. State the gaps in the artefact itself.** Known limits are published beside the tool,
      not discovered by the user. Analogue: [6] line 168, "Known gaps, stated rather than
      hidden". The toolkit already does this in `README.md` and `docs/DESIGN.md`.

Items 1, 2, 3, 4, 5, 6, 8 and 9 are not met today. Item 7 is stated but unenforced. Items 10 and
11 are met in spirit and need item 10 written down as a rule rather than a habit.

---

## 4. The honest constraint

### 4.1 The guarantee that is unavailable

`iscp-author` can say "headings, table titles and column headers verbatim" [6] line 22 because
a specific file exists: a FedRAMP-published `.docx`, at a stable government URL, free to fetch
and free to reproduce, whose own revision history establishes which version is current.

**No such file exists for an ITSCP.** ITIL 4 and ISO 22301 are both paywalled and copyrighted.
The specific consequences, each traceable:

| Constraint | Evidence |
|---|---|
| The ITIL 4 ITSCM practice guide, which defines the terms an ITSCP is structured around, is paywalled and was not read | [1] source-honesty note; [1] reference entry 1, "Unverifiable by URL: paywalled (PeopleCert/AXELOS)" |
| ISO 22301:2019's text is paywalled; only a 12-page redline preview was readable, and the clauses defining MTPD, MBCO, RTO and RPO are not in it. The ISO Online Browsing Platform returned HTTP 403 to automated fetch | [1] reference entry 8 |
| ISO/IEC 27031:2025, the ICT-readiness guidance an ITSCP sits under, is paywalled; only the catalogue entry was read | [1] reference entry 7 |
| The one ITIL source that was readable is a Foundation glossary, third-party-hosted, undated, defining six relevant terms | §2.1, findings F1 to F4 |

So the toolkit cannot copy an authoritative ITSCP structure, because there is nothing to copy.
And the one ITIL text it can read is one it should not bake into a template corpus even
technically: reproducing a copyrighted training glossary verbatim inside every generated
repository is a different act from quoting six definitions with attribution in one crosswalk
document. *(Judgement, not legal advice; recorded in Unverified statements.)*

The asymmetry that makes the recommendation obvious: **NIST's text is free to reproduce and
ITIL's is not.** `iscp-author` already relies on this, transcribing NIST Appendix B into
`BIA_BLOCKS` without qualification [7] lines 18 to 24.

### 4.2 The options

**(a) Structure on NIST SP 800-34, carry an explicit ITIL crosswalk.** What `oci-itscp` does
through `docs/07`.

| For | Against |
|---|---|
| The structure is free, citable, quotable and transcribable verbatim, so checklist items 3 and 4 become achievable today | Leaves the five "Beyond NIST" coverage-map rows with no declared provenance at all |
| The audit skill already audits against 800-34 and the 800-53 CP family, so the structure and the audit agree | Says nothing about elements an ITSCP needs that an ISCP has no slot for: the availability boundary, the alert catalogue, service-level targets |
| The crosswalk pattern is proven, and the compliance-audit skill [10] already knows how to reason across it | Under (a) alone, MBCO and the review cadence either get dropped, losing the gap-closing that is the toolkit's best feature, or get carried with an implied ITIL provenance that cannot be shown |

**(b) Declare the structure as the project's own.** What `iscp-author` does for its runbooks and
CI inventory [6] lines 24 to 25.

| For | Against |
|---|---|
| Perfectly honest. Claims nothing | Throws away a free, citable structure that NIST already publishes and that the toolkit is already using |
| No ambiguity about what is derived from a standard | Makes the generated plan unauditable against any instrument, which breaks `itscp-audit` |
| Covers elements no standard gives us a slot for | Overstates the novelty. 36 of the 44 coverage-map rows really are NIST's; calling them ours would be a second kind of misattribution |

**(c) Combination.** Partition every element by structural provenance, exactly as
`iscp-author` partitions its four outputs in one table [6] lines 22 to 25.

### 4.3 Recommendation: (c), as a three-class partition with a fourth thing forbidden

**Recommendation.** Adopt (c). Every element of a generated ITSCP carries exactly one
structural-provenance class, and the crosswalk class is annotation only and can never introduce
structure.

| Class | Means | Heading text comes from | Example |
|---|---|---|---|
| `nist` | The element and its heading are NIST SP 800-34 Rev. 1's | Transcribed NIST text, verbatim | §3.3 Outage Assessment; Appendix K |
| `ours` | This project's own element. No standards provenance claimed | Written by us, declared as ours | Minimum business continuity objective per tier; cost model; alert catalogue |
| `crosswalk` | An ITIL 4 or ISO term named against an element the other two classes already placed | Nothing. It is an annotation | "The tier assignment workshop is a business impact analysis [glossary]" |

**There is no fourth class**, which is the same shape of guarantee as [8] lines 3 to 21. In
particular there is no class meaning "ITIL requires this", because we cannot read the text that
would say so.

**The load-bearing rule: the crosswalk never contributes structure.** A `crosswalk` annotation
may only attach to an element that a `nist` or `ours` class already justified. It can never be
the reason a field exists. Without this rule, "ITIL says we need X" becomes a route by which an
unread paywalled standard smuggles invented requirements into a generated plan, which is the
failure both repositories exist to prevent, wearing a citation.

**Two markers, and never an unmarked ITIL claim.** Every ITIL term in a generated document
carries one of exactly two markers, following the convention `oci-itscp/docs/07` already uses:

- `[glossary]` with the citation, for the six terms of §2.1 that are quotable from [1].
- `(practice guide; not verified)` for everything else. Terms in this class may be **used** but
  never **quoted**, and may never be the sole justification for a required field.

**The substitute guarantee**, replacing "headings copied verbatim from the authoritative
template", is three claims, all mechanically checkable:

1. **Structural provenance.** Every heading in a generated ITSCP is either verbatim NIST SP
   800-34 Rev. 1 heading text, checkable as a substring of a transcribed corpus exactly as
   `template_corpus()` [7] line 997 is checked, or is declared `ours` in a manifest. No heading
   exists whose provenance is an unread standard.
2. **Content provenance.** Every non-markup byte of a generated document is transcribed
   structural text, a value from the answer store, or a status marker (`**[MISSING — owner: ...]**`,
   `**[DEFERRED to ... — owner: ...]**`, `*(low confidence; not measured)*`, quoted from
   `templates/repo-scaffold.md` lines 56 to 63). This is the Iron Rule
   of `interview-method.md` promoted from prose to a test.
3. **Crosswalk provenance.** Every ITIL or ISO term carries one of the two markers above, and no
   crosswalk annotation is attached to an element that has no independent structural
   justification.

**The refusal rule**, the direct analogue of §3.3. The toolkit must never emit a document whose
title asserts conformance to an instrument it has not read. No "ISO 22301 conformance
statement", no "ITIL 4 ITSCM practice assessment", no "ITIL-compliant continuity plan". It may
emit `docs/07-standards-alignment.md`, already in the scaffold at `templates/repo-scaffold.md`
line 21, because a crosswalk asserts *correspondence*, which we can show, rather than
*conformance*, which we cannot.

**Why not (a) alone.** It has no home for the five "Beyond NIST" rows, and those rows are where
the toolkit's advantage over a plain ISCP generator lives. MBCO is the sharpest case: it is a
term whose only definition is paywalled, it closes gap G1, and under (a) alone the toolkit would
have to either drop it or carry it with an unshowable provenance.

**Why not (b) alone.** It discards NIST's structure for the 36 rows that genuinely are NIST's,
and it breaks `itscp-audit`, which audits against 800-34 and the 800-53 CP family and needs the
generated document to be traceable to those instruments.

**Why the combination is not a fudge.** It is the same move `iscp-author` already makes. That
plugin does not pick one provenance for its whole output. It emits four things with three
different provenances and puts them in one table where the reader can see which is which [6]
lines 22 to 25. The recommendation here is that table, generalised to element level and made
mandatory.

### 4.4 What the generated document must never imply

Stated as a short list because it is the single failure mode both repositories exist to prevent.

- Never "ITIL-compliant", "ITIL 4 conformant", "ISO 22301 aligned" or any equivalent. The
  toolkit has not read either text.
- Never an ITIL definition in our own words presented as ITIL's. Six terms may be quoted with
  attribution; everything else is paraphrase and must be marked as one.
- Never a heading justified by an unread standard.
- Never the reference plan's numbers as a default. `README.md` already says "Do not copy the
  reference plan's numbers"; checklist item 8 makes it a test.
- Never a citation to the third-party-hosted glossary presented as a citation to ITIL 4 itself.
  Cite it the way `oci-itscp` does, naming the hosting arrangement in the entry.

---

## 5. What this changes

### 5.1 Coverage map

`skills/_method/coverage-map.md`, 53 table lines across nine tables, of which 44 are
substantive rows: 36 NIST-derived, 5 "Beyond NIST", 3 "Not yet covered".

**Framing changes, three lines.**

| Line | Today | Change |
|---|---|---|
| 1 | `# Coverage map — every ISCP section, the skill that elicits it, the file it lands in` | Retitle to name the ITSCP. The map's own subject is misnamed |
| 7 | "Structure follows NIST SP 800-34 Rev. 1 Appendix A (Sample ISCP Templates) and §4.1 to §4.5." | Keep, and add the sentence that makes it a declared borrowing rather than a category error: the artefact is an ITSCP, structured on NIST's ISCP skeleton, per §1 of this document |
| 13, 20, 28, 36, 44, 52, 67 | Column header `ISCP element` / `ISCP appendix` | Rename to `Element` and add a `Provenance` column carrying `nist`, `ours` or `crosswalk` |

**Row changes.**

| Rows | Change |
|---|---|
| All 36 NIST-derived rows | Add `Provenance: nist`. Separately, replace the paraphrased element names with the transcribed NIST heading text (see §5.3, item 3); today's "1.1 Background — why the plan exists, its objectives" is a gloss, not a heading |
| All 5 "Beyond NIST" rows | Add `Provenance: ours`. The section's existing preamble already half-declares this; make it explicit per row |
| New rows, `ours` | Availability and continuity boundary (closes G4); monitoring, alarms and the alert catalogue; service-level targets and the link to any existing SLA; change authority for a planned switchover, and whether invocation is a pre-authorised emergency change; the major-incident entry condition to the activation gate; threat and scenario basis, mapped to NIST Step 3 preventive controls; information-security contributions (backup immutability, evidence sensitivity) |
| New table, `crosswalk` | The ITIL and ISO term map, six quotable terms and the rest marked `(practice guide; not verified)`, feeding `docs/07-standards-alignment.md` |
| "Not yet covered" table | Add a row: the toolkit produces no threat basis, and add the copyright and paywall constraint of §4.1 as a stated limit |

### 5.2 Skills

| Skill | New or altered questions |
|---|---|
| `itscp-interview-infrastructure` | **New section: monitoring and the alert catalogue.** What pages today, what should, what the app team needs the SRE to see, and what alarms on the *absence* of signal. This is the largest single hole; it also fills `docs/04-monitoring.md`, which currently has no owner. **New section: availability versus continuity.** Which controls are availability controls, which are continuity controls, and what single-point dependency the local recovery claim rests on. Closes G4. **New questions: threat basis and preventive controls.** What is this protecting against, and which preventive controls were considered and rejected |
| `itscp-interview-continuity` | **New: the major-incident entry condition.** What the organisation's existing major-incident process is, and where the declaration gate hangs off it. **New: change authority.** Who authorises a planned switchover and a failback, and whether invocation is a pre-authorised emergency change recorded after the fact |
| `itscp-interview-governance` | **New: which instruments this plan will be assessed against**, so the crosswalk document is generated against the right set rather than all of them. **New: does an SLA document exist**, and is it the home of the availability targets. **New: is `docs/07-standards-alignment.md` wanted**, and to which instruments |
| `itscp-interview-business` | No new questions. MBCO, mechanisms, workarounds and time dependence are already elicited. One wording change: §4 says "Not in NIST; asked because MTD alone is insufficient and an ISO 22301 auditor will ask", which should carry the `(practice guide; not verified)` marker for MBCO rather than an unqualified appeal to ISO |
| `itscp-interview-application` | No new questions. One wording change: line 45 "ISCP §1.2 scope" and line 118 "an ISCP is expected to address it" become crosswalk references, not descriptions of our own output |
| `itscp-build` | Description and body must stop calling the output an ISCP (lines 3, 19, 149). Coverage reporting gains a provenance breakdown beside the confidence distribution |
| `itscp-audit` | Description says "checking against NIST SP 800-34". Keep the instruments, add the sentence `oci-itscp/skills/itscp-compliance-audit/SKILL.md` §1 already carries: every row assesses an ISCP requirement against an ITSCP by way of the crosswalk |
| `itscp-discover` | No change. Line 82 already inventories monitoring alarms; that inventory becomes the opening material for the new infrastructure monitoring section |
| `skills/_method/interview-method.md` | Line 8, "A generated ISCP that says RTO: 4 hours", becomes ITSCP |
| `skills/_method/answer-store.md` | Line 85 "ISCP §1 Introduction" becomes a crosswalk reference. Add key namespaces for the new elicitation: monitoring, availability boundary, threat basis, change authority |
| `templates/repo-scaffold.md` | `docs/07-standards-alignment.md` (line 21) needs an owner and a defined content contract. `docs/04-monitoring.md` (line 18) and `docs/06-test-environments.md` (line 20) currently have no eliciting skill at all |

### 5.3 What genuinely does not exist yet

Ordered by how much stands on it.

1. **A renderer.** `templates/repo-scaffold.md` describes a directory tree and a rendering-rules
   table. There is no code, in any language, that turns `.itscm/answers.yaml` into a document.
   Every provenance guarantee in §4.3 is a property of a renderer, so none of them can be
   enforced until one exists. `iscp-author` has `iscp_render.py`; this repository has a
   description of one.
2. **Any test harness for the plan pipeline.** The only tests in the repository are
   `scripts/discover/test-readonly.sh` and the guard's unit tests, which cover discovery safety.
   There is nothing that could hold a `ProvenanceTests` equivalent. Checklist items 5, 6, 8 and
   9 all need one.
3. **A transcribed NIST corpus.** No file in this repository carries NIST heading text verbatim.
   `coverage-map.md` paraphrases every element with a gloss ("2.1 System description, architecture,
   locations, I/O and architecture diagrams"). Checklist item 3 is a transcription job that has not
   been started, and it is the prerequisite for item 2.
4. **A structural-provenance manifest.** Nothing anywhere records where an element's structure
   comes from. The `Provenance` column of §5.1 is the minimum version of this.
5. **A fetch record.** Nothing records which edition of SP 800-34 was read, when, or with what
   byte count. Compare [7] lines 12 to 14.
6. **The crosswalk document's content.** `docs/07-standards-alignment.md` exists as a filename in
   the scaffold with the note "NIST / ITIL / ISO crosswalk" and nothing else. No skill renders it,
   no coverage-map row covers it, and no question elicits what it should contain.
7. **A threat basis, anywhere.** §2.3. Not a missing renderer or a missing test: a missing
   question, in a plan family whose whole purpose is to survive an event.
8. **An anti-leak tripwire for the reference plan's numbers.** `README.md` warns the operator not
   to copy `oci-itscp`'s figures. Nothing checks. `iscp-author` checks the equivalent at [9] line
   454.

---

## References

Numbers are local to this document. Sources marked "read locally" were read from a checkout on
the machine that produced this document. No source was fetched over the network.

1. `oci-itscp/docs/07-itil4-alignment.md`, ITIL 4 Alignment and Terminology Conformance. Read
   locally. Supports: the practice list (§4), the vocabulary map (§1), the NIST and DoD
   crosswalk (§1a), gaps G1 to G4 and findings T1 to T14 (§3), and the source-honesty note
   recording that the ITIL 4 practice guide and ISO 22301 are paywalled and were not read.
2. `oci-itscp/docs/citation-audit.md`. Read locally. Supports: the verification status of every
   reference in [1], including row 1 (VERIFIED, 14 markers, body "Supported") and row 6 (NOT
   FOUND), and the audit method paragraph describing the adversarial fetch of 2026-09-01.
3. *Glossary, ITIL 4 Foundation Official Training Materials.* PeopleCert, copy hosted by a
   training provider, undated, accessed 2026-09-01 by [2].
   `https://igen.nl/wp-content/uploads/2024/10/ITIL-4-Foundation_Glossary_Digital.pdf` Supports:
   the six quotable definitions of §2.1. **Not fetched by this document**; its content status is
   taken from [2]. The ITIL 4 Service Continuity Management practice guide is paywalled
   (PeopleCert / AXELOS) and was not read by this document or by [1].
4. *NIST SP 800-34 Rev. 1, Contingency Planning Guide for Federal Information Systems*, May 2010
   with errata 2010-11-11. Cited here only as quoted or characterised by [1] §1a, [2] and [6].
   Supports: process Steps 2 to 7 as used in §2.3; §2.2 plan types and Appendix B as recorded by
   [6]. **Not fetched by this document.**
5. `picoagent/docs/engineering/continuity-tooling.md`. Read locally. Supports: §3, the three plan
   families table, the "inherits the wrong requirement set in both directions" statement and the
   naming rule (§1); §2, the alert-catalogue and dependency-graph constraints (§2.2).
6. `picoagent/examples/plugins/iscp-author/README.md`, 186 lines. Read locally. Supports: the
   emit table (lines 22 to 25), the DRP refusal (lines 27 to 40), the anti-fabrication guarantee
   (lines 48 to 74), the sources record (lines 128 to 166) and the known-gaps section (line 168).
7. `picoagent/examples/plugins/iscp-author/iscp_template.py`, 1017 lines. Read locally. Supports:
   the DATA ONLY docstring (lines 1 to 46), the FedRAMP fetch record with version, date, byte
   count and md5 (lines 9 to 17), the NIST Appendix B record (lines 18 to 24), the two editorial
   rules (lines 26 to 38), and `template_corpus()` (line 997).
8. `picoagent/examples/plugins/iscp-author/iscp_render.py`, 508 lines. Read locally. Supports:
   the three-kind invariant (lines 3 to 21), `MARKUP_ONLY` (line 50), `Segment` (lines 53 to 57),
   the three `_Writer` methods (lines 79, 83, 87), `answer_value` (lines 91 to 100), `_slot`
   (lines 111 to 120) and `render_iscp` (line 141).
9. `picoagent/tests/test_iscp_plugin.py`, 636 lines. Read locally. Supports: `answer_values`
   (line 34), `source_corpus` (line 51), `ProvenanceTests` (line 408), `assert_provenance` (lines
   411 to 422) and the six supporting tests (lines 424 to 471).
10. `oci-itscp/skills/itscp-compliance-audit/SKILL.md`. Read locally. Supports: the ITSCP versus
    ISCP scope paragraph, the "aligns to the ISCP structure; it is not one" statement, and the
    verdict vocabulary this repository's `itscp-audit` descends from.
11. This repository, read locally: `skills/_method/coverage-map.md`, `skills/_method/interview-method.md`,
    `skills/_method/answer-store.md`, the eight `skills/itscp-*/SKILL.md` files,
    `templates/repo-scaffold.md`, `README.md`, `GETTING-STARTED.md`, `docs/DESIGN.md`. Supports:
    every claim in §1, §2.2, §2.3, §2.4 and §5 about what the toolkit does and does not elicit.

### Unverified statements

- **The ITSCM practice activity list.** The six activities in §2.3 are the set commonly
  attributed to service continuity management. Only the business impact analysis is verifiable
  as an ITSCM activity from a source in this chain, via the glossary's own BIA definition [3].
  The other five are not quoted from ITIL 4 and are assessed here against their NIST SP 800-34
  process-step equivalents instead. Reason: the practice guide is paywalled.
- **Seven of the eight practice names in [1] §4 carry no inline citation.** [1] states that only
  the service continuity management definition is quoted and that the other purposes are
  paraphrased. This document therefore treats the seven names as [1]'s own editorial choice,
  reproduced unchanged, and does not present them as quotable ITIL 4 wording. Whether the
  glossary lists them as practice names was not checked.
- **The copyright judgement in §4.1.** That a copyrighted training glossary should not be
  reproduced verbatim inside every generated repository, while quoting six definitions with
  attribution in one crosswalk document is ordinary citation, is an engineering and editorial
  judgement made by this document. It is not legal advice and no legal source was consulted.
- **That NIST publications are free to reproduce.** Used as the working assumption behind
  recommendation (c) and behind checklist item 3. It is the same assumption `iscp-author` relies
  on when it transcribes NIST Appendix B into `BIA_BLOCKS` [7]. No source establishing it was
  read for this document.
- **NIST SP 800-34 Rev. 1 was not read directly for this document.** Every statement about its
  contents, including the Appendix A element set that `coverage-map.md` is structured on, the
  process steps of §2.3, and the §2.2 plan-type definition, is taken from [1], [2] or [6]. The
  coverage map's 36 NIST-derived rows have therefore **not** been checked against NIST's own
  headings by anyone, which is precisely why checklist item 3 exists.
- **Whether ISO 22301:2019 still uses MTPD** rests on a secondary source, carried across from
  [1]'s own unverified-statements list.
- **The count of 44 substantive coverage-map rows** was derived by counting table rows in the
  file and subtracting nine header rows. The commonly quoted figure of 53 counts header rows as
  well. Both refer to the same file.
