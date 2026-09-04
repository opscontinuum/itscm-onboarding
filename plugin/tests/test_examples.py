"""The two committed example plans, rebuilt from their stores and compared byte for byte.

``examples/`` holds generated output that is committed on purpose, so that a reader can
judge the toolkit by reading a plan rather than by running one. Committed generated output
rots: the renderer grows a heading, the question bank grows a field, and the tree on disk
quietly stops being what the code produces. This section is the guard. It rebuilds both
trees from their own answer stores and fails on the first byte that differs.

Two examples, one generator:

* ``examples/day-one`` is the shipped starter store rendered as a plan: eighty-two fields
  MISSING, each naming the role who can close it. It is what an engagement hands over
  before anybody has been interviewed, and it is the only example that can show the
  drawings carrying the store's MISSING marker rather than a chart.
* ``examples/worked-plan`` is the same generator over a store derived from the reference
  plan at ``../oci-itscp``. Its answer store is committed too, which is a deliberate
  exception to the rule that an answer store is never committed, so the checks below also
  hold that file to the terms of the exception: canonical form, no real identifier, and no
  provenance claiming an interview that never happened.
"""
from __future__ import annotations

import re
import sys
import tempfile
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import itscp_build as build
import itscp_questions as bank
import itscp_session as session
import itscp_store as store
from harness import Section, equal

_ROOT = Path(__file__).resolve().parents[2]

EXAMPLES = _ROOT / "examples"
WORKED_STORE = EXAMPLES / "worked-plan" / "answers.toml"
WORKED_SESSION = EXAMPLES / "worked-plan" / "session.toml"
WORKED_PLAN = EXAMPLES / "worked-plan" / "plan"
DAY_ONE_PLAN = EXAMPLES / "day-one" / "plan"

#: The store the day-one example is rendered from. The starter store the plugin already
#: ships, rather than a second copy of it, so the two cannot disagree.
STARTER_STORE = _ROOT / "plugin" / "answers.example.toml"

#: What the committed worked store has to say for itself, in the header the emitter does not
#: write. Checked as properties rather than as an exact string, so the wording can improve
#: without a test edit, and the terms of the exception cannot quietly go missing.
EXCEPTION_TERMS: tuple[str, ...] = ("hypothetical", "oci-itscp", "never")

#: Shapes that would mean a real identifier reached a committed file. Shapes rather than
#: characters: the reference plan writes a masked database connect string, which contains an
#: at sign and is not an address, and refusing the character would refuse the procedure.
FORBIDDEN_IDENTIFIERS: tuple[str, ...] = ("ocid1.", "http://", "https://")

#: An electronic mail address, which is the shape the at sign is actually being watched for.
EMAIL_SHAPE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")

#: The only provenance class a derivation from a document may write. An ``interview:``
#: provenance here would be the store claiming a conversation that did not happen, which is
#: the exact failure the toolkit exists to prevent.
DOCUMENT_PROVENANCE_PREFIX = "document:"


def main() -> None:
    section = Section("9", "the committed examples")

    section.check("the worked answer store exists", lambda: _exists(WORKED_STORE))
    section.check("every record in the worked store is valid", _worked_records_validate)
    section.check("the worked store is in the emitter's canonical form", _worked_is_canonical)
    section.check("the worked store states why it is committed", _worked_states_the_exception)
    section.check("the worked store carries no real identifiers", _worked_has_no_identifiers)
    section.check("no answer claims an interview that did not happen", _worked_cites_documents)

    section.check("the worked plan is what the build step writes",
                  lambda: _plan_is_rebuilt(WORKED_PLAN, _worked_document()))
    section.check("the day-one plan is what the build step writes",
                  lambda: _plan_is_rebuilt(DAY_ONE_PLAN, _starter_document()))

    section.check("the day-one plan is a page of named gaps", _day_one_names_every_owner)
    section.check("the day-one drawings carry the MISSING marker", _day_one_drawings_are_marked)

    section.check("the worked transcript is valid", _transcript_validates)
    section.check("the worked transcript covers every field", _transcript_covers_the_bank)

    section.finish()


# ----------------------------------------------------------------- the stores on disk

def _exists(path: Path) -> None:
    assert path.exists(), f"{path} is missing; the committed example is incomplete"


def _document(path: Path) -> dict:
    return store.load_document(tomllib.loads(path.read_text(encoding="utf-8")))


def _worked_document() -> dict:
    return _document(WORKED_STORE)


def _starter_document() -> dict:
    return _document(STARTER_STORE)


def _worked_records_validate() -> None:
    for stored in _worked_document()["facts"].values():
        store.validate(stored)


