"""DATA ONLY: the ITSCP question bank, one entry per key in the answer store.

Every key in ``templates/answers.example.yaml`` maps to exactly one :class:`Question` here,
and nothing else may be written to the store. The bank is the schema: there is no separate
schema file, because a second copy of the field list is a second thing to drift.

Read alongside:

* ``skills/_method/answer-store.md`` — the record shape, the namespace ownership rules and
  the seven-role owner vocabulary.
* ``skills/_method/interview-method.md`` — the Iron Rule, the status lattice, the confidence
  rubric and the closed provenance list.
* ``docs/ITIL-GROUNDING.md`` §4 — the three-class structural-provenance partition that
  :attr:`Question.structural_provenance` implements, and the rule that ``crosswalk`` may
  never justify a field on its own.

The module holds no behaviour beyond lookup. Validation lives in ``itscp_store``; rendering
lives in a module this one knows nothing about.

Ported from ``picoagent/examples/plugins/iscp-author/iscp_questions.py``: the frozen
dataclass, ``SECTIONS``, ``BY_ID`` and ``for_section`` are the same shape. The content is
not. That plugin fills a FedRAMP ISCP template; this one elicits an ITSCP.

Deliberate deviations from the ported shape, all reported:

* There is no ``placeholder`` field. ``iscp-author`` renders the source template's own
  ``<Insert ...>`` token for an unanswered spot. We have no source template, and
  ``templates/repo-scaffold.md`` already fixes the marker text for every status
  (``**[MISSING - owner: ...]**`` and the rest). A per-question placeholder would be a
  second source for one string.
* There is no ``required`` field. Every field is required to carry a *status*; none is
  required to carry a *value*. That is the status lattice, not a per-question flag.
* ``prefill`` becomes :attr:`Question.seedable` plus :attr:`Question.seed_operation`, because
  a seeded value has to name the read-only operation that produced it in order to write a
  legal ``oci-discovery:<operation>`` provenance.
"""
from __future__ import annotations

import sys

if sys.version_info < (3, 11):
    raise RuntimeError(
        "itscp-author needs Python 3.11 or newer (this is "
        f"{sys.version_info.major}.{sys.version_info.minor}). The store reads TOML through "
        "the standard library's tomllib, added in 3.11. There is no pip dependency to "
        "install; run the plugin under a newer interpreter."
    )

from dataclasses import dataclass, field

# --------------------------------------------------------------------------- vocabularies

#: The status lattice, from ``interview-method.md``. Every field carries exactly one.
STATUSES: tuple[str, ...] = ("MISSING", "ANSWERED", "DEFERRED", "NOT_APPLICABLE")

#: The confidence rubric, assigned from how the answer arrived rather than how plausible it
#: sounds. ``interview-method.md``, "Separate what they know from what they are guessing".
CONFIDENCES: tuple[str, ...] = ("high", "medium", "low")

#: Key namespaces and the skill that owns each, from ``answer-store.md`` "Key namespaces".
#: A skill writes only within its own prefix.
NAMESPACES: dict[str, str] = {
    "system": "itscp-interview-application",
    "business": "itscp-interview-business",
    "app": "itscp-interview-application",
    "infra": "itscp-interview-infrastructure",
    "continuity": "itscp-interview-continuity",
    "governance": "itscp-interview-governance",
    "discovery": "itscp-discover",
}

#: The seven roles and their deputies, from ``answer-store.md`` "Owner vocabulary". ``owner``
#: names a role, never a person, so the store stays shareable and survives a leaver.
ROLES: tuple[str, ...] = (
    "business owner",
    "application owner",
    "lead engineer",
    "infrastructure owner",
    "DR process owner",
    "governance/risk contact",
    "signing authority",
)

#: Every legal ``owner`` value: the seven roles and the deputy of each.
OWNER_VOCABULARY: tuple[str, ...] = ROLES + tuple(f"{role} deputy" for role in ROLES)

#: The three structural-provenance classes of ``docs/ITIL-GROUNDING.md`` §4.3. There is no
#: fourth class, and ``crosswalk`` is annotation only: see :data:`CROSSWALK_NEVER_JUSTIFIES`.
STRUCTURAL_PROVENANCE: tuple[str, ...] = ("nist", "ours", "crosswalk")

#: The load-bearing rule of §4.3, stated once so the test that enforces it can quote it.
CROSSWALK_NEVER_JUSTIFIES = (
    "A crosswalk annotation may only attach to an element a nist or ours class already "
    "justified. It can never be the reason a field exists. Without this rule, 'ITIL says we "
    "need X' becomes a route by which an unread paywalled standard smuggles invented "
    "requirements into a generated plan."
)

#: The two markers §4.3 permits on an ITIL or ISO term, and never an unmarked ITIL claim.
#: ``[glossary]`` for the six terms quotable from the one readable source; the other for
#: everything else, which may be used but never quoted.
CROSSWALK_MARKERS: tuple[str, ...] = ("[glossary]", "(practice guide; not verified)")

#: Answer kinds.
#:
#: ``rows`` is a list of maps, which the emitter writes as a TOML array of tables; there are
#: exactly seven of them and :func:`row_questions` returns them.
#:
#: ``narrative`` is a multi-paragraph answer and is a first-class value, not a long ``text``.
#: The reference plan this toolkit has to reproduce is mostly narrative: design rationale,
#: architecture assumptions, why one topology was chosen over another. Those came from a
#: human working through their understanding against sources, which is an interview answer
#: with ordinary provenance, so a narrative carries provenance, confidence, mechanism,
#: supersede history and conflicts exactly as a scalar does. The one thing it carries in
#: addition is a read-back: see :attr:`Question.readback_required`.
KINDS: tuple[str, ...] = (
    "text", "narrative", "duration", "number", "currency", "enum", "list", "rows", "date",
)

