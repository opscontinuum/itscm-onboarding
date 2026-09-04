"""Enforcement rules, round-trip fidelity and coverage arithmetic for the answer store.

One check per rule, each proving the rule refuses bad input rather than merely accepting
good input. A validator that accepts everything passes a suite that only tries valid data.

The round-trip check is the load-bearing one. The emitter is hand written; ``tomllib`` is
the standard library's parser. Emitting every value shape the bank can hold, parsing it back
with ``tomllib`` and comparing structures is what proves the emitter correct against an
implementation nobody here wrote.
"""
from __future__ import annotations

import sys
import tempfile
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import itscp_store as store
from harness import Section, equal

INTERVIEW = "interview:business-owner:2026-09-02"
DISCOVERY = "oci-discovery:ListVolumeGroupReplicas"

#: A coverage fixture whose percentage is not a whole number, so a rounding bug shows up.
#: 17 of 37 is 45.94 per cent: floors to 45, rounds to 46. itscp-build's own illustration
#: prints 46 for these figures, which is the bug this check exists to keep out of the code.
FIXTURE_COVERED = 17
FIXTURE_TOTAL = 37
FIXTURE_PERCENT = 45


def _answered(key: str = "business.mbco.tier0", **overrides) -> store.Record:
    fields = {
        "key": key,
        "status": "ANSWERED",
        "value": "Card authorisations only, no settlement",
        "provenance": INTERVIEW,
        "confidence": "medium",
        "readback": "confirmed",
    }
    fields.update(overrides)
    return store.Record(**fields)


def main() -> None:
    section = Section("2", "answer store enforcement")

    section.rejects(
        "an unknown key is not a field",
        lambda: store.validate(store.Record("business.invented", "MISSING",
                                            owner="business owner")),
        "is not a key in the question bank")

    section.rejects(
        "an unknown status is refused",
        lambda: store.validate(store.Record("business.mbco.tier0", "PROBABLY")),
        "status must be one of")

    section.rejects(
        "ANSWERED without a value is refused",
        lambda: store.validate(_answered(value=None)),
        "ANSWERED requires a value")

    section.rejects(
        "ANSWERED without provenance is refused",
        lambda: store.validate(_answered(provenance="")),
        "ANSWERED requires a provenance")

    section.rejects(
        "ANSWERED without confidence is refused",
        lambda: store.validate(_answered(confidence="")),
        "ANSWERED requires a confidence")

    section.rejects(
        "a confidence outside the rubric is refused",
        lambda: store.validate(_answered(confidence="very high")),
        "confidence must be one of")

    section.rejects(
        "MISSING without an owner is refused",
        lambda: store.validate(store.Record("business.mbco.tier0", "MISSING")),
        "MISSING requires an owner")

    section.rejects(
        "an owner outside the roster is refused",
        lambda: store.validate(store.Record("business.mbco.tier0", "MISSING",
                                            owner="Head of Finance Systems")),
        "owner must be a role from the roster")

    section.rejects(
        "DEFERRED without a due date is refused",
        lambda: store.validate(store.Record("business.mbco.tier0", "DEFERRED",
                                            owner="business owner")),
        "DEFERRED requires a due date")

    section.rejects(
        "DEFERRED without an owner is refused",
        lambda: store.validate(store.Record("business.mbco.tier0", "DEFERRED",
                                            due="2026-10-01")),
        "DEFERRED requires an owner")

    section.rejects(
        "a due date that is not a calendar date is refused",
        lambda: store.validate(store.Record("business.mbco.tier0", "DEFERRED",
                                            owner="business owner", due="2026-02-30")),
        "due must be a calendar date")

    section.rejects(
        "NOT_APPLICABLE without a reason is refused",
        lambda: store.validate(store.Record("app.concurrent_processing", "NOT_APPLICABLE")),
        "NOT_APPLICABLE requires a reason")

    section.rejects(
        "an unparseable provenance is refused",
        lambda: store.validate(_answered(provenance="Fiona in accounts told me")),
        "provenance must be one of")

    section.rejects(
        "a provenance meaning the assistant worked it out is refused",
        lambda: store.validate(_answered(provenance="assistant")),
        "no provenance value means the assistant worked it out")

    section.rejects(
        "inferred is refused as a provenance",
        lambda: store.validate(_answered(provenance="inferred")),
        "no provenance value means the assistant worked it out")

    section.rejects(
        "an interview provenance naming a person is refused",
        lambda: store.validate(_answered(provenance="interview:fiona:2026-09-02")),
        "provenance must be one of")

    section.rejects(
        "an interview provenance with no date is refused",
        lambda: store.validate(_answered(provenance="interview:business-owner")),
        "provenance must be one of")

    section.check("the four legal provenance forms are accepted", _legal_provenance_accepted)

    section.rejects(
        "a duration answered with no mechanism is refused",
        lambda: store.validate(_answered("business.mtd.tier0", value="4h",
                                         mechanism="", readback="confirmed")),
        "requires a mechanism")

    section.rejects(
        "a narrative answered without a read-back is refused",
        lambda: store.validate(_answered("continuity.activation_criteria",
                                         value="Two paragraphs of criteria.",
                                         readback="not_required")),
        "requires a read-back")

    section.rejects(
        "an unknown read-back state is refused",
        lambda: store.validate(_answered(readback="probably confirmed")),
        "readback must be one of")

    section.rejects(
        "a conflict with one source is refused",
        lambda: store.validate(_answered(conflict=store.Conflict(
            "24h", INTERVIEW, "business owner", "Same speaker, so not a conflict"))),
        "a conflict needs two distinct sources")

    section.rejects(
        "a conflict with one value is refused",
        lambda: store.validate(_answered(
            value="4h",
            conflict=store.Conflict("4h", "interview:application-owner:2026-09-03",
                                    "business owner", "Same value, so not a conflict"))),
        "a conflict needs two different values")

    section.rejects(
        "a conflict with no named decision owner is refused",
        lambda: store.validate(_answered(conflict=store.Conflict(
            "24h", "interview:application-owner:2026-09-03", "", "Unresolved"))),
        "a conflict needs a named decision owner")

    section.rejects(
        "a conflict on an unanswered field is refused",
        lambda: store.validate(store.Record(
            "business.mbco.tier0", "MISSING", owner="business owner",
            conflict=store.Conflict("24h", "interview:application-owner:2026-09-03",
                                    "business owner", "Unresolved"))),
        "a conflict needs two values")

    section.check("a well formed conflict is accepted", _well_formed_conflict_accepted)

    section.check("supersede keeps the prior value", _supersede_keeps_the_prior_value)
    section.check("supersede never deletes a record", _supersede_never_deletes)
    section.rejects(
        "supersede without a reason is refused",
        _supersede_without_a_reason,
        "superseding requires a reason")

    section.check("coverage counts answered plus not applicable", _coverage_counts)
    section.check("coverage never rounds up", _coverage_never_rounds_up)
    section.check("coverage reports the confidence distribution", _coverage_reports_confidence)
    section.check("coverage of an empty store is zero, not an error", _coverage_of_nothing)
    section.check("coverage can be scoped to one namespace", _coverage_by_namespace)

    section.check("every value shape survives a round trip", _round_trip_every_shape)
    section.check("an absent key stays absent", _absent_keys_are_omitted)
    section.check("comments are regenerated, not preserved", _comments_are_regenerated)
    section.check("guidance reaches the file as comments", _guidance_becomes_comments)
    section.check("a corrupt file is reported, never reset", _corrupt_file_is_reported)
    section.check("a write is atomic", _write_is_atomic)

    section.finish()