def _worked_is_canonical() -> None:
    """The committed file is its own header followed by exactly what the emitter writes.

    Anything else means the file was edited by hand after generation, and a hand-edited
    answer store is one whose comments no longer match the question bank behind them.
    """
    text = WORKED_STORE.read_text(encoding="utf-8")
    emitted = store.emit(_worked_document())
    assert text.endswith(emitted), (
        "the committed worked store is not what the emitter produces from its own values. "
        "Regenerate it rather than editing it: the guidance comments are rendered from the "
        "question bank on every write.")


def _worked_states_the_exception() -> None:
    text = WORKED_STORE.read_text(encoding="utf-8")
    header = text[:-len(store.emit(_worked_document()))]
    assert header.strip(), (
        "the committed worked store carries no header of its own. The emitter's header says "
        "an answer store must never be committed; a file that is committed anyway has to say "
        "on its own first line why it is the exception.")
    for term in EXCEPTION_TERMS:
        assert term in header, (
            f"the worked store's header does not mention {term!r}, so it does not state the "
            f"terms on which committing an answer store was acceptable this once.")


def _worked_has_no_identifiers() -> None:
    text = WORKED_STORE.read_text(encoding="utf-8")
    for forbidden in FORBIDDEN_IDENTIFIERS:
        assert forbidden not in text, (
            f"the worked store contains {forbidden!r}, which looks like a real identifier")
    found = EMAIL_SHAPE.search(text)
    assert found is None, (
        f"the worked store contains {found.group()!r}, which is shaped like an address")


def _worked_cites_documents() -> None:
    claimed = sorted(stored.key for stored in _worked_document()["facts"].values()
                     if stored.provenance
                     and not stored.provenance.startswith(DOCUMENT_PROVENANCE_PREFIX))
    assert not claimed, (
        f"{claimed} carry a provenance that is not a document. Every value in this example "
        f"was read out of the reference plan; a provenance naming an interview would be the "
        f"store recording a conversation nobody had.")


# ------------------------------------------------------------------ the plans on disk

def _plan_is_rebuilt(committed: Path, document: dict) -> None:
    """Rebuild into a temporary directory and compare the whole tree, path by path."""
    _exists(committed)
    with tempfile.TemporaryDirectory() as workspace:
        rebuilt = Path(workspace)
        build.build_plan(rebuilt, build.Plan(answers=document))
        _same_paths(committed, rebuilt)
        _same_bytes(committed, rebuilt)


def _relative_paths(root: Path) -> list[str]:
    return sorted(str(path.relative_to(root)) for path in root.rglob("*") if path.is_file())


def _same_paths(committed: Path, rebuilt: Path) -> None:
    equal(_relative_paths(committed), _relative_paths(rebuilt),
          f"the files under {committed.name} against the files the build step writes")


def _same_bytes(committed: Path, rebuilt: Path) -> None:
    for relative in _relative_paths(rebuilt):
        equal((committed / relative).read_text(encoding="utf-8"),
              (rebuilt / relative).read_text(encoding="utf-8"),
              f"{relative} as committed against {relative} as generated now")


# ----------------------------------------------------------------- what day one shows

def _day_one_names_every_owner() -> None:
    """Every gap on the page names the role who can close it, and there are no other cells.

    This is the day-one claim in one check: the deliverable before an interview is not an
    empty document, it is a work assignment. A marker naming nobody would make it one.
    """
    coverage = store.coverage(_starter_document())
    equal(coverage.covered, 0, "covered fields in the day-one store")
    unassigned = store.status_marker(None)
    for page in DAY_ONE_PLAN.rglob("*.md"):
        assert unassigned not in page.read_text(encoding="utf-8"), (
            f"{page.name} carries a gap with no owner, so the day-one plan is a list of "
            f"unknowns rather than a list of people who owe an answer")


def _day_one_drawings_are_marked() -> None:
    """A drawing with no data behind it says so, rather than drawing an empty chart."""
    marker = store.status_marker(None)
    for name in build.DIAGRAMS:
        drawing = (DAY_ONE_PLAN / "docs" / "diagrams" / name).read_text(encoding="utf-8")
        assert marker in drawing, (
            f"{name} was written with no data and without the store's MISSING marker, so it "
            f"reads as a chart of nothing rather than as an unanswered question")


# ------------------------------------------------------------------- the transcript

def _transcript() -> dict:
    _exists(WORKED_SESSION)
    return session.load_transcript(tomllib.loads(WORKED_SESSION.read_text(encoding="utf-8")))


def _transcript_validates() -> None:
    for entry in _transcript()["entries"]:
        session.validate(entry)


def _transcript_covers_the_bank() -> None:
    recorded = {entry.question_id for entry in _transcript()["entries"]}
    unrecorded = sorted(question.id for question in bank.QUESTIONS
                        if question.id not in recorded)
    assert not unrecorded, (
        f"the transcript says nothing about {len(unrecorded)} field(s): {unrecorded}. A "
        f"store whose values have no record of where they came from is the thing the "
        f"transcript exists to prevent.")


if __name__ == "__main__":
    main()