#: How a narrative answer came to be attributable. Recorded on the record, not only in the
#: session transcript, because the renderer reads the store and never sees the transcript: if
#: confirmation lived only in the transcript, a store copied without it would launder drafts
#: into facts.
#:
#: ``not_required``
#:     The answer was given directly. Nothing was drafted on the interviewee's behalf.
#: ``confirmed``
#:     A draft was read back and the interviewee accepted it as written.
#: ``corrected``
#:     A draft was read back, the interviewee changed it, and the stored value is theirs.
#:
#: There is deliberately no state meaning "drafted but not yet shown to anybody". A draft
#: nobody has confirmed is not an answer; it stays out of the store, the field stays MISSING
#: with the read-back owed by a named owner, and the draft lives in the session transcript.
READBACKS: tuple[str, ...] = ("not_required", "confirmed", "corrected")


# --------------------------------------------------------------------------- the question

@dataclass(frozen=True)
class Question:
    """One key in the answer store.

    ``prompt`` is the *observable*: what the interviewer actually asks, per
    ``interview-method.md`` "Ask for the observable, not the abstraction". ``records`` is the
    abstraction the answer is filed under. People do not know their RTO; they know their pain.

    ``guidance`` is migrated verbatim from ``templates/answers.example.yaml`` wherever that
    file carried a note. It is regenerated into the emitted TOML as comments on every write,
    which is what makes TOML viable given that ``tomllib`` discards comments on read.

    ``mechanism_required`` marks every duration, threshold and currency figure. The store's
    own note says a number without a mechanism is a guess wearing a suit; the store rejects
    an ANSWERED value on one of these fields with no ``mechanism``.

    ``seedable`` is the answer to picoagent's open question 5. True means discovery may
    prefill the field and the interview reads it back for correction rather than asking
    cold; the prefill carries provenance ``oci-discovery:<seed_operation>``. False means the
    field is asked independently, and a discovery value that disagrees lands in ``conflict``,
    never in ``value``.

    ``structural_provenance`` is the §4.3 class. ``nist`` fields carry the verbatim NIST
    heading in ``nist_heading``; ``ours`` fields carry the empty string and claim nothing.
    ``crosswalk`` is legal in the enum and illegal on a question, which is the point of it.
    """

    id: str
    namespace: str
    section: str
    coverage_row: str
    written_to: str
    prompt: str
    records: str
    owner_role: str
    structural_provenance: str
    guidance: str = ""
    kind: str = "text"
    unit: str = ""
    options: tuple[str, ...] = ()
    columns: tuple[str, ...] = ()
    enum_columns: dict[str, tuple[str, ...]] = field(default_factory=dict)
    provenance_required: bool = True
    confidence_required: bool = True
    mechanism_required: bool = False
    readback_required: bool = False
    seedable: bool = False
    seed_operation: str = ""
    nist_heading: str = ""
    nist_source: str = ""
    crosswalk_note: str = ""


# --------------------------------------------------------------- transcribed NIST headings
#
# NIST SP 800-34 Rev. 1 is a US government publication and is free to reproduce. These are
# transcriptions, not paraphrases: every string below was read off the published text at
# nvlpubs.nist.gov and is reproduced with NIST's own capitalisation, spacing and punctuation.
# Where the template's table of contents and its body disagree, the body wins and the
# disagreement is recorded in NIST_DISCREPANCIES.

#: Appendix A.3, Sample Template for High-Impact Systems. The moderate template (A.2) shares
#: this lettering; the low template (A.1) has no Appendix F and letters G through L one lower.
NIST_A3_HEADINGS: tuple[str, ...] = (
    "Plan Approval",
    "1. Introduction",
    "1.1 Background",
    "1.2 Scope",
    "1.3 Assumptions",
    "2. Concept of Operations",
    "2.1 System Description",
    "2.2 Overview of Three Phases",
    "2.3 Roles and Responsibilities",
    "3. Activation and Notification",
    "3.1 Activation Criteria and Procedure",
    "3.2 Notification",
    "3.3 Outage Assessment",
    "4. Recovery",
    "4.1 Sequence of Recovery Activities",
    "4.2 Recovery Procedures",
    "4.3 Recovery Escalation Notices/Awareness",
    "5. Reconstitution",
    "5.1 Concurrent Processing",
    "5.2 Validation Data Testing",
    "5.3 Validation Functionality Testing",
    "5.4 Recovery Declaration",
    "5.5 Notifications (users)",
    "5.6 Cleanup",
    "5.7 Offsite Data Storage",
    "5.8 Data Backup",
    "5.9 Event Documentation",
    "5.10 Deactivation",
    "APPENDIX A PERSONNEL CONTACT LIST",
    "APPENDIX B VENDOR CONTACT LIST",
    "APPENDIX C DETAILED RECOVERY PROCEDURES",
    "APPENDIX D ALTERNATE PROCESSING PROCEDURES",
    "APPENDIX E SYSTEM VALIDATION TEST PLAN",
    "APPENDIX F ALTERNATE STORAGE, SITE, AND TELECOMMUNICATIONS",
    "APPENDIX G DIAGRAMS (SYSTEM AND INPUT/OUTPUT)",
    "APPENDIX H HARDWARE AND SOFTWARE INVENTORY",
    "APPENDIX I INTERCONNECTIONS TABLE",
    "APPENDIX J TEST AND MAINTENANCE SCHEDULE",
    "APPENDIX K ASSOCIATED PLANS AND PROCEDURES",
    "APPENDIX L BUSINESS IMPACT ANALYSIS",
    "APPENDIX M DOCUMENT CHANGE PAGE",
)