def _legal_provenance_accepted() -> None:
    for provenance in (INTERVIEW, DISCOVERY, "document:docs/existing-dr-plan.pdf", "operator",
                       "interview:governance-risk-contact-deputy:2026-09-03"):
        store.validate(_answered(provenance=provenance))


def _well_formed_conflict_accepted() -> None:
    store.validate(_answered(conflict=store.Conflict(
        "at least 24h", "interview:application-owner:2026-09-03", "business owner",
        "Application owner states batch reprocessing alone exceeds the stated MTD.")))


def _supersede_keeps_the_prior_value() -> None:
    document = store.new_document("Payments")
    document = store.put(document, _answered(value="2h"))
    document = store.supersede(
        document, _answered(value="6h", provenance="interview:business-owner:2026-09-10",
                            confidence="high"),
        "Revised after Treasury confirmed the file cut-off is 22:00, not 18:00.")
    record = store.record(document, "business.mbco.tier0")
    equal(record.value, "6h", "current value")
    equal(len(record.superseded), 1, "superseded entries")
    equal(record.superseded[0].value, "2h", "prior value")
    assert record.superseded[0].reason, "a superseded entry with no reason"


def _supersede_never_deletes() -> None:
    document = store.new_document("Payments")
    document = store.put(document, _answered(value="2h"))
    for index, value in enumerate(("4h", "6h", "8h"), start=1):
        document = store.supersede(document, _answered(value=value), f"Revision {index}")
    record = store.record(document, "business.mbco.tier0")
    equal([entry.value for entry in record.superseded], ["2h", "4h", "6h"], "the whole trail")


