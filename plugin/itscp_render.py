"""Render the plan repository from the answer store. A pure function of its inputs.

The anti-fabrication guarantee
------------------------------
Every byte of every generated document is one of exactly four things, and the renderer is
built so that it *cannot* produce a fifth:

``Segment("structural", ...)``
    A heading transcribed from NIST SP 800-34 Rev. 1, a phrase the question bank already
    carries, the templated text of a ``method`` element, or boilerplate this project declares
    as its own. :func:`structural_corpus` enumerates every legal string, and
    ``tests/test_render`` asserts membership rather than trusting the renderer to have been
    careful.
``Segment("answer", ...)``
    A value a person or a read-only API recorded, stringified and nothing more.
``Segment("markup", ...)``
    Markdown structure. Matches :data:`MARKUP_ONLY`, which admits no letter and no digit, so
    "the renderer cannot invent a word or a number" is a regular expression rather than a
    promise.
``Segment("annotation", ...)``
    The MISSING, low-confidence, DEFERRED, not-applicable and conflict markers.

:func:`render` returns the segments alongside the text, and
``"".join(segment.text for segment in page.segments) == page.text`` always holds.

The fourth kind
---------------
``iscp-author`` had three. The fourth is added deliberately, and it is the one that needed
approval, because a marker is neither template text nor an answer. Nothing in NIST says
``**[MISSING - owner: business owner]**``; filing it as structural would launder generated
text into transcribed text, and filing it as an answer would claim somebody said it. It is
ours, it is generated, and the document is honest only if it is labelled as such.

What keeps the fourth kind safe is that its vocabulary is closed. An annotation is not
composed here: :func:`annotation_of` returns ``itscp_store.status_marker`` minus the part of
that marker which is the value, so every annotation is a suffix of a string the store owns
and is a pure function of the record's ``status``, ``confidence``, ``owner``, ``due`` and
``reason``. :func:`conflict_note` is the one addition, derived the same way from the
record's own ``conflict``. :meth:`Writer.annotate` takes a record, never a string, so there
is no route from caller-supplied text into an annotation segment.

There is deliberately no kind meaning "the renderer wrote this". Anything that is none of
the four is a defect.

The document set
----------------
:data:`SCAFFOLD` is the tree ``skills/_method/repo-scaffold`` specifies, and which field
lands in which document is read from the question bank's own ``written_to`` map rather than
restated here. That is what makes structural completeness a property of the code instead of
a thing somebody has to remember: a field cannot name a destination that is not a file, and
a file cannot be referenced without being written.

The marker text quoted in :data:`CONFLICT_MARKER` uses the em dashes the scaffold uses, so
a conflict reads beside a MISSING marker rather than beside it in a different dialect.
"""
from __future__ import annotations

import sys

if sys.version_info < (3, 11):
    raise RuntimeError(
        "itscp-author needs Python 3.11 or newer (this is "
        f"{sys.version_info.major}.{sys.version_info.minor}). The renderer reads the answer "
        "store, which reads TOML through the standard library's tomllib, added in 3.11. "
        "There is no pip dependency to install; run the plugin under a newer interpreter."
    )

import re
from dataclasses import dataclass

import itscp_questions as bank
import itscp_store as store
from itscp_store import Record

#: The four kinds, and there is no fifth.
SEGMENT_KINDS: tuple[str, ...] = ("structural", "answer", "markup", "annotation")

#: What a markup segment may contain: anything that is not a letter and not a digit. Stated
#: as the property rather than as a list of permitted characters, because the property is
#: the guarantee and a list would need extending every time a document grew a new bracket.
MARKUP_ONLY = re.compile(r"^[^0-9A-Za-z]*$")

#: The heading a field carries when the question bank declares it ours rather than NIST's.
#: One heading and not one per field, so a reader can see at a glance which part of a
#: document this project invented and which part follows the standard.
OURS_HEADING = "Recorded for this plan"

#: The heading a ``method`` field carries. Distinct from :data:`OURS_HEADING` because the two
#: classes differ in who supplied the words, which is exactly what a reader has to be able to
#: see: under ours the element is this project's and the answer is the interviewee's; under
#: this heading the words below it are the toolkit's, and the answer parameterises them.
#: See ``itscp_questions.METHOD_IS_NEVER_A_CUSTOMER_CLAIM``.
METHOD_HEADING = "Supplied by the toolkit's method"

