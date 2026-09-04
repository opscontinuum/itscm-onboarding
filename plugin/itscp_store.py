"""The answer store: a TOML file, the rules that keep it honest, and a hand written emitter.

``tomllib`` reads. It does not write, and it discards comments, so the emitter here writes
and re-renders every comment from the question bank on every write. That is why comments are
regenerated rather than preserved: guidance lives in the schema, the file is a projection of
schema plus data, and a projection is always current.

Enforcement is the module's reason to exist. A store that accepts anything is a store that
launders a guess into a signed design target, which is the failure
``skills/_method/interview-method.md`` was written to prevent:

    A fact enters the answer store only when a human said it, a read-only API returned it,
    or it is marked MISSING. There is no fourth source.

The provenance enum is closed and there is deliberately no value meaning the assistant
worked it out. :func:`validate` refuses one by name, not only by failing to match a pattern,
so the refusal message says why rather than leaving the caller to guess at the syntax.

Read ``skills/_method/answer-store.md`` for the record shape and
``docs/ITIL-GROUNDING.md`` section 4.3 for the structural-provenance classes.
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

import datetime as _datetime
import os
import re
import tomllib
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import itscp_questions as bank

SCHEMA_VERSION = 1

#: Where a regenerated guidance comment wraps. Wide enough that most guidance is two
#: lines, narrow enough to read beside the values in a terminal.
_COMMENT_WIDTH = 86

#: How ``itscp-build`` names the status counts in its coverage report.
_REPORT_STATUS_ORDER = ("ANSWERED", "NOT_APPLICABLE", "DEFERRED", "MISSING")

#: A calendar date, checked for shape here and for reality by :func:`_is_a_calendar_date`.
_DATE = r"\d{4}-\d{2}-\d{2}"

#: ``interview:<role>:<YYYY-MM-DD>``. The role is the roster role, slugified: the store is
#: shared, so provenance names a role and never a person.
_INTERVIEW_PROVENANCE = re.compile(rf"^interview:(?P<role>[a-z0-9-]+):(?P<date>{_DATE})$")

#: ``oci-discovery:<operation>``, naming the read-only API operation that returned the value.
_DISCOVERY_PROVENANCE = re.compile(r"^oci-discovery:(?P<operation>[A-Za-z][A-Za-z0-9]*)$")

#: ``document:<path>``, naming a document the organisation supplied.
_DOCUMENT_PROVENANCE = re.compile(r"^document:(?P<path>\S.*)$")

#: ``operator``, exactly: the person running the toolkit, about themselves.
_OPERATOR_PROVENANCE = "operator"

#: Words people reach for when they mean "the assistant worked it out". Refused by name so
#: the refusal can explain itself instead of reading as a syntax error.
_FORBIDDEN_PROVENANCE = (
    "assistant", "inferred", "inference", "derived", "generated", "model", "ai", "llm",
    "assumed", "assumption", "default", "reasonable default", "best guess", "estimated",
)

_PROVENANCE_FORMS = (
    "interview:<role>:<YYYY-MM-DD>", "oci-discovery:<operation>", "document:<path>",
    "operator",
)


def _slugify_role(role: str) -> str:
    """The roster role as it appears inside an ``interview:`` provenance."""
    return re.sub(r"[^a-z0-9]+", "-", role.lower()).strip("-")


#: Every role slug an ``interview:`` provenance may name. Derived from the roster rather
#: than listed again, so the two cannot drift.
PROVENANCE_ROLES: frozenset[str] = frozenset(
    _slugify_role(role) for role in bank.OWNER_VOCABULARY
)


class StoreError(Exception):
    """The store file exists but is not usable. Expected, reported, never a crash."""


class ValidationError(Exception):
    """A record breaks one of the store's rules. The message names the rule."""


# --------------------------------------------------------------------------- record shapes

@dataclass(frozen=True)
class Conflict:
    """A second source disagreeing with the record's own value.

    Holds the competing side only; the record holds the first side. Together they are the
    two values and two sources a conflict needs, which is the shape ``answer-store.md``
    fixes. ``decision_owner`` is a role from the roster, because a conflict nobody owns is a
    contradiction the plan will carry into the outage.
    """

    value: Any
    provenance: str
    decision_owner: str
    notes: str = ""


@dataclass(frozen=True)
class Superseded:
    """A value this field used to hold. Written by :func:`supersede`, never deleted."""

    value: Any
    provenance: str
    confidence: str
    reason: str


