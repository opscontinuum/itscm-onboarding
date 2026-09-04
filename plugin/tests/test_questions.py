"""Invariants on the question bank.

The bank is the schema. Every rule the store enforces at write time rests on the bank being
internally consistent, so these run first and the rest of the suite assumes them.

The check that matters most over time is :func:`_crosswalk_never_justifies`. The partition of
``docs/ITIL-GROUNDING.md`` section 4.3 is only worth having if the forbidden class is
mechanically forbidden, and a future edit that classifies a field ``crosswalk`` would
otherwise be a silent route for an unread paywalled standard to introduce a required field.

The second-most load bearing group is the mechanism pairing. ``mechanism_required`` on its
own can only ever *reject* a figure that arrived without an explanation; it cannot elicit
one, because nothing asks. The checks below make the pairing structural: a question yields a
figure exactly when it is mechanism-required, and a mechanism-required question carries the
follow-up that asks what breaks, on the same record as the figure it explains.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import itscp_questions as bank
from harness import Section, equal

EXPECTED_STARTER_KEYS = 37
#: The seven fields ``templates/answers.example.yaml`` annotates ``# list of {...}``. Named
#: rather than counted, so a rename cannot silently satisfy the check.
YAML_LIST_FIELDS = (
    "business.processes",
    "business.workarounds",
    "app.interconnections",
    "app.validation_pack",
    "app.wrt_activities",
    "infra.replication",
    "continuity.succession",
)

#: One field beyond those seven is modelled as rows here and was a bare ``value: null`` in the
#: YAML: ``governance.risk_register``. A register with an owner and a review date per row is
#: rows; prose that lists risks is not a register. Recorded as a deliberate deviation rather
#: than left to be discovered as an off-by-one in the emitted example.
DELIBERATE_EXTRA_ROW_FIELDS = ("governance.risk_register",)

#: Fields ``docs`` and the brief name as load bearing: they are asked independently, and a
#: discovery value that disagrees becomes a conflict rather than a value.
NEVER_SEEDABLE = (
    "business.mtd.tier0",
    "business.rpo.tier0",
    "business.mbco.tier0",
    "business.tier_signoff",
    "continuity.declaration_authority",
)


def _every_question(assertion, subject: str):
    """Wrap a per-question assertion so a failure names the question that broke it."""

    def run() -> None:
        for question in bank.QUESTIONS:
            try:
                assertion(question)
            except AssertionError as failure:
                raise AssertionError(f"{question.id} ({subject}): {failure}") from None

    return run


def main() -> None:
    section = Section("1", "question bank invariants")

    section.check("every id is unique", lambda: equal(
        len({question.id for question in bank.QUESTIONS}), len(bank.QUESTIONS),
        "distinct ids"))

    section.check("every id sits under its own namespace", _every_question(
        lambda question: _assert_namespace_matches_id(question), "namespace"))

    section.check("every namespace is an owned prefix", _every_question(
        lambda question: _assert_in(question.namespace, bank.NAMESPACES, "namespace"),
        "namespace"))

    section.check("every owner is a role from the roster", _every_question(
        lambda question: _assert_in(question.owner_role, bank.OWNER_VOCABULARY, "owner_role"),
        "owner"))

    section.check("every kind is a known kind", _every_question(
        lambda question: _assert_in(question.kind, bank.KINDS, "kind"), "kind"))

    section.check("every structural provenance is one of the three classes", _every_question(
        lambda question: _assert_in(
            question.structural_provenance, bank.STRUCTURAL_PROVENANCE,
            "structural_provenance"),
        "provenance class"))

    section.check("no field is justified by the crosswalk class", _every_question(
        _crosswalk_never_justifies, "crosswalk rule"))

    section.check("every crosswalk note carries one of the two markers", _every_question(
        _crosswalk_note_is_marked, "crosswalk marker"))

    section.check("every nist field cites a transcribed heading", _every_question(
        _nist_heading_is_transcribed, "nist heading"))

    section.check("no ours field claims a nist heading", _every_question(
        _ours_claims_nothing, "ours claims nothing"))

    section.check("no field opts out of provenance", _every_question(
        lambda question: _assert(question.provenance_required,
                                 "provenance_required is False; the Iron Rule has no exception"),
        "iron rule"))

    section.check("mechanism is required exactly where a figure is", _every_question(
        _mechanism_attaches_to_a_figure, "mechanism"))

    section.check("every figure question carries the paired follow-up", _every_question(
        _figures_are_paired_with_a_mechanism_prompt, "mechanism pairing"))

    section.check("a table of figures pairs each figure with the column that explains it",
                  _every_question(_figure_columns_name_their_explanation, "figure columns"))

    section.check("read-back is required for every narrative", _every_question(
        _narrative_requires_readback, "read-back"))

    section.check("seedable fields name the operation that seeds them", _every_question(
        _seed_operation_matches_seedable, "seeding"))

    section.check("load-bearing fields are never seedable", _no_load_bearing_field_is_seedable)

    section.check("row questions declare their columns", _every_question(
        _rows_declare_columns, "columns"))

    section.check("the seven annotated list fields are all rows", _yaml_list_fields_are_rows)

    section.check("no field is rows by accident", _row_fields_are_the_declared_ones)

    section.check("enum questions offer options", _every_question(
        _enums_offer_options, "options"))

    section.check("every question carries a prompt and guidance", _every_question(
        _prompt_and_guidance_are_present, "prose"))

    section.check("the starter set is the pinned denominator", lambda: equal(
        len(bank.STARTER_KEYS), EXPECTED_STARTER_KEYS, "starter keys"))

    section.check("every starter key is in the bank", _starter_keys_are_in_the_bank)

    section.check("lookup by id finds every question", _lookup_round_trips)

    section.check("every discrepancy has a known kind", _discrepancy_kinds_are_closed)

    section.finish()


def _assert(condition: object, message: str) -> None:
    assert condition, message


def _assert_in(value: str, permitted, field_name: str) -> None:
    assert value in permitted, f"{field_name}={value!r} is not in the permitted set"


def _assert_namespace_matches_id(question) -> None:
    prefix = question.id.split(".", 1)[0]
    assert prefix == question.namespace, (
        f"id starts {prefix!r} but namespace is {question.namespace!r}; a skill writes only "
        f"within its own prefix"
    )


def _crosswalk_never_justifies(question) -> None:
    assert question.structural_provenance != "crosswalk", bank.CROSSWALK_NEVER_JUSTIFIES


def _crosswalk_note_is_marked(question) -> None:
    if not question.crosswalk_note:
        return
    assert any(marker in question.crosswalk_note for marker in bank.CROSSWALK_MARKERS), (
        f"crosswalk note carries neither marker: {question.crosswalk_note!r}"
    )


def _nist_heading_is_transcribed(question) -> None:
    if question.structural_provenance != "nist":
        return
    assert question.nist_heading, "classified nist but cites no heading"
    assert question.nist_heading in bank.NIST_CORPUS, (
        f"{question.nist_heading!r} is not in the transcribed NIST corpus"
    )
    assert question.nist_source, "classified nist but names no source location"


def _ours_claims_nothing(question) -> None:
    if question.structural_provenance != "ours":
        return
    assert not question.nist_heading, (
        f"classified ours but claims NIST heading {question.nist_heading!r}"
    )


def _mechanism_attaches_to_a_figure(question) -> None:
    """A figure and a demand for its mechanism are the same thing, in both directions.

    The reverse direction is the one that matters. Checking only that mechanism_required
    implies a figure lets a new duration question ship without the flag, and a duration with
    no mechanism is the defect the flag exists to catch.
    """
    if question.mechanism_required:
        assert question.kind in bank.FIGURE_KINDS, (
            f"mechanism_required on a {question.kind!r} field; a mechanism explains a figure"
        )
    if question.kind in bank.FIGURE_KINDS:
        assert question.mechanism_required, (
            f"kind is {question.kind!r} and nothing demands the mechanism behind the figure"
        )


def _figures_are_paired_with_a_mechanism_prompt(question) -> None:
    """The pairing, stated as a property of the record rather than as interviewer habit.

    A mechanism the store demands and no question asks for is a rule that can only refuse an
    answer. The follow-up lives on the same record as the figure because that is where the
    store keeps the mechanism.
    """
    wants_a_mechanism = question.mechanism_required or bool(question.figure_columns)
    if not wants_a_mechanism:
        assert not question.mechanism_prompt, (
            f"carries a mechanism follow-up but yields no figure: "
            f"{question.mechanism_prompt!r}"
        )
        return
    assert question.mechanism_prompt.strip(), (
        "yields a figure and asks nothing about what breaks; mechanism_required can refuse "
        "an answer but only a question can elicit one"
    )
    assert question.mechanism_prompt.strip().endswith("?"), (
        f"the mechanism follow-up is not a question: {question.mechanism_prompt!r}"
    )
    assert question.mechanism_prompt != question.prompt, (
        "the mechanism follow-up repeats the question that produced the figure"
    )


def _figure_columns_name_their_explanation(question) -> None:
    """A figure in a table is still a figure, so its row carries the cell that explains it."""
    if not question.figure_columns:
        return
    assert question.kind == "rows", (
        f"figure_columns on a {question.kind!r} field; only a table has columns"
    )
    for figure, explanation in question.figure_columns.items():
        assert figure in question.columns, f"figure column {figure!r} is not a column"
        assert explanation in question.columns, (
            f"the column said to explain {figure!r} is not a column: {explanation!r}"
        )
        assert explanation != figure, (
            f"{figure!r} is said to explain itself, which explains nothing"
        )


def _narrative_requires_readback(question) -> None:
    if question.kind != "narrative":
        return
    assert question.readback_required, (
        "a narrative drafted from someone's understanding is attributable only once they "
        "have confirmed it"
    )


def _seed_operation_matches_seedable(question) -> None:
    if question.seedable:
        assert question.seed_operation, "seedable but names no read-only operation"
    else:
        assert not question.seed_operation, (
            f"not seedable but names operation {question.seed_operation!r}"
        )


def _no_load_bearing_field_is_seedable() -> None:
    for key in NEVER_SEEDABLE:
        question = bank.BY_ID[key]
        assert not question.seedable, (
            f"{key} is seedable; a tier, an MTD, an RPO, an MBCO or a declaration authority "
            f"is asked independently and a disagreeing discovery value becomes a conflict"
        )


def _rows_declare_columns(question) -> None:
    if question.kind == "rows":
        assert question.columns, "kind is rows but declares no columns"
    else:
        assert not question.columns, f"kind is {question.kind!r} but declares columns"


def _enums_offer_options(question) -> None:
    if question.kind == "enum":
        assert question.options, "kind is enum but offers no options"
    else:
        assert not question.options, f"kind is {question.kind!r} but offers options"


def _prompt_and_guidance_are_present(question) -> None:
    assert question.prompt.strip(), "has no prompt"
    assert question.guidance.strip(), "has no guidance"
    assert question.records.strip(), "does not say what it records"


def _yaml_list_fields_are_rows() -> None:
    for key in YAML_LIST_FIELDS:
        equal(bank.BY_ID[key].kind, "rows", f"kind of {key}")


def _row_fields_are_the_declared_ones() -> None:
    actual = {entry.id for entry in bank.row_questions()}
    expected = set(YAML_LIST_FIELDS) | set(DELIBERATE_EXTRA_ROW_FIELDS)
    equal(sorted(actual), sorted(expected), "fields modelled as rows")


def _starter_keys_are_in_the_bank() -> None:
    unknown = [key for key in bank.STARTER_KEYS if key not in bank.BY_ID]
    assert not unknown, f"starter keys absent from the bank: {unknown}"


def _lookup_round_trips() -> None:
    for question in bank.QUESTIONS:
        equal(bank.question(question.id), question, f"lookup of {question.id}")
    assert bank.question("nonexistent.key") is None, "lookup invented a question"


def _discrepancy_kinds_are_closed() -> None:
    for discrepancy in bank.NIST_DISCREPANCIES:
        _assert_in(discrepancy.kind, bank.DISCREPANCY_KINDS, "discrepancy kind")


if __name__ == "__main__":
    main()