#: The two sections ``repo-scaffold`` says every generated document carries. Not optional.
REFERENCES_HEADING = "References"
UNVERIFIED_HEADING = "Unverified statements"

#: How a conflicted record renders: both values, both sources and the named decision owner,
#: which is what ``repo-scaffold`` requires and what ``status_marker`` does not cover.
#: The leading space is the low-confidence marker's, copied deliberately: a marker that
#: follows a value has to separate itself from it, and the store's own caveat already does.
CONFLICT_MARKER = (" **[CONFLICT — {value} ({provenance}) against {other} ({other_source}); "
                   "decision owner: {owner}]**")

#: Every sentence this project declares as its own, each named so that a writer names the
#: line it wants rather than indexing a tuple by a position somebody has to count.
GENERATED_NOTICE = ("This document is generated from the answer store. Correct it by "
                    "correcting the interview, not by editing this file.")
REFERENCES_PREAMBLE = "Sources for every value above, as recorded when the value was given."
NO_SOURCES_YET = "No value in this document has a recorded source yet."
UNVERIFIED_PREAMBLE = ("Engineering judgements, outstanding gaps and disagreements, "
                       "labelled as such.")
NOTHING_UNVERIFIED = "Every value in this document is traceable to a recorded source."
NO_FIELDS_HERE = ("No field of the answer store is written to this document. It is part of "
                  "the plan's structure and is filled by hand or by a later phase.")
RECORDED_BY = "recorded by"
MECHANISM = "mechanism"

#: Boilerplate this project declares as its own. Every string the renderer writes as
#: structural text is either here, in the question bank, or a transcribed NIST heading.
BOILERPLATE: tuple[str, ...] = (
    OURS_HEADING, METHOD_HEADING, REFERENCES_HEADING, UNVERIFIED_HEADING, GENERATED_NOTICE,
    REFERENCES_PREAMBLE, NO_SOURCES_YET, UNVERIFIED_PREAMBLE, NOTHING_UNVERIFIED,
    NO_FIELDS_HERE, RECORDED_BY, MECHANISM,
)


@dataclass(frozen=True)
class Segment:
    """One piece of the output, tagged with where it came from."""

    kind: str
    text: str


@dataclass(frozen=True)
class Figure:
    """One diagram a document embeds. Generated elsewhere; referenced here."""

    alt: str
    path: str


@dataclass(frozen=True)
class DocumentSpec:
    """One file of the generated repository, as ``repo-scaffold`` specifies it."""

    path: str
    title: str
    purpose: str
    figures: tuple[Figure, ...] = ()


@dataclass(frozen=True)
class RenderedDocument:
    """One generated file: its path, its bytes, and where every byte came from."""

    path: str
    text: str
    segments: tuple[Segment, ...]


_TIER_LADDER = Figure("Four recovery tiers plotted by maximum tolerable downtime against "
                      "relative run cost", "diagrams/tier-ladder.svg")
_MTD_TIMELINE = Figure("Recovery point objective before the incident, recovery time and "
                       "work recovery time after it", "diagrams/mtd-timeline.svg")

