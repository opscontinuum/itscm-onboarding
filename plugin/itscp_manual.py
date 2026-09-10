"""DERIVED: the manual engagement, assembled from the skills and the question bank.

``docs/manual/`` is the same onboarding a loaded plugin runs, written for somebody working
from a printed page instead: the phases in order, the technique for each one, and the field
checklist that says what to record and who owes it.

It is generated rather than written, for the reason the answer store's example is generated.
A hand-written manual is a second copy of the method, and a second copy drifts the first time
a skill improves and nobody remembers the manual exists. What a reader would then have is a
document that is wrong in exactly the places the toolkit recently got better, which is worse
than not shipping one. So every sentence here comes from a file that is already the source of
truth for it:

* the phase technique is the body of the skill that runs that phase, demoted a heading level
  and otherwise verbatim;
* the field checklist is :mod:`itscp_questions`, the same bank ``answers.example.toml`` is
  emitted from, so the manual asks exactly what the interview asks;
* the orientation material is ``GETTING-STARTED.md``, extracted by heading.

Only the phase sequence and a lead paragraph per phase are written here, because the sequence
is this module's own claim and nothing else states it in one place.

Two consequences, both deliberate:

* **Editing ``docs/manual/`` by hand is a change the next regeneration deletes.** Change the
  skill, the bank or the getting-started guide, and regenerate.
* **A skill restructured past what the extractors expect fails loudly.** Every extraction
  raises :class:`ManualError` when the heading or field it needs is gone, so a renamed section
  is a failing test rather than a silently truncated manual.

Run it:

.. code-block:: console

   $ python3 plugin/itscp_manual.py            # write docs/manual/
   $ python3 plugin/itscp_manual.py --check    # exit 1 if the committed files are stale
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, fields as dataclass_fields
from pathlib import Path

if sys.version_info < (3, 11):
    raise RuntimeError(
        "itscp-author needs Python 3.11 or newer (this is "
        f"{sys.version_info.major}.{sys.version_info.minor})."
    )

sys.path.insert(0, str(Path(__file__).resolve().parent))

import itscp_questions as bank        # noqa: E402 - after the path insert, deliberately
import itscp_store as store           # noqa: E402
import itscp_portfolio as portfolio   # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugin"
SKILLS = PLUGIN / "skills"
OUTPUT_DIR = ROOT / "docs" / "manual"
GETTING_STARTED = ROOT / "GETTING-STARTED.md"


class ManualError(Exception):
    """A source file no longer holds what the manual extracts from it. Never a crash."""


# --------------------------------------------------------------------------- the sequence

@dataclass(frozen=True)
class Phase:
    """One file of the manual: a phase, the skills that carry it, the fields it records."""

    slug: str
    #: What the phase is called in ``GETTING-STARTED.md``. A label, not an index: ``0`` is a
    #: phase and ``3`` is two of them.
    number: str
    title: str
    #: Skill directory names under ``plugin/skills/``, embedded in order.
    skills: tuple[str, ...]
    #: Answer-store namespaces this phase records. Empty means the phase writes no fields:
    #: phase 0 writes the register, phase 6 writes the plan.
    namespaces: tuple[str, ...]
    #: This module's own claim about where the phase sits. Everything else is extracted.
    lead: str
    #: Whether to pull the ``Interviewee`` and ``Time`` lines from the first skill.
    session: bool = True


PHASES: tuple[Phase, ...] = (
    Phase(
        "00-portfolio", "0", "The portfolio and the dependency map",
        ("itscp-portfolio", "itscp-dependencies"),
        (),
        "Runs once for the organization, before any plan. It produces `portfolio.toml`: the "
        "register of systems, the comparative tier ranking, the recovery waves, and the "
        "dependency graph between them. Four failures live only above the level of a single "
        "plan and none of them are visible from inside one, which is why this comes first "
        "rather than after the plan that would have to be rebuilt.\n\n"
        "**Nothing in this phase is recorded in an answer store.** A register of systems is a "
        "different shape from a set of facts about one system, so it is written by hand into "
        "`portfolio.toml` and checked with `python3 plugin/itscp_portfolio.py portfolio.toml`. "
        "The fields that file holds are listed at the end of this page.\n\n"
        "**Do not start a per-system plan while the validator reports errors.** An inversion "
        "means two signed figures contradict each other, and a plan built on top of one bakes "
        "the contradiction in.",
        session=True,
    ),
    Phase(
        "01-discovery", "1", "Discovery",
        ("itscp-discover",),
        ("discovery",),
        "Sixty read-only minutes against the tenancy, run before the technical interviews so "
        "that those interviews start from a list rather than a blank page. Every call is a "
        "`list` or a `get`.\n\n"
        "The skill below drives a tool; by hand you run the same script the tool spawns, from "
        "your clone. Prove it is read-only first, then show the customer the dry run before "
        "the real walk:\n\n"
        "```bash\n"
        "bash plugin/scripts/discover/test-readonly.sh\n"
        "bash plugin/scripts/discover/oci-discover.sh \\\n"
        "    --compartment <ocid> --regions <primary>,<standby> \\\n"
        "    --out discovery-output --dry-run\n"
        "bash plugin/scripts/discover/oci-discover.sh \\\n"
        "    --compartment <ocid> --regions <primary>,<standby> --out discovery-output\n"
        "```\n\n"
        "**Working manually, the output that matters is `gaps.md`, not the inventory.** The "
        "gaps are interview material: resources nobody can name, a standby that was supposed "
        "to exist, a replication policy covering three of five buckets. Take that file into "
        "phase 3 and ask about each line.\n\n"
        "Discovery may prefill a handful of interview fields. Each one is marked in the "
        "checklists that follow, and a prefilled value is **read back for correction, never "
        "recorded as though somebody said it.**",
        session=False,
    ),
    Phase(
        "02-business", "2", "The business interview, which gates the rest",
        ("itscp-interview-business",),
        ("business",),
        "**Do not proceed past this phase without a signed tier assignment.** Tier determines "
        "standby capacity, replication topology and run cost. Everything after this is built "
        "to these numbers and all of it is expensive to change.\n\n"
        "If the business owner is unavailable for three weeks, wait three weeks. Proceeding "
        "on assumed tiers feels productive and is the most costly mistake available here: "
        "assumed tiers become real architecture within a day and are never revisited.",
        session=True,
    ),
    Phase(
        "03a-application", "3a", "The application interview",
        ("itscp-interview-application",),
        ("system", "app"),
        "Phase 3 is two interviews that do not depend on each other. Run them in either order "
        "or in parallel with different people. This is the first.\n\n"
        "**Bring the deputy to at least one of the two.** The backup lead engineer sitting in "
        "is the cheapest test available of whether the deputy could really do it, and it "
        "usually answers the question before you have to ask it.\n\n"
        "**Expect a contradiction with phase 2, and do not resolve it yourself.** The business "
        "said four hours; the application owner says batch reprocessing alone takes a day. "
        "Record both, name whose decision it is, and take it back to the business owner.",
        session=True,
    ),
    Phase(
        "03b-infrastructure", "3b", "The infrastructure interview",
        ("itscp-interview-infrastructure",),
        ("infra",),
        "The second half of phase 3, and the one that turns the signed targets into a topology "
        "and a monthly figure. Bring the lead engineer for anything measured and for anything "
        "that has actually been executed rather than designed.\n\n"
        "**Take `gaps.md` from phase 1 into this session.** It is the difference between "
        "reconstructing the environment for forty minutes and correcting a list for ten.",
        session=True,
    ),
    Phase(
        "04-continuity", "4", "The continuity interview",
        ("itscp-interview-continuity",),
        ("continuity",),
        "Runs after phase 3, because escalation thresholds need real recovery steps to "
        "threshold against.\n\n"
        "This is where most organizations discover that **nobody owns the declaration "
        "decision.** That is not a failure of the interview; it is the single most valuable "
        "thing it produces.\n\n"
        "The succession elicited here and the deputy roster from phase 0 must agree. Where "
        "they do not, that is a recorded conflict with a named decision owner, not something "
        "to reconcile quietly.",
        session=True,
    ),
    Phase(
        "05-governance", "5", "The governance interview",
        ("itscp-interview-governance",),
        ("governance",),
        "**A design describes what would happen; a plan is a design somebody committed to.** "
        "The difference is a signature, a review date and a trained population, and this phase "
        "is where all three are elicited.",
        session=True,
    ),
    Phase(
        "06-generate-and-audit", "6", "Assemble and audit",
        ("itscp-audit",),
        (),
        "Half a day, on your own. Working manually there is no renderer, so this phase is two "
        "jobs rather than one: write the repository from the answers you hold, then audit what "
        "you wrote.\n\n"
        "**The assembly is mechanical and the map for it is generated.** Every recorded field "
        "names the file it lands in; [`fields.md`](fields.md) lists them the other way round, "
        "file by file, which is the order you write in. The tree to create is below, and so "
        "are the rendering rules for a `MISSING` field, a low-confidence value and the "
        "*Unverified statements* section. A manually written plan that quietly omits its gaps "
        "has thrown away the thing this method produces.\n\n"
        "Then audit. Fix what blocks approval and leave the rest visible.",
        session=False,
    ),
)

#: Embedded whole in ``06-generate-and-audit.md``, ahead of the audit skill, because a manual
#: assembly needs the tree and the marker rules ``itscp-build`` would otherwise apply.
SCAFFOLD_SKILL = "_method/repo-scaffold"

#: Embedded whole in ``method.md``. The discipline every phase is run under.
METHOD_SKILL = "_method/interview"

#: Also embedded in ``method.md``: what a complete plan contains, element by element.
COVERAGE_SKILL = "_method/coverage-map"

#: The answer-store rules, embedded in ``method.md`` under the record shape.
STORE_SKILL = "_method/answer-store"

#: Sections lifted verbatim from ``GETTING-STARTED.md`` into the manual's index page. The
#: guide is the source for all three; repeating them here would be the drift this module
#: exists to avoid.
GETTING_STARTED_SECTIONS: tuple[str, ...] = (
    "Before you start",
    "What good looks like after one pass",
    "Common ways this goes wrong",
)

#: What the guide's own words do not say, because the guide assumes a loaded plugin and this
#: document does not. Rendered above the extracted section rather than folded into it, so a
#: reader can see which sentences are the guide's.
GETTING_STARTED_PREFACE: dict[str, str] = {
    "Before you start": (
        "Working by hand, the first of the four is optional: you need a clone of this "
        "repository for the validator and the discovery script, not a loaded plugin. **The "
        "other three are not optional, and the fourth is the one people skip.**"
    ),
}

#: One line per :class:`itscp_store.Record` field, for the recording table in ``method.md``.
#: A test asserts this covers the dataclass exactly, so a new field on the record is a failing
#: test rather than a column the manual quietly stops mentioning.
RECORD_FIELD_NOTES: dict[str, str] = {
    "key": "The field being answered. One of the keys in this manual's checklists, and never anything else.",
    "status": "`MISSING`, `ANSWERED`, `DEFERRED` or `NOT_APPLICABLE`. Every field carries one; none are absent.",
    "value": "What they said. Absent on anything but `ANSWERED`.",
    "mechanism": "What changes on either side of a figure. Required on every duration, count and currency amount.",
    "provenance": "Where it came from: `interview:<role>:<YYYY-MM-DD>`, `oci-discovery:<Operation>`, `document:<path>` or `operator`.",
    "confidence": "`high`, `medium` or `low`, assigned from how the answer arrived rather than from how plausible it sounds.",
    "owner": "The role who can answer. Required on `MISSING` and `DEFERRED`; a gap with no owner is not a finding, it is a hole.",
    "due": "When a `DEFERRED` answer is expected. A deferral with no date is a `MISSING` wearing a suit.",
    "reason": "Why a field is `DEFERRED` or `NOT_APPLICABLE`. Never the interviewer's opinion on its own.",
    "notes": "Anything a later reader needs: who was in the room, what was contested, what the answer depends on.",
    "readback": "`not_required`, `confirmed` or `corrected`. A draft nobody has confirmed is not an answer and does not belong here.",
    "conflict": "The other answer, when two people gave different ones: its value, its provenance, and the named owner of the decision.",
    "superseded": "What this answer replaced, and why. Corrections are appended; nothing is overwritten in place.",
}


# --------------------------------------------------------------------------- extraction

_FRONTMATTER = re.compile(r"\A---\n(?P<body>.*?)\n---\n", re.S)
_FENCE = re.compile(r"^\s*(?:```|~~~)")
_HEADING = re.compile(r"^#{1,5} ")


def _read(path: Path) -> str:
    if not path.exists():
        raise ManualError(f"{path} is missing; the manual is assembled from it")
    return path.read_text(encoding="utf-8")


def _frontmatter(text: str, path: Path) -> dict[str, str]:
    """``name`` and ``description`` from a skill's frontmatter."""
    match = _FRONTMATTER.match(text)
    if match is None:
        raise ManualError(f"{path} has no frontmatter block")
    parsed: dict[str, str] = {}
    for line in match.group("body").splitlines():
        if ": " in line:
            label, value = line.split(": ", 1)
            parsed[label.strip()] = value.strip()
    for required in ("name", "description"):
        if required not in parsed:
            raise ManualError(f"{path} frontmatter has no {required}")
    return parsed