@dataclass(frozen=True)
class Record:
    """One field of the answer store.

    ``status`` is authoritative and always present. ``value`` is present only when the
    status is ANSWERED; there is no null and no empty-string stand-in, because a field that
    renders as blank is indistinguishable from one that was never asked.

    ``readback`` records how a narrative became attributable. It lives here rather than only
    in the session transcript because the renderer reads the store and never sees the
    transcript, so a store copied without its transcript would otherwise turn unconfirmed
    drafts into facts.
    """

    key: str
    status: str
    value: Any = None
    mechanism: str = ""
    provenance: str = ""
    confidence: str = ""
    owner: str = ""
    due: str = ""
    reason: str = ""
    notes: str = ""
    readback: str = "not_required"
    conflict: Conflict | None = None
    superseded: tuple[Superseded, ...] = ()


# --------------------------------------------------------------------------- validation

def validate(record: Record) -> None:
    """Raise :class:`ValidationError` naming the first rule ``record`` breaks.

    Rules are checked in the order a reader would ask them: is this a real field, is the
    status real, does the status have what it requires, is the provenance one we accept, and
    does this particular question demand more than the status alone does.
    """
    question = bank.question(record.key)
    if question is None:
        raise ValidationError(
            f"{record.key!r} is not a key in the question bank. The bank is the schema; a "
            f"field nobody defined has no owner, no guidance and no place in the plan. Add "
            f"it to itscp_questions.QUESTIONS or correct the key."
        )
    if record.status not in bank.STATUSES:
        raise ValidationError(
            f"{record.key}: status must be one of {', '.join(bank.STATUSES)}; "
            f"got {record.status!r}"
        )
    _validate_status_requirements(record)
    _validate_provenance(record)
    _validate_question_requirements(record, question)
    _validate_conflict(record)


def _validate_status_requirements(record: Record) -> None:
    if record.status == "ANSWERED":
        _require(record.value is not None, record.key,
                 "ANSWERED requires a value. Absence means unanswered, so a field with no "
                 "value is MISSING with a named owner.")
        _require(record.provenance, record.key,
                 "ANSWERED requires a provenance. Nothing enters the store without a source.")
        _require(record.confidence, record.key,
                 "ANSWERED requires a confidence, assigned from how the answer arrived.")
    if record.status == "MISSING":
        _require(record.owner, record.key,
                 "MISSING requires an owner: the role who can answer it. A gap with no name "
                 "on it is a gap nobody closes.")
    if record.status == "DEFERRED":
        _require(record.owner, record.key, "DEFERRED requires an owner.")
        _require(record.due, record.key,
                 "DEFERRED requires a due date. Postponed without one is abandoned.")
    if record.status == "NOT_APPLICABLE":
        _require(record.reason, record.key,
                 "NOT_APPLICABLE requires a reason, never the interviewer's opinion alone.")
    if record.confidence and record.confidence not in bank.CONFIDENCES:
        raise ValidationError(
            f"{record.key}: confidence must be one of {', '.join(bank.CONFIDENCES)}; "
            f"got {record.confidence!r}"
        )
    if record.readback not in bank.READBACKS:
        raise ValidationError(
            f"{record.key}: readback must be one of {', '.join(bank.READBACKS)}; "
            f"got {record.readback!r}"
        )
    if record.owner:
        _require(record.owner in bank.OWNER_VOCABULARY, record.key,
                 f"owner must be a role from the roster, not a person's name. Permitted: "
                 f"{', '.join(bank.OWNER_VOCABULARY)}. Got {record.owner!r}.")
    if record.due:
        _require(_is_a_calendar_date(record.due), record.key,
                 f"due must be a calendar date as YYYY-MM-DD; got {record.due!r}")


def _validate_provenance(record: Record) -> None:
    if not record.provenance:
        return
    if record.provenance.strip().lower() in _FORBIDDEN_PROVENANCE:
        raise ValidationError(
            f"{record.key}: {record.provenance!r} is refused because no provenance value "
            f"means the assistant worked it out. If you worked it out it is not a fact: it "
            f"is a MISSING with a named owner, or an engineering judgement for the "
            f"generated document's Unverified statements section."
        )
    if _provenance_is_legal(record.provenance):
        return
    raise ValidationError(
        f"{record.key}: provenance must be one of {', '.join(_PROVENANCE_FORMS)}; "
        f"got {record.provenance!r}. An interview provenance names a role from the roster, "
        f"slugified, and the date it was said, because the store is shared and outlives the "
        f"people in it."
    )


