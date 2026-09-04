"""The renderer's anti-fabrication guarantee, proved segment by segment.

Every byte of every generated document is one of exactly four things, and the renderer is
built so that it cannot produce a fifth:

``structural``
    A heading transcribed from NIST SP 800-34 Rev. 1, or boilerplate this project declares
    as its own. Either way it comes out of a named corpus, and the check below asserts
    membership rather than trusting the renderer to have been careful.
``answer``
    Something a person or a read-only API recorded, stringified and nothing more.
``markup``
    Markdown structure. Contains no letter and no digit, which is how "the renderer cannot
    invent a word or a number" stops being a claim and starts being a regular expression.
``annotation``
    The MISSING, low-confidence, DEFERRED, not-applicable and conflict markers. This is the
    fourth kind and the one the ported design did not have. It exists because a marker is
    not template text: nothing in NIST says ``**[MISSING - owner: business owner]**``. It is
    ours, it is generated, and pretending it is structural would hide exactly the bytes a
    reader most needs to distrust.

The load-bearing check is :func:`_annotations_are_a_pure_function_of_the_record`. An
annotation the renderer could compose freely would be a back door into the document for text
nobody said, wearing the authority of a warning. So the vocabulary is closed: every
annotation the renderer emits has to be a member of the set derived mechanically from the
records themselves, and the writer is given no method that turns caller-supplied text into
an annotation. Both halves are checked, because the set test alone would pass a renderer
that happened to guess a legal string.

There is deliberately no kind meaning "the renderer wrote this". Anything that is none of
the four is a defect, and section 6 fails.
"""
from __future__ import annotations

import inspect
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import itscp_questions as bank
import itscp_render as render
import itscp_store as store
import scripted_answers
from harness import Section, equal

EMPTY = store.new_document(scripted_answers.SYSTEM_NAME)


def main() -> None:
    section = Section("6", "the renderer's four segment kinds")

    section.check("every segment carries one of the four kinds", _kinds_are_the_four)
    section.check("segments reassemble into the document exactly", _segments_reassemble)
    section.check("an empty store produces no answer segments", _empty_store_answers_nothing)
    section.check("structural text comes from the declared corpus", _structural_is_corpus)
    section.check("NIST headings render verbatim", _nist_headings_are_verbatim)
    section.check("method text is structural, never an answer", _method_text_is_structural)
    section.check("a method field is headed as the toolkit's own", _method_is_headed_as_ours)
    section.check("appendix letters follow the categorization", _lettering_follows_the_level)
    section.check("an appendix the low template lacks is declared ours",
                  _an_absent_appendix_is_declared_ours)
    section.check("an uncategorized plan keeps the transcribed heading",
                  _no_level_keeps_the_transcribed_heading)
    section.check("answer text comes from the store", _answers_come_from_the_store)
    section.check("markup contains no letter and no digit", _markup_has_no_content)
    section.check("annotations come from a closed vocabulary", _annotations_are_closed)
    section.check("annotations are a pure function of the record",
                  _annotations_are_a_pure_function_of_the_record)
    section.check("the writer cannot annotate caller-supplied text",
                  _the_writer_takes_a_record_not_a_string)
    section.check("a MISSING field never renders blank", _missing_never_renders_blank)
    section.check("a low-confidence value renders with its caveat", _low_confidence_is_marked)
    section.check("a DEFERRED field renders its date and owner", _deferred_shows_date_and_owner)
    section.check("a conflict renders both sides and its decision owner", _conflict_is_surfaced)
    section.check("every document carries the two mandatory sections", _mandatory_sections)
    section.check("every scaffold document is written", _every_scaffold_document_is_written)
    section.check("every field is written to a document that exists", _fields_land_somewhere)
    section.check("rendering twice produces the same bytes", _rendering_is_deterministic)

    section.finish()


def _rendered(document: dict) -> tuple[render.RenderedDocument, ...]:
    return render.render(document)