#: Headings from the body chapters, used where NIST places an element in the guidance rather
#: than in the plan template. A field justified from here is still ``nist``, but the coverage
#: map's claim that the structure follows "Appendix A and 4.1-4.5" does not reach it, so the
#: source is named explicitly in ``nist_source``.
NIST_CHAPTER_HEADINGS: tuple[str, ...] = (
    "3.2 Conduct the Business Impact Analysis (BIA)",
    "3.2.1 Determine Business Processes and Recovery Criticality",
    "3.2.2 Identify Resource Requirements",
    "3.2.3 Identify System Resource Recovery Priorities",
    "3.4.1 Backup and Recovery",
    "3.4.2 Backup Methods and Offsite Storage",
    "3.4.3 Alternate Sites",
    "3.4.5 Cost Considerations",
    "3.4.6 Roles and Responsibilities",
    "3.5 Plan Testing, Training, and Exercises (TT&E)",
    "3.5.2 Training",
    "3.6 Plan Maintenance",
    "4.1 Supporting Information",
    "4.2.1 Activation Criteria and Procedure",
    "4.2.2 Notification Procedures",
    "4.2.3 Outage Assessment",
    "4.3.3 Recovery Escalation and Notification",
    "4.4 Reconstitution Phase",
)

#: Every heading a ``nist`` question may cite. A test asserts membership, which is the
#: mechanically-checkable form of claim 1 in ``docs/ITIL-GROUNDING.md`` §4.3: no heading
#: exists whose provenance is an unread standard.
NIST_CORPUS: frozenset[str] = frozenset(NIST_A3_HEADINGS) | frozenset(NIST_CHAPTER_HEADINGS)


@dataclass(frozen=True)
class Discrepancy:
    """One place where ``skills/_method/coverage-map.md`` and NIST's own text disagree.

    Recorded in code rather than only in a report, because the coverage map is edited by
    people who will not have read the report and the disagreement should outlive it.

    ``kind`` is one of:

    ``paraphrase``
        The coverage map states a heading in its own words. NIST's text is free to
        reproduce, so there is no reason not to transcribe it.
    ``wrong-letter``
        The coverage map's appendix letter is not the letter NIST gives that element in any
        of the three sample templates.
    ``wrong-source``
        The element exists in NIST but not where the coverage map implies it does.
    ``no-nist-basis``
        Nothing in SP 800-34 Rev. 1 corresponds. Reclassified ``ours``.
    """

    coverage_row: str
    coverage_text: str
    nist_text: str
    kind: str
    note: str