def _body(text: str, path: Path) -> str:
    """Everything after the frontmatter and the H1, which the manual supplies itself."""
    match = _FRONTMATTER.match(text)
    remainder = text[match.end():] if match else text
    lines = remainder.lstrip("\n").splitlines()
    if not lines or not lines[0].startswith("# "):
        raise ManualError(f"{path} does not open with a level-one heading")
    return "\n".join(lines[1:]).strip("\n")


def _demote(markdown: str, levels: int = 1) -> str:
    """Push every heading down, leaving anything inside a fenced block alone."""
    output: list[str] = []
    fenced = False
    for line in markdown.splitlines():
        if _FENCE.match(line):
            fenced = not fenced
        elif not fenced and _HEADING.match(line):
            line = "#" * levels + line
        output.append(line)
    return "\n".join(output)


def _bold_field(body: str, label: str, path: Path) -> str:
    """The paragraph a skill opens with a ``**Label:**`` marker, as one line."""
    pattern = re.compile(
        rf"^\*\*{re.escape(label)}:\*\*[ ]*(?P<value>.+?)(?=\n\n|\Z)", re.S | re.M)
    match = pattern.search(body)
    if match is None:
        raise ManualError(f"{path} no longer carries a **{label}:** line")
    return " ".join(match.group("value").split())