def _scripted() -> tuple[render.RenderedDocument, ...]:
    return _rendered(scripted_answers.scripted_document())


def _every_segment(rendered) -> list[render.Segment]:
    return [segment for page in rendered for segment in page.segments]


def _of_kind(rendered, kind: str) -> list[render.Segment]:
    return [segment for segment in _every_segment(rendered) if segment.kind == kind]


# --------------------------------------------------------------------- the four kinds

def _kinds_are_the_four() -> None:
    equal(len(render.SEGMENT_KINDS), 4, "the number of segment kinds")
    for segment in _every_segment(_scripted()):
        assert segment.kind in render.SEGMENT_KINDS, (
            f"segment kind {segment.kind!r} is not one of {render.SEGMENT_KINDS}")


def _segments_reassemble() -> None:
    for page in _scripted():
        equal("".join(segment.text for segment in page.segments), page.text,
              f"{page.path}: the segments joined against the document")


def _empty_store_answers_nothing() -> None:
    answers = _of_kind(_rendered(EMPTY), "answer")
    assert not answers, f"an unanswered store produced {len(answers)} answer segment(s): " \
                        f"{[segment.text for segment in answers][:3]}"


def _structural_is_corpus() -> None:
    corpus = render.structural_corpus()
    for segment in _of_kind(_scripted(), "structural"):
        assert segment.text in corpus, (
            f"structural text is in neither the question bank nor the declared "
            f"boilerplate: {segment.text!r}")


def _nist_headings_are_verbatim() -> None:
    corpus = render.structural_corpus()
    cited = {question.nist_heading for question in bank.QUESTIONS if question.nist_heading}
    for heading in cited:
        assert heading in bank.NIST_CORPUS, f"{heading!r} is not a transcribed NIST heading"
        assert heading in corpus, f"{heading!r} is cited by the bank but never rendered"


def _method_questions() -> list[bank.Question]:
    return [question for question in bank.QUESTIONS
            if question.structural_provenance == "method"]


def _method_text_is_structural() -> None:
    """Templated text the toolkit supplies is in the corpus, and never in an answer segment.

    This is the whole of the fourth class's guarantee. Method content is neither elicited nor
    transcribed, so a reader has to be able to tell it from both, and the one way it could be
    mistaken for something a customer said is by arriving as an answer segment.
    """
    corpus = render.structural_corpus()
    statements = {question.method_statement for question in _method_questions()}
    assert statements, "nothing is classified method, so the class guarantees nothing"
    for statement in statements:
        assert statement in corpus, f"method text is in no corpus: {statement!r}"
    for segment in _of_kind(_scripted(), "answer"):
        assert segment.text not in statements, (
            f"method text rendered as an answer, which says a customer supplied it: "
            f"{segment.text!r}")


def _method_is_headed_as_ours() -> None:
    """A method field sits under its own heading, distinct from ours and from NIST's."""
    assert render.METHOD_HEADING != render.OURS_HEADING, (
        "method and ours share a heading, so a reader cannot tell the toolkit's own approach "
        "from a field this plan simply recorded")
    assert render.METHOD_HEADING not in bank.NIST_CORPUS, (
        "the method heading is a transcribed NIST heading, which claims NIST supplied it")
    rendered = _scripted()
    for question in _method_questions():
        text = _text_for(rendered, question.id)
        assert render.METHOD_HEADING in text, (
            f"{question.id} is method and its document never says so")
        assert question.method_statement in text, (
            f"{question.id} is method and the text the toolkit supplies is not rendered")


#: A field whose NIST element is an appendix that both templates carry, at different
#: letters. Named rather than searched for, so a bank edit that drops it fails loudly.
_APPENDIX_FIELD = "app.interconnections"

#: A field whose NIST element the low-impact template has no appendix for at all.
_ABSENT_AT_LOW_IMPACT = "infra.standby_region"


