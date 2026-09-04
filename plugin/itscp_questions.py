"""DATA ONLY: the ITSCP question bank, one entry per key in the answer store.

Every key in ``templates/answers.example.yaml`` maps to exactly one :class:`Question` here,
and nothing else may be written to the store. The bank is the schema: there is no separate
schema file, because a second copy of the field list is a second thing to drift.

Read alongside:

* ``skills/_method/answer-store.md`` for the record shape, the namespace ownership rules and
  the seven-role owner vocabulary.
* ``skills/_method/interview-method.md`` for the Iron Rule, the status lattice, the confidence
  rubric and the closed provenance list.
* ``docs/ITIL-GROUNDING.md`` §4 for the structural-provenance partition that
  :attr:`Question.structural_provenance` implements, and the rule that ``crosswalk`` may
  never justify a field on its own. §4.3 recommended three classes; §4.3a records the fourth,
  ``method``, and why the three did not cover the toolkit's own templated content.

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

#: The structural-provenance classes: the three of ``docs/ITIL-GROUNDING.md`` §4.3 and the
#: fourth of §4.3a. ``crosswalk`` is annotation only, see :data:`CROSSWALK_NEVER_JUSTIFIES`;
#: ``method`` is the toolkit's own templated content, see
#: :data:`METHOD_IS_NEVER_A_CUSTOMER_CLAIM`.
STRUCTURAL_PROVENANCE: tuple[str, ...] = ("nist", "ours", "crosswalk", "method")

#: The load-bearing rule of §4.3, stated once so the test that enforces it can quote it.
CROSSWALK_NEVER_JUSTIFIES = (
    "A crosswalk annotation may only attach to an element a nist or ours class already "
    "justified. It can never be the reason a field exists. Without this rule, 'ITIL says we "
    "need X' becomes a route by which an unread paywalled standard smuggles invented "
    "requirements into a generated plan."
)

#: The rule of §4.3a, stated once so the tests and the renderer can both quote it.
#:
#: ``ours`` and ``method`` are near neighbours and the difference is the whole point of
#: splitting them. ``ours`` means this project chose to carry an element no standard gives it
#: a slot for, and the answer in that element still came from an interview. ``method`` means
#: the toolkit supplied the words. A reader who cannot tell the two apart cannot tell what
#: the customer actually said, which is the failure the whole partition exists to prevent.
METHOD_IS_NEVER_A_CUSTOMER_CLAIM = (
    "Method content is templated text the toolkit supplies. It must be identifiable as the "
    "toolkit's in the rendered document, and it may never be presented as something a "
    "customer said. It renders as structural text under its own heading and never as an "
    "answer, because an answer segment is the claim that a person or a read-only API "
    "produced the words."
)

#: The two markers §4.3 permits on an ITIL or ISO term, and never an unmarked ITIL claim.
#: ``[glossary]`` for the six terms quotable from the one readable source; the other for
#: everything else, which may be used but never quoted.
CROSSWALK_MARKERS: tuple[str, ...] = ("[glossary]", "(practice guide; not verified)")

#: Answer kinds.
#:
#: ``rows`` is a list of maps, which the emitter writes as a TOML array of tables.
#: :func:`row_questions` returns them; their number is counted there and never quoted here.
#:
#: ``narrative`` is a multi-paragraph answer and is a first-class value, not a long ``text``.
#: The reference plan this toolkit has to reproduce is mostly narrative: design rationale,
#: architecture assumptions, why one topology was chosen over another. Those came from a
#: human working through their understanding against sources, which is an interview answer
#: with ordinary provenance, so a narrative carries provenance, confidence, mechanism,
#: supersede history and conflicts exactly as a scalar does. The one thing it carries in
#: addition is a read-back: see :attr:`Question.readback_required`.
#: Six further kinds come from surveying the reference plan this toolkit has to reproduce.
#: That survey found 51 distinct value shapes across its 30 files and 6,481 lines; 25 fitted
#: the nine kinds above and the other 26 collapsed into these six families. ``code`` is in
#: use, on the question that asks for the recovery procedure at the level of what is actually
#: typed. The other five are declared so that adding the questions that need them is data:
#:
#: ``code``
#:     An exact-fidelity block: shell, SQL, a configuration stanza, Terraform, a formula
#:     with its worked example. Reproduced byte for byte or not at all. Dictated by a lead
#:     engineer or taken from a file, so ordinary provenance covers it.
#: ``diagram``
#:     Nodes and edges, participants and messages, states and transitions, bars and
#:     durations. Elicited as structure; the layout is the renderer's problem.
#: ``citation``
#:     A source record: title, publisher, version, date accessed, and what it supports. Also
#:     the negative form, recording a source that could not be read and what was used
#:     instead, which is the one the reference plan most needs and least has.
#: ``blank``
#:     A cell deliberately left empty, which is a value and not an unanswered question. A
#:     cost template with elicited row labels and empty rates is complete; a signature block
#:     with no signature is correct until it is signed.
#: ``range``
#:     A compound scalar that is meaningless split: a rehearsed duration range, a warning
#:     and critical threshold pair, a cadence with a per-tier override, a measurement that
#:     has to carry whether it was measured or published.
#: ``reference``
#:     A pointer that must resolve: an identifier used elsewhere, a role name shared across
#:     files, a cross-reference to another document's section. A typo here breaks something
#:     silently, which plain text does not imply.
KINDS: tuple[str, ...] = (
    "text", "narrative", "duration", "number", "currency", "enum", "list", "rows", "date",
    "code", "diagram", "citation", "blank", "range", "reference",
)

#: The kinds that yield a figure, and therefore the kinds that owe a mechanism. Named here
#: rather than repeated at each use, because the set is the definition of "a figure" and the
#: store, the bank and the tests all have to agree on it.
FIGURE_KINDS: tuple[str, ...] = ("duration", "number", "currency")

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

    ``mechanism_prompt`` is the paired question that produces what the flag demands. The flag
    alone can only refuse a figure that arrived without an explanation; it cannot elicit one,
    because nothing asks. The follow-up sits on the same record as the figure it explains,
    which is where the store keeps the mechanism, so the two cannot be separated by an edit
    to one of them. ``mechanism_required`` and a non-empty ``mechanism_prompt`` are the same
    condition, and a test asserts it in both directions.

    ``figure_columns`` is the table-shaped form of that pairing: it maps a column holding a
    target or a threshold to the column that says what breaks against it. It is declarative
    rather than inferred, because a column name does not say whether a duration in it is a
    target somebody has to meet or an elapsed time somebody measured. Only the first owes an
    explanation, and inventing one for the second would fill a plan with cells nobody can
    answer.

    ``seedable`` is the answer to picoagent's open question 5. True means discovery may
    prefill the field and the interview reads it back for correction rather than asking
    cold; the prefill carries provenance ``oci-discovery:<seed_operation>``. False means the
    field is asked independently, and a discovery value that disagrees lands in ``conflict``,
    never in ``value``.

    ``structural_provenance`` is the §4.3 class. ``nist`` fields carry the verbatim NIST
    heading in ``nist_heading``; ``ours`` and ``method`` fields carry the empty string and
    claim nothing. ``crosswalk`` is legal in the enum and illegal on a question, which is the
    point of it.

    ``method_statement`` carries the templated text a ``method`` field's element consists of,
    and is empty on every other class. The text lives in the bank rather than in the renderer
    because the renderer may only write strings a corpus already holds, and because an
    element the toolkit supplies has to be readable beside the question that parameterises it.
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
    mechanism_prompt: str = ""
    figure_columns: dict[str, str] = field(default_factory=dict)
    readback_required: bool = False
    seedable: bool = False
    seed_operation: str = ""
    nist_heading: str = ""
    nist_source: str = ""
    crosswalk_note: str = ""
    method_statement: str = ""


# --------------------------------------------------------------- transcribed NIST headings
#
# NIST SP 800-34 Rev. 1 is a US government publication and is free to reproduce. These are
# transcriptions, not paraphrases: every string below was read off the published text at
# nvlpubs.nist.gov and is reproduced with NIST's own capitalisation, spacing and punctuation.
# Where the template's table of contents and its body disagree, the body wins and the
# disagreement is recorded in NIST_DISCREPANCIES.

#: Appendix A.3, Sample Template for High-Impact Systems. The moderate template (A.2) shares
#: this lettering; the low template (A.1) has no Appendix F and letters G through M one
#: lower, which :func:`_low_impact_headings` derives rather than restating.
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

#: The impact levels FIPS PUB 199 defines, and the three sample templates NIST publishes one
#: for each of: A.1 low, A.2 moderate, A.3 high.
IMPACT_LEVELS: tuple[str, ...] = ("low", "moderate", "high")

#: The key the categorisation is recorded under. Named once, because the lettering, the
#: renderer and the tests all have to read the same field.
IMPACT_LEVEL_KEY = "system.impact_level"

_APPENDIX = "APPENDIX "

#: The one appendix the low-impact template does not have. Everything after it in A.2 and A.3
#: letters one lower in A.1, and that single omission is the whole of the difference between
#: the two lettering schemes. Recorded in :data:`NIST_DISCREPANCIES` under "App. C" ("NIST
#: letters this F in the moderate and high templates and omits it entirely from the low
#: template") and under "App. K" ("K is right only for the low-impact template").
ABSENT_FROM_THE_LOW_TEMPLATE = "ALTERNATE STORAGE, SITE, AND TELECOMMUNICATIONS"


def _appendix_title(heading: str) -> str:
    """The words after ``APPENDIX <letter> ``, or the empty string for a section heading."""
    if not heading.startswith(_APPENDIX):
        return ""
    return heading.split(" ", 2)[2]


def _low_impact_headings() -> tuple[str, ...]:
    """A.1's headings, derived from A.3's rather than transcribed a second time.

    Derived because the difference between the two templates is one omission and a shift,
    and a second transcription would be a second thing to keep right. The section headings
    are identical in all three templates, so only the appendices move.
    """
    headings: list[str] = []
    letter = ord("A")
    for heading in NIST_A3_HEADINGS:
        title = _appendix_title(heading)
        if not title:
            headings.append(heading)
        elif title != ABSENT_FROM_THE_LOW_TEMPLATE:
            headings.append(f"{_APPENDIX}{chr(letter)} {title}")
            letter += 1
    return tuple(headings)


#: Appendix A.1, Sample Template for Low-Impact Systems. Runs A to L.
NIST_A1_HEADINGS: tuple[str, ...] = _low_impact_headings()

_APPENDIX_TITLES: frozenset[str] = frozenset(
    title for title in map(_appendix_title, NIST_A3_HEADINGS) if title)


def heading_in_scheme(nist_heading: str, impact_level: str) -> str:
    """The heading this element carries in the template ``impact_level`` selects.

    A section heading is returned unchanged: NIST numbers 1.1 to 5.10 the same way in all
    three templates. An appendix is re-lettered, and comes back as the empty string when the
    selected template has no appendix for it at all, which for the low-impact template is
    exactly one element.

    Raises rather than defaulting when the level is not one of the three. An uncategorised
    system has no template, and picking one on its behalf is the guess the toolkit exists to
    refuse; the caller decides what an unstated categorisation renders as.
    """
    if impact_level not in IMPACT_LEVELS:
        raise ValueError(
            f"{impact_level!r} is not one of {', '.join(IMPACT_LEVELS)}. The appendix letter "
            f"is a function of the categorisation, and a system nobody has categorised has "
            f"no letter rather than a default one."
        )
    title = _appendix_title(nist_heading)
    if not title:
        return nist_heading
    if title not in _APPENDIX_TITLES:
        raise ValueError(f"{title!r} is not an appendix of any of NIST's three templates")
    scheme = NIST_A1_HEADINGS if impact_level == "low" else NIST_A3_HEADINGS
    lettered = [heading for heading in scheme if _appendix_title(heading) == title]
    return lettered[0] if lettered else ""


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
NIST_CORPUS: frozenset[str] = (frozenset(NIST_A3_HEADINGS) | frozenset(NIST_A1_HEADINGS)
                               | frozenset(NIST_CHAPTER_HEADINGS))


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

#: The templated text of the ``method`` elements. Each is the toolkit's own approach, stated
#: once here so that the questions which parameterise it and the documents which render it
#: quote the same words. None of it is elicited and none of it is transcribed from anything;
#: see :data:`METHOD_IS_NEVER_A_CUSTOMER_CLAIM`.
_MTD_DECOMPOSITION = (
    "Maximum tolerable downtime is recovery time plus work recovery time. The toolkit "
    "decomposes it that way so that a recovery which meets its technical target and still "
    "misses what the business can tolerate is visible on paper rather than at four in the "
    "morning."
)

_POSTURE_MODEL = (
    "A standby is held in one of a small number of postures, and the posture is a decision "
    "about cost against readiness rather than a property of the estate. The toolkit asks "
    "what is done to the standby when nothing is happening, what is done when there is "
    "warning, and who may change it. A posture nobody may change is a cost nobody may "
    "reduce; a posture anybody may change is a recovery nobody can rely on."
)

_ONE_WAY_DOOR = (
    "Some decisions in a continuity design cost a change ticket to undo and some cannot be "
    "undone at all without rebuilding from nothing. The toolkit separates the two and costs "
    "the second kind before it is taken, because otherwise the moment a one-way door is "
    "noticed is the moment somebody has already walked through it to save money."
)

_DRILL_LEVELS = (
    "An exercise proves one of three things and rarely all three: that the plan reads "
    "correctly, that the steps run, or that the business can work afterwards. The toolkit "
    "asks which level each exercise reaches and what it therefore leaves unproven, because a "
    "plan whose only evidence is a reading has never been shown to work."
)

_DUTY_CROSSWALK = (
    "The toolkit names duties, not posts. It asks who decides to declare, who runs the "
    "recovery, who authorises the spending and who says it is over, and it maps those "
    "answers onto the roles this plan already uses. A standard's own post names are supplied "
    "by the standard and never by the person being interviewed, because a question that "
    "names a post supplies the answer it was asked to elicit."
)

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
    Question(
        "system.impact_level", "system", "1.2", "1.2 Scope",
        "README.md, docs/02-mtd-tiers.md, docs/07-standards-alignment.md",
        "Of low, moderate and high, which one is this system's availability impact? Not what "
        "you would choose today: what is written down. If nothing is, say so and we record "
        "that.",
        "The assigned availability impact level, which selects the template this plan is "
        "graded against",
        "governance/risk contact", "nist", kind="enum", options=IMPACT_LEVELS,
        readback_required=True,
        guidance="Three answers are legal and 'nobody ever assigned one' is not among them: "
                 "an uncategorised system leaves this MISSING with the governance contact "
                 "owing it, which is the honest record and the finding an auditor wants. The "
                 "answer decides which of NIST's three sample templates the plan is graded "
                 "against, and therefore what letter each of its appendices carries. "
                 "Uncategorised, the plan keeps the high-impact lettering, because that "
                 "template is the superset and an auditor with no stated level grades "
                 "against it.",
        nist_heading="1.2 Scope", nist_source=_A3,
    ),
    Question(
        "system.assumptions", "system", "1.3", "1.3 Assumptions",
        "docs/01-architecture.md, checklists/risk-register.md",
        "What are we taking as read about this estate that I have not asked you about "
        "directly? Take them one at a time, and for each one tell me what changes if it "
        "turns out to be wrong.",
        "Each stated assumption, what breaks if it is wrong, who confirms it and by when",
        "lead engineer", "nist", kind="rows",
        columns=("assumption", "impact_if_wrong", "owner", "confirm_by"),
        readback_required=True,
        guidance="An assumption is a fact nobody confirmed, so every row here is a question "
                 "somebody did not get asked. Read each one back. The owner and the date are "
                 "not decoration: a table of unowned assumptions is a list of things that "
                 "will still be assumptions at the next review, and one of them will be the "
                 "one that was wrong.",
        nist_heading="1.3 Assumptions", nist_source=_A3,
    ),
    Question(
        "system.component_terms", "system", "2.1", "2.1 System description",
        "docs/01-architecture.md",
        "You used a few words for parts of this that could mean more than one thing. Tell me "
        "what each of them means here, in your words, before I draw anything.",
        "The words this organisation uses for its own components, and what each one means",
        "application owner", "ours", kind="narrative", readback_required=True,
        guidance="One word that means two things is the cheapest catastrophic mistake in a "
                 "continuity design: a whole section gets written for the wrong layer and "
                 "reads perfectly well. Ask before drawing, not after. If they cannot say, "
                 "that is a MISSING with the application owner's name on it, not a guess.",
    ),
    Question(
        "system.releases", "system", "2.1", "2.1 System description",
        "docs/01-architecture.md, docs/11-inventory.md",
        "What release is the application on, exactly, and what release is the database? If "
        "you are part way through an upgrade, tell me both.",
        "The release of each major component, and any upgrade in flight",
        "application owner", "nist", readback_required=True,
        guidance="Say the numbers back. This is the fact most often carried as an assumption "
                 "and it changes recovery mechanics more than almost anything else. A "
                 "half-finished upgrade is the answer that matters most and the one people "
                 "forget to mention.",
        nist_heading="2.1 System Description", nist_source=_A3,
    ),
    Question(
        "system.operating_systems", "system", "2.1", "2.1 System description",
        "docs/01-architecture.md, docs/11-inventory.md",
        "What does each tier run on? And if any of it is a platform your recovery scripts "
        "would have to be written differently for, say so now.",
        "The operating system of each tier, and what that constrains",
        "infrastructure owner", "nist", readback_required=True,
        guidance="Decides what language every recovery script is written in, and therefore "
                 "who can run it at three in the morning. Read it back.",
        nist_heading="2.1 System Description", nist_source=_A3,
    ),
    Question(
        "system.instances", "system", "2.1", "2.1 System description",
        "docs/01-architecture.md, docs/02-mtd-tiers.md",
        "Is this one production instance, or several? Separate ledgers, separate legal "
        "entities, anything split across sites?",
        "Whether the production estate is one instance or several, and how they are split",
        "application owner", "nist", kind="narrative", readback_required=True,
        guidance="A second instance nobody mentioned changes the tier map, the recovery "
                 "order and the cost. Ask it early and read the answer back.",
        nist_heading="2.1 System Description", nist_source=_A3,
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
        mechanism_prompt="What happens at that hour that does not happen at the hour before "
                         "it? Name the deadline, the cut-off, the batch that has to run, or "
                         "the person who picks up the phone.",
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
        mechanism_prompt="What is in those minutes that nobody could rebuild from anywhere "
                         "else, and who finds out first that it is gone?",
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
        columns=("process", "workaround", "sustainable_for", "what_fails_first"),
        figure_columns={"sustainable_for": "what_fails_first"},
        mechanism_prompt="When each of those workarounds runs out, what is the first thing "
                         "that fails, and who notices it?",
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
    Question(
        "business.tier_targets", "business", "App. K", "K. Business impact analysis",
        "docs/02-mtd-tiers.md",
        "For each recovery tier you have: how long may it be down in total, how long may the "
        "technical recovery take, how long does the business need afterwards before it can "
        "work, and how much data may be lost? And what is the least service that still counts "
        "as trading?",
        "Per tier: maximum tolerable downtime, recovery time, work recovery time, recovery "
        "point and the minimum service that counts as trading",
        "business owner", "method", kind="rows",
        columns=("tier", "mtd", "rto", "wrt", "rpo", "minimum_service",
                 "what_breaks_at_the_mtd"),
        figure_columns={"mtd": "what_breaks_at_the_mtd"},
        mechanism_prompt="For each tier, what happens at that hour and not the hour before "
                         "it? Name the deadline, the cut-off or the person who calls.",
        method_statement=_MTD_DECOMPOSITION, readback_required=True,
        guidance="One table, filled a row at a time, and the last column is the one that "
                 "makes the rest worth having. A tier ladder of round numbers with nothing "
                 "behind them is the single most common defect in a continuity plan: it "
                 "reads as a measurement and it is a preference. Do not accept a figure "
                 "until the row beside it says what it collides with.",
    ),
    Question(
        "business.tier_assignment", "business", "App. K", "K. Business impact analysis",
        "docs/02-mtd-tiers.md, checklists/tier-assignment-workshop.md",
        "I am going to read you back what this system does. Sort each one into the tiers we "
        "just defined, and argue with me where it does not fit.",
        "Each business process, the tier it is assigned to, and the argument for it",
        "business owner", "nist", kind="rows",
        columns=("process", "tier", "rationale"),
        guidance="The impact question asks what stops. This one asks the business to commit. "
                 "They are different sessions and people answer them differently: 'it is "
                 "critical' survives the first and does not survive the second. Record the "
                 "argument, not just the letter, because the argument is what gets "
                 "re-examined when the cost lands.",
        nist_heading="3.2.3 Identify System Resource Recovery Priorities", nist_source=_CH3,
        crosswalk_note="ITIL calls this session a business impact analysis [glossary]",
    ),
    Question(
        "business.freeze_periods", "business", "Beyond NIST",
        "Periods when recovery is more expensive than the outage",
        "checklists/dr-authority-matrix.md, docs/08-phase-activation.md",
        "Are there weeks in the year when failing over would be worse than staying down? "
        "Period close, year end, a filing deadline?",
        "Each period when failing over costs more than the outage, and who decides during it",
        "business owner", "ours", kind="rows",
        columns=("period", "why", "who_decides"), readback_required=True,
        guidance="Nobody volunteers this and everybody has one. It changes the activation "
                 "criteria for a fortnight a quarter, which is when the plan is most likely "
                 "to be used and least likely to have been read.",
    ),
    Question(
        "business.freeze_override_authority", "business", "Beyond NIST",
        "Periods when recovery is more expensive than the outage",
        "checklists/dr-authority-matrix.md",
        "If we were inside one of those periods and had to fail over anyway, who is allowed "
        "to say yes, and what do they need in front of them first?",
        "Who may authorise a failover inside a freeze period, and on what evidence",
        "business owner", "ours", readback_required=True,
        guidance="A freeze with no override is a plan that stops working four weeks a year. "
                 "Name one individual and what they need to see; 'the board' is nobody at "
                 "two in the morning.",
    ),
    Question(
        "business.reconstruction_effort", "business", "Beyond NIST",
        "Minimum business continuity objective per tier",
        "docs/02-mtd-tiers.md, checklists/manual-workarounds.md",
        "If we lost the work from the last few minutes before the failure, how long would it "
        "take to put it back, and who would be doing it?",
        "How long rebuilding the lost work takes, and who does it",
        "business owner", "ours", kind="duration", unit="hours", mechanism_required=True,
        mechanism_prompt="What are they rebuilding it from, and what happens if that source "
                         "went down with everything else?",
        guidance="This is the recovery point objective turned into work recovery time, which "
                 "is the half of the sum that never gets costed. If the source they would "
                 "rebuild from is inside the failed estate, the answer is not a duration, it "
                 "is a design finding.",
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
        "application owner", "method", kind="rows",
        columns=("activity", "duration", "parallel_with_bringup"),
        method_statement=_MTD_DECOMPOSITION,
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
    Question(
        "app.recovery_procedures", "app", "4.2", "4.2 Recovery procedures",
        "runbooks/RB-02-failover.md, runbooks/RB-01-switchover.md",
        "Talk me through the recovery as if I were doing it and you were not there. Give me "
        "the commands, in order, exactly as you would type them.",
        "The recovery procedure at the level of what is actually typed, in order",
        "lead engineer", "nist", kind="code", readback_required=True,
        guidance="Reproduced byte for byte or not at all. A paraphrased command is worse than "
                 "no command, because it looks runnable. Where a step is a decision rather "
                 "than a keystroke, say so in the block; where a step needs a value nobody "
                 "has yet, leave the placeholder visible rather than inventing one. Read the "
                 "block back to them before it is written down.",
        nist_heading="4.2 Recovery Procedures", nist_source=_A3,
    ),
    Question(
        "app.validation_data_tests", "app", "5.2", "5.2 Validation data testing",
        "checklists/validation-pack.md, docs/10-phase-reconstitution.md",
        "Once it is back up, how would you satisfy yourself that the data is right, as "
        "opposed to the system being up? Who is the person whose word settles it?",
        "Each data validation check, what it proves and who signs it off",
        "application owner", "nist", kind="rows",
        columns=("check", "what_it_proves", "who_signs"),
        guidance="Not the same as the functional pack, and the difference is the point. A "
                 "database opening read-write proves the system is up. Only somebody who "
                 "runs the process can say the data is right, so the signature column names "
                 "a person's role and never the infrastructure team.",
        nist_heading="5.2 Validation Data Testing", nist_source=_A3,
    ),
    Question(
        "app.interface_landing", "app", "Beyond NIST",
        "Interface landing and replication of inbound data",
        "docs/12-interconnections.md",
        "Today, before we change anything: where do inbound files from other systems land, "
        "and does anything read them from somewhere that is not replicated?",
        "Where inbound interface data lands today and whether that location is replicated",
        "lead engineer", "ours", kind="narrative", readback_required=True,
        guidance="Ask what it is, not what it should be. The recommended pattern is easy to "
                 "write and useless without the current state beside it, and a design "
                 "proposal in a description's clothes is how a plan ends up recovering an "
                 "estate nobody has.",
    ),
    Question(
        "app.unsafe_reruns", "app", "Beyond NIST",
        "Interface landing and replication of inbound data",
        "runbooks/RB-02-failover.md, docs/10-phase-reconstitution.md",
        "After a failover, which scheduled jobs would be dangerous to run again, and which "
        "are safe to just resubmit?",
        "Each scheduled job, whether it is safe to resubmit, and what a second run does",
        "application owner", "ours", kind="rows",
        columns=("job", "safe_to_resubmit", "what_happens_if_it_runs_twice"),
        enum_columns={"safe_to_resubmit": ("safe", "unsafe", "nobody knows")},
        guidance="'Nobody knows' is a legal answer and a useful one: it is the list somebody "
                 "has to work through before the next drill. A job that pays suppliers twice "
                 "is a worse outage than the one that caused the failover.",
    ),
    Question(
        "app.reconfiguration_duration", "app", "Beyond NIST",
        "Measured durations on the recovery critical path",
        "docs/09-phase-recovery.md, runbooks/RB-01-switchover.md",
        "Has anyone ever timed the full reconfiguration of the application tier after a move, "
        "start to finish? What did it come out at?",
        "How long a full application-tier reconfiguration takes, measured",
        "lead engineer", "ours", kind="duration", unit="hours", mechanism_required=True,
        mechanism_prompt="Was that timed on a rehearsal or estimated from experience? And "
                         "what is the longest it has ever taken?",
        guidance="This figure usually carries the plan's whole design argument and usually "
                 "arrives as a range somebody remembers. If it has never been timed, record "
                 "that: an untimed step on the critical path is the reason the recovery "
                 "misses its target by an afternoon.",
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
        mechanism_prompt="What was running when it was measured, and at what time of day? "
                         "And at what figure would this design stop working?",
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
        columns=("tier", "mechanism", "sync", "measured_lag", "what_breaks_at_that_lag",
                 "failover_behaviour", "rebaseline_on_reversal", "one_way"),
        figure_columns={"measured_lag": "what_breaks_at_that_lag"},
        mechanism_prompt="For each tier, at what lag would you stop trusting the standby, "
                         "and what is the first thing that breaks when it reaches that?",
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
        mechanism_prompt="What is in that figure and what is not? Name the lines it covers, "
                         "and say what would have to be switched off to make it smaller.",
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
    Question(
        "infra.availability_domains", "infra", "2.1", "2.1 System description",
        "docs/01-architecture.md",
        "Within each region, which availability domains is this spread across, and where does "
        "anything that arbitrates between the two regions sit?",
        "The availability domains in use, and where any arbitrator sits",
        "infrastructure owner", "nist",
        seedable=True, seed_operation="ListAvailabilityDomains",
        guidance="Discovery can name these, so read them back rather than asking cold. The "
                 "arbitrator is the half people forget: one that sits in the primary region "
                 "is a vote that is always lost at exactly the moment it is needed.",
        nist_heading="2.1 System Description", nist_source=_A3,
    ),
    Question(
        "infra.inter_region_transport", "infra", "Beyond NIST",
        "Cost model and posture economics", "docs/01-architecture.md",
        "How does traffic get between the two regions today? A dedicated circuit, the "
        "provider's own backbone, or the public internet? And is there a bandwidth commitment "
        "anywhere in writing?",
        "How the two regions are joined and what is committed in writing",
        "infrastructure owner", "ours", kind="narrative", readback_required=True,
        guidance="Press on the writing. A replication design rests on this link, and 'it has "
                 "always been fine' is a measurement of the past. If nothing is committed, "
                 "that is a risk register row with an owner, not a footnote.",
    ),
    Question(
        "infra.storage_constraints", "infra", "Beyond NIST",
        "Cost model and posture economics",
        "docs/03-replication-matrix.md, docs/05-cost-and-teardown.md",
        "Does the data use any storage feature that only works on particular hardware? "
        "Compression, encryption at a layer below the database, anything the standby would "
        "have to match?",
        "Storage features that constrain what the standby may be built on",
        "lead engineer", "ours", kind="narrative", readback_required=True,
        guidance="A single feature here can rule out the cheap standby entirely, and it is "
                 "usually discovered after the budget is signed. Read the answer back and "
                 "record who confirmed it.",
    ),
    Question(
        "infra.shared_storage", "infra", "2.1", "2.1 System description",
        "docs/01-architecture.md",
        "What sits on shared storage that more than one node needs, and what protocol do "
        "those nodes speak to it?",
        "What lives on shared storage and how it is reached",
        "infrastructure owner", "nist", kind="narrative", readback_required=True,
        guidance="This decides a real fork in the recovery design and is usually answered by "
                 "whoever is in the room rather than by whoever knows. Ask for the protocol, "
                 "not the product.",
        nist_heading="2.1 System Description", nist_source=_A3,
    ),
    Question(
        "infra.standby_posture", "infra", "Beyond NIST",
        "Cost model and posture economics",
        "runbooks/RB-05-replication-lifecycle.md, docs/05-cost-and-teardown.md",
        "What do you do to the standby when nothing is happening? Leave it running, stop "
        "things, scale something down? And who is allowed to change that?",
        "The standby's steady-state posture and who may change it",
        "infrastructure owner", "method", kind="narrative", readback_required=True,
        method_statement=_POSTURE_MODEL,
        guidance="Two answers, and the second one matters more. A posture with no named owner "
                 "gets changed by whoever is looking at the bill that month, which is how a "
                 "standby quietly stops being one.",
    ),
    Question(
        "infra.warned_posture_time", "infra", "Beyond NIST",
        "Cost model and posture economics", "runbooks/RB-05-replication-lifecycle.md",
        "When you get warning, a storm track or an announced maintenance window, is there a "
        "readier state you move to? How long does getting there take?",
        "How long it takes to move the standby to its warned state",
        "infrastructure owner", "ours", kind="duration", unit="hours",
        mechanism_required=True,
        mechanism_prompt="What does that state cost while you are holding it, and what "
                         "decides when you come back down from it?",
        guidance="Most estates have no warned state and have never been asked for one. "
                 "NOT_APPLICABLE with a reason is a good answer here; silence is not.",
    ),
    Question(
        "infra.silent_failures", "infra", "Beyond NIST", "Alert catalogue",
        "docs/04-monitoring.md",
        "What has broken before without anyone noticing until it mattered?",
        "The failures this estate does not notice, and what would have shown them",
        "lead engineer", "ours", kind="narrative", readback_required=True,
        guidance="Ask it exactly like that and then stop talking. It is the question that "
                 "produces the alert catalogue, and it produces it as a story about something "
                 "that already happened rather than as a list of metrics somebody invented.",
    ),
    Question(
        "infra.irreversible_choices", "infra", "Beyond NIST",
        "Reversibility and one-way doors", "docs/03-replication-matrix.md",
        "Which of the choices in this design could you undo next week, and which could you "
        "not undo at all without starting again? What would undoing each one cost?",
        "Each decision that cannot be cheaply reversed, what reversing it costs and who may "
        "take it",
        "lead engineer", "method", kind="rows",
        columns=("decision", "cost_to_reverse", "who_may_take_it"),
        method_statement=_ONE_WAY_DOOR,
        guidance="Deleting a replication relationship to save money is the one everybody "
                 "finds by doing it. Ask whether it has happened here; a scar is worth more "
                 "than a warning.",
    ),
    Question(
        "infra.licensing", "infra", "Beyond NIST",
        "Cost model and posture economics", "docs/05-cost-and-teardown.md",
        "Which optional features is the standby entitled to use? And do you have that in "
        "writing rather than in somebody's memory of a call?",
        "Each optional feature the design needs, whether it is licensed and where that is "
        "recorded",
        "infrastructure owner", "ours", kind="rows",
        columns=("feature", "licensed", "where_it_is_recorded"),
        enum_columns={"licensed": ("yes", "no", "nobody knows")},
        readback_required=True,
        guidance="The line item most often discovered late, and the one the plan is least "
                 "likely to ask about. 'Nobody knows' is the most useful answer in the "
                 "column and belongs in the risk register the same day.",
    ),
    Question(
        "infra.offsite_storage", "infra", "5.7", "5.7 Offsite data storage",
        "docs/03-replication-matrix.md",
        "Where do the backups live, how long are they kept, and what would you actually do to "
        "get one back? If none of it is physical, say so.",
        "Each backup copy, where it is held, how long it is kept and how it is retrieved",
        "infrastructure owner", "nist", kind="rows",
        columns=("copy", "where_it_is_held", "retention", "how_it_is_retrieved"),
        guidance="NOT_APPLICABLE with a reason is a legitimate and common answer where "
                 "nothing is on physical media, and it is a better answer than an invented "
                 "courier. What is never legitimate is leaving retention blank: a retention "
                 "shorter than the records the business has to keep is a finding on its own.",
        nist_heading="5.7 Offsite Data Storage", nist_source=_A3,
    ),
    Question(
        "infra.post_recovery_backup", "infra", "5.8", "5.8 Data backup",
        "docs/10-phase-reconstitution.md, docs/03-replication-matrix.md",
        "Once you are running in the other region, what protects you? When does the first "
        "backup of the new primary happen, and who checks that it did?",
        "How the recovered system is protected again, when, and who confirms it",
        "infrastructure owner", "nist", kind="narrative", readback_required=True,
        guidance="The step most likely to be missed, because the system is up and everyone "
                 "goes home. Until this is done a second event is unrecoverable, so the "
                 "answer needs a name and a time attached to it, not an intention.",
        nist_heading="5.8 Data Backup", nist_source=_A3,
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
        mechanism_prompt="What is happening to the outage while that decision is being "
                         "taken, and what stops being recoverable once the budget is spent?",
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
    Question(
        "continuity.contact_roster", "continuity", "App. A", "A. Personnel contact list",
        "checklists/contact-roster.md",
        "For every role we have named: who holds it, how do I reach them out of hours, and "
        "when did anyone last ring that number and get an answer?",
        "Each role, who holds it, how they are reached and when that was last verified",
        "DR process owner", "nist", kind="rows",
        columns=("role", "held_by", "reached_by", "last_verified"),
        readback_required=True,
        guidance="The one file that must never be committed to a shared repository, and the "
                 "one that is useless if it is out of date. Press on the last column: a "
                 "roster nobody has rung is a list of numbers, not a call tree. A role with "
                 "no holder is a gap with a name on it and belongs here as MISSING rather "
                 "than being quietly left out.",
        nist_heading="APPENDIX A PERSONNEL CONTACT LIST", nist_source=_A3,
    ),
    Question(
        "continuity.vendor_contacts", "continuity", "App. B", "B. Vendor contact list",
        "checklists/contact-roster.md",
        "Which outside organisations would you have to call during this, how do you reach "
        "them out of hours, and what reference do they need you to quote before they will "
        "help?",
        "Each vendor, what they supply, how they are reached and the reference they need",
        "DR process owner", "nist", kind="rows",
        columns=("organisation", "what_they_supply", "reached_by", "reference_to_quote"),
        guidance="The reference column is the one that saves an hour. A support contract "
                 "number stored only inside the system being recovered is not a contract "
                 "number. Ask where a printed copy lives.",
        nist_heading="APPENDIX B VENDOR CONTACT LIST", nist_source=_A3,
    ),
    Question(
        "continuity.vendor_obligations", "continuity", "Beyond NIST",
        "Vendor obligations during a recovery", "checklists/contact-roster.md, "
        "checklists/risk-register.md",
        "Is anyone outside this organisation contracted to do part of this if you cannot? "
        "What does the contract actually oblige them to do, and how fast?",
        "Each external party, what their contract obliges, how fast, and where the contract "
        "is held",
        "governance/risk contact", "ours", kind="rows",
        columns=("organisation", "what_the_contract_obliges", "response_time",
                 "where_the_contract_is_held"),
        guidance="Not a NIST appendix: the templates have no heading for this and the "
                 "coverage map invented one. It is still worth asking, because a recovery "
                 "that assumes a vendor will help is a recovery resting on goodwill. If the "
                 "answer is that nobody has read the contract, record that.",
    ),
    Question(
        "continuity.decision_and_recovery_roles", "continuity", "2.3",
        "2.3 Roles and responsibilities", "checklists/roles-and-responsibilities.md",
        "Who decides to declare, who runs the recovery, who authorises spending, and who says "
        "it is over? Take them one at a time, and tell me where the same person appears "
        "twice.",
        "Each duty in a recovery, the role that holds it and the deputy behind them",
        "DR process owner", "method", kind="rows",
        columns=("duty", "held_by", "deputy"),
        enum_columns={"duty": ("decides to declare", "runs the recovery",
                               "authorises the spending", "says it is over")},
        method_statement=_DUTY_CROSSWALK, readback_required=True,
        guidance="Four duties, asked separately, because asking for one job title gets you "
                 "one name and hides the overlap. Where the same role holds two of them, say "
                 "so out loud and ask what they put down to do the other. Deciding whether "
                 "the repair estimate beats the remaining budget and running the storage "
                 "sequence are not the same work and cannot be done at the same minute.",
    ),
    Question(
        "continuity.people_unavailable", "continuity", "2.3",
        "2.3 Roles and responsibilities", "checklists/roles-and-responsibilities.md",
        "If whatever caused this also took your people, one office or one time zone, who is "
        "left who could execute this, and where are they?",
        "Who could execute the plan if the disruption also removed the primary team",
        "DR process owner", "nist", kind="narrative", readback_required=True,
        guidance="Almost never asked and almost never has an answer. 'Nobody' is the correct "
                 "answer where it is true, and it belongs in the plan as a named hole rather "
                 "than being filled in by whoever is drafting.",
        nist_heading="3.4.6 Roles and Responsibilities", nist_source=_CH3,
    ),
    Question(
        "continuity.assessment_calibration", "continuity", "3.3", "3.3 Outage assessment",
        "checklists/outage-assessment.md",
        "Last time something broke badly, how long was it before anyone could say how long it "
        "would take to fix?",
        "How long this organisation actually takes to produce a repair estimate",
        "DR process owner", "ours", kind="duration", unit="minutes",
        mechanism_required=True,
        mechanism_prompt="What were they waiting on for that long, and is that thing any "
                         "faster now?",
        guidance="Calibrates the assessment budget against what this organisation can do "
                 "rather than against what the plan would like. If the honest answer is two "
                 "hours, a ten-minute assessment step is fiction and the plan should say so.",
    ),
    Question(
        "continuity.declaration_threshold_rule", "continuity", "3.1",
        "3.1 Activation criteria and procedure; who may activate",
        "checklists/dr-authority-matrix.md",
        "Should the point at which you stop waiting be a fixed number of hours, or should it "
        "be worked out from how much of the tolerable downtime is left at that moment?",
        "How the point of no return is calculated rather than what it is today",
        "DR process owner", "ours", kind="narrative", readback_required=True,
        guidance="The default action when nobody can estimate is a separate field and this "
                 "is the rule behind it. A fixed threshold ages badly; one computed from what "
                 "is left of the budget survives a change to the tier. Ask which they want "
                 "and write down why.",
    ),
    Question(
        "continuity.data_loss_gate", "continuity", "3.1",
        "3.1 Activation criteria and procedure; who may activate",
        "checklists/dr-authority-matrix.md",
        "If you came up having lost more data than the tier allows, does downstream "
        "processing stay stopped until somebody clears it, or does it run?",
        "What happens to downstream processing when the recovery point was missed",
        "DR process owner", "ours", kind="narrative", readback_required=True,
        guidance="Decide it in daylight. In the event this is asked of whoever is nearest, "
                 "at speed, and the wrong answer pays somebody twice or fails to pay them at "
                 "all. Name who clears it.",
    ),
    Question(
        "continuity.recovery_declaration", "continuity", "5.4", "5.4 Recovery declaration",
        "docs/10-phase-reconstitution.md",
        "Who tells the business it is recovered, and what do they have to have seen before "
        "they are allowed to say it?",
        "Who declares recovery complete and the evidence they need first",
        "DR process owner", "nist", kind="narrative", readback_required=True,
        guidance="Distinct from standing the plan down. This is the moment users are told "
                 "they may work, and the evidence for it is the validation pack rather than "
                 "the infrastructure being green.",
        nist_heading="5.4 Recovery Declaration", nist_source=_A3,
    ),
    Question(
        "continuity.user_notification", "continuity", "5.5", "5.5 Notification (users)",
        "checklists/contact-roster.md, docs/10-phase-reconstitution.md",
        "How do users find out they can work again? Who sends it, through what, and what does "
        "it have to tell them?",
        "How users are told service is restored, by whom and what the message must carry",
        "DR process owner", "nist", kind="narrative", readback_required=True,
        guidance="Ask what the message has to say, not just who sends it. Users coming back "
                 "to a system that lost fifteen minutes of work need to be told that, and a "
                 "channel that runs through the recovered estate is a channel with a loop "
                 "in it.",
        nist_heading="5.5 Notifications (users)", nist_source=_A3,
    ),
    Question(
        "continuity.cleanup", "continuity", "5.6", "5.6 Cleanup",
        "docs/10-phase-reconstitution.md",
        "Once it is over, what has to be taken down or put back? And what is the thing you "
        "would most regret leaving running?",
        "What is dismantled after the event, and who is responsible for each of it",
        "DR process owner", "nist", kind="narrative", readback_required=True,
        guidance="The second half of the question finds the expensive one. Ask also what must "
                 "deliberately not be torn down: the replication that was rebuilt is the "
                 "thing most often cleaned up by somebody tidying.",
        nist_heading="5.6 Cleanup", nist_source=_A3,
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
    Question(
        "governance.event_documentation", "governance", "5.9", "5.9 Event documentation",
        "docs/00-record-of-changes.md, runbooks/RB-04-dr-drill.md",
        "After a real event, who writes down what happened, what goes in it, and where does "
        "it end up? And has that ever actually been done here?",
        "How a real event is written up, by whom, and where the record goes",
        "governance/risk contact", "nist", kind="narrative", readback_required=True,
        guidance="A drill report and an event report are different documents and most "
                 "organisations have neither. Ask the last part plainly: if it has never been "
                 "done, the answer is what the plan should say, not an intention dressed as "
                 "a procedure.",
        nist_heading="5.9 Event Documentation", nist_source=_A3,
    ),
    Question(
        "governance.associated_plans", "governance", "App. K",
        "K. Associated plans and procedures", "docs/07-standards-alignment.md, README.md",
        "What other plans does this one lean on or feed into? Anything for the building, for "
        "a security incident, for the wider business?",
        "Each related plan, who owns it and how it relates to this one",
        "governance/risk contact", "nist", kind="rows",
        columns=("plan", "owner", "how_it_relates"),
        guidance="A continuity plan that assumes a facilities plan exists, and a facilities "
                 "plan that assumes this one does, is a pair of documents each waiting for "
                 "the other. Naming the owner is what makes the assumption checkable.",
        nist_heading="APPENDIX K ASSOCIATED PLANS AND PROCEDURES", nist_source=_A3,
    ),
    Question(
        "governance.drill_cadence", "governance", "App. J",
        "J. Test, training and exercise documentation", "runbooks/RB-04-dr-drill.md",
        "How often will you actually exercise this? Not what the policy says: what you will "
        "fund and staff.",
        "How often the plan is exercised, in practice",
        "governance/risk contact", "nist", kind="duration", unit="months",
        mechanism_required=True,
        mechanism_prompt="What would have to happen for one to be skipped, and who notices "
                         "when it is?",
        guidance="Two questions in one and the second is the real one. A stricter cadence "
                 "than the organisation will fund is worse than an honest looser one, "
                 "because the plan then documents a control that does not run and an "
                 "auditor will find the gap rather than the intention.",
        nist_heading="3.5 Plan Testing, Training, and Exercises (TT&E)", nist_source=_CH3,
    ),
    Question(
        "governance.drill_levels", "governance", "Beyond NIST",
        "Drill levels and what each proves",
        "docs/06-test-environments.md, runbooks/RB-04-dr-drill.md",
        "For each exercise you run: does it prove the plan reads correctly, that the steps "
        "run, or that the business can work afterwards? And what does it leave unproven?",
        "Each exercise level, what it proves and what it does not",
        "governance/risk contact", "method", kind="rows",
        columns=("level", "what_it_proves", "what_it_does_not_prove"),
        method_statement=_DRILL_LEVELS,
        guidance="The last column is the one that gets argued about, which is why it is a "
                 "column. An organisation whose only evidence is a reading has a plan nobody "
                 "has run, and it will believe otherwise until this table is filled in.",
    ),
    Question(
        "governance.availability_boundary", "governance", "Beyond NIST",
        "Plan review and maintenance cadence", "docs/07-standards-alignment.md",
        "Who owns keeping this available day to day, and who owns getting it back after a "
        "disaster? Same person, or different?",
        "Where day-to-day availability ends and continuity begins, and who owns each side",
        "governance/risk contact", "ours", kind="narrative", readback_required=True,
        guidance="The boundary most plans raise against themselves and never close. Where it "
                 "is the same person, ask what they stop doing during a recovery; where it "
                 "is two, ask who decides which one a given incident is.",
    ),
    Question(
        "governance.plan_custody", "governance", "Plan Approval", "Plan Approval statement",
        "docs/00-plan-approval.md",
        "Where will the signed copy of this plan live? And where will it live when the thing "
        "holding it is the thing that is down?",
        "Where the approved plan is held, and where it is held when the estate is unavailable",
        "signing authority", "ours", kind="narrative", readback_required=True,
        guidance="A plan readable only from the system it recovers is a plan nobody can read "
                 "when they need it. The second half of the question is the whole question; "
                 "ask it separately and wait.",
    ),
    Question(
        "governance.breach_disclosure_clock", "governance", "Beyond NIST",
        "Risk register", "checklists/roles-and-responsibilities.md, "
        "docs/08-phase-activation.md",
        "If the cause turns out to be an attack rather than a failure, who has to be told, "
        "how fast, and whose job is that clock? Name the role, not the department.",
        "Who owns the disclosure clock when the cause is an attack, and how fast it runs",
        "governance/risk contact", "ours", kind="narrative", readback_required=True,
        guidance="A recovery driven by an attack is not only a continuity event, and this "
                 "plan has no authority over the disclosure clock. Record who does. An "
                 "unowned regulatory clock is the one gap in a continuity plan that costs "
                 "money after the service is back.",
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


#: The starter field set, and the denominator ``itscp-build`` reports against today. It is
#: every question in the bank: a plan that adds fields for its own tiers, processes or
#: interfaces reports against its own counted total, which is ``itscp-build`` rule 2.
#: ``plugin/answers.example.toml`` emits exactly these.
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
