"""Acceptance: a scripted answer set goes in, a plan repository comes out, assertions run.

This is the project's first end-to-end test, and it runs with no human and no model in the
loop. ``scripted_answers`` plays the interview, :func:`itscp_build.build_plan` writes the
whole repository into a temporary directory, and the checks below read it back off disk as
a reader would.

The harness calls the product's own build step rather than assembling a plan itself. That
distinction is the whole point of test 1: a structural guarantee that only holds because
the test wrote the missing files is not a guarantee, it is the reference plan's defect with
a green tick on it.

Why three graded tests and not one byte-identical comparison
------------------------------------------------------------
The obvious acceptance test is "reproduce the reference plan byte for byte". That would be
the wrong test. A third of the reference plan's figures carry no source, five of the files
it names do not exist, and its own tier chart draws hedged numbers with the authority of a
measurement. Reproducing it exactly would reproduce all of that, and the resulting green
tick would certify the defects along with the plan.

So the reference is graded rather than copied, on three properties, each asserted of the
generated plan and separately measured on the reference so the difference is on the record:

1. **Structural completeness.** Every file the plan points at exists. The reference fails
   this today, on five files, and the generator cannot fail it because the field map and the
   document set are the same data.
2. **Provenance completeness.** Every rendered byte is attributable through the segment
   invariant, and every fact carries either a recorded source or a marker naming who owes
   it. The reference cannot be scored on the byte invariant at all, having no answer store
   behind it, so it is scored on the closest measurable proxy and the proxy is stated.
3. **Byte-similarity on the sourced tier.** Where the plan quotes a standard, it quotes it
   exactly. This is the one place a byte comparison is the right instrument, because the
   text has an owner outside this project and paraphrasing it silently is the failure.

Nothing about the reference plan can fail this suite. Its scores are printed as notes, not
asserted, because a check that could never fail would misrepresent what is being enforced.
"""
from __future__ import annotations

import os
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import itscp_build as build
import itscp_diagrams as diagrams
import itscp_questions as bank
import itscp_render as render
import itscp_store as store
import scripted_answers
from harness import Section, equal

#: Where the reference plan is, when it is on this machine. The suite is complete without
#: it: its absence costs the comparison notes and nothing else.
REFERENCE_PLAN = Path(os.environ.get(
    "ITSCP_REFERENCE_PLAN",
    Path(__file__).resolve().parents[3] / "oci-itscp"))

#: Where the generated diagrams land, relative to the plan root.
DIAGRAM_DIRECTORY = "docs/diagrams"

#: A relative Markdown link, which is how one generated document points at another.
_LINK = re.compile(r"\[[^\]]*\]\((?!https?:|mailto:|#)([^)\s#]+)")

#: An inline citation marker, and the reference plan's own hedge on an unsourced figure.
#: Either one means the statement on that line says where it came from.
_CITED = re.compile(r"\[\d{1,2}\]")
_HEDGED = re.compile(r"\(unverified:")

_FENCE = "```"
_LETTER = re.compile(r"[A-Za-z]")
_FIGURE = re.compile(r"\d")


def main() -> None:
    section = Section("8", "acceptance: a scripted plan, end to end")

    with tempfile.TemporaryDirectory() as workspace:
        plan = Path(workspace)
        written = _build_plan(plan)
        section.check("the build step reports what it wrote",
                      lambda: _assert_all_exist(plan, written))
        _run_checks(section, plan)

    section.finish()


def _run_checks(section: Section, plan: Path) -> None:
    section.check("the build step writes a plan with no human in the loop",
                  lambda: _the_plan_was_written(plan))

    section.check("1. every file the plan points at exists",
                  lambda: _structural_completeness(plan))
    section.check("1. a plan with no diagram data is still complete",
                  _a_plan_with_no_diagram_data_is_still_complete)
    _report_reference_structure(section)

    section.check("2. every rendered byte is attributable", _provenance_completeness)
    section.check("2. every fact carries a source or names who owes it", _every_fact_is_owned)
    _report_reference_provenance(section)

    section.check("3. quoted NIST headings match byte for byte", _byte_similarity_on_nist)
    _report_reference_similarity(section)


# ------------------------------------------------------------------------- the harness

def _build_plan(plan: Path) -> tuple[str, ...]:
    """The whole toolkit, run once: a scripted interview in, a plan repository on disk out."""
    return build.build_plan(plan, build.Plan(
        answers=scripted_answers.scripted_document(),
        tiers=_tiers(),
        timeline=_timeline_labels()))


#: The scripted plan's tier table. Only the tier 0 downtime is a field of the question bank
#: today, so it is the only figure that can carry a recorded source; the rest are drawn
#: unsourced, which is exactly what the drawing has to make visible.
_TIER_TABLE: tuple[tuple[str, str, float, str, str], ...] = (
    ("Tier 0", "hot standby", 2, "MTD 2 hr or less", "highest relative run cost"),
    ("Tier 1", "warm pilot light", 6, "MTD 6 hr or less", "about half of production"),
    ("Tier 2", "cold pre-staged", 24, "MTD 24 hr or less", "about a quarter of production"),
    ("Tier 3", "backup and restore", 120, "MTD 5 days or less", "lowest relative run cost"),
)