def _provenance_is_legal(provenance: str) -> bool:
    if provenance == _OPERATOR_PROVENANCE:
        return True
    interview = _INTERVIEW_PROVENANCE.match(provenance)
    if interview:
        return (interview["role"] in PROVENANCE_ROLES
                and _is_a_calendar_date(interview["date"]))
    if _DISCOVERY_PROVENANCE.match(provenance):
        return True
    return bool(_DOCUMENT_PROVENANCE.match(provenance))


def _validate_question_requirements(record: Record, question: bank.Question) -> None:
    if record.status != "ANSWERED":
        return
    if question.mechanism_required:
        _require(record.mechanism, record.key,
                 "requires a mechanism alongside the figure. A number with no mechanism "
                 "behind it is a guess wearing a suit; ask what happens on either side of it.")
    if question.readback_required:
        _require(record.readback in ("confirmed", "corrected"), record.key,
                 "requires a read-back before it is written. Say it back in one sentence and "
                 "get a yes; a draft nobody confirmed is not an answer they gave.")
    if question.confidence_required:
        _require(record.confidence, record.key, "requires a confidence.")


def _validate_conflict(record: Record) -> None:
    conflict = record.conflict
    if conflict is None:
        return
    _require(record.value is not None and conflict.value is not None, record.key,
             "a conflict needs two values, so it can only sit on an ANSWERED field. An "
             "unanswered field with a competing source is two MISSING sources, not a "
             "conflict.")
    _require(conflict.value != record.value, record.key,
             "a conflict needs two different values; both sides say the same thing.")
    _require(conflict.provenance != record.provenance, record.key,
             "a conflict needs two distinct sources; both sides cite the same one.")
    _require(conflict.decision_owner, record.key,
             "a conflict needs a named decision owner. Surfaced and unowned is the same as "
             "silently resolved by whoever renders it.")
    _require(conflict.decision_owner in bank.OWNER_VOCABULARY, record.key,
             f"a conflict's decision owner must be a role from the roster; "
             f"got {conflict.decision_owner!r}")


def _require(condition: object, key: str, message: str) -> None:
    if not condition:
        raise ValidationError(f"{key}: {message}")


def _is_a_calendar_date(text: str) -> bool:
    try:
        _datetime.date.fromisoformat(text)
    except ValueError:
        return False
    return True


# --------------------------------------------------------------------------- document ops

def new_document(system_name: str) -> dict:
    """An empty store for one system. ``meta`` first, ``facts`` empty."""
    today = _datetime.date.today().isoformat()
    return {
        "meta": {
            "schema_version": SCHEMA_VERSION,
            "system_name": system_name,
            "created": today,
            "last_updated": today,
        },
        "facts": {},
    }


def starter_document() -> dict:
    """Every field in the bank, MISSING, owned by the role who can answer it.

    The shape ``templates/answers.example.toml`` ships and the shape a new plan starts in.
    Every field starts refuted: nobody has answered anything, and each gap already names who
    can close it, which is the state an interview is supposed to begin from.
    """
    document = new_document("")
    for question in bank.QUESTIONS:
        document = put(document, Record(question.id, "MISSING", owner=question.owner_role))
    return document


def put(document: dict, record: Record) -> dict:
    """A copy of ``document`` with ``record`` stored, after validating it.

    Returns rather than mutates so a rejected write cannot leave a half-updated store, which
    matters because interviews write after every answer and get interrupted mid-question.
    """
    validate(record)
    facts = dict(document["facts"])
    facts[record.key] = record
    return {**document, "facts": facts}


def record(document: dict, key: str) -> Record | None:
    """The record for ``key``, or ``None`` if the field is unanswered and unrecorded."""
    return document["facts"].get(key)


def supersede(document: dict, replacement: Record, reason: str) -> dict:
    """Replace a value in place, keeping the one it replaced and why.

    ``answer-store.md``: never delete a fact to change it. The question "when did this become
    six hours, and who said so" is asked exactly once, in the worst week.
    """
    if not reason.strip():
        raise ValidationError(
            f"{replacement.key}: superseding requires a reason. A number that moves without "
            f"a trail cannot be audited."
        )
    previous = record(document, replacement.key)
    if previous is None:
        raise ValidationError(
            f"{replacement.key}: nothing to supersede; the field has no record yet."
        )
    trail = previous.superseded + (Superseded(
        value=previous.value, provenance=previous.provenance,
        confidence=previous.confidence, reason=reason),)
    return put(document, replace(replacement, superseded=trail))


