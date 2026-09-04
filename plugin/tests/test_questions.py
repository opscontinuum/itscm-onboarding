"""Invariants on the question bank.

The bank is the schema. Every rule the store enforces at write time rests on the bank being
internally consistent, so these run first and the rest of the suite assumes them.

The check that matters most over time is :func:`_crosswalk_never_justifies`. The partition
of ``docs/ITIL-GROUNDING.md`` section 4.3, extended here by a fourth class, is only worth
having if the forbidden class is mechanically forbidden, and a future edit that classifies a
field ``crosswalk`` would otherwise be a silent route for an unread paywalled standard to
introduce a required field.

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

EXPECTED_STARTER_KEYS = 82
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

#: Every other field modelled as rows, named rather than counted so that a question cannot
#: become a table by accident. ``governance.risk_register`` was a bare ``value: null`` in the
#: YAML; a register with an owner and a review date per row is rows, and prose that lists
#: risks is not a register. The rest arrived with the questions recovered from the reference
#: plan, where the same content is carried as a table in the plan itself.
DELIBERATE_EXTRA_ROW_FIELDS = (
    "governance.risk_register",
    "system.assumptions",
    "business.tier_targets",
    "business.tier_assignment",
    "business.freeze_periods",
    "app.validation_data_tests",
    "app.unsafe_reruns",
    "infra.irreversible_choices",
    "infra.licensing",
    "infra.offsite_storage",
    "continuity.contact_roster",
    "continuity.vendor_contacts",
    "continuity.vendor_obligations",
    "continuity.decision_and_recovery_roles",
    "governance.associated_plans",
    "governance.drill_levels",
)

#: The plan rows that had no question at all, as the NIST headings a question now has to
#: cite. Nine were named in the brief; three more turned up in the same sweep and are here
#: because the reference plan carries content for each of them and nothing elicited it.
NIST_ROWS_THAT_OWED_A_QUESTION = (
    "1.3 Assumptions",
    "4.2 Recovery Procedures",
    "5.2 Validation Data Testing",
    "5.4 Recovery Declaration",
    "5.5 Notifications (users)",
    "5.6 Cleanup",
    "5.7 Offsite Data Storage",
    "5.8 Data Backup",
    "5.9 Event Documentation",
    "APPENDIX A PERSONNEL CONTACT LIST",
    "APPENDIX B VENDOR CONTACT LIST",
    "APPENDIX K ASSOCIATED PLANS AND PROCEDURES",
)

#: The tenth row of the brief's nine, which cannot be named by a NIST heading because it has
#: none: ``NIST_DISCREPANCIES`` records that no appendix of vendor SLAs and reciprocal
#: agreements exists in any of the three templates, and reclassifies the row ours.
VENDOR_OBLIGATIONS_KEY = "continuity.vendor_obligations"

#: The platform facts the reference plan carries as unconfirmed assumptions. Every one of
#: them is something a person knows and nobody was asked to confirm, which is how a human
#: fact ends up in an assumption table. Each is read back before it is written down.
ASSUMPTION_BEARING = (
    "system.assumptions",
    "system.component_terms",
    "system.releases",
    "system.operating_systems",
    "system.instances",
    "infra.inter_region_transport",
    "infra.storage_constraints",
    "infra.shared_storage",
)

#: The columns an assumption row carries beyond the assumption itself. A flag on an
#: unconfirmed fact says it is unconfirmed; these say who closes it and by when.
ASSUMPTION_COLUMNS = ("owner", "confirm_by")

#: The role question. NIST's own template names posts, and a customer does not know them; a
#: question that asks who the ISCP Director is teaches the interviewee the answer.
ROLE_CROSSWALK_KEY = "continuity.decision_and_recovery_roles"

#: Words that would mean the question had asked for a post rather than for a duty.
POSTS_NOBODY_SHOULD_BE_ASKED_FOR = ("Director", "Coordinator", "ISCP")

#: Fields ``docs`` and the brief name as load bearing: they are asked independently, and a
#: discovery value that disagrees becomes a conflict rather than a value.
NEVER_SEEDABLE = (
    "system.impact_level",
    "business.tier_targets",
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

    section.check("every structural provenance is one of the four classes", _every_question(
        lambda question: _assert_in(
            question.structural_provenance, bank.STRUCTURAL_PROVENANCE,
            "structural_provenance"),
        "provenance class"))

    section.check("method is the fourth class and is in use", _method_is_a_class_in_use)

    section.check("every method field carries the text the toolkit supplies", _every_question(
        _method_supplies_its_own_text, "method statement"))

    section.check("no field is justified by the crosswalk class", _every_question(
        _crosswalk_never_justifies, "crosswalk rule"))

    section.check("every crosswalk note carries one of the two markers", _every_question(
        _crosswalk_note_is_marked, "crosswalk marker"))

    section.check("every nist field cites a transcribed heading", _every_question(
        _nist_heading_is_transcribed, "nist heading"))

    section.check("only a nist field claims a nist heading", _every_question(
        _only_nist_claims_a_nist_heading, "claims nothing"))

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

    section.check("every plan row that owed a question has one", _the_owed_rows_are_covered)

    section.check("an assumption is read back, owned and dated", _assumptions_are_read_back)

    section.check("the role question asks for duties, not for NIST's posts",
                  _the_role_question_asks_for_duties)

    section.check("the bank asks which impact level was assigned", _the_bank_asks_for_a_level)

    section.check("the moderate and high templates letter to M", _moderate_and_high_lettering)

    section.check("the low template omits one appendix and letters one lower",
                  _low_impact_lettering)

    section.check("only the appendices re-letter", _only_the_appendices_move)

    section.check("an unstated impact level is refused, never guessed",
                  _an_unknown_level_is_refused)

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


def _only_nist_claims_a_nist_heading(question) -> None:
    """``ours`` and ``method`` both claim no standards provenance, so neither cites one."""
    if question.structural_provenance == "nist":
        return
    assert not question.nist_heading, (
        f"classified {question.structural_provenance!r} but claims NIST heading "
        f"{question.nist_heading!r}"
    )


def _method_is_a_class_in_use() -> None:
    """The fourth class exists, and something is actually classified by it.

    A class nobody uses is a claim in a tuple. The posture model, the decomposition of
    maximum tolerable downtime and the one-way-door rule are the toolkit's own approach:
    neither elicited from anybody nor transcribed from anything, and the reference plan
    carries all three with no provenance a reader can check.
    """
    equal(len(bank.STRUCTURAL_PROVENANCE), 4, "the structural-provenance classes")
    _assert_in("method", bank.STRUCTURAL_PROVENANCE, "the fourth class")
    counts = bank.structural_provenance_counts()
    assert counts["method"], (
        "method is declared and nothing is classified by it, so the class is a word in a "
        "tuple rather than a partition of the bank"
    )


def _method_supplies_its_own_text(question) -> None:
    """Method content is text the toolkit supplies, so the bank has to carry the text."""
    if question.structural_provenance == "method":
        assert question.method_statement.strip(), (
            "classified method and supplies no text; method means the toolkit brought the "
            "element, and an element nobody wrote down cannot be shown to a reader as ours"
        )
        return
    assert not question.method_statement, (
        f"supplies method text without being classified method: "
        f"{question.method_statement!r}"
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
    assert "?" in question.mechanism_prompt, (
        f"the mechanism follow-up asks nothing: {question.mechanism_prompt!r}"
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


#: Where the coverage map's appendix lettering came apart, restated as the two anchors the
#: derivation has to reproduce. Both are already recorded in ``bank.NIST_DISCREPANCIES``: the
#: business impact analysis is Appendix K in the low template and L in the other two, and the
#: document change page is L in the low template and M in the other two.
_LOW_ANCHORS = (
    ("BUSINESS IMPACT ANALYSIS", "APPENDIX K BUSINESS IMPACT ANALYSIS"),
    ("DOCUMENT CHANGE PAGE", "APPENDIX L DOCUMENT CHANGE PAGE"),
    ("ASSOCIATED PLANS AND PROCEDURES", "APPENDIX J ASSOCIATED PLANS AND PROCEDURES"),
    ("INTERCONNECTIONS TABLE", "APPENDIX H INTERCONNECTIONS TABLE"),
)

_HIGH_ANCHORS = (
    ("BUSINESS IMPACT ANALYSIS", "APPENDIX L BUSINESS IMPACT ANALYSIS"),
    ("DOCUMENT CHANGE PAGE", "APPENDIX M DOCUMENT CHANGE PAGE"),
    ("ALTERNATE STORAGE, SITE, AND TELECOMMUNICATIONS",
     "APPENDIX F ALTERNATE STORAGE, SITE, AND TELECOMMUNICATIONS"),
    ("INTERCONNECTIONS TABLE", "APPENDIX I INTERCONNECTIONS TABLE"),
)

_ABSENT_FROM_THE_LOW_TEMPLATE = "ALTERNATE STORAGE, SITE, AND TELECOMMUNICATIONS"


def _the_bank_asks_for_a_level() -> None:
    """The letter is a function of the categorisation, so the categorisation is elicited.

    The reference plan never states one, and its own compliance skill says a plan that states
    none has that row REFUTED. A toolkit whose appendix lettering depends on an answer nobody
    is asked for would reproduce that.
    """
    question = bank.BY_ID[bank.IMPACT_LEVEL_KEY]
    equal(question.kind, "enum", f"kind of {bank.IMPACT_LEVEL_KEY}")
    equal(question.options, bank.IMPACT_LEVELS, "the levels offered")
    assert question.readback_required, (
        "the impact level decides which template the plan is graded against and is not "
        "written down without being said back")


def _lettering_matches(anchors, impact_level: str) -> None:
    for title, expected in anchors:
        equal(bank.heading_in_scheme(f"APPENDIX ? {title}", impact_level), expected,
              f"{title} at {impact_level} impact")


def _moderate_and_high_lettering() -> None:
    for impact_level in ("moderate", "high"):
        _lettering_matches(_HIGH_ANCHORS, impact_level)


def _low_impact_lettering() -> None:
    _lettering_matches(_LOW_ANCHORS, "low")
    equal(bank.heading_in_scheme(f"APPENDIX F {_ABSENT_FROM_THE_LOW_TEMPLATE}", "low"), "",
          "the appendix the low template does not have")


def _only_the_appendices_move() -> None:
    """A section number is the same in all three templates; only the letters shift."""
    for heading in bank.NIST_A3_HEADINGS:
        if heading.startswith("APPENDIX "):
            continue
        equal(bank.heading_in_scheme(heading, "low"), heading, f"{heading} at low impact")


def _an_unknown_level_is_refused() -> None:
    for level in ("", "medium", "LOW"):
        try:
            bank.heading_in_scheme("APPENDIX L BUSINESS IMPACT ANALYSIS", level)
        except ValueError:
            continue
        raise AssertionError(
            f"lettered an appendix at impact level {level!r}; an uncategorised system has no "
            f"template, and picking one silently is the guess the toolkit exists to refuse")


def _the_owed_rows_are_covered() -> None:
    """Every plan row the bank could not fill, now filled.

    A row of the plan with no question behind it is a section the toolkit will render as a
    heading with nothing under it, or worse, a section somebody fills in by hand and nobody
    can trace. The reference plan carries content for every row named here.
    """
    cited = {question.nist_heading for question in bank.QUESTIONS if question.nist_heading}
    uncited = [heading for heading in NIST_ROWS_THAT_OWED_A_QUESTION if heading not in cited]
    assert not uncited, f"plan rows still with no question: {uncited}"
    vendors = bank.BY_ID[VENDOR_OBLIGATIONS_KEY]
    equal(vendors.structural_provenance, "ours", f"class of {VENDOR_OBLIGATIONS_KEY}")


def _assumptions_are_read_back() -> None:
    """An assumption is a human fact nobody confirmed, so confirming it is the whole fix.

    The reference plan's seven material assumptions are all things a person knows: which
    release, which operating system, one instance or several, how the two regions are joined.
    They became assumptions because the interview never said them back. A flag marking them
    unconfirmed is not the fix; a read-back, an owner and a date are.
    """
    for key in ASSUMPTION_BEARING:
        assert bank.BY_ID[key].readback_required, (
            f"{key} carries a fact that ends up in an assumption table and is written down "
            f"without being said back")
    columns = bank.BY_ID["system.assumptions"].columns
    for column in ASSUMPTION_COLUMNS:
        assert column in columns, (
            f"an assumption row has no {column!r} column, so the gap is flagged and unowned")


def _the_role_question_asks_for_duties() -> None:
    """Ask who decides and who recovers. Never ask a customer to name an ISCP Director.

    The post names belong to NIST's template, not to the organisation being interviewed.
    Putting one in the question supplies the answer, and the plan then records a role the
    customer heard from us rather than the one they actually have.
    """
    question = bank.BY_ID[ROLE_CROSSWALK_KEY]
    equal(question.structural_provenance, "method", f"class of {ROLE_CROSSWALK_KEY}")
    asked = f"{question.prompt} {question.guidance}"
    for post in POSTS_NOBODY_SHOULD_BE_ASKED_FOR:
        assert post not in asked, (
            f"the question puts {post!r} in front of the interviewee, which supplies the "
            f"answer it is meant to elicit")
    duties = question.enum_columns.get("duty", ())
    assert len(duties) > 1, (
        "the question offers no duty vocabulary, so nothing distinguishes who decides from "
        "who recovers")


def _discrepancy_kinds_are_closed() -> None:
    for discrepancy in bank.NIST_DISCREPANCIES:
        _assert_in(discrepancy.kind, bank.DISCREPANCY_KINDS, "discrepancy kind")


if __name__ == "__main__":
    main()