#: The tree ``skills/_method/repo-scaffold`` specifies, in the order it lists it.
SCAFFOLD: tuple[DocumentSpec, ...] = (
    DocumentSpec("README.md", "IT service continuity plan",
                 "What this plan covers, how to read it, and how it is kept current."),
    DocumentSpec("docs/00-plan-approval.md", "Plan approval",
                 "Who signs this plan, what they are attesting to, and when."),
    DocumentSpec("docs/00-record-of-changes.md", "Record of changes",
                 "Every revision of this plan, derived from the repository's own history."),
    DocumentSpec("docs/01-architecture.md", "Architecture",
                 "The estate this plan recovers, and the assumptions the design rests on."),
    DocumentSpec("docs/02-mtd-tiers.md", "Maximum tolerable downtime and recovery tiers",
                 "What the business can tolerate losing, and for how long.",
                 (_MTD_TIMELINE, _TIER_LADDER)),
    DocumentSpec("docs/03-replication-matrix.md", "Replication matrix",
                 "What is replicated, by which mechanism, and which choices cannot be "
                 "reversed."),
    DocumentSpec("docs/04-monitoring.md", "Monitoring and attestation",
                 "The alarms that prove the recovery point objective is being met."),
    DocumentSpec("docs/05-cost-and-teardown.md", "Cost and teardown",
                 "What the standby posture costs and what changing it costs."),
    DocumentSpec("docs/06-test-environments.md", "Test environments",
                 "What each tier of testing proves, and what it does not."),
    DocumentSpec("docs/07-standards-alignment.md", "Standards alignment",
                 "Where this plan follows a published standard and where it does not."),
    DocumentSpec("docs/08-phase-activation.md", "Phase one: activation and notification",
                 "How an incident becomes a declared disaster, and who is told."),
    DocumentSpec("docs/09-phase-recovery.md", "Phase two: recovery",
                 "The order things are brought back, and who escalates when they are not."),
    DocumentSpec("docs/10-phase-reconstitution.md", "Phase three: reconstitution",
                 "How normal operation is restored and the plan stood down."),
    DocumentSpec("docs/11-inventory.md", "Inventory",
                 "The hardware and software this plan depends on."),
    DocumentSpec("docs/12-interconnections.md", "Interconnections",
                 "Every system this one exchanges data with, and who to call about each."),
    DocumentSpec("docs/references.md", "References",
                 "The consolidated index of every source this plan cites."),
    DocumentSpec("docs/compliance-audit.md", "Compliance audit",
                 "The adversarial audit of this plan's own claims."),
    DocumentSpec("runbooks/RB-01-switchover.md", "RB-01 Switchover",
                 "A planned transition of the production role, rehearsed and reversible."),
    DocumentSpec("runbooks/RB-02-failover.md", "RB-02 Failover",
                 "An unplanned transition, and the decision gate in front of it."),
    DocumentSpec("runbooks/RB-03-failback.md", "RB-03 Failback",
                 "The return trip, which is the leg most plans never rehearse."),
    DocumentSpec("runbooks/RB-04-dr-drill.md", "RB-04 Recovery drill",
                 "The exercise procedure and what evidence it has to produce."),
    DocumentSpec("runbooks/RB-05-replication-lifecycle.md", "RB-05 Replication lifecycle",
                 "Building, holding and tearing down the standby posture."),
    DocumentSpec("checklists/roles-and-responsibilities.md", "Roles and responsibilities",
                 "Who does what during a recovery, and who does it when they are away."),
    DocumentSpec("checklists/contact-roster.md", "Contact roster",
                 "Who is called, in what order, and on what bridge."),
    DocumentSpec("checklists/outage-assessment.md", "Outage assessment",
                 "How long the repair will take, and what to do when nobody can say."),
    DocumentSpec("checklists/dr-authority-matrix.md", "Recovery authority matrix",
                 "Who may declare, who may spend, and how long they have to decide."),
    DocumentSpec("checklists/tier-assignment-workshop.md", "Tier assignment workshop",
                 "The session that turns business impact into a recovery tier."),
    DocumentSpec("checklists/manual-workarounds.md", "Manual workarounds",
                 "What people do while the systems are down, and for how long it holds."),
    DocumentSpec("checklists/validation-pack.md", "Validation pack",
                 "The checks that decide whether the recovered system may be used."),
    DocumentSpec("checklists/pre-failover-precheck.md", "Pre-failover precheck",
                 "What is confirmed before the decision to fail over is taken."),
    DocumentSpec("checklists/drill-timing-sheet.md", "Drill timing sheet",
                 "The stopwatch record a drill has to produce to be worth anything."),
    DocumentSpec("checklists/contingency-training.md", "Contingency training",
                 "Who is trained on this plan, on what, and how recently."),
    DocumentSpec("checklists/risk-register.md", "Risk register",
                 "The accepted risks to this plan, each with an owner and a review date."),
)

_SCAFFOLD_PATHS: tuple[str, ...] = tuple(page.path for page in SCAFFOLD)


# --------------------------------------------------------------------- the closed sets