#: Verified against the published text of NIST SP 800-34 Rev. 1 (May 2010, with the 5/21/2010
#: errata), read in full. Before this check, no one had compared the coverage map's 36
#: NIST-derived rows against NIST's own headings; ``docs/ITIL-GROUNDING.md`` says so plainly.
#: Every row was checked. These are the ones that did not match.
NIST_DISCREPANCIES: tuple[Discrepancy, ...] = (
    Discrepancy(
        "Front matter", "Plan Approval statement", "Plan Approval", "paraphrase",
        "NIST's heading is the two words. 'statement' comes from the body text under it "
        "('Provide a statement in accordance with the agency's contingency planning "
        "policy'), not from the heading.",
    ),
    Discrepancy(
        "Front matter", "Record of Changes", "APPENDIX M DOCUMENT CHANGE PAGE",
        "wrong-source",
        "NIST does print the words 'Record of Changes', twice: as Table 3-7 in section 3.6 "
        "Plan Maintenance, and as the table caption inside the sample templates' last "
        "appendix. It is not front matter in any of the three templates. In A.1 it is "
        "Appendix L, in A.2 and A.3 Appendix M, and the heading is DOCUMENT CHANGE PAGE. "
        "Placing it in front matter is our choice and should be declared ours, or the "
        "coverage map should move the row to the appendix table under NIST's own letter. "
        "Separately, NIST's own table of contents calls it Table 3-6 and its body calls it "
        "Table 3-7; that one is NIST's error, not the coverage map's.",
    ),
    Discrepancy(
        "2.2", "Overview of the three phases", "2.2 Overview of Three Phases", "paraphrase",
        "Two inserted words. Trivial in isolation, and exactly the class of drift the "
        "verbatim-transcription rule exists to stop.",
    ),
    Discrepancy(
        "4.3", "Recovery escalation and notification",
        "4.3 Recovery Escalation Notices/Awareness", "wrong-source",
        "'Recovery Escalation and Notification' is a real NIST heading, but it is section "
        "4.3.3 of Chapter 4, the guidance. All three sample templates head the plan section "
        "'4.3 Recovery Escalation Notices/Awareness'. The coverage map labels the row 4.3, "
        "which is the template's numbering, and then gives Chapter 4's wording. One or the "
        "other.",
    ),
    Discrepancy(
        "5.5", "User notification", "5.5 Notifications (users)", "paraphrase",
        "The A.3 body prints 'Notifications (users)' and the A.3 table of contents prints "
        "'Notification (users)'. NIST disagrees with itself by one letter; the coverage map "
        "agrees with neither.",
    ),
    Discrepancy(
        "5.8", "Data backup after reconstitution", "5.8 Data Backup", "paraphrase",
        "'after reconstitution' is added. True of the section's placement, absent from its "
        "heading.",
    ),
    Discrepancy(
        "5.9", "Event documentation and after-action report", "5.9 Event Documentation",
        "paraphrase",
        "'and after-action report' is added. NIST does use 'After Action Report', but in "
        "Appendix J of the templates, describing where test results go, not in the 5.9 "
        "heading.",
    ),
    Discrepancy(
        "App. B", "Vendor contacts, offsite storage and alternate site POCs",
        "APPENDIX B VENDOR CONTACT LIST", "paraphrase",
        "The letter is right and the first three words are right. 'offsite storage and "
        "alternate site POCs' is NIST's Appendix F content, not its Appendix B content; "
        "folding it into B loses the row that would have carried it.",
    ),
    Discrepancy(
        "App. C", "Alternate site, storage and telecommunications",
        "APPENDIX F ALTERNATE STORAGE, SITE, AND TELECOMMUNICATIONS", "wrong-letter",
        "NIST letters this F in the moderate and high templates and omits it entirely from "
        "the low template. NIST's C is DETAILED RECOVERY PROCEDURES. The coverage map's C "
        "is FedRAMP's C ('Appendix C Alternate Storage, Processing and Provisions'), which "
        "is a different document's lettering.",
    ),
    Discrepancy(
        "App. D", "Detailed recovery procedures and checklists",
        "APPENDIX C DETAILED RECOVERY PROCEDURES", "wrong-letter",
        "NIST letters this C in all three templates. FedRAMP letters it C as well. The "
        "coverage map's D matches neither, and 'and checklists' is added.",
    ),
    Discrepancy(
        "App. E", "Alternate mission/business processing - manual workarounds",
        "APPENDIX D ALTERNATE PROCESSING PROCEDURES", "wrong-letter",
        "NIST letters this D in all three templates, FedRAMP letters it D. The coverage "
        "map's E matches neither.",
    ),
    Discrepancy(
        "App. F", "System validation test plan", "APPENDIX E SYSTEM VALIDATION TEST PLAN",
        "wrong-letter",
        "NIST letters this E in all three templates, FedRAMP letters it E. The coverage "
        "map's F matches neither. The title itself is verbatim, which makes the letter the "
        "only error and the easiest to miss.",
    ),
    Discrepancy(
        "App. H", "Hardware, software and firmware inventory",
        "APPENDIX H HARDWARE AND SOFTWARE INVENTORY", "paraphrase",
        "The letter is right. 'firmware' is not in the heading. NIST does use the word, in "
        "the outage-assessment list in 4.2.3 and in the CP-9 control text of Appendix E, "
        "but an inventory appendix that promises firmware and is graded against a heading "
        "that does not mention it is a gap manufactured by a paraphrase.",
    ),
    Discrepancy(
        "App. I", "System interconnections", "APPENDIX I INTERCONNECTIONS TABLE",
        "paraphrase",
        "The letter is right in the moderate and high templates. 'System interconnections' "
        "is FedRAMP's wording ('Appendix I System Interconnections with Other Services'); "
        "NIST's is 'INTERCONNECTIONS TABLE'.",
    ),
    Discrepancy(
        "App. J", "Test, training and exercise documentation",
        "APPENDIX J TEST AND MAINTENANCE SCHEDULE", "paraphrase",
        "The letter is right in the moderate and high templates. The words are NIST's, but "
        "from section 3.5 'Plan Testing, Training, and Exercises (TT&E)' in the guidance "
        "chapter, not from the appendix heading. Training is genuinely a separate NIST "
        "element (3.5.2) and the appendix does not carry it, so the coverage map's row "
        "silently merges two NIST elements into one.",
    ),
    Discrepancy(
        "App. K", "Business impact analysis", "APPENDIX L BUSINESS IMPACT ANALYSIS",
        "wrong-letter",
        "K is right only for the low-impact template (A.1). In A.2 and A.3 the BIA is "
        "Appendix L, and Appendix K is ASSOCIATED PLANS AND PROCEDURES. FedRAMP also "
        "letters the BIA L. Given the coverage map's other rows track the moderate and high "
        "templates, K is the wrong letter here.",
    ),
    Discrepancy(
        "App. L", "Vendor SLAs and reciprocal agreements", "", "no-nist-basis",
        "No appendix of this name exists in any of the three NIST templates or in FedRAMP's. "
        "NIST's L is BUSINESS IMPACT ANALYSIS in the moderate and high templates and "
        "DOCUMENT CHANGE PAGE in the low one. SLAs appear in NIST prose, under Appendix F's "
        "alternate-processing-site bullet list and in 3.4.3 Alternate Sites, but there is no "
        "appendix for them and 'reciprocal agreements' as a heading is ours. Reclassified "
        "ours. It is a good element; it just is not NIST's.",
    ),
    Discrepancy(
        "Beyond NIST", "Plan review and maintenance cadence",
        "APPENDIX J TEST AND MAINTENANCE SCHEDULE / 3.6 Plan Maintenance", "wrong-source",
        "Filed under Beyond NIST as though NIST were silent on it. NIST is not: the "
        "templates' Appendix J opens 'All ISCPs should be reviewed and tested at the "
        "organization defined frequency (e.g. yearly) or whenever there is a significant "
        "change to the system', and section 3.6 is Plan Maintenance. The row understates "
        "its own provenance, which is the rarer and less dangerous direction of error, but "
        "it is still wrong, and it means the audit skill cannot trace the field to the "
        "instrument it audits against. Reclassified nist.",
    ),
    Discrepancy(
        "Beyond NIST", "Cost model and posture economics",
        "3.4.5 Cost Considerations / Table 3-4 Contingency Strategy Budget Planning Template",
        "wrong-source",
        "Also filed Beyond NIST. NIST has 3.4.5 Cost Considerations and a budget planning "
        "table. The distinction the coverage map wanted is real but is not the one it drew: "
        "NIST costs contingency strategy in the planning chapter and gives the plan template "
        "no cost heading at all. So the element is NIST's; the decision to carry it as a "
        "section of the generated plan is ours. Kept ours, with the NIST element named, "
        "because the coverage map's claim is about plan structure.",
    ),
    Discrepancy(
        "coverage-map header", "Structure follows NIST SP 800-34 Rev. 1 Appendix A (Sample "
        "ISCP Templates) and 4.1-4.5.",
        "Appendix A templates number their sections 1 to 5; Chapter 4 numbers its own 4.1 "
        "to 4.5 differently", "wrong-source",
        "The two sources cited number differently and the map takes its numbering from the "
        "first. Chapter 4's 4.1 is Supporting Information, 4.2 Activation and Notification "
        "Phase, 4.3 Recovery Phase, 4.4 Reconstitution Phase, 4.5 Plan Appendices. The "
        "template's 4.1 is Sequence of Recovery Activities. Citing both without saying which "
        "supplies the numbering is how row 4.3 ended up with the template's number and the "
        "chapter's title.",
    ),
)


#: The closed set of ways the coverage map and NIST can disagree.
DISCREPANCY_KINDS: tuple[str, ...] = (
    "paraphrase", "wrong-letter", "wrong-source", "no-nist-basis",
)