def _section(text: str, heading: str, path: Path) -> str:
    """One ``## heading`` section of a document, without the heading line itself."""
    pattern = re.compile(
        rf"^## {re.escape(heading)}[ ]*\n(?P<body>.*?)(?=\n---\n|\n## |\Z)", re.S | re.M)
    match = pattern.search(text)
    if match is None:
        raise ManualError(f"{path} has no '## {heading}' section")
    return match.group("body").strip("\n")


def _skill(name: str) -> tuple[dict[str, str], str, Path]:
    path = SKILLS / name / "SKILL.md"
    text = _read(path)
    return _frontmatter(text, path), _body(text, path), path


# --------------------------------------------------------------------------- field blocks

def _answer_shape(question: bank.Question) -> str:
    """One clause saying what a legal answer to this question looks like."""
    unit = f" in {question.unit}" if question.unit else ""
    if question.kind == "enum":
        return "one of " + ", ".join(f"`{option}`" for option in question.options)
    if question.kind == "rows":
        return "one row per item, columns " + " | ".join(f"`{column}`" for column in question.columns)
    if question.kind == "narrative":
        return "several paragraphs, in their words"
    if question.kind == "code":
        return "exact text, reproduced byte for byte or not at all"
    if question.kind == "date":
        return "a date, `YYYY-MM-DD`"
    if question.kind == "list":
        return "a list"
    if question.kind in ("duration", "number", "currency"):
        return f"a {question.kind}{unit}"
    return f"free text{unit}"