def _categorized(level: str) -> dict:
    """The scripted store with an impact level recorded against it."""
    return store.put(scripted_answers.scripted_document(), store.Record(
        bank.IMPACT_LEVEL_KEY, "ANSWERED", value=level, confidence="high",
        readback="confirmed",
        provenance=f"interview:governance-risk-contact:{scripted_answers.INTERVIEW_DATE}"))


def _lettering_follows_the_level() -> None:
    """The letter in front of an appendix is a function of the categorization.

    NIST's low-impact template omits one appendix and letters everything after it one lower.
    A plan that prints a constant letter is right for at most one of the two schemes, and the
    coverage map this bank was built against was wrong about six of them.
    """
    for level, expected in (("low", "APPENDIX H INTERCONNECTIONS TABLE"),
                            ("moderate", "APPENDIX I INTERCONNECTIONS TABLE"),
                            ("high", "APPENDIX I INTERCONNECTIONS TABLE")):
        text = _text_for(_rendered(_categorized(level)), _APPENDIX_FIELD)
        assert expected in text, (
            f"at {level} impact the interconnections table should head {expected!r} and "
            f"does not")


def _an_absent_appendix_is_declared_ours() -> None:
    """The low template has no alternate-storage appendix, so the plan claims none."""
    text = _text_for(_rendered(_categorized("low")), _ABSENT_AT_LOW_IMPACT)
    absent = "APPENDIX F ALTERNATE STORAGE, SITE, AND TELECOMMUNICATIONS"
    assert absent not in text, (
        f"a low-impact plan heads a section {absent!r}, which is an appendix NIST's "
        f"low-impact template does not have")
    assert render.OURS_HEADING in text, (
        "the element survives the categorization but its NIST provenance does not, so it "
        "has to be declared ours rather than quietly kept under a heading NIST never wrote")


def _no_level_keeps_the_transcribed_heading() -> None:
    """Uncategorized, the plan keeps the heading the bank transcribed and claims nothing more.

    The reference plan's own compliance skill audits an uncategorized plan against the
    high-impact template as the superset. Rendering the transcribed heading is that rule.
    """
    question = bank.BY_ID[_APPENDIX_FIELD]
    uncategorized = store.put(scripted_answers.scripted_document(), store.Record(
        bank.IMPACT_LEVEL_KEY, "MISSING", owner="governance/risk contact"))
    text = _text_for(_rendered(uncategorized), _APPENDIX_FIELD)
    assert question.nist_heading in text, (
        f"with no impact level recorded the plan should keep {question.nist_heading!r}")


def _answers_come_from_the_store() -> None:
    document = scripted_answers.scripted_document()
    recorded = scripted_answers.stored_scalars(document)
    for segment in _of_kind(_rendered(document), "answer"):
        assert segment.text in recorded, (
            f"answer text is in no record in the store: {segment.text!r}")


def _markup_has_no_content() -> None:
    for segment in _of_kind(_scripted(), "markup"):
        assert render.MARKUP_ONLY.match(segment.text), (
            f"a markup segment carries a letter or a digit, so the renderer wrote "
            f"content it called structure: {segment.text!r}")


# ------------------------------------------------------------------- the fourth kind

def _annotations_are_closed() -> None:
    document = scripted_answers.scripted_document()
    vocabulary = render.annotation_vocabulary(document)
    emitted = {segment.text for segment in _of_kind(_rendered(document), "annotation")}
    assert emitted, "the scripted store carries gaps but nothing rendered as an annotation"
    assert emitted <= vocabulary, (
        f"annotation text outside the closed vocabulary: {sorted(emitted - vocabulary)}")