def annotation_of(stored: Record | None) -> str:
    """Whatever the store marks this record with, and nothing else.

    ``status_marker`` returns the record's whole rendered cell, which for an answered field
    is the value followed by any caveat. The value half belongs to the answer, so it is
    sliced off here and what remains is the annotation: empty for a confident answer, the
    caveat for a guessed one, the whole marker for a field with no value at all.

    Slicing rather than re-composing is the point. Every annotation is a suffix of a string
    ``itscp_store`` owns, so the marker text has exactly one definition.
    """
    marker = store.status_marker(stored)
    if stored is None or stored.status != "ANSWERED":
        return marker
    return marker[len(str(stored.value)):]


def conflict_note(stored: Record | None) -> str:
    """How a second, disagreeing source renders. Empty when the record has no conflict.

    Both values, both sources and the named decision owner, because a conflict surfaced
    without an owner is one resolved silently by whoever reads the document first.
    """
    if stored is None or stored.conflict is None:
        return ""
    disagreement = stored.conflict
    return CONFLICT_MARKER.format(
        value=stored.value, provenance=stored.provenance,
        other=disagreement.value, other_source=disagreement.provenance,
        owner=disagreement.decision_owner)


def annotation_vocabulary(document: dict) -> frozenset[str]:
    """Every annotation this store can produce. The closed set, derived from the records.

    An annotation segment whose text is not in here is text the renderer composed, which is
    the one thing the fourth kind exists to make impossible.
    """
    marks = {annotation_of(None)}
    for stored in document["facts"].values():
        marks.update((annotation_of(stored), conflict_note(stored)))
    return frozenset(mark for mark in marks if mark)


def structural_corpus() -> frozenset[str]:
    """Every string the renderer may write as structural text.

    Three sources and no fourth: the transcribed NIST headings, the phrases the question
    bank already carries, and the boilerplate this project declares in :data:`BOILERPLATE`
    and :data:`SCAFFOLD`. A ``method`` element's templated text is one of the bank's phrases,
    which is why it lives in the bank and not here.
    """
    corpus = set(BOILERPLATE) | set(bank.NIST_CORPUS)
    for question in bank.QUESTIONS:
        corpus.add(question.records)
        corpus.update(question.columns)
        corpus.add(question.method_statement)
    corpus.discard("")
    for page in SCAFFOLD:
        corpus.update((page.title, page.purpose))
        corpus.update(text for figure in page.figures
                      for text in (figure.alt, figure.path))
    return frozenset(corpus)


# --------------------------------------------------------------------------- the field map

def destinations(question: bank.Question) -> tuple[str, ...]:
    """Every scaffold document this field is written to, read from the bank's own map.

    The map's entries name a document and sometimes a section within it; only the document
    is wanted here. Some name a document by its numeric prefix, which is resolved against
    the scaffold so that the bank never has to repeat a filename it might mistype.
    """
    named = (entry.strip().split(" ")[0] for entry in question.written_to.split(","))
    return tuple(dict.fromkeys(_resolved(token) for token in named if token))


def _resolved(token: str) -> str:
    """One entry of the field map as a scaffold path, or as itself when nothing matches.

    Returning the token unmatched rather than raising keeps a mistyped destination a failing
    test with a readable message instead of an exception during a render.
    """
    if token in _SCAFFOLD_PATHS:
        return token
    matches = [path for path in _SCAFFOLD_PATHS if path.startswith(token)]
    return matches[0] if len(matches) == 1 else token


def questions_for(path: str) -> list[bank.Question]:
    """Every field written to one document, in the bank's order."""
    return [question for question in bank.QUESTIONS if path in destinations(question)]


# --------------------------------------------------------------------------- the writer