def _question_block(question: bank.Question) -> list[str]:
    asked = question.prompt.startswith("Not asked")
    lines = [
        f"#### `{question.id}`",
        "",
        f"*{question.prompt}*" if asked else f"> \"{question.prompt}\"",
        "",
        f"- **Records:** {question.records}",
        f"- **Owner:** {question.owner_role} · **Answer:** {_answer_shape(question)}",
    ]
    for column, options in sorted(question.enum_columns.items()):
        lines.append(f"- **`{column}` is one of:** "
                     + ", ".join(f"`{option}`" for option in options))
    for figure, explains in sorted(question.figure_columns.items()):
        lines.append(f"- **Every `{figure}` owes a `{explains}`.** A target with no stated "
                     "consequence is a number nobody has to meet.")
    if question.mechanism_required:
        lines.append(f"- **Then ask:** \"{question.mechanism_prompt}\" Record the answer in "
                     "`mechanism`. Without one the figure is `confidence: low`.")
    if question.readback_required:
        lines.append("- **Read it back** in one sentence and get a yes before recording it.")
    if question.seedable:
        lines.append(f"- **Discovery may prefill this** (`{question.seed_operation}`). Read "
                     "the value back for correction rather than asking cold; a value the "
                     "interviewee did not confirm keeps its discovery provenance and never "
                     "gains theirs.")
    if question.guidance:
        lines.append(f"- **Note:** {question.guidance}")
    lines.append(f"- **Lands in:** {question.written_to}")
    if question.structural_provenance == "nist":
        lines.append(f"- **NIST:** {question.nist_heading} ({question.nist_source})")
    elif question.structural_provenance == "ours":
        lines.append("- **No NIST slot.** This element is one the toolkit carries "
                     "deliberately; the answer in it is elicited like any other.")
    else:
        lines.append("- **The toolkit supplies this element's words, not the customer.** They "
                     "render as the toolkit's own and are never presented as something "
                     f"anybody said: {question.method_statement}")
    if question.crosswalk_note:
        lines.append(f"- **Terminology:** {question.crosswalk_note}")
    lines.append("")
    return lines


