"""The per-session Q and A transcript: append-only, and distinct from the answer store.

The store holds current state. A superseded value is no longer current, so the store cannot
answer "where did the four-hour figure come from". The transcript can: it is what was asked,
what was said, by whom and when, in order, including the questions that got no answer.

An unanswered question with a named owner is the toolkit's most valuable single output, so
asking and getting nothing is a recorded event here rather than an absence.
"""
from __future__ import annotations

import sys
import tempfile
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import itscp_session as session
from harness import Section, equal

WHEN = "2026-09-02T10:15:00Z"
LATER = "2026-09-02T10:22:00Z"
ROLE = "business owner"
NAME = "Interviewee A"


def _asked(**overrides) -> session.Entry:
    fields = {
        "event": "asked",
        "at": WHEN,
        "interviewee_role": ROLE,
        "interviewee_name": NAME,
        "question_id": "business.mtd.tier0",
        "prompt": bank_prompt("business.mtd.tier0"),
    }
    fields.update(overrides)
    return session.Entry(**fields)


def bank_prompt(question_id: str) -> str:
    return session.bank.BY_ID[question_id].prompt


def main() -> None:
    section = Section("3", "session transcript")

    section.rejects(
        "an unknown event kind is refused",
        lambda: session.validate(_asked(event="chatted")),
        "event must be one of")

    section.rejects(
        "an entry about an unknown question is refused",
        lambda: session.validate(_asked(question_id="business.invented")),
        "is not a key in the question bank")

    section.rejects(
        "an entry with no timestamp is refused",
        lambda: session.validate(_asked(at="")),
        "every entry is timestamped")

    section.rejects(
        "an entry with no interviewee role is refused",
        lambda: session.validate(_asked(interviewee_role="")),
        "every entry names who was in the room")

    section.rejects(
        "an interviewee role outside the roster is refused",
        lambda: session.validate(_asked(interviewee_role="Head of Finance Systems")),
        "must be a role from the roster")

    section.rejects(
        "an asked event with no prompt is refused",
        lambda: session.validate(_asked(prompt="")),
        "records the prompt exactly as asked")

    section.rejects(
        "an answered event with no answer is refused",
        lambda: session.validate(_asked(event="answered", answer="")),
        "records the answer exactly as given")

    section.rejects(
        "an unanswered event with no owner is refused",
        lambda: session.validate(_asked(event="unanswered", answer="I do not know")),
        "an unanswered question records who would know")

    section.check("an unanswered question is a recorded event", _unanswered_is_recorded)

    section.rejects(
        "a read-back with nothing drafted is refused",
        lambda: session.validate(_asked(event="readback_confirmed", answer="Yes")),
        "a read-back records what was shown")

    section.check("the read-back cycle is three events", _readback_cycle_is_recorded)
    section.check("a rejected draft is distinguishable from a confirmed one",
                  _rejected_draft_is_distinguishable)

    section.check("appending never rewrites history", _append_never_rewrites)
    section.check("a correction is appended, not applied in place", _correction_is_appended)
    section.check("entries keep the order they were appended in", _order_is_preserved)
    section.check("a transcript round trips through tomllib", _transcript_round_trips)
    section.check("a session id is stable across appends", _session_id_is_stable)
    section.check("the transcript records the store mutation", _mutation_is_recorded)
    section.check("a corrupt transcript is reported, never reset", _corrupt_transcript_reported)
    section.check("the file says it is sensitive", _file_warns_it_is_sensitive)

    section.finish()


def _unanswered_is_recorded() -> None:
    entry = _asked(event="unanswered", answer="I do not know whether the file has a cut-off.",
                   owner="business owner",
                   notes="Raised 2026-09-02; Treasury to confirm.")
    session.validate(entry)
    equal(entry.event, "unanswered", "event")