# --------------------------------------------------------------------------- the bank
#
# Adding a question is adding a literal to this tuple. Nothing below the tuple needs editing,
# nothing in itscp_store needs editing, and no key is hardcoded anywhere else in the plugin.
#
# `guidance` is migrated verbatim from templates/answers.example.yaml wherever that file
# carried a note; the line wrapping is the YAML's, the words are not changed. Questions the
# YAML left unannotated carry guidance written here.

_BIA = "SP 800-34 Rev. 1 Appendix A.3 heading, and Appendix B Sample BIA"
_A3 = "SP 800-34 Rev. 1 Appendix A.3, Sample Template for High-Impact Systems"
_CH3 = "SP 800-34 Rev. 1 Chapter 3, Information System Contingency Planning Process"
_CH4 = "SP 800-34 Rev. 1 Chapter 4, Information System Contingency Plan Development"

QUESTIONS: tuple[Question, ...] = (
    # ------------------------------------------------------ system.* - application owner
    Question(
        "system.name", "system", "2.1", "2.1 System description",
        "docs/01-architecture.md 2",
        "What is this application suite called in the systems that run it: the name on the "
        "servers, in the monitoring, in the change tickets?",
        "The system's technical name, as the plan's title and throughout",
        "application owner", "nist",
        guidance="The name the estate uses. Where the business calls it something else, that "
                 "goes in system.business_name and both appear in the plan.",
        nist_heading="2.1 System Description", nist_source=_A3,
    ),
    Question(
        "system.business_name", "system", "1.1", "1.1 Background",
        "README.md, docs/00-plan-approval.md",
        "And what do the people who use it call it? The name that would appear in an email "
        "from Finance saying it is down.",
        "The business-facing name for the same system",
        "business owner", "ours",
        guidance="What the business calls it. The ITSCP is read by both audiences.",
    ),
    Question(
        "system.categorization", "system", "1.2", "1.2 Scope",
        "README.md, docs/02-mtd-tiers.md",
        "Has this system ever been given an impact level or a data classification? If so, "
        "where is that recorded and what does it say?",
        "The impact level or data classification and where it is recorded",
        "governance/risk contact", "nist",
        guidance="Impact level or data classification. Determines which controls are "
                 "mandatory. If never categorised, that is itself the finding.",
        nist_heading="1.2 Scope", nist_source=_A3,
        crosswalk_note="ISO 22301 uses a different categorisation vocabulary "
                       "(practice guide; not verified)",
    ),
    # ------------------------------------------------------ business.* - business owner
    Question(
        "business.processes", "business", "App. K", "K. Business impact analysis",
        "docs/02-mtd-tiers.md, checklists/tier-assignment-workshop.md",
        "Walk me through what stops if this is down for an hour. Then for a day. Then for a "
        "week. Take the processes one at a time.",
        "Each business process and what its outage costs at one hour, four hours, a day and "
        "a week",
        "business owner", "nist", kind="rows",
        columns=("name", "impact_1h", "impact_4h", "impact_1d", "impact_1w"),
        guidance="The BIA's first step. Ask about impact at each horizon separately; people "
                 "answer 'it is critical' to the general question and give you something "
                 "usable when the horizon is named.",
        nist_heading="3.2.1 Determine Business Processes and Recovery Criticality",
        nist_source=_CH3,
        crosswalk_note="ITIL calls this session a business impact analysis [glossary]",
    ),
    Question(
        "business.mtd.tier0", "business", "App. K", "K. Business impact analysis",
        "docs/02-mtd-tiers.md",
        "At what point does this stop being an IT problem and become something the chief "
        "executive hears about?",
        "Maximum tolerable downtime for the tier 0 processes",
        "business owner", "nist", kind="duration", unit="hours",
        mechanism_required=True, readback_required=True,
        guidance="A number without a mechanism is a guess wearing a suit.",
        nist_heading="3.2.1 Determine Business Processes and Recovery Criticality",
        nist_source=_BIA,
        crosswalk_note="ISO 22301's term is maximum tolerable period of disruption "
                       "(practice guide; not verified)",
    ),
    Question(
        "business.rpo.tier0", "business", "App. K", "K. Business impact analysis",
        "docs/02-mtd-tiers.md",
        "If we recovered to fifteen minutes before the failure, what work would people have "
        "to redo, and who would have to redo it?",
        "Recovery point objective for the tier 0 processes",
        "business owner", "nist", kind="duration", unit="minutes",
        mechanism_required=True, readback_required=True,
        guidance="Elicited as: if we lost 15 minutes, who redoes the work, and can they?",
        nist_heading="3.2.1 Determine Business Processes and Recovery Criticality",
        nist_source=_BIA,
    ),
    Question(
        "business.mbco.tier0", "business", "Beyond NIST",
        "Minimum business continuity objective per tier", "docs/02-mtd-tiers.md",
        "While we are recovering, what is the smallest amount of this service that keeps you "
        "trading? Not the full thing. The part you cannot do without for a day.",
        "The minimum service level that must be available during work recovery",
        "business owner", "ours", readback_required=True,
        guidance="Not NIST. What must work to keep trading while recovery runs.",
        crosswalk_note="ITIL and ISO 22301 both use minimum business continuity objective "
                       "(practice guide; not verified)",
    ),
    Question(
        "business.workarounds", "business", "App. E",
        "E. Alternate mission/business processing - manual workarounds",
        "checklists/manual-workarounds.md",
        "Last time this was down, what did people actually do? Did anyone write anything on "
        "paper, and how long could they keep that up?",
        "Each process, the workaround used, and how long it is sustainable",
        "business owner", "nist", kind="rows",
        columns=("process", "workaround", "sustainable_for"),
        guidance="Appendix E. Ask about the last real outage, not the hypothetical one.",
        nist_heading="APPENDIX D ALTERNATE PROCESSING PROCEDURES", nist_source=_A3,
    ),
    Question(
        "business.tier_signoff", "business", "Beyond NIST",
        "Citation and unverified-statement discipline", "docs/02-mtd-tiers.md",
        "Have you signed off the tier assignment, or is it still with you? If it is not "
        "signed, who owes the signature and by when?",
        "Whether the tier assignment is signed, and by whom, or who owes it",
        "business owner", "ours", kind="enum",
        options=("signed", "not signed", "signed with exceptions"),
        readback_required=True,
        guidance="Signed, or explicitly recorded as not signed and who owes it.",
    ),
    # ------------------------------------------------------ app.* - application owner
    Question(
        "app.start_order", "app", "4.1", "4.1 Sequence of recovery activities",
        "runbooks/RB-01-switchover.md, docs/09 3",
        "If everything were off and you had to bring it up from cold, what would you start "
        "first, and what would break if you started it second?",
        "The component start order and what depends on what",
        "lead engineer", "nist", kind="narrative", readback_required=True,
        guidance="Rarely written down, usually in one person's head. Capture verbatim. If "
                 "only one engineer holds it, that is a deputy gap as well as a "
                 "documentation gap.",
        nist_heading="4.1 Sequence of Recovery Activities", nist_source=_A3,
    ),
    Question(
        "app.interconnections", "app", "App. I", "I. System interconnections",
        "docs/12-interconnections.md",
        "Who sends you files, and who is waiting on files from you? What breaks on their "
        "side first?",
        "Each interconnection, its direction, transport, contact and whether it is replayable",
        "application owner", "nist", kind="rows",
        columns=("partner", "direction", "transport", "contact", "replayable"),
        guidance="Appendix I. A partner contact stored only inside the system being "
                 "recovered is not a contact.",
        nist_heading="APPENDIX I INTERCONNECTIONS TABLE", nist_source=_A3,
    ),
    Question(
        "app.validation_pack", "app", "App. F", "F. System validation test plan",
        "checklists/validation-pack.md",
        "Once it is back up, what do you personally check before you would tell users it is "
        "working? How long does each check take, and who does it?",
        "Each validation check, its duration and its owner",
        "application owner", "nist", kind="rows",
        columns=("check", "duration", "who"),
        guidance="Appendix F. On the MTD critical path and routinely omitted from timings.",
        nist_heading="APPENDIX E SYSTEM VALIDATION TEST PLAN", nist_source=_A3,
    ),
    Question(
        "app.wrt_activities", "app", "Beyond NIST",
        "Minimum business continuity objective per tier", "docs/10 3",
        "After the system is technically up but before the business can use it, what has to "
        "happen? Which of those can run while we are still bringing things up?",
        "Each work-recovery activity, its duration, and whether it runs in parallel with "
        "bring-up",
        "application owner", "ours", kind="rows",
        columns=("activity", "duration", "parallel_with_bringup"),
        guidance="The parallel/serial flag decides whether the MTD is achievable.",
    ),
    Question(
        "app.concurrent_processing", "app", "5.1", "5.1 Concurrent processing",
        "docs/10 3",
        "During recovery, would you ever run the old and the new environment at the same "
        "time? If not, why not?",
        "Whether concurrent processing is performed, and the reason either way",
        "application owner", "nist", kind="narrative", readback_required=True,
        guidance="Usually NOT_APPLICABLE. NIST does not require it; the plan must still "
                 "address it, with the reason.",
        nist_heading="5.1 Concurrent Processing", nist_source=_A3,
    ),
    # ------------------------------------- infra.* - infrastructure owner and discovery
    Question(
        "infra.primary_region", "infra", "2.1", "2.1 System description",
        "docs/01-architecture.md 2",
        "Where does this run today? Discovery says the primary region is the one I will read "
        "back to you; correct me if that is wrong.",
        "The primary region",
        "infrastructure owner", "nist",
        seedable=True, seed_operation="ListAvailabilityDomains",
        guidance="Discovery can name this, so it is read back for correction rather than "
                 "asked cold. A correction is itself worth having: it usually means "
                 "something moved and nobody updated the diagram.",
        nist_heading="2.1 System Description", nist_source=_A3,
    ),
    Question(
        "infra.standby_region", "infra", "App. C",
        "C. Alternate site, storage and telecommunications", "docs/01 5, docs/03",
        "And where would it run instead? Discovery found resources in a second region; I "
        "will read back what it found.",
        "The standby region",
        "infrastructure owner", "nist",
        seedable=True, seed_operation="ListDrProtectionGroups",
        guidance="Where discovery finds standby resources in a region nobody names as the "
                 "standby, that is a shadow estate and worth surfacing before the interview "
                 "moves on.",
        nist_heading="APPENDIX F ALTERNATE STORAGE, SITE, AND TELECOMMUNICATIONS",
        nist_source=_A3,
    ),
    Question(
        "infra.measured_rtt_ms", "infra", "Beyond NIST",
        "Cost model and posture economics", "docs/03-replication-matrix.md",
        "Has anyone measured the round-trip time between the two regions, as opposed to "
        "reading the published figure? What did it come out at, and when?",
        "Measured inter-region round-trip time in milliseconds",
        "lead engineer", "ours", kind="number", unit="ms", mechanism_required=True,
        guidance="Measured, not published. A synchronous design over an unmeasured link has "
                 "an unexploded assumption in the middle of it.",
    ),
    Question(
        "infra.replication", "infra", "4.2", "4.2 Recovery procedures",
        "docs/03-replication-matrix.md",
        "For each tier, how does the data get to the other region, is it synchronous, and "
        "what is the measured lag? Then: when you fail back, do you have to re-baseline?",
        "Per tier: the replication mechanism, whether it is synchronous, measured lag, "
        "failover behaviour, whether reversal needs a re-baseline, and whether it is one-way",
        "infrastructure owner", "nist", kind="rows",
        columns=("tier", "mechanism", "sync", "measured_lag", "failover_behaviour",
                 "rebaseline_on_reversal", "one_way"),
        seedable=True, seed_operation="ListVolumeGroupReplicas",
        guidance="Press the re-baseline question. It is the failback cost and it is almost "
                 "never costed.",
        nist_heading="3.4.1 Backup and Recovery", nist_source=_CH3,
    ),
    Question(
        "infra.standby_cost_floor", "infra", "Beyond NIST",
        "Cost model and posture economics", "docs/05-cost-and-teardown.md",
        "What does the standby cost to keep running when nothing is happening? The floor, "
        "not the average.",
        "The monthly standby cost floor",
        "infrastructure owner", "ours", kind="currency", mechanism_required=True,
        guidance="The tier the business chose may be unaffordable at the floor. Now is when "
                 "that conversation is cheap.",
    ),
    Question(
        "infra.region_locked_naming", "infra", "Beyond NIST",
        "Cost model and posture economics", "docs/01-architecture.md 1",
        "Do any hostnames, connection strings or certificates have the region baked into "
        "them? What would have to change on failover?",
        "Which names are region-locked and what changing them costs in recovery time",
        "infrastructure owner", "ours", kind="narrative", readback_required=True,
        guidance="Often the single largest RTO lever, and cheaper than more capacity.",
    ),
    Question(
        "infra.last_end_to_end_execution", "infra", "App. J",
        "J. Test, training and exercise documentation", "runbooks/RB-04-dr-drill.md",
        "When did anyone last run this end to end, and who ran it?",
        "The date of the last end-to-end execution and who performed it",
        "lead engineer", "nist", kind="date",
        guidance="'Never' is common and acceptable. Record it; it calibrates how much every "
                 "duration in the plan can be trusted. Record who ran it, too: one name "
                 "means the runbook has an availability requirement on a person.",
        nist_heading="APPENDIX J TEST AND MAINTENANCE SCHEDULE", nist_source=_A3,
    ),
    # ------------------------------------------------ continuity.* - DR process owner
    Question(
        "continuity.declaration_authority", "continuity", "3.1",
        "3.1 Activation criteria and procedure; who may activate",
        "runbooks/RB-02-failover.md 0, checklists/dr-authority-matrix.md",
        "If this broke at two in the morning and somebody had to say 'we are failing over', "
        "who says it? And if they do not answer?",
        "The single individual with declaration authority, and their named deputy",
        "DR process owner", "nist", readback_required=True,
        guidance="Exactly one individual, and one named deputy. Not 'the incident team', "
                 "which is nobody, and not a rota, which is not a name.",
        nist_heading="4.2.1 Activation Criteria and Procedure", nist_source=_CH4,
    ),
    Question(
        "continuity.succession", "continuity", "2.3", "2.3 Roles and responsibilities",
        "checklists/roles-and-responsibilities.md",
        "If the first person does not answer, who is next? And after them? Keep going until "
        "you reach someone who is always reachable.",
        "The ordered line of succession and what each hand-off waits for",
        "DR process owner", "nist", kind="rows",
        columns=("order", "role", "passes_after"), readback_required=True,
        guidance="Must terminate in someone always reachable. Must agree with the Phase 0 "
                 "deputy roster; a disagreement is a conflict with a named decision owner, "
                 "never a silent preference for one list.",
        nist_heading="2.3 Roles and Responsibilities", nist_source=_A3,
    ),
    Question(
        "continuity.activation_criteria", "continuity", "3.1",
        "3.1 Activation criteria and procedure; who may activate",
        "runbooks/RB-02-failover.md 0",
        "What would you have to see, at three in the morning, to know this is a failover and "
        "not a bad hour?",
        "The activation criteria, each one observable",
        "DR process owner", "nist", kind="narrative", readback_required=True,
        guidance="Comparisons against something knowable at 3am, not feelings.",
        nist_heading="3.1 Activation Criteria and Procedure", nist_source=_A3,
    ),
    Question(
        "continuity.decision_time_budget", "continuity", "3.1",
        "3.1 Activation criteria and procedure; who may activate",
        "checklists/dr-authority-matrix.md",
        "How long may the decision itself take before the delay is the problem?",
        "The time budget for the declaration decision",
        "DR process owner", "ours", kind="duration", unit="minutes",
        mechanism_required=True,
        guidance="Deciding is on the recovery critical path and is almost never budgeted. "
                 "Whatever the number is, it comes out of the MTD.",
    ),
    Question(
        "continuity.unknown_estimate_default", "continuity", "3.3",
        "3.3 Outage assessment", "checklists/outage-assessment.md",
        "If nobody can say how long the repair will take, do you declare or do you wait?",
        "The default action when the repair estimate is unknown",
        "DR process owner", "ours", kind="enum", options=("declare", "wait"),
        readback_required=True,
        guidance="Declare, or wait? Nobody has answered this. Decide it in daylight.",
    ),
    Question(
        "continuity.call_tree", "continuity", "3.2", "3.2 Notification",
        "checklists/contact-roster.md",
        "Once it is declared, who gets told, in what order, and by whom? What happens when "
        "one of them does not pick up?",
        "The call tree, its order, and the unreachable procedure",
        "DR process owner", "nist", kind="narrative", readback_required=True,
        guidance="The unreachable branch is the half that gets skipped and the half that "
                 "gets used.",
        nist_heading="3.2 Notification", nist_source=_A3,
    ),
    Question(
        "continuity.bridge", "continuity", "3.2", "3.2 Notification",
        "checklists/contact-roster.md",
        "Where does everyone gather to work the incident, and what does joining it depend "
        "on?",
        "The incident bridge and its dependencies",
        "DR process owner", "ours",
        guidance="Check what it depends on. A bridge that authenticates through the failed "
                 "estate is a plan with a loop in it.",
    ),
    Question(
        "continuity.assessment_procedure", "continuity", "3.3", "3.3 Outage assessment",
        "checklists/outage-assessment.md",
        "Who works out how bad it is, and how do they produce a repair estimate the person "
        "declaring can act on?",
        "The outage assessment procedure and where the repair estimate comes from",
        "DR process owner", "nist", kind="narrative", readback_required=True,
        guidance="Where the repair estimate the activation criteria consume comes from.",
        nist_heading="3.3 Outage Assessment", nist_source=_A3,
    ),
    Question(
        "continuity.escalation_thresholds", "continuity", "4.3",
        "4.3 Recovery escalation and notification", "docs/09 5",
        "Once recovery is running, what would tell a tired person at 4am that it is going "
        "badly enough to wake someone more senior?",
        "The escalation thresholds, each observable",
        "DR process owner", "nist", kind="narrative", readback_required=True,
        guidance="Observable at 3am by a tired person. 'When it feels wrong' is not one.",
        nist_heading="4.3 Recovery Escalation Notices/Awareness", nist_source=_A3,
    ),
    Question(
        "continuity.deactivation_authority", "continuity", "5.10", "5.10 Deactivation",
        "docs/10 4.2",
        "Who says it is over, and what do they have to see before they can say it?",
        "Who may deactivate the plan and on what evidence",
        "DR process owner", "nist", readback_required=True,
        guidance="Declaration and deactivation are a matched pair.",
        nist_heading="5.10 Deactivation", nist_source=_A3,
    ),
    # ---------------------------------------- governance.* - governance / risk / audit
    Question(
        "governance.signing_authority", "governance", "Plan Approval",
        "Plan Approval statement", "docs/00-plan-approval.md",
        "Who signs this plan, and who signs it if they are away for a month?",
        "The signatory and the alternate signatory",
        "signing authority", "nist", readback_required=True,
        guidance="The signatory and the alternate signatory. A plan that can only be "
                 "approved by one reachable person cannot be reapproved after a material "
                 "change while they are away.",
        nist_heading="Plan Approval", nist_source=_A3,
    ),
    Question(
        "governance.review_cadence", "governance", "App. J",
        "J. Test, training and exercise documentation", "README.md",
        "How often does this get reviewed, what else triggers a review, and whose job is it "
        "to start one?",
        "Review frequency, the triggers, and the owner of the review",
        "governance/risk contact", "nist",
        guidance="Frequency AND triggers AND an owner. An unowned cadence does not happen.",
        nist_heading="APPENDIX J TEST AND MAINTENANCE SCHEDULE", nist_source=_A3,
    ),
    Question(
        "governance.training_programme", "governance", "App. J",
        "J. Test, training and exercise documentation",
        "checklists/contingency-training.md",
        "Separately from drills: how does someone new become competent to do their part of "
        "this?",
        "The training programme, distinct from the drill programme",
        "governance/risk contact", "nist", kind="narrative", readback_required=True,
        guidance="Distinct from drills. Drills exercise the plan; training makes individuals "
                 "competent. Auditors check for both.",
        nist_heading="3.5.2 Training", nist_source=_CH3,
    ),
    Question(
        "governance.finding_to_change_route", "governance", "Beyond NIST",
        "Plan review and maintenance cadence", "README.md",
        "A drill finds something wrong. What happens to that finding, and who closes it?",
        "The route from a drill finding to a change in the plan",
        "governance/risk contact", "ours", kind="narrative", readback_required=True,
        guidance="If there is no route, the drills are theatre.",
    ),
    Question(
        "governance.risk_register", "governance", "Beyond NIST", "Risk register",
        "checklists/risk-register.md",
        "What are you assuming for this to work, that you would not want to discover was "
        "wrong during an outage? Take them one at a time.",
        "Each material assumption or design risk, its owner and its review date",
        "governance/risk contact", "ours", kind="rows",
        columns=("risk", "owner", "review_date", "mitigation"),
        guidance="Material assumptions and design risks, owned and reviewed rather than "
                 "scattered.",
    ),
    # ---------------------------------------- discovery.* - written only by itscp-discover
    Question(
        "discovery.completed", "discovery", "App. H",
        "H. Hardware, software and firmware inventory", "docs/11-inventory.md",
        "Not asked. Set by itscp-discover when a read-only walk completes.",
        "Whether a discovery walk has run, and when",
        "infrastructure owner", "nist", kind="date",
        confidence_required=False,
        seedable=True, seed_operation="ListCompartments",
        guidance="Set by itscp-discover. Never written by an interview.",
        nist_heading="APPENDIX H HARDWARE AND SOFTWARE INVENTORY", nist_source=_A3,
    ),
)