def _supersede_without_a_reason():
    document = store.put(store.new_document("Payments"), _answered(value="2h"))
    return store.supersede(document, _answered(value="6h"), "")


def _coverage_fixture() -> dict:
    """A store with 14 ANSWERED, 3 NOT_APPLICABLE, 2 DEFERRED and the rest MISSING."""
    document = store.new_document("Payments")
    keys = list(store.bank.STARTER_KEYS)
    confidences = ["high"] * 4 + ["medium"] * 7 + ["low"] * 3
    for key, confidence in zip(keys[:14], confidences):
        document = store.put(document, _fixture_answer(key, confidence))
    for key in keys[14:17]:
        document = store.put(document, store.Record(
            key, "NOT_APPLICABLE", reason="This estate has no such component."))
    for key in keys[17:19]:
        document = store.put(document, store.Record(
            key, "DEFERRED", owner="business owner", due="2026-10-01"))
    for key in keys[19:]:
        document = store.put(document, store.Record(key, "MISSING", owner="business owner"))
    return document


def _fixture_answer(key: str, confidence: str) -> store.Record:
    question = store.bank.BY_ID[key]
    return store.Record(
        key, "ANSWERED", value="stated", provenance=INTERVIEW, confidence=confidence,
        mechanism="stated mechanism" if question.mechanism_required else "",
        readback="confirmed" if question.readback_required else "not_required")


def _coverage_counts() -> None:
    coverage = store.coverage(_coverage_fixture())
    equal(coverage.answered, 14, "answered")
    equal(coverage.not_applicable, 3, "not applicable")
    equal(coverage.deferred, 2, "deferred")
    equal(coverage.missing, FIXTURE_TOTAL - 19, "missing")
    equal(coverage.covered, FIXTURE_COVERED, "covered")
    equal(coverage.total, FIXTURE_TOTAL, "total")


def _coverage_never_rounds_up() -> None:
    coverage = store.coverage(_coverage_fixture())
    equal(coverage.percent, FIXTURE_PERCENT, "17 of 37 floored")
    assert f"{FIXTURE_COVERED}/{FIXTURE_TOTAL} fields ({FIXTURE_PERCENT}%)" in coverage.report(), (
        f"the report line does not show {FIXTURE_PERCENT} per cent:\n{coverage.report()}"
    )


def _coverage_reports_confidence() -> None:
    coverage = store.coverage(_coverage_fixture())
    equal(coverage.confidence, {"high": 4, "medium": 7, "low": 3}, "confidence distribution")
    assert "Confidence of ANSWERED: high 4 | medium 7 | low 3" in coverage.report(), (
        f"the confidence line is missing:\n{coverage.report()}"
    )


def _coverage_of_nothing() -> None:
    coverage = store.coverage(store.new_document("Payments"))
    equal(coverage.percent, 0, "percent of an empty store")
    equal(coverage.covered, 0, "covered in an empty store")


def _coverage_by_namespace() -> None:
    coverage = store.coverage(_coverage_fixture(), namespace="governance")
    equal(coverage.total, len(store.bank.for_namespace("governance")), "governance total")