def _readback_cycle_is_recorded() -> None:
    log = session.new_transcript("s-001", "Payments")
    log = session.append(log, _asked(question_id="app.start_order",
                                     prompt=bank_prompt("app.start_order"),
                                     interviewee_role="lead engineer"))
    log = session.append(log, _asked(
        event="drafted", question_id="app.start_order", interviewee_role="lead engineer",
        prompt=bank_prompt("app.start_order"),
        drafted="The database comes up first, then the application tier one node at a time.",
        notes="Drafted from what the lead engineer described plus runbooks/RB-01."))
    log = session.append(log, _asked(
        event="readback_corrected", at=LATER, question_id="app.start_order",
        interviewee_role="lead engineer", prompt=bank_prompt("app.start_order"),
        drafted="The database comes up first, then the application tier one node at a time.",
        answer="The database has to be open read write, not just up.",
        mutation="app.start_order ANSWERED readback=corrected"))
    equal([entry.event for entry in log["entries"]],
          ["asked", "drafted", "readback_corrected"], "the read-back cycle")


def _rejected_draft_is_distinguishable() -> None:
    confirmed = _asked(event="readback_confirmed", drafted="A draft.", answer="Yes, that is it.")
    rejected = _asked(event="readback_rejected", drafted="A draft.",
                      answer="No, that is not what I said.", owner="business owner")
    session.validate(confirmed)
    session.validate(rejected)
    assert confirmed.event != rejected.event, "confirmed and rejected are the same event"


def _append_never_rewrites() -> None:
    log = session.new_transcript("s-001", "Payments")
    first = session.append(log, _asked())
    second = session.append(first, _asked(event="answered", at=LATER, answer="Four hours."))
    equal(len(first["entries"]), 1, "the first transcript after a second append")
    equal(len(second["entries"]), 2, "the second transcript")
    equal(second["entries"][0], first["entries"][0], "the first entry after an append")


def _correction_is_appended() -> None:
    log = session.new_transcript("s-001", "Payments")
    log = session.append(log, _asked(event="answered", answer="Four hours."))
    log = session.append(log, _asked(event="answered", at=LATER, answer="Six hours.",
                                     notes="Interviewee corrected themselves."))
    equal([entry.answer for entry in log["entries"]], ["Four hours.", "Six hours."],
          "both answers, in order")


def _order_is_preserved() -> None:
    log = session.new_transcript("s-001", "Payments")
    for index in range(5):
        log = session.append(log, _asked(answer="", notes=f"entry {index}"))
    equal([entry.notes for entry in log["entries"]],
          [f"entry {index}" for index in range(5)], "append order")


def _transcript_round_trips() -> None:
    log = session.new_transcript("s-001", "Payments")
    log = session.append(log, _asked())
    log = session.append(log, _asked(
        event="answered", at=LATER,
        answer="Four hours.\n\nAt hour five the bank file has gone and settlement defers a "
               "day. That is the point it stops being ours to fix.",
        mutation="business.mtd.tier0 ANSWERED confidence=medium"))
    log = session.append(log, _asked(
        event="unanswered", question_id="business.mbco.tier0",
        prompt=bank_prompt("business.mbco.tier0"),
        answer="I would have to ask Treasury.", owner="business owner"))
    text = session.emit(log)
    reread = session.load_transcript(tomllib.loads(text))
    equal(session.as_comparable(reread), session.as_comparable(log),
          f"transcript after a round trip\n--- emitted ---\n{text}")


def _session_id_is_stable() -> None:
    log = session.new_transcript("s-001", "Payments")
    for _ in range(3):
        log = session.append(log, _asked())
    equal(log["meta"]["session_id"], "s-001", "session id after three appends")


def _mutation_is_recorded() -> None:
    entry = _asked(event="answered", answer="Four hours.",
                   mutation="business.mtd.tier0 ANSWERED confidence=medium")
    session.validate(entry)
    assert entry.mutation, "an answered entry recorded no store mutation"


def _corrupt_transcript_reported() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "session-001.toml"
        path.write_text("[[entries]\nbroken", encoding="utf-8")
        try:
            session.SessionLog(path).read()
        except session.StoreError as reported:
            assert "nothing has been overwritten" in str(reported).lower(), (
                f"reported without saying the file is intact: {reported}")
            return
        raise AssertionError("a corrupt transcript was accepted")


def _file_warns_it_is_sensitive() -> None:
    log = session.append(session.new_transcript("s-001", "Payments"), _asked())
    text = session.emit(log)
    assert "GITIGNORED" in text, f"the transcript does not warn it is sensitive:\n{text[:400]}"


if __name__ == "__main__":
    main()