class Writer:
    """Accumulates segments. Every append goes through one of these four methods.

    The methods are the whole enforcement mechanism. There is no way to append a segment of
    an arbitrary kind, and :meth:`annotate` accepts a record rather than text, so annotation
    bytes cannot originate anywhere but a record.
    """

    def __init__(self) -> None:
        self.segments: list[Segment] = []

    def markup(self, text: str) -> None:
        """Markdown structure. Rejected here if it carries a letter or a digit."""
        if not text:
            return
        if not MARKUP_ONLY.match(text):
            raise ValueError(
                f"{text!r} is not markup: it carries a letter or a digit. Text with content "
                f"is structural, an answer or an annotation, and has to say which.")
        self.segments.append(Segment("markup", text))

    def structural(self, text: str) -> None:
        """A heading or declared boilerplate. Rejected here if it is in no corpus."""
        if not text:
            return
        if text not in structural_corpus():
            raise ValueError(
                f"{text!r} is in neither the question bank nor the declared boilerplate. A "
                f"sentence nobody wrote down cannot enter a generated plan.")
        self.segments.append(Segment("structural", text))

    def answer(self, value: object) -> None:
        """One recorded value, stringified.

        A list becomes one segment per item so each stays traceable to its record; joining
        them here would produce a string that is in no record, which is the whole failure.
        """
        if isinstance(value, list):
            for position, item in enumerate(value):
                if position:
                    self.markup(", ")
                self.answer(item)
            return
        if value is None or value == "":
            return
        self.segments.append(Segment("answer", str(value)))

    def annotate(self, stored: Record | None) -> None:
        """Whatever the store marks this record with, then any conflict on it.

        Takes a record and not a string. That is the mechanical half of the guarantee: no
        caller can hand this method text of its own.
        """
        for mark in (annotation_of(stored), conflict_note(stored)):
            if mark:
                self.segments.append(Segment("annotation", mark))

    @property
    def text(self) -> str:
        return "".join(segment.text for segment in self.segments)


# --------------------------------------------------------------------------- rendering

def render(document: dict) -> tuple[RenderedDocument, ...]:
    """The whole plan repository, one entry per file of the scaffold."""
    return tuple(_render_page(page, document) for page in SCAFFOLD)


def _render_page(page: DocumentSpec, document: dict) -> RenderedDocument:
    writer = Writer()
    _write_masthead(writer, page)
    _write_fields(writer, page, document)
    _write_references(writer, page, document)
    _write_unverified(writer, page, document)
    return RenderedDocument(page.path, writer.text, tuple(writer.segments))


def _write_masthead(writer: Writer, page: DocumentSpec) -> None:
    _write_heading(writer, "# ", page.title)
    writer.structural(page.purpose)
    writer.markup("\n\n")
    writer.structural(GENERATED_NOTICE)
    writer.markup("\n")
    for figure in page.figures:
        writer.markup("\n![")
        writer.structural(figure.alt)
        writer.markup("](")
        writer.structural(figure.path)
        writer.markup(")\n")


def _write_heading(writer: Writer, prefix: str, text: str) -> None:
    writer.markup(prefix)
    writer.structural(text)
    writer.markup("\n\n")


def _write_fields(writer: Writer, page: DocumentSpec, document: dict) -> None:
    questions = questions_for(page.path)
    if not questions:
        writer.markup("\n")
        writer.structural(NO_FIELDS_HERE)
        writer.markup("\n")
        return
    impact_level = impact_level_of(document)
    heading = ""
    for question in questions:
        if _heading_for(question, impact_level) != heading:
            heading = _heading_for(question, impact_level)
            _write_heading(writer, "\n## ", heading)
        _write_field(writer, question, store.record(document, question.id))


def impact_level_of(document: dict) -> str:
    """The categorisation this plan states about itself, or the empty string for none.

    Empty is the reference plan's own position and is not a defect of this function: no
    sentence anywhere in it says the system is low, moderate or high impact.
    """
    stored = store.record(document, bank.IMPACT_LEVEL_KEY)
    if stored is None or stored.status != "ANSWERED":
        return ""
    return str(stored.value)


def _heading_for(question: bank.Question, impact_level: str) -> str:
    """The heading a field sits under, which is its structural-provenance class made visible.

    NIST's own heading where the bank cites one, the method heading where the toolkit
    supplied the element, and ours for everything this project carries on its own account.

    NIST's own heading is not a constant. Its appendix letters depend on which of the three
    sample templates applies, so the categorisation selects the letter. An uncategorised plan
    keeps the transcribed high-impact heading, which is the superset an auditor with no
    stated level grades against. Where the selected template has no appendix for the element
    at all, the element survives and its NIST provenance does not, so it is declared ours.
    """
    if question.structural_provenance == "method":
        return METHOD_HEADING
    if not question.nist_heading:
        return OURS_HEADING
    if not impact_level:
        return question.nist_heading
    return bank.heading_in_scheme(question.nist_heading, impact_level) or OURS_HEADING