def _tiers() -> tuple[diagrams.Tier, ...]:
    """The tier table, with the downtime provenance read from the store rather than assumed."""
    stored = store.record(scripted_answers.scripted_document(), "business.mtd.tier0")
    sourced = stored.provenance if stored and stored.status == "ANSWERED" else ""
    return tuple(
        diagrams.Tier(name=name, posture=posture, mtd_hours=hours, mtd_label=label,
                      cost_label=cost, mtd_provenance=sourced, cost_provenance="")
        for name, posture, hours, label, cost in _TIER_TABLE)


def _timeline_labels() -> diagrams.TimelineLabels:
    return diagrams.TimelineLabels(
        data_at_risk="committed work not yet replicated",
        recovery_activities="database open, application tier up, traffic steered",
        recovery_owner="owner: infrastructure owner",
        work_recovery_activities="queue cleanup, interface replay, reconciliation",
        work_recovery_owner="owner: business owner")


def _the_plan_was_written(plan: Path) -> None:
    written = sorted(str(path.relative_to(plan)) for path in plan.rglob("*") if path.is_file())
    equal(len(written), len(render.SCAFFOLD) + len(build.DIAGRAMS),
          f"the files the build step wrote\n{written}")


def _a_plan_with_no_diagram_data_is_still_complete() -> None:
    """A plan whose tier table was never elicited still writes both drawings.

    Otherwise the two documents that embed them point at files nobody wrote, which is the
    reference plan's own failure. The drawing carries the store's MISSING marker instead of
    a chart, for the same reason a missing value never renders blank.
    """
    with tempfile.TemporaryDirectory() as workspace:
        bare = Path(workspace)
        build.build_plan(bare, build.Plan(answers=store.new_document("")))
        _structural_completeness(bare)
        for name in build.DIAGRAMS:
            drawing = (bare / DIAGRAM_DIRECTORY / name).read_text(encoding="utf-8")
            assert store.status_marker(None) in drawing, (
                f"{name} was written without data and without the store's MISSING marker, "
                f"so it reads as a chart of nothing rather than as an unanswered question")


# ------------------------------------------------------- 1. structural completeness

def _referenced_paths(plan: Path) -> set[str]:
    """Every path the plan points at: its own field map, and every relative link it writes."""
    referenced = {destination for question in bank.QUESTIONS
                  for destination in render.destinations(question)}
    for document in plan.rglob("*.md"):
        parent = document.parent.relative_to(plan)
        referenced.update(str((parent / target).as_posix())
                          for target in _LINK.findall(document.read_text(encoding="utf-8")))
    return referenced


def _structural_completeness(plan: Path) -> None:
    missing = sorted(target for target in _referenced_paths(plan)
                     if not (plan / target).exists())
    assert not missing, (
        f"the generated plan points at {len(missing)} file(s) it never wrote: {missing}. A "
        f"plan that names a checklist nobody can open is a plan that fails at the moment it "
        f"is read under pressure.")


def _report_reference_structure(section: Section) -> None:
    if not REFERENCE_PLAN.is_dir():
        section.note(f"reference plan not at {REFERENCE_PLAN}; comparison skipped")
        return
    destinations = sorted({destination for question in bank.QUESTIONS
                           for destination in render.destinations(question)})
    missing = [target for target in destinations
               if not _resolves_in(REFERENCE_PLAN, target)]
    section.note(f"reference plan, test 1: {len(destinations) - len(missing)}/"
                 f"{len(destinations)} destinations of the field map exist "
                 f"({_percent(len(destinations) - len(missing), len(destinations))}%)")
    for target in missing:
        section.note(f"  referenced and absent: {target}")


def _resolves_in(root: Path, target: str) -> bool:
    """Whether a destination exists, allowing for the reference's own filenames.

    The reference numbers some documents differently from the scaffold, so a destination is
    also satisfied by a single file whose path starts with it. Two matches is not a
    resolution, because a plan that points at two files points at neither.
    """
    if (root / target).exists():
        return True
    matches = [path for path in root.rglob("*")
               if path.is_file() and str(path.relative_to(root)).startswith(target)]
    return len(matches) == 1


# ------------------------------------------------------- 2. provenance completeness

def _provenance_completeness() -> None:
    """The segment invariant, over every byte of every generated document."""
    document = scripted_answers.scripted_document()
    recorded = scripted_answers.stored_scalars(document)
    corpus, vocabulary = render.structural_corpus(), render.annotation_vocabulary(document)
    for page in render.render(document):
        equal("".join(segment.text for segment in page.segments), page.text,
              f"{page.path}: the segments joined against the file")
        for segment in page.segments:
            _assert_attributable(segment, (corpus, recorded, vocabulary))