# --------------------------------------------------------------------------- coverage

@dataclass(frozen=True)
class Coverage:
    """Coverage over a counted denominator, with the confidence distribution beside it.

    Coverage is not quality. A store at full coverage where two thirds of the fields are low
    confidence describes an organisation that has guessed comprehensively, so the two
    numbers are produced together and :meth:`report` prints them together.
    """

    total: int
    answered: int
    not_applicable: int
    deferred: int
    missing: int
    confidence: dict[str, int]
    scope: str

    @property
    def covered(self) -> int:
        """ANSWERED plus NOT_APPLICABLE: the fields that need nothing further."""
        return self.answered + self.not_applicable

    @property
    def percent(self) -> int:
        """Coverage as a whole per cent, always floored.

        Never rounded up. 17 of 37 is 45 per cent, not "about half done". The number is the
        deliverable, and a report that flatters itself by one point is a report that will be
        flattered by ten somewhere else.
        """
        if self.total == 0:
            return 0
        return self.covered * 100 // self.total

    def report(self) -> str:
        """The three-line report ``itscp-build`` prints after every phase."""
        counts = {
            "ANSWERED": self.answered, "NOT_APPLICABLE": self.not_applicable,
            "DEFERRED": self.deferred, "MISSING": self.missing,
        }
        statuses = " | ".join(f"{name} {counts[name]}" for name in _REPORT_STATUS_ORDER)
        confidences = " | ".join(
            f"{name} {self.confidence[name]}" for name in bank.CONFIDENCES)
        return (
            f"Coverage: {self.covered}/{self.total} fields ({self.percent}%)\n"
            f"  {statuses}\n"
            f"  Confidence of ANSWERED: {confidences}"
        )


def coverage(document: dict, namespace: str = "") -> Coverage:
    """Coverage over the whole bank, or over one namespace.

    The denominator is counted from the bank, never quoted. A field with no record counts as
    MISSING, because a field nobody has recorded is a field nobody has answered.
    """
    questions = bank.for_namespace(namespace) if namespace else list(bank.QUESTIONS)
    counts = dict.fromkeys(bank.STATUSES, 0)
    confidence = dict.fromkeys(bank.CONFIDENCES, 0)
    for question in questions:
        stored = record(document, question.id)
        status = stored.status if stored else "MISSING"
        counts[status] += 1
        if stored and status == "ANSWERED" and stored.confidence:
            confidence[stored.confidence] += 1
    return Coverage(
        total=len(questions), answered=counts["ANSWERED"],
        not_applicable=counts["NOT_APPLICABLE"], deferred=counts["DEFERRED"],
        missing=counts["MISSING"], confidence=confidence, scope=namespace or "all",
    )


# --------------------------------------------------------------------------- rendering aid

def status_marker(stored: Record | None) -> str:
    """How ``templates/repo-scaffold.md`` says this record renders in a generated document.

    Lives here rather than in the renderer so one file fixes the marker text. A renderer that
    invented its own would eventually render a MISSING field as blank, which is the single
    failure the toolkit exists to prevent. The em dashes are the scaffold's own.
    """
    if stored is None:
        return "**[MISSING — owner: unassigned]**"
    if stored.status == "MISSING":
        return f"**[MISSING — owner: {stored.owner}]**"
    if stored.status == "DEFERRED":
        return f"**[DEFERRED to {stored.due} — owner: {stored.owner}]**"
    if stored.status == "NOT_APPLICABLE":
        return f"Not applicable — {stored.reason}"
    if stored.confidence == "low":
        return f"{stored.value} *(low confidence; not measured)*"
    return str(stored.value)


# --------------------------------------------------------------------------- TOML emitting

def emit(document: dict) -> str:
    """The whole store as TOML, comments and all, rendered from schema plus data.

    Deterministic: the same document always produces the same bytes, so a diff shows what
    changed in the interview rather than what changed in the emitter.
    """
    lines = [_header(), "", "[meta]"]
    lines.extend(_named_lines(document["meta"]))
    for question in bank.QUESTIONS:
        stored = record(document, question.id)
        if stored is None:
            continue
        lines.append("")
        lines.extend(_comment_block(question))
        lines.extend(_fact_block(stored))
    return "\n".join(lines) + "\n"