def _annotations_are_a_pure_function_of_the_record() -> None:
    """Change one record's owner; only that record's annotation may change.

    A renderer that composed annotation text from anything but the record would either fail
    to move when the record moves, or move something else at the same time.
    """
    document = scripted_answers.scripted_document()
    gap = next(key for key, state in scripted_answers.EXCEPTIONS.items()
               if state == "MISSING")
    before = render.annotation_vocabulary(document)
    moved = store.put(document, store.Record(gap, "MISSING", owner="lead engineer deputy"))
    after = render.annotation_vocabulary(moved)
    equal(sorted(after - before), [store.status_marker(store.record(moved, gap))],
          "the annotations that appeared when one owner changed")
    equal(sorted(before - after), [store.status_marker(store.record(document, gap))],
          "the annotations that disappeared when one owner changed")


def _the_writer_takes_a_record_not_a_string() -> None:
    """The mechanical half: there is no route from caller text to an annotation segment."""
    parameters = inspect.signature(render.Writer.annotate).parameters
    equal([name for name in parameters if name != "self"], ["stored"],
          "the parameters of the only method that emits an annotation")
    equal(parameters["stored"].annotation, "Record | None",
          "what the annotating method accepts")


# ---------------------------------------------------------------- the rendering rules

def _text_for(rendered, key: str) -> str:
    question = bank.question(key)
    paths = render.destinations(question)
    pages = [page.text for page in rendered if page.path in paths]
    assert pages, f"{key} is written to {paths}, none of which was rendered"
    return "\n".join(pages)


def _missing_never_renders_blank() -> None:
    document = scripted_answers.scripted_document()
    gap = next(key for key, state in scripted_answers.EXCEPTIONS.items()
               if state == "MISSING")
    marker = store.status_marker(store.record(document, gap))
    assert marker in _text_for(_rendered(document), gap), (
        f"{gap} is MISSING and its marker {marker!r} is not in the document it writes to")


def _low_confidence_is_marked() -> None:
    document = scripted_answers.scripted_document()
    guessed = next(key for key, state in scripted_answers.EXCEPTIONS.items()
                   if state == "LOW_CONFIDENCE")
    marker = store.status_marker(store.record(document, guessed))
    assert marker in _text_for(_rendered(document), guessed), (
        f"{guessed} is low confidence and renders without its caveat; expected {marker!r}")


def _deferred_shows_date_and_owner() -> None:
    document = scripted_answers.scripted_document()
    postponed = next(key for key, state in scripted_answers.EXCEPTIONS.items()
                     if state == "DEFERRED")
    text = _text_for(_rendered(document), postponed)
    assert scripted_answers.DEFERRAL_DATE in text, "a DEFERRED field renders without its date"
    assert store.status_marker(store.record(document, postponed)) in text, \
        "a DEFERRED field renders without the store's own marker"


def _conflict_is_surfaced() -> None:
    document = scripted_answers.scripted_document()
    disputed = next(key for key, state in scripted_answers.EXCEPTIONS.items()
                    if state == "CONFLICT")
    stored = store.record(document, disputed)
    text = _text_for(_rendered(document), disputed)
    for expected in (str(stored.value), str(stored.conflict.value), stored.provenance,
                     stored.conflict.provenance, stored.conflict.decision_owner):
        assert expected in text, f"a conflicted field renders without {expected!r}"


# ------------------------------------------------------------------ the document set

def _mandatory_sections() -> None:
    for page in _scripted():
        for heading in (render.REFERENCES_HEADING, render.UNVERIFIED_HEADING):
            assert heading in page.text, f"{page.path} has no {heading!r} section"


def _every_scaffold_document_is_written() -> None:
    equal(sorted(page.path for page in _scripted()),
          sorted(specification.path for specification in render.SCAFFOLD),
          "the rendered paths against the scaffold")


def _fields_land_somewhere() -> None:
    paths = {specification.path for specification in render.SCAFFOLD}
    for question in bank.QUESTIONS:
        destinations = render.destinations(question)
        assert destinations, f"{question.id} names no destination document"
        for path in destinations:
            assert path in paths, f"{question.id} is written to {path}, which is not a file"


def _rendering_is_deterministic() -> None:
    equal([page.text for page in _scripted()], [page.text for page in _scripted()],
          "two renders of the same store")


if __name__ == "__main__":
    main()