def _assert_attributable(segment: render.Segment, sources: tuple) -> None:
    corpus, recorded, vocabulary = sources
    if segment.kind == "structural":
        assert segment.text in corpus, f"structural text from nowhere: {segment.text!r}"
    elif segment.kind == "answer":
        assert segment.text in recorded, f"an answer in no record: {segment.text!r}"
    elif segment.kind == "annotation":
        assert segment.text in vocabulary, f"an annotation composed: {segment.text!r}"
    else:
        assert render.MARKUP_ONLY.match(segment.text), (
            f"markup carrying content: {segment.text!r}")


def _every_fact_is_owned() -> None:
    """No silent gaps: a fact either says where it came from or says who owes it."""
    document = scripted_answers.scripted_document()
    for question in bank.QUESTIONS:
        stored = store.record(document, question.id)
        assert stored is not None, f"{question.id} has no record at all"
        assert stored.provenance or render.annotation_of(stored), (
            f"{question.id} carries neither a recorded source nor a marker naming an owner, "
            f"so it renders as a fact nobody said")


def _report_reference_provenance(section: Section) -> None:
    if not REFERENCE_PLAN.is_dir():
        return
    stated, sourced = _figure_lines(REFERENCE_PLAN)
    section.note(f"reference plan, test 2: {sourced}/{stated} lines stating a figure carry "
                 f"a source marker or a hedge ({_percent(sourced, stated)}%)")
    section.note("  the reference has no answer store, so the byte invariant cannot be "
                 "measured on it; this counts lines, which is stricter than a fact count")


def _figure_lines(root: Path) -> tuple[int, int]:
    """How many lines state a figure, and how many of those say where the figure came from.

    Reference sections are skipped, because a citation list is not a claim, and fenced code
    is skipped, because a port number in a command is not a design figure.
    """
    stated = sourced = 0
    for document in sorted(root.rglob("*.md")):
        if ".claude" in document.parts:
            continue
        for line in _claim_lines(document.read_text(encoding="utf-8")):
            if not _FIGURE.search(_CITED.sub("", line)):
                continue
            stated += 1
            sourced += bool(_CITED.search(line) or _HEDGED.search(line))
    return stated, sourced


def _claim_lines(text: str) -> list[str]:
    lines, fenced, in_references = [], False, False
    for line in text.splitlines():
        if line.startswith(_FENCE):
            fenced = not fenced
        elif fenced:
            continue
        elif line.startswith("#"):
            in_references = render.REFERENCES_HEADING in line
        elif not in_references and _LETTER.search(line):
            lines.append(line)
    return lines


# --------------------------------------------------- 3. byte-similarity, sourced tier

def _cited_headings() -> list[str]:
    return sorted({question.nist_heading for question in bank.QUESTIONS
                   if question.nist_heading})


def _byte_similarity_on_nist() -> None:
    """Where the plan quotes NIST, it quotes NIST exactly, and as a heading rather than prose."""
    rendered = _headings_of("\n".join(page.text
                                      for page in render.render(scripted_answers
                                                                .scripted_document())))
    for heading in _cited_headings():
        assert heading in bank.NIST_CORPUS, (
            f"{heading!r} is cited as NIST's and is not in the transcribed corpus")
        assert heading in rendered, (
            f"{heading!r} is quoted from NIST and does not appear as a heading, so the plan "
            f"paraphrased a standard whose text it does not own")


def _headings_of(text: str) -> set[str]:
    return {line.lstrip("#").strip().strip("*") for line in text.splitlines()
            if line.startswith("#")}


def _report_reference_similarity(section: Section) -> None:
    if not REFERENCE_PLAN.is_dir():
        return
    found = set()
    for document in sorted(REFERENCE_PLAN.rglob("*.md")):
        if ".claude" not in document.parts:
            found |= _headings_of(document.read_text(encoding="utf-8"))
    cited = _cited_headings()
    matched = sum(heading in found for heading in cited)
    section.note(f"reference plan, test 3: {matched}/{len(cited)} of the NIST headings this "
                 f"bank cites appear verbatim as headings ({_percent(matched, len(cited))}%)")
    appendix = sum(heading in found for heading in bank.NIST_A3_HEADINGS)
    section.note(f"  and {appendix}/{len(bank.NIST_A3_HEADINGS)} of the Appendix A.3 "
                 f"template headings")


def _assert_all_exist(plan: Path, written: tuple[str, ...]) -> None:
    absent = sorted(path for path in written if not (plan / path).exists())
    assert not absent, f"the build step reported writing files it did not write: {absent}"


def _percent(part: int, whole: int) -> int:
    """A share as a whole per cent, always floored. A score never flatters itself."""
    return part * 100 // whole if whole else 0


if __name__ == "__main__":
    main()
