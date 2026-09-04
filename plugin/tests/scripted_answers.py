"""A scripted answer set: one store, filled without a human and without a model.

The acceptance harness needs an interview it can replay. This module is that interview,
written down. It walks the question bank and produces a valid record for every field, so it
cannot go stale when the bank grows: a new question gets an answer here automatically, and
the day the store learns a new rule this file fails loudly rather than quietly covering less.

The values are invented and say so. No real system, person, region or identifier appears
anywhere in this file, because a fixture that carries a real one becomes a leak the moment
somebody copies it into a bug report.

The mix is deliberate. A store where every field is ANSWERED and confident proves nothing
about a renderer whose whole job is to make gaps visible, so :data:`EXCEPTIONS` names the
handful of fields that carry each of the other states: a gap nobody has closed, a decision
postponed with a date on it, a field that does not apply, a figure somebody guessed, and two
sources that disagree.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import itscp_questions as bank
import itscp_store as store

#: The interview date every scripted provenance carries. Fixed, so the rendered documents
#: are byte-stable across runs and a diff shows a change in the renderer, not the calendar.
INTERVIEW_DATE = "2026-09-03"

#: The due date the one DEFERRED field carries.
DEFERRAL_DATE = "2026-12-01"

#: The system this scripted interview is about. Invented.
SYSTEM_NAME = "Ledger Suite"

#: Filler for a scalar text answer, per kind. Every one is obviously invented.
_VALUE_BY_KIND: dict[str, object] = {
    "text": "the northern data hall",
    "narrative": "The order is stated here as the interviewee gave it, in their words, "
                 "read back to them and confirmed before it was written down.",
    "duration": 4,
    "number": 12,
    "currency": 1800,
    "date": INTERVIEW_DATE,
    "list": ["the first item", "the second item"],
    "code": "the recorded command, reproduced exactly",
    "diagram": "one node, one edge",
    "citation": "an internal note, dated and filed",
    "blank": "",
    "range": "between two and four",
    "reference": "the same role named in the roster",
}

#: What one row of a table answer says, per column name, when the column has no enum.
_ROW_FILLER = "as recorded in the interview"

#: The fields that carry a state other than a confident ANSWERED, and which state.
#: Chosen to put one of every rendering rule in front of the renderer at least once.
EXCEPTIONS: dict[str, str] = {
    "business.workarounds": "MISSING",
    "governance.risk_register": "DEFERRED",
    "infra.measured_rtt_ms": "NOT_APPLICABLE",
    "business.rpo.tier0": "LOW_CONFIDENCE",
    "infra.standby_cost_floor": "CONFLICT",
}


def scripted_document() -> dict:
    """The whole bank, answered as scripted. Deterministic and free of real identifiers."""
    document = store.new_document(SYSTEM_NAME)
    for question in bank.QUESTIONS:
        document = store.put(document, _record_for(question))
    return document


def stored_scalars(document: dict) -> frozenset[str]:
    """Every scalar the store holds, stringified: what an ``answer`` segment may say.

    Rows are flattened to their cells, because a table renders one cell per segment and a
    cell that is not in this set is a cell the renderer invented.
    """
    texts: set[str] = set()
    for stored in document["facts"].values():
        texts.update(_scalars_of(stored.value))
        texts.update(text for text in (stored.provenance, stored.mechanism) if text)
        if stored.conflict is not None:
            texts.update(_scalars_of(stored.conflict.value))
            texts.add(stored.conflict.provenance)
            texts.add(stored.conflict.decision_owner)
    return frozenset(texts)


def _scalars_of(value: object) -> set[str]:
    if isinstance(value, list):
        return {text for item in value for text in _scalars_of(item)}
    if isinstance(value, dict):
        return {text for item in value.values() for text in _scalars_of(item)}
    if value is None:
        return set()
    return {str(value)}


def _record_for(question: bank.Question) -> store.Record:
    state = EXCEPTIONS.get(question.id, "ANSWERED")
    if state == "MISSING":
        return store.Record(question.id, "MISSING", owner=question.owner_role)
    if state == "DEFERRED":
        return store.Record(question.id, "DEFERRED", owner=question.owner_role,
                            due=DEFERRAL_DATE)
    if state == "NOT_APPLICABLE":
        return store.Record(question.id, "NOT_APPLICABLE",
                            reason="this environment has one region and no second leg to measure")
    answered = _answered(question, "low" if state == "LOW_CONFIDENCE" else "high")
    if state != "CONFLICT":
        return answered
    return _with_a_conflict(answered)


def _answered(question: bank.Question, confidence: str) -> store.Record:
    return store.Record(
        question.id, "ANSWERED",
        value=_value_for(question),
        mechanism="observed on the last rehearsal" if question.mechanism_required else "",
        provenance=_provenance_for(question),
        confidence=confidence,
        readback="confirmed" if question.readback_required else "not_required",
    )


def _with_a_conflict(answered: store.Record) -> store.Record:
    conflict = store.Conflict(
        value=2400,
        provenance="document:finance/standing-costs.md",
        decision_owner="business owner",
        notes="the finance record and the engineer disagree about the standing floor",
    )
    return store.Record(**{**vars(answered), "conflict": conflict})


def _provenance_for(question: bank.Question) -> str:
    if question.seedable and question.seed_operation:
        return f"oci-discovery:{question.seed_operation}"
    role = question.owner_role.lower().replace("/", "-").replace(" ", "-")
    return f"interview:{role}:{INTERVIEW_DATE}"


def _value_for(question: bank.Question) -> object:
    if question.kind == "rows":
        return [_row_for(question)]
    if question.kind == "enum":
        return question.options[0]
    return _VALUE_BY_KIND[question.kind]


def _row_for(question: bank.Question) -> dict[str, str]:
    options = question.enum_columns
    return {column: options[column][0] if column in options else _ROW_FILLER
            for column in question.columns}