def _checklist(namespaces: tuple[str, ...]) -> list[str]:
    """Every field the phase records, grouped by the coverage row it feeds."""
    questions = [entry for namespace in namespaces for entry in bank.for_namespace(namespace)]
    if not questions:
        return []
    lines = [
        "---",
        "",
        "## The field checklist",
        "",
        f"{len(questions)} fields, in the order the bank holds them, grouped by the section of "
        "the plan each one feeds. Every one of them ends the session with a status. A field "
        "nobody could answer is `MISSING` against a named owner, which is a result and not a "
        "failure; a field left absent is an error.",
        "",
    ]
    for row in dict.fromkeys(question.coverage_row for question in questions):
        lines += [f"### {row}", ""]
        for question in (entry for entry in questions if entry.coverage_row == row):
            lines += _question_block(question)
    return lines


# --------------------------------------------------------------------------- pages

_BANNER = (
    "> **Generated file.** It is assembled from the skills, the question bank and "
    "`GETTING-STARTED.md` by `plugin/itscp_manual.py`, and an edit made here is deleted by "
    "the next regeneration. Change the source and run `python3 plugin/itscp_manual.py`."
)


def _phase_link(phase: Phase) -> str:
    return f"[Phase {phase.number} — {phase.title}]({phase.slug}.md)"


def _index_page() -> str:
    guide = _read(GETTING_STARTED)
    lines = [
        "# The manual",
        "",
        _BANNER,
        "",
        "The onboarding run by hand: the same phases in the same order, for somebody working "
        "from this page rather than from a loaded plugin. Every phase carries the technique "
        "the corresponding skill carries, and every interview phase ends with the checklist "
        "of fields it records.",
        "",
        "**Read [the method](method.md) before the first interview.** It is the discipline "
        "all of the phases are run under, and the one thing here that is not optional: a plan "
        "whose numbers nobody gave is worse than one with visible gaps, and the method is "
        "what keeps the difference legible.",
        "",
        "## The sequence",
        "",
        "| Phase | Who is in the room | Fields recorded |",
        "|---|---|---|",
    ]
    for phase in PHASES:
        if phase.session:
            _, body, path = _skill(phase.skills[0])
            extracted = _bold_field(body, "Interviewee", path)
            who = extracted[0].upper() + extracted[1:]
        else:
            who = "You, on your own"
        counted = sum(len(bank.for_namespace(namespace)) for namespace in phase.namespaces)
        lines.append(f"| {_phase_link(phase)} | {who} | "
                     f"{counted if counted else 'none — see the page'} |")
    lines += [
        "",
        "Phase 7 is not a document. It is the signature, and then the drill: **every duration "
        "in the plan is a design target, and none of them are commitments until a drill has "
        "measured one.** Schedule the first drill before the approval meeting ends.",
        "",
        "## Supporting pages",
        "",
        "- [The method](method.md) — the Iron Rule, the statuses, confidence, provenance, and "
        "how to write a record by hand.",
        "- [Every field, by the file it lands in](fields.md) — the order to write the plan in, "
        "and the full index of keys.",
        "",
        "---",
        "",
    ]
    for heading in GETTING_STARTED_SECTIONS:
        lines += [f"## {heading}", ""]
        if heading in GETTING_STARTED_PREFACE:
            lines += [GETTING_STARTED_PREFACE[heading], ""]
        lines += [_section(guide, heading, GETTING_STARTED), "", "---", ""]
    return "\n".join(lines).rstrip("\n") + "\n"