def _write_field(writer: Writer, question: bank.Question, stored: Record | None) -> None:
    """One field, as a table when it holds rows and as a list item when it holds a scalar.

    A table cannot be a list item: Markdown will not render one nested under a bullet, and a
    plan whose business impact analysis silently degrades to pipe characters is worse than
    one that never had the table.
    """
    _write_method_statement(writer, question)
    if question.columns and _is_answered(stored):
        _write_table_field(writer, question, stored)
        return
    writer.markup("- **")
    writer.structural(question.records)
    writer.markup("**: ")
    if _is_answered(stored):
        writer.answer(stored.value)
    writer.annotate(stored)
    writer.markup("\n")


def _write_method_statement(writer: Writer, question: bank.Question) -> None:
    """The templated text a method element consists of, as structural text and nothing else.

    Written before the field it frames, so the answer below it reads as a parameter of a
    stated approach rather than as a claim the interviewee made about the approach itself.
    """
    if not question.method_statement:
        return
    writer.structural(question.method_statement)
    writer.markup("\n\n")


def _write_table_field(writer: Writer, question: bank.Question, stored: Record) -> None:
    writer.markup("\n**")
    writer.structural(question.records)
    writer.markup("**\n\n")
    _write_table(writer, question, stored)


def _is_answered(stored: Record | None) -> bool:
    return stored is not None and stored.status == "ANSWERED"


def _write_table(writer: Writer, question: bank.Question, stored: Record) -> None:
    writer.markup("| ")
    for position, column in enumerate(question.columns):
        if position:
            writer.markup(" | ")
        writer.structural(column)
    writer.markup(" |\n|")
    writer.markup(" --- |" * len(question.columns))
    writer.markup("\n")
    for row in stored.value:
        writer.markup("| ")
        for position, column in enumerate(question.columns):
            if position:
                writer.markup(" | ")
            writer.answer(row.get(column, ""))
        writer.markup(" |\n")
    writer.annotate(stored)
    writer.markup("\n")


def _write_references(writer: Writer, page: DocumentSpec, document: dict) -> None:
    _write_heading(writer, "\n## ", REFERENCES_HEADING)
    writer.structural(REFERENCES_PREAMBLE)
    writer.markup("\n\n")
    sourced = [question for question in questions_for(page.path)
               if _is_answered(store.record(document, question.id))]
    if not sourced:
        writer.structural(NO_SOURCES_YET)
        writer.markup("\n")
        return
    for question in sourced:
        _write_source(writer, question, store.record(document, question.id))


def _write_source(writer: Writer, question: bank.Question, stored: Record) -> None:
    writer.markup("- **")
    writer.structural(question.records)
    writer.markup("**, ")
    writer.structural(RECORDED_BY)
    writer.markup(" ")
    writer.answer(stored.provenance)
    if stored.mechanism:
        writer.markup("; ")
        writer.structural(MECHANISM)
        writer.markup(": ")
        writer.answer(stored.mechanism)
    writer.markup("\n")


def _write_unverified(writer: Writer, page: DocumentSpec, document: dict) -> None:
    _write_heading(writer, "\n### ", UNVERIFIED_HEADING)
    writer.structural(UNVERIFIED_PREAMBLE)
    writer.markup("\n\n")
    marked = [question for question in questions_for(page.path)
              if _is_marked(store.record(document, question.id))]
    if not marked:
        writer.structural(NOTHING_UNVERIFIED)
        writer.markup("\n")
        return
    for question in marked:
        writer.markup("- **")
        writer.structural(question.records)
        writer.markup("**: ")
        writer.annotate(store.record(document, question.id))
        writer.markup("\n")


def _is_marked(stored: Record | None) -> bool:
    """Whether this record earns an annotation: a gap, a caveat or a disagreement."""
    return bool(annotation_of(stored) or conflict_note(stored))