#: The starter field set, and the denominator ``itscp-build`` reports against today. It is a
#: subset of the bank, not the whole of it: the bank grows as elicitation gets more complete,
#: and ``itscp-build`` rule 2 already says a plan reports against its own counted total
#: rather than a quoted one. ``templates/answers.example.toml`` emits exactly these.
STARTER_KEYS: tuple[str, ...] = tuple(question.id for question in QUESTIONS)

BY_ID: dict[str, Question] = {question.id: question for question in QUESTIONS}

#: Every section a question feeds, in bank order, de-duplicated.
SECTIONS: tuple[str, ...] = tuple(dict.fromkeys(question.section for question in QUESTIONS))


def question(question_id: str) -> Question | None:
    """The question with this id, or ``None``. Never raises, never invents."""
    return BY_ID.get(question_id)


def for_section(section: str) -> list[Question]:
    """Questions feeding one section, in bank order. ``section`` is matched exactly."""
    return [entry for entry in QUESTIONS if entry.section == section]


def for_namespace(namespace: str) -> list[Question]:
    """Questions one skill owns, in bank order. See :data:`NAMESPACES` for who owns what."""
    return [entry for entry in QUESTIONS if entry.namespace == namespace]


def row_questions() -> list[Question]:
    """The list-of-map questions, which the emitter writes as TOML arrays of tables."""
    return [entry for entry in QUESTIONS if entry.kind == "rows"]


def seedable_questions() -> list[Question]:
    """Questions discovery may prefill, for the interview to read back and correct."""
    return [entry for entry in QUESTIONS if entry.seedable]


def structural_provenance_counts() -> dict[str, int]:
    """How many questions sit in each class of ``docs/ITIL-GROUNDING.md`` section 4.3."""
    counts = dict.fromkeys(STRUCTURAL_PROVENANCE, 0)
    for entry in QUESTIONS:
        counts[entry.structural_provenance] += 1
    return counts