def _header() -> str:
    return "\n".join(
        f"# {line}".rstrip() for line in (
            "The answer store. One file per plan; every interview reads it and appends to it.",
            "",
            "THIS FILE IS GITIGNORED AND MUST STAY THAT WAY. It accumulates names, phone",
            "numbers, OCIDs, MTD figures and organisational weak points. It is the most",
            "sensitive file the toolkit produces.",
            "",
            "Generated by itscp_store.emit. Comments are re-rendered from the question bank on",
            "every write, so editing a comment here has no effect; edit the guidance in",
            "itscp_questions.py instead. Values are yours to correct, and a correction is read",
            "back into the interview rather than overwritten.",
            "",
            "A key that is absent is unanswered. There is no null and no empty stand-in.",
        )
    )


def _comment_block(question: bank.Question) -> list[str]:
    lines = [f"# {question.id} - asked of the {question.owner_role}"]
    lines.extend(_wrapped_comment(question.guidance))
    if question.mechanism_prompt:
        lines.append("# The figure needs its mechanism beside it. Ask:")
        lines.extend(_wrapped_comment(question.mechanism_prompt))
    if question.readback_required:
        lines.append("# Read this back and get a yes before recording it.")
    return lines


def _wrapped_comment(text: str, width: int = _COMMENT_WIDTH) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = "#"
    for word in words:
        candidate = f"{current} {word}"
        if len(candidate) > width and current != "#":
            lines.append(current)
            current = f"# {word}"
        else:
            current = candidate
    if current != "#":
        lines.append(current)
    return lines


def _fact_block(stored: Record) -> list[str]:
    table = _quoted_key(stored.key)
    lines = [f"[facts.{table}]"]
    lines.extend(_scalar_lines(stored))
    if isinstance(stored.value, list):
        for row in stored.value:
            lines.append("")
            lines.append(f"[[facts.{table}.value]]")
            lines.extend(f"{name} = {toml_value(cell)}" for name, cell in row.items())
    for previous in stored.superseded:
        lines.append("")
        lines.append(f"[[facts.{table}.superseded]]")
        lines.extend(_named_lines({
            "value": previous.value, "provenance": previous.provenance,
            "confidence": previous.confidence, "reason": previous.reason,
        }))
    if stored.conflict is not None:
        lines.append("")
        lines.append(f"[facts.{table}.conflict]")
        lines.extend(_named_lines({
            "value": stored.conflict.value, "provenance": stored.conflict.provenance,
            "decision_owner": stored.conflict.decision_owner, "notes": stored.conflict.notes,
        }))
    return lines


def _scalar_lines(stored: Record) -> list[str]:
    fields = {"status": stored.status}
    if not isinstance(stored.value, list):
        fields["value"] = stored.value
    fields.update({
        "mechanism": stored.mechanism, "provenance": stored.provenance,
        "confidence": stored.confidence, "owner": stored.owner, "due": stored.due,
        "reason": stored.reason, "notes": stored.notes,
    })
    if stored.readback != "not_required":
        fields["readback"] = stored.readback
    return _named_lines(fields)


def _named_lines(fields: dict[str, Any]) -> list[str]:
    """Assignment lines for the fields that carry something. Absence means unanswered."""
    return [f"{name} = {toml_value(value)}"
            for name, value in fields.items()
            if value is not None and value != ""]


def _quoted_key(key: str) -> str:
    """A dotted key as one quoted TOML table name, so the dots are not table separators."""
    return f'"{_escape_basic(key)}"'


def toml_value(value: Any) -> str:
    """One TOML value, chosen by Python type. Shared with :mod:`itscp_session`.

    A string containing a newline becomes a multi-line basic string so a narrative answer
    stays readable to whoever opens the file to correct it.
    """
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, list):
        return "[" + ", ".join(toml_value(item) for item in value) + "]"
    text = str(value)
    if "\n" in text:
        return f'"""\n{_escape_multiline(text)}"""'
    return f'"{_escape_basic(text)}"'


_BASIC_ESCAPES = {
    "\\": "\\\\", '"': '\\"', "\b": "\\b", "\f": "\\f", "\n": "\\n", "\r": "\\r",
    "\t": "\\t",
}