def _every_value_shape() -> dict:
    """One record per value shape the bank can hold, plus a supersede trail and a conflict."""
    document = store.new_document("Payments")
    document = store.put(document, store.Record(
        "system.name", "ANSWERED", value="Payments Suite", provenance=INTERVIEW,
        confidence="high"))
    document = store.put(document, store.Record(
        "infra.measured_rtt_ms", "ANSWERED", value=61, provenance="operator",
        confidence="high", mechanism="Measured with ten runs of a TCP echo, worst case taken."))
    document = store.put(document, store.Record(
        "continuity.unknown_estimate_default", "ANSWERED", value="declare",
        provenance=INTERVIEW, confidence="medium", readback="confirmed"))
    document = store.put(document, store.Record(
        "infra.last_end_to_end_execution", "ANSWERED", value="2026-03-14",
        provenance="document:evidence/2026-03-drill.md", confidence="high"))
    document = store.put(document, store.Record(
        "app.start_order", "ANSWERED",
        value="The database comes up first and has to be open read write before anything "
              "else is started.\n\nThe application tier follows, one node at a time. Starting "
              "two nodes together has produced a split concurrent-manager state twice, and "
              "the recovery from that is longer than the restart it saved.\n\nThe load "
              "balancer is last, because a health check that passes before the batch queues "
              "have drained will admit traffic the system cannot yet serve.",
        provenance="interview:lead-engineer:2026-09-05", confidence="medium",
        readback="corrected"))
    document = store.put(document, store.Record(
        "infra.replication", "ANSWERED",
        value=[
            {"tier": "0", "mechanism": "Data Guard", "sync": "true", "measured_lag": "0s",
             "failover_behaviour": "automatic", "rebaseline_on_reversal": "false",
             "one_way": "false"},
            {"tier": "1", "mechanism": "volume group replication", "sync": "false",
             "measured_lag": "11m", "failover_behaviour": "manual",
             "rebaseline_on_reversal": "true", "one_way": "true"},
        ],
        provenance=DISCOVERY, confidence="high"))
    document = store.put(document, store.Record(
        "app.concurrent_processing", "NOT_APPLICABLE",
        reason="There is one licensed production environment, so the two cannot run at once."))
    document = store.put(document, store.Record(
        "governance.review_cadence", "DEFERRED", owner="governance/risk contact deputy",
        due="2026-11-30", notes="Awaiting the audit committee's own calendar."))
    document = store.put(document, store.Record(
        "system.business_name", "MISSING", owner="business owner",
        notes="Business owner did not know whether \"Payments\" is the name Finance uses.\n"
              "A quotation mark, a backslash \\ and a tab\there, to exercise the escaper."))
    document = store.put(document, _answered(value="2h"))
    document = store.supersede(document, _answered(value="6h", confidence="high"),
                               "Treasury confirmed the cut-off is 22:00.")
    document = store.put(document, store.Record(
        "business.mtd.tier0", "ANSWERED", value="4h", provenance=INTERVIEW, confidence="low",
        mechanism="The bank file cuts at 18:00.", readback="confirmed",
        conflict=store.Conflict(
            "at least 24h", "interview:application-owner:2026-09-03", "business owner",
            "Application owner states batch reprocessing alone exceeds the stated MTD.")))
    return document


def _emit_and_parse(document: dict) -> tuple[str, dict]:
    text = store.emit(document)
    return text, tomllib.loads(text)


def _round_trip_every_shape() -> None:
    document = _every_value_shape()
    text, parsed = _emit_and_parse(document)
    reread = store.load_document(parsed)
    equal(store.as_comparable(reread), store.as_comparable(document),
          f"structure after a round trip through tomllib\n--- emitted ---\n{text}")


def _absent_keys_are_omitted() -> None:
    document = store.put(store.new_document("Payments"), _answered(value="2h"))
    _, parsed = _emit_and_parse(document)
    equal(list(parsed["facts"]), ["business.mbco.tier0"], "keys in the file")
    assignments = [line for line in store.emit(document).splitlines()
                   if line and not line.startswith("#")]
    stand_ins = [line for line in assignments
                 if line.endswith(("= null", '= ""', "= none", "= nil", "= []"))]
    assert not stand_ins, f"the emitter wrote a stand-in for an absent value: {stand_ins}"
    for question in store.bank.QUESTIONS:
        if question.id != "business.mbco.tier0":
            assert question.id not in parsed["facts"], f"{question.id} appeared uninvited"


def _comments_are_regenerated() -> None:
    document = store.put(store.new_document("Payments"), _answered(value="2h"))
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "answers.toml"
        store.AnswerStore(path).write(document)
        path.write_text(path.read_text() + "\n# a hand written comment\n", encoding="utf-8")
        answer_store = store.AnswerStore(path)
        answer_store.write(answer_store.read())
        assert "a hand written comment" not in path.read_text(encoding="utf-8"), (
            "a comment survived a rewrite; the emitter must re-render from schema and data"
        )


def _guidance_becomes_comments() -> None:
    document = store.put(store.new_document("Payments"), _answered(value="2h"))
    text = store.emit(document)
    guidance = store.bank.BY_ID["business.mbco.tier0"].guidance
    assert guidance.split(".")[0] in text, f"guidance did not reach the file:\n{text}"


def _corrupt_file_is_reported() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "answers.toml"
        path.write_text("this is not [ valid toml", encoding="utf-8")
        try:
            store.AnswerStore(path).read()
        except store.StoreError as reported:
            assert "nothing has been overwritten" in str(reported).lower(), (
                f"a corrupt file was reported without saying the file is intact: {reported}"
            )
            equal(path.read_text(encoding="utf-8"), "this is not [ valid toml",
                  "the corrupt file after a failed read")
            return
        raise AssertionError("a corrupt file was accepted")


def _write_is_atomic() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "nested" / "answers.toml"
        answer_store = store.AnswerStore(path)
        answer_store.write(store.put(store.new_document("Payments"), _answered(value="2h")))
        leftovers = [entry.name for entry in path.parent.iterdir() if entry.name != path.name]
        equal(leftovers, [], "temporary files left behind by a write")


if __name__ == "__main__":
    main()