def _record_example() -> list[str]:
    return [
        "```toml",
        "# Answered, with the mechanism the figure depends on.",
        '[facts."business.mtd.tier0"]',
        'status = "ANSWERED"',
        'value = "8h"',
        'mechanism = "The overnight bank file cuts at 18:00. Missing it loses a day of settlement."',
        'provenance = "interview:business-owner:2026-09-10"',
        'confidence = "medium"',
        'readback = "confirmed"',
        "",
        "# Nobody in the room knew. This is a result, not a blank.",
        '[facts."continuity.declaration_authority"]',
        'status = "MISSING"',
        'owner = "business owner"',
        'notes = "Nobody present could name who declares. Raised 2026-09-10."',
        "",
        "# Postponed on purpose, with a date and a reason.",
        '[facts."infra.failover_cost"]',
        'status = "DEFERRED"',
        'owner = "infrastructure owner"',
        'due = "2026-10-01"',
        'reason = "Awaiting the standby quote from the account team."',
        "",
        "# Two people, two answers. Both are recorded and the decision is owned.",
        '[facts."business.rto"]',
        'status = "ANSWERED"',
        'value = "4h"',
        'provenance = "interview:business-owner:2026-09-10"',
        'confidence = "low"',
        "",
        '[facts."business.rto".conflict]',
        'value = ">=24h"',
        'provenance = "interview:application-owner:2026-09-11"',
        'decision_owner = "business owner"',
        'notes = "Application owner states batch reprocessing alone exceeds the stated target."',
        "```",
    ]


def _method_page() -> str:
    _, method_body, _ = _skill(METHOD_SKILL)
    _, store_body, _ = _skill(STORE_SKILL)
    _, coverage_body, _ = _skill(COVERAGE_SKILL)
    record_fields = [field.name for field in dataclass_fields(store.Record)]
    undescribed = [name for name in record_fields if name not in RECORD_FIELD_NOTES]
    if undescribed:
        raise ManualError("the answer record has fields the manual does not describe: "
                          + ", ".join(undescribed))
    lines = [
        "# The method",
        "",
        _BANNER,
        "",
        "Read this before the first interview. It is the discipline every phase is run under, "
        "and it is the same file the skills read.",
        "",
        "---",
        "",
        "## The elicitation discipline",
        "",
        _demote(method_body),
        "",
        "---",
        "",
        "## Recording an answer by hand",
        "",
        "One `answers.toml` per plan, one table per field, written as the answer arrives "
        "rather than at the end of the session. **The file is gitignored and must stay that "
        "way:** it accumulates names, telephone numbers, identifiers, downtime figures and "
        "the organization's weak points, and it is the most sensitive thing the engagement "
        "produces.",
        "",
        "A key that is absent is unanswered. There is no null and no empty stand-in.",
        "",
        *_record_example(),
        "",
        "### Every field of a record",
        "",
        "| Field | What it holds |",
        "|---|---|",
        *[f"| `{name}` | {RECORD_FIELD_NOTES[name]} |" for name in record_fields],
        "",
        f"Statuses: {', '.join(f'`{status}`' for status in bank.STATUSES)}. "
        f"Confidence: {', '.join(f'`{level}`' for level in bank.CONFIDENCES)}. "
        f"Read-back: {', '.join(f'`{state}`' for state in bank.READBACKS)}.",
        "",
        "The seven roles an `owner` may name, each of which also owes a deputy: "
        + ", ".join(f"`{role}`" for role in bank.ROLES) + ".",
        "",
        "---",
        "",
        "## The store's own rules",
        "",
        _demote(store_body),
        "",
        "---",
        "",
        "## What a complete plan contains",
        "",
        _demote(coverage_body),
        "",
    ]
    return "\n".join(lines).rstrip("\n") + "\n"