def _escape_basic(text: str) -> str:
    """Escape for a single-line TOML basic string."""
    return "".join(_BASIC_ESCAPES.get(character, character) for character in text)


def _escape_multiline(text: str) -> str:
    """Escape for a multi-line TOML basic string, keeping real newlines readable.

    Backslashes and quotation marks are escaped individually. Escaping every quotation mark
    rather than only runs of three costs a little noise and removes the whole class of bug
    where a value ending in a quotation mark closes the delimiter early.

    A value that does not end in a newline gets a line-ending backslash before the closing
    delimiter, which TOML trims along with the newline after it. Without that the closing
    delimiter has to sit on its own line and every narrative comes back one newline longer
    than it went in.
    """
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    if escaped.endswith("\n"):
        return escaped
    return escaped + "\\\n"


# --------------------------------------------------------------------------- TOML reading

def load_document(parsed: dict) -> dict:
    """Turn a parsed TOML mapping back into records. The inverse of :func:`emit`."""
    facts = {key: _load_record(key, table)
             for key, table in parsed.get("facts", {}).items()}
    return {"meta": dict(parsed.get("meta", {})), "facts": facts}


def _load_record(key: str, table: dict) -> Record:
    conflict = table.get("conflict")
    return Record(
        key=key,
        status=table.get("status", "MISSING"),
        value=table.get("value"),
        mechanism=table.get("mechanism", ""),
        provenance=table.get("provenance", ""),
        confidence=table.get("confidence", ""),
        owner=table.get("owner", ""),
        due=table.get("due", ""),
        reason=table.get("reason", ""),
        notes=table.get("notes", ""),
        readback=table.get("readback", "not_required"),
        conflict=Conflict(
            value=conflict.get("value"), provenance=conflict.get("provenance", ""),
            decision_owner=conflict.get("decision_owner", ""),
            notes=conflict.get("notes", ""),
        ) if conflict else None,
        superseded=tuple(Superseded(
            value=entry.get("value"), provenance=entry.get("provenance", ""),
            confidence=entry.get("confidence", ""), reason=entry.get("reason", ""),
        ) for entry in table.get("superseded", ())),
    )


def as_comparable(document: dict) -> dict:
    """``document`` reduced to plain data, for comparing a round trip to its original.

    ``meta.last_updated`` is dropped: a write stamps it, so comparing it would compare the
    clock rather than the content.
    """
    meta = {name: value for name, value in document["meta"].items()
            if name != "last_updated"}
    return {"meta": meta,
            "facts": {key: _record_as_data(stored)
                      for key, stored in document["facts"].items()}}


def _record_as_data(stored: Record) -> dict:
    data = {name: value for name, value in vars(stored).items()
            if name not in ("conflict", "superseded") and value not in (None, "")}
    if stored.conflict is not None:
        data["conflict"] = {name: value for name, value in vars(stored.conflict).items()
                            if value not in (None, "")}
    if stored.superseded:
        data["superseded"] = [
            {name: value for name, value in vars(entry).items() if value not in (None, "")}
            for entry in stored.superseded]
    return data


# --------------------------------------------------------------------------- the file

class AnswerStore:
    """The store as a file: read it, write it atomically, never silently reset it."""

    def __init__(self, path: Path):
        self.path = path

    def read(self) -> dict:
        """The stored document, or an empty one. A corrupt file is reported, never reset."""
        if not self.path.exists():
            return new_document("")
        try:
            parsed = tomllib.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as failure:
            raise StoreError(
                f"{self.path} is not readable as TOML ({failure}). Fix or move it; nothing "
                f"has been overwritten and no answer has been lost."
            ) from failure
        if "facts" not in parsed:
            raise StoreError(
                f"{self.path} has no [facts] table, so it may not be an itscp-author answer "
                f"store. Nothing has been overwritten."
            )
        return load_document(parsed)

    def write(self, document: dict) -> None:
        """Replace the file atomically, so an interrupted write never truncates the interview.

        Interviews write after every answer and end unexpectedly. A partial file is the one
        outcome that loses work, so the render goes to a temporary file in the same directory
        and is moved into place by a single rename.
        """
        stamped = {**document,
                   "meta": {**document["meta"],
                            "schema_version": SCHEMA_VERSION,
                            "last_updated": _datetime.date.today().isoformat()}}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_name(self.path.name + ".tmp")
        temporary.write_text(emit(stamped), encoding="utf-8")
        os.replace(temporary, self.path)