def _portfolio_fields() -> list[str]:
    """The register's shape, named from the module that validates it."""
    return [
        "---",
        "",
        "## What `portfolio.toml` holds",
        "",
        "Written by hand and checked with `python3 plugin/itscp_portfolio.py portfolio.toml`. "
        "`plugin/portfolio.example.toml` is a fourteen-system register in this shape.",
        "",
        "**Once for the organization**",
        "",
        "| Field | What it holds |",
        "|---|---|",
        "| `organization` | The organization's name |",
        "| `tier_budget` | How many systems each tier may hold. The budget is what makes the "
        "ranking comparative; without one every owner answers tier 0, and is not wrong to |",
        "| `wave` | One block per step of the recovery order: `id`, `name`, `purpose`, and "
        "`max_concurrent` — how many of that wave's systems can genuinely be recovered at "
        "once, which is a statement about people far more often than about capacity |",
        "",
        "**Once per system**",
        "",
        "| Field | What it holds |",
        "|---|---|",
        "| `slug`, `name` | The name the business uses, not the hostname |",
        "| `class` | One of " + ", ".join(f"`{item}`" for item in portfolio.SYSTEM_CLASSES) + " |",
        "| `business_owner`, `application_owner` | A system with neither is an error, not a "
        "gap: nobody can sign its recovery target |",
        "| `tier`, `rto`, `rpo`, `mtd` | Ranked against the other systems, never in isolation. "
        "Durations as people write them: `0`, `30m`, `4h`, `2d` |",
        "| `wave` | Which step of the recovery order it belongs to |",
        "| `plan_repo` | Where its plan lives. Empty means known about and unplanned |",
        "| `notes` | Anything the register would otherwise lose |",
        "",
        "**Once per dependency, under the system that has it**",
        "",
        "| Field | What it holds |",
        "|---|---|",
        "| `on` | The slug of the system depended on. A slug not in the register is an error |",
        "| `kind` | One of " + ", ".join(f"`{item}`" for item in portfolio.DEPENDENCY_KINDS)
        + ". `recovery` is the one almost nobody asks for, and the one that finds the "
          "circular plans |",
        "| `criticality` | " + " or ".join(f"`{item}`" for item in portfolio.CRITICALITIES)
        + ". Only hard edges constrain the recovery order |",
        "| `notes` | What breaks without it. This is what survives a reorganization; the slug "
        "is only a pointer |",
        "",
        f"A system with {portfolio.SHARED_SERVICE_THRESHOLD} or more hard dependants is a "
        "shared service in practice, whatever its declared class, and the validator says so.",
        "",
    ]


def _phase_page(phase: Phase) -> str:
    lines = [
        f"# Phase {phase.number} — {phase.title}",
        "",
        _BANNER,
        "",
    ]
    if phase.session:
        _, body, path = _skill(phase.skills[0])
        lines += [
            f"**Who is in the room:** {_bold_field(body, 'Interviewee', path)}",
            "",
            f"**How long:** {_bold_field(body, 'Time', path)}",
            "",
        ]
    lines += [
        phase.lead,
        "",
        "**Run under [the method](method.md).** No fact enters the plan unless a human said "
        "it, a read-only API returned it, or it is marked `MISSING` against a named owner.",
        "",
    ]
    if phase.slug == "06-generate-and-audit":
        front, body, _ = _skill(SCAFFOLD_SKILL)
        lines += [
            "---",
            "",
            f"## The repository to write — `{front['name']}`",
            "",
            f"*{front['description']}*",
            "",
            _demote(body),
            "",
        ]
    for name in phase.skills:
        front, body, _ = _skill(name)
        lines += [
            "---",
            "",
            f"## The technique — `{front['name']}`",
            "",
            f"*{front['description']}*",
            "",
            _demote(body),
            "",
        ]
    if phase.slug == "00-portfolio":
        lines += _portfolio_fields()
    lines += _checklist(phase.namespaces)
    return "\n".join(lines).rstrip("\n") + "\n"


def _landing_files(written_to: str) -> list[str]:
    """The files one field lands in, with any trailing section number dropped."""
    return [token.split(" ")[0] for token in written_to.split(", ")]


def _fields_page() -> str:
    known = {landing for question in bank.QUESTIONS
             for landing in _landing_files(question.written_to) if landing.endswith(".md")}

    def resolve(landing: str) -> str:
        """``docs/09`` is ``docs/09-phase-recovery.md`` written short. Match it back."""
        if landing.endswith(".md"):
            return landing
        matches = sorted(name for name in known if name.startswith(landing + "-"))
        return matches[0] if matches else landing + ".md"

    by_file: dict[str, list[bank.Question]] = {}
    for question in bank.QUESTIONS:
        for landing in _landing_files(question.written_to):
            by_file.setdefault(resolve(landing), []).append(question)

    phase_of = {namespace: phase for phase in PHASES for namespace in phase.namespaces}

    lines = [
        "# Every field, and where it lands",
        "",
        _BANNER,
        "",
        f"The {len(bank.QUESTIONS)} fields of the starter plan, listed twice: by the file each "
        "one is written into, which is the order phase 6 assembles in, and then as a flat "
        "index. A field feeding two files appears under both.",
        "",
        "---",
        "",
        "## By file",
        "",
    ]
    for path in sorted(by_file):
        lines += [f"### `{path}`", "", "| Field | Records | Owner |", "|---|---|---|"]
        for question in by_file[path]:
            lines.append(f"| `{question.id}` | {question.records} | {question.owner_role} |")
        lines.append("")
    lines += [
        "---",
        "",
        "## The full index",
        "",
        "| Field | Phase | Answer | Owner | Section of the plan |",
        "|---|---|---|---|---|",
    ]
    for question in bank.QUESTIONS:
        phase = phase_of[question.namespace]
        lines.append(f"| `{question.id}` | [{phase.number}]({phase.slug}.md) | "
                     f"{question.kind} | {question.owner_role} | {question.coverage_row} |")
    lines += [
        "",
        f"Figures owing a mechanism: {sum(q.mechanism_required for q in bank.QUESTIONS)}. "
        f"Answers to read back before recording: "
        f"{sum(q.readback_required for q in bank.QUESTIONS)}. "
        f"Fields discovery may prefill: {sum(q.seedable for q in bank.QUESTIONS)}.",
        "",
    ]
    return "\n".join(lines).rstrip("\n") + "\n"


def pages() -> dict[str, str]:
    """Every file of the manual, keyed by its name under ``docs/manual/``."""
    written = {"README.md": _index_page(), "method.md": _method_page(),
               "fields.md": _fields_page()}
    for phase in PHASES:
        written[f"{phase.slug}.md"] = _phase_page(phase)
    return written


# --------------------------------------------------------------------------- entry point

def main(argv: list[str]) -> int:
    checking = "--check" in argv[1:]
    written = pages()
    stale: list[str] = []
    for name, content in sorted(written.items()):
        path = OUTPUT_DIR / name
        if path.exists() and path.read_text(encoding="utf-8") == content:
            continue
        if checking:
            stale.append(name)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"wrote docs/manual/{name}")
    for path in sorted(OUTPUT_DIR.glob("*.md")) if OUTPUT_DIR.exists() else []:
        if path.name in written:
            continue
        if checking:
            stale.append(f"{path.name} (generated by nothing)")
        else:
            path.unlink()
            print(f"removed docs/manual/{path.name}")
    if stale:
        print("stale; regenerate with python3 plugin/itscp_manual.py:")
        for name in stale:
            print(f"  {name}")
        return 1
    if checking:
        print(f"docs/manual/ is current: {len(written)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
