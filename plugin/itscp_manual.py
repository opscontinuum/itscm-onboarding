"""DERIVED: the tabletop, assembled from the skills and the question bank.

``docs/manual/`` is this engagement run as a facilitated exercise: the application and
infrastructure teams in one room, a printed worksheet on the table, and nothing to install.
It covers the same phases the plugin runs and asks the same questions, because it is generated
from the same files.

It is not a transcript of the skills. They are written for an agent with the plugin loaded, so
they say *invoke this*, *run that script*, *write it to the answer store*, and a room has none
of those. Sections that only drive the toolkit are left out by name in
:data:`SKIPPED_SECTIONS`. Every mention that survives is answered in the page's own *Running
this without the toolkit* table, rendered from :data:`TRANSLATIONS` against the text that
actually got embedded, and a reference nothing translates fails the build.

Nor does it produce TOML. The plugin's answer store is a file; the tabletop's is the stack of
worksheets, holding the same things in columns: the answer, who gave it, how sure they were,
what breaks at that number. Typing those up into the store is an appendix, for an organization
that later adopts the toolkit.

It assumes no particular cloud either. Phase 1 is whatever the teams already use to see their
environment. The read-only walk the toolkit ships is one provider's shortcut, and what
generalises out of it is the rule that discovery never changes anything.

What is generated, and from where:

* the technique is the named sections of the skill that runs each phase, verbatim;
* the questions, the worksheets and the field index are :mod:`itscp_questions`, the bank
  ``answers.example.toml`` is emitted from;
* the register's shape is :mod:`itscp_portfolio`, the module that validates it;
* the orientation is ``GETTING-STARTED.md``, extracted by heading.

Written here and nowhere else: the phase sequence, the room each phase needs, and the by-hand
procedures that replace a script. Those are this module's own claims.

Freshness is enforced, not remembered. ``test_manual`` rebuilds every page and fails on the
first differing line, and it fails too when a skill grows a section nobody has classified as
embedded or skipped. Every extractor raises :class:`ManualError` rather than guessing, so a
restructured skill is a failing build instead of a manual with a hole in it.

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


# --------------------------------------------------------------------------- what to embed

@dataclass(frozen=True)
class Embed:
    """One skill, and the sections of it this page carries, in the order it carries them."""

    skill: str
    sections: tuple[str, ...]
    #: Carry the skill's opening text as well, the part before its first ``##``. Off by
    #: default, because for most skills that text is a *Read first* pointer and an
    #: ``Interviewee`` line the manual states in its own words. On for the scaffold, whose
    #: opening text is the directory tree — the one thing phase 6 cannot be run without.
    preamble: bool = False


#: Every interview skill ends by listing the fields it produces and where they land. The
#: manual has that list twice already, generated from the bank rather than restated: once as
#: the page's own checklist and once in ``fields.md``. Carrying the section as well would put
#: a third, hand-maintained copy in front of a facilitator.
_OUTPUT_SKIP = ("Output",
                "Lists the fields the session produces. The page's own checklist and "
                "fields.md are that list, generated from the bank.")

#: Sections deliberately left out, with the reason, one entry per skill that has any. The
#: reason is not decoration: a later reader deciding whether to put a section back needs to
#: know it was a decision. ``test_manual`` asserts that every ``##`` heading of an embedded
#: skill is either carried by a page or named here, so a skill that grows a section fails the
#: build until somebody classifies it.
SKIPPED_SECTIONS: dict[str, tuple[tuple[str, str], ...]] = {
    "itscp-discover": (
        ("Prerequisites", "The tool's credentials and CLI. A room brings what it already has."),
        ("Running it", "Invocations of a tool nobody in the room has loaded."),
        ("One walk, many systems", "How the tool's output is reused across plans."),
        ("Handling commands that do not exist",
         "How the script degrades when an API is missing. Nothing to degrade by hand."),
        ("Output", "The files the tool writes."),
    ),
    "itscp-interview-business": (_OUTPUT_SKIP,),
    "itscp-interview-application": (_OUTPUT_SKIP,),
    "itscp-interview-infrastructure": (_OUTPUT_SKIP,),
    "itscp-interview-continuity": (_OUTPUT_SKIP,),
    "itscp-interview-governance": (_OUTPUT_SKIP,),
    "itscp-portfolio": (
        ("What a register holds",
         "The file's field list. Rendered from itscp_portfolio instead, so the manual "
         "describes the register the validator actually enforces."),
    ),
    "_method/answer-store": (
        ("Why a store at all", "Argues for a file. The tabletop's answer is the worksheet."),
        ("Shape", "The record's TOML shape. Carried in the transcription appendix instead."),
        ("Coverage", "How the plugin counts coverage. Counted from the worksheets by hand."),
    ),
}

#: Every tool, file or command the embedded text still names, and what the room does instead.
#: Rendered per page against the text that was actually embedded, so a row appears only where
#: it is needed and disappears when a skill stops saying it. ``test_manual`` scans the other
#: way as well: a command-shaped reference nothing here covers fails the build.
TRANSLATIONS: tuple[tuple[str, str, str], ...] = (
    ("itscp_portfolio.py", "`python3 itscp_portfolio.py`",
     "Check the register by hand. [Five passes over the wall](00-portfolio.md#checking-the-register-by-hand), "
     "each one a question you can answer from the cards in front of you."),
    ("itscp_discover_oci", "`itscp_discover_oci`",
     "A read-only walk for one cloud provider. Bring the equivalent from whatever your teams "
     "already use: a console export, a CMDB extract, last quarter's architecture review. What "
     "generalises is the rule, not the tool — discovery never changes anything."),
    (".sh", "a script under `plugin/scripts/`",
     "Nothing to run. Whatever produced your inventory is what you bring."),
    ("picoagent", "`picoagent -e ...`",
     "Nothing to load. A tabletop needs the pages you are holding, a wall, and the people."),
    ("itscp-build", "`itscp-build`",
     "There is no generator in a tabletop. Phase 6 is you writing the documents, and "
     "[fields.md](fields.md) is the map of which answer goes into which one."),
    ("portfolio.toml", "`portfolio.toml`",
     "The register is the wall: one card per system, one line per dependency. The file is "
     "only how it gets stored if somebody types it up afterwards."),
    ("answer store", "the answer store",
     "The stack of worksheets. It holds the same things — the answer, who gave it, how sure "
     "they were — in columns rather than in keys."),
    ("answers.yaml", "`answers.yaml` in the tree",
     "The worksheets. Nothing to create; the stack of paper is the store."),
    ("the store", "\"the store\"", "The worksheet in front of you."),
)


# --------------------------------------------------------------------------- the sequence

@dataclass(frozen=True)
class Phase:
    """One page: a phase, the room it needs, the technique it carries, the fields it records."""

    slug: str
    #: What the phase is called in ``GETTING-STARTED.md``. A label, not an index.
    number: str
    title: str
    #: Which session this is, in the manual's own words. The tabletop is one exercise in
    #: segments; two phases are deliberately not part of it.
    room: str
    embeds: tuple[Embed, ...]
    #: Answer-store namespaces this phase records. Empty means the phase records no fields.
    namespaces: tuple[str, ...]
    #: This module's own claim about where the phase sits and how it is run.
    lead: str
    #: What the session comes away with, where counting worksheet lines does not say it. A
    #: phase that records no fields still produces something, and two that do record fields
    #: produce more than the count suggests.
    produces: str = ""
    #: Whether to pull the ``Interviewee`` and ``Time`` lines from the first embedded skill.
    session: bool = True


_TABLETOP = ("**The tabletop.** Application and infrastructure teams in the room together, "
             "with the DR process owner. One exercise in segments; run it in a single long "
             "sitting or across several, but keep both teams present for all of it.")

PHASES: tuple[Phase, ...] = (
    Phase(
        "00-portfolio", "0", "The portfolio and the dependency map",
        "**A workshop, before the tabletop.** Whoever can see the whole environment, which is "
        "usually two or three people and never one.",
        (
            Embed("itscp-portfolio", ("Why this exists", "Run order", "Then, per system",
                                      "Red flags")),
            Embed("itscp-dependencies", ("Three kinds of edge", "Eliciting recovery "
                                         "dependencies", "Checking the graph", "What to record",
                                         "Red flags")),
        ),
        (),
        "Once for the organization, before anybody plans anything. You come out of it with a "
        "register: every system, how the tiers rank against each other, the recovery waves, "
        "and what each system needs from the others.\n\n"
        "Four of the failures this method exists to catch live above the level of a single "
        "plan, and none of them can be seen from inside one. That is why this runs first, "
        "rather than after the plan that would have to be rebuilt.\n\n"
        "Do it on a wall. One card per system, laid out left to right in waves, a line drawn "
        "for every dependency. A room will argue with a wall in a way it never argues with a "
        "document, and the failures turn into things you can point at: a line running "
        "backwards, a loop, a card promising to be back sooner than the card it depends on. "
        "The blank register and the five checks are at the foot of this page.\n\n"
        "**Do not start a per-system plan while a check is still failing.** An inversion "
        "means two signed figures contradict each other, and a plan built on top of one "
        "carries that contradiction into everything after it.",
        produces="the register, on a wall",
        session=True,
    ),
    Phase(
        "01-discovery", "1", "What the room brings",
        _TABLETOP + " This segment opens it.",
        (Embed("itscp-discover", ("The hard rule: discovery never mutates",
                                  "What it collects, and why each matters to the plan",
                                  "What it deliberately does not collect",
                                  "What discovery cannot tell you")),),
        ("discovery",),
        "The technical segments go badly from a blank page and well from a list, so the "
        "teams bring the list. There is nothing to install for this. Whatever your people "
        "already use to see the environment will do: the provider console, a CMDB extract, "
        "last quarter's architecture review, the spreadsheet somebody keeps. Print it and "
        "put it on the table.\n\n"
        "Two rules matter more than where the list came from. The first is that **discovery "
        "never changes anything.** Read, export, screenshot; never run a command that "
        "writes, in what is currently somebody's production environment.\n\n"
        "The second is that what the list cannot tell you is most of the reason for bringing "
        "it. A resource nobody can name, a standby that was supposed to exist, a replication "
        "policy covering three buckets out of five: each one goes on the wall as a question "
        "with a name against it, and those questions are what the next two segments are "
        "for.\n\n"
        "If you happen to be on the provider the toolkit supports, and somebody has a clone "
        "of the repository, the read-only walk it ships will build the same list faster. Use "
        "it if you have it. The room works the same either way.",
        produces="the inventory and the gaps in it",
        session=False,
    ),
    Phase(
        "02-business", "2", "The business figures, which gate everything after them",
        "**Not the tabletop.** A separate session with the business or process owner, before "
        "the technical segments. Deliberately not in the room with the IT teams.",
        (Embed("itscp-interview-business",
               ("Tiering is comparative, and this interview does not set the budget",
                "Why this interview gates the others", "Run order",
                "The cost conversation, once", "Red flags")),),
        ("business",),
        "Tiers, maximum tolerable downtime and recovery point are the business's numbers, "
        "and they only stay the business's numbers if the business gives them alone. Put the "
        "same questions to a room full of engineers and what you get is IT deciding what it "
        "is allowed to fail at, which is the failure this whole sequence is arranged to "
        "prevent. So this session happens on its own, and keeping it that way is most of the "
        "work.\n\n"
        "**The technical segments do not start until a tier assignment is signed.** Tier "
        "decides standby capacity, replication topology and what the thing costs to run. "
        "Everything after this is built to those numbers and all of it is expensive to "
        "change later. Running the toolkit, a build step holds that gate for you. Here you "
        "are the gate.\n\n"
        "If the business owner cannot meet for three weeks, wait three weeks. Carrying on "
        "with assumed tiers feels like progress and is the most expensive mistake on offer: "
        "an assumed tier becomes real architecture within a day, and nobody goes back to "
        "check it.",
        session=True,
    ),
    Phase(
        "03a-application", "3a", "The application segment",
        _TABLETOP + " The application team leads this segment; keep the infrastructure team "
        "in the room, because half the corrections come from them.",
        (Embed("itscp-interview-application",
               ("Open with the inventory, not a blank page", "What to elicit", "Hand-offs",
                "Red flags")),),
        ("system", "app"),
        "Open by putting phase 1's inventory on the table. A team corrects a list much "
        "faster than it rebuilds one from memory, and the corrections are themselves "
        "findings worth writing down.\n\n"
        "Bring the deputies to this one. A backup lead engineer sitting quietly through the "
        "session is the cheapest test you will get of whether the deputy could really do any "
        "of it, and it usually answers that question before you have to ask.\n\n"
        "Expect a contradiction with phase 2 here, and do not settle it in the room. The "
        "business said four hours; the application owner says the batch reprocessing alone "
        "takes a day. Write both down, write the name of whoever decides between them, and "
        "carry it back to the business owner. A plan that shows a contradiction and says who "
        "owns it is more honest than one where somebody quietly picked a side.",
        session=True,
    ),
    Phase(
        "03b-infrastructure", "3b", "The infrastructure segment",
        _TABLETOP + " The infrastructure team leads this segment, with the lead engineer "
        "present for anything measured.",
        (Embed("itscp-interview-infrastructure",
               ("Start from the targets, not the technology", "What to elicit",
                "The conversation where targets meet price", "Red flags")),),
        ("infra",),
        "This is where the signed targets turn into a topology and a monthly bill. Read the "
        "tier targets from phase 2 out loud before anything else, so the design conversation "
        "starts from what it has to meet rather than from what already exists.\n\n"
        "Anything that has been measured, ask the lead engineer rather than the owner. A "
        "replication design that has been executed and one that has only been drawn look "
        "identical on a whiteboard, and the person who has run it is the only one in the "
        "room who can tell you which you are looking at. How much of this plan turns out to "
        "be real mostly comes down to that difference.\n\n"
        "Keep the gaps from phase 1 up on the wall while this runs. They are the ones this "
        "particular room can close.",
        session=True,
    ),
    Phase(
        "04-continuity", "4", "The continuity segment",
        _TABLETOP + " The DR process owner leads this segment, with their deputy, and both "
        "technical teams still in the room.",
        (Embed("itscp-interview-continuity",
               ("The one question this interview exists to answer",
                "Part 1 — Roles and succession (§2.3)", "Part 2 — Activation criteria (§3.1)",
                "Part 3 — Notification (§3.2)", "Part 4 — Outage assessment (§3.3)",
                "Part 5 — Escalation thresholds (§4.3) and deactivation (§5.4)", "Red flags")),),
        ("continuity",),
        "This one goes last of the technical segments, because you cannot set an escalation "
        "threshold without real recovery steps to set it against. By the time you get here "
        "the room has them.\n\n"
        "It is also the segment where most organizations find out that nobody owns the "
        "decision to declare. That is not the exercise going wrong. It is the most useful "
        "thing the exercise produces, and a tabletop finds it faster than any interview "
        "will, because everybody who assumed somebody else owned it is sitting at the same "
        "table.\n\n"
        "The succession named here has to agree with the deputy roster from phase 0. Where "
        "the two disagree, write both versions down with the decision owner named against "
        "them, rather than settling it quietly at the whiteboard.",
        session=True,
    ),
    Phase(
        "05-governance", "5", "Approval, review and training",
        "**Not the tabletop.** A separate session with governance, risk or audit, after the "
        "technical segments.",
        (Embed("itscp-interview-governance",
               ("The distinction that frames the whole interview", "What to elicit",
                "Red flags")),),
        ("governance",),
        "A design describes what would happen. A plan is a design somebody committed to, "
        "and the difference is a signature, a review date and a population that has been "
        "trained. This session collects all three.\n\n"
        "It is short and it does not need the technical teams. It does need somebody who can "
        "commit the organization to a review cadence and an exercise schedule, which is why "
        "it sits outside the tabletop rather than inside it.",
        session=True,
    ),
    Phase(
        "06-generate-and-audit", "6", "Writing it up, and auditing what you wrote",
        "**You, on your own,** with the worksheets from every session in front of you.",
        (
            Embed("_method/repo-scaffold", ("Rendering rules",
                                            "Sections every generated document carries"),
                  preamble=True),
            Embed("itscp-audit", ("The rule that makes this an audit rather than a review",
                                  "Verdicts", "Coverage-derived findings", "Portfolio findings",
                                  "Scope", "Output", "Red flags")),
        ),
        (),
        "Half a day on your own, and two jobs rather than one: write the documents out of "
        "the worksheets, then audit what you wrote.\n\n"
        "The writing is mechanical. [fields.md](fields.md) lists every answer under the "
        "document it belongs in, which is also the order to work through them. What people "
        "skip is the part below about marking a missing answer, flagging a low-confidence "
        "figure and keeping the *Unverified statements* section honest, and skipping it is "
        "exactly how a plan riddled with gaps comes out looking finished. **A cell your "
        "worksheet left open becomes a marked gap in the document.** It never becomes a "
        "sentence you wrote to fill the space.\n\n"
        "Then audit, starting from the position that nothing in the plan is met until a "
        "sentence in your own document proves it. Fix whatever blocks approval and leave the "
        "rest visible.",
        produces="the written plan",
        session=False,
    ),
)

#: Embedded whole in ``method.md``. The discipline every phase is run under, and the one file
#: here that needed no adaptation: it is about how people answer, not about what runs.
METHOD_SKILL = "_method/interview"

#: Also embedded in ``method.md``: what a complete plan contains, element by element.
COVERAGE_SKILL = "_method/coverage-map"

#: Embedded in ``method.md``'s appendix, for a room that later types its worksheets up.
STORE_SKILL = "_method/answer-store"

METHOD_EMBEDS: tuple[Embed, ...] = (
    Embed(METHOD_SKILL, ("The Iron Rule", "Every field starts REFUTED",
                         "Ask for the observable, not the abstraction",
                         "Never accept a number without a mechanism", "One question at a time",
                         "\"I don't know\" is data, and it is often the most valuable answer",
                         "Separate what they know from what they are guessing",
                         "Read back before you write", "Provenance on every fact",
                         "Interviews resume; they do not restart",
                         "Contradictions are surfaced, never resolved silently",
                         "Red flags — stop and re-read this file",
                         "What a finished interview looks like")),
)

COVERAGE_EMBEDS: tuple[Embed, ...] = (
    Embed(COVERAGE_SKILL, ("Portfolio scope (above any single plan)", "Front matter",
                           "1. Introduction", "2. Concept of Operations",
                           "3. Activation and Notification", "4. Recovery", "5. Reconstitution",
                           "Appendices", "Beyond NIST", "Not yet covered")),
)

STORE_EMBEDS: tuple[Embed, ...] = (
    Embed(STORE_SKILL, ("Writing rules", "Reading rules")),
)

#: Sections lifted verbatim from ``GETTING-STARTED.md`` into the index page. The guide is the
#: source for all three; repeating them here would be the drift this module exists to avoid.
GETTING_STARTED_SECTIONS: tuple[str, ...] = (
    "Before you start",
    "What good looks like after one pass",
    "Common ways this goes wrong",
)

#: What the guide's own words do not say, because it assumes a loaded plugin.
GETTING_STARTED_PREFACE: dict[str, str] = {
    "Before you start": (
        "Running this as a tabletop, the first of the four does not apply: there is nothing "
        "to install and nothing to load. **The other three do, and the fourth is the one "
        "people skip.**"
    ),
}

#: The findings the validator reports, which the by-hand checks below reproduce. Named here so
#: that ``test_manual`` can assert each one is still a finding the module raises: a check that
#: survives in the manual after the code stopped making it would be a procedure for finding
#: something nobody considers a problem any more.
REGISTER_FINDINGS: tuple[str, ...] = (
    "rto-inversion", "recovery-cycle", "runtime-cycle", "wave-inversion", "wave-concurrency",
    "tier-budget-exceeded", "undeclared-shared-service",
)

#: One line per :class:`itscp_store.Record` field, for the transcription appendix. A test
#: asserts this covers the dataclass exactly.
RECORD_FIELD_NOTES: dict[str, str] = {
    "key": "The field. One of the keys in this manual's checklists, and never anything else.",
    "status": "`MISSING`, `ANSWERED`, `DEFERRED` or `NOT_APPLICABLE`. Every field carries one.",
    "value": "The **Answer** column.",
    "mechanism": "The **What breaks at that number** column.",
    "provenance": "The **Who said it** column, as `interview:<role>:<YYYY-MM-DD>`.",
    "confidence": "The **Sure?** column: `high`, `medium` or `low`.",
    "owner": "The name written in an unanswered row. Required on `MISSING` and `DEFERRED`.",
    "due": "When a deferred answer is expected. A deferral with no date is a gap in disguise.",
    "reason": "Why a row was deferred or ruled out. Never the facilitator's opinion alone.",
    "notes": "Who was in the room, what was contested, what the answer depends on.",
    "readback": "`not_required`, `confirmed` or `corrected`. What happened when you said it back.",
    "conflict": "The second answer, when two people gave different ones, and whose call it is.",
    "superseded": "What an answer replaced, and why. Corrections are appended, never rubbed out.",
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


def skill_preamble(name: str) -> str:
    """A skill's opening text: everything before its first ``##`` heading."""
    path = SKILLS / name / "SKILL.md"
    body = _body(_read(path), path)
    opening: list[str] = []
    fenced = False
    for line in body.splitlines():
        if _FENCE.match(line):
            fenced = not fenced
        if not fenced and line.startswith("## "):
            break
        opening.append(line)
    text = "\n".join(opening).strip("\n")
    if not text:
        raise ManualError(f"{path} has no text before its first section")
    return text


def skill_sections(name: str) -> dict[str, str]:
    """Every ``##`` section of a skill, by heading, in file order.

    Anything before the first heading is dropped: it is the skill's own lead, its *Read
    first* pointer and its ``Interviewee`` and ``Time`` lines, and the manual supplies its
    own lead and reads those two fields separately.
    """
    path = SKILLS / name / "SKILL.md"
    body = _body(_read(path), path)
    sections: dict[str, str] = {}
    heading: str | None = None
    buffer: list[str] = []
    fenced = False

    def close() -> None:
        if heading is None:
            return
        while buffer and buffer[-1].strip() in ("", "---"):
            buffer.pop()
        sections[heading] = "\n".join(buffer).strip("\n")

    for line in body.splitlines():
        if _FENCE.match(line):
            fenced = not fenced
        if not fenced and line.startswith("## "):
            close()
            heading = line[3:].strip()
            buffer = []
            continue
        if heading is not None:
            buffer.append(line)
    close()
    return sections


def _embedded(embeds: tuple[Embed, ...]) -> list[tuple[str, str, str]]:
    """``(skill, heading, text)`` for every section a page carries, in page order."""
    carried: list[tuple[str, str, str]] = []
    for embed in embeds:
        available = skill_sections(embed.skill)
        if embed.preamble:
            carried.append((embed.skill, "", skill_preamble(embed.skill)))
        for heading in embed.sections:
            if heading not in available:
                raise ManualError(
                    f"{embed.skill} has no '## {heading}' section. It was renamed or removed; "
                    "update the page that carries it, or add it to SKIPPED_SECTIONS.")
            carried.append((embed.skill, heading, available[heading]))
    return carried


# --------------------------------------------------------------------------- translation

def _translations_for(text: str) -> list[tuple[str, str]]:
    """The substitutions a page needs, from what its embedded text actually says."""
    return [(label, note) for marker, label, note in TRANSLATIONS if marker in text]


def _translation_table(text: str) -> list[str]:
    found = _translations_for(text)
    if not found:
        return []
    return [
        "### Running this without the toolkit",
        "",
        "The technique below is the skills' own words, and the skills assume a loaded plugin. "
        "You do not have one. These are the substitutions in effect on this page.",
        "",
        "| Where it says | In the room you |",
        "|---|---|",
        *[f"| {label} | {note} |" for label, note in found],
        "",
    ]


# --------------------------------------------------------------------------- field blocks

def _answer_shape(question: bank.Question) -> str:
    """One clause saying what a legal answer to this question looks like."""
    unit = f" in {question.unit}" if question.unit else ""
    if question.kind == "enum":
        return "one of " + ", ".join(f"`{option}`" for option in question.options)
    if question.kind == "rows":
        return "one row per item, columns " + " | ".join(
            f"`{column}`" for column in question.columns)
    if question.kind == "narrative":
        return "several paragraphs, in their words"
    if question.kind == "code":
        return "exact text, written down as dictated or not at all"
    if question.kind == "date":
        return "a date"
    if question.kind == "list":
        return "a list"
    if question.kind in ("duration", "number", "currency"):
        return f"a {question.kind}{unit}"
    return f"free text{unit}"


def _question_block(question: bank.Question) -> list[str]:
    unasked = question.prompt.startswith("Not asked")
    lines = [
        f"#### `{question.id}`",
        "",
        f"*{question.prompt}*" if unasked else f"> \"{question.prompt}\"",
        "",
        f"- **Records:** {question.records}",
        f"- **Answers:** {question.owner_role} · **Shape:** {_answer_shape(question)}",
    ]
    for column, options in sorted(question.enum_columns.items()):
        lines.append(f"- **`{column}` is one of:** "
                     + ", ".join(f"`{option}`" for option in options))
    for figure, explains in sorted(question.figure_columns.items()):
        lines.append(f"- **Every `{figure}` owes a `{explains}`.** A target with no stated "
                     "consequence is a number nobody has to meet.")
    if question.mechanism_required:
        lines.append(f"- **Then ask:** \"{question.mechanism_prompt}\" It goes in the **what "
                     "breaks at that number** column. An empty one makes the figure a guess, "
                     "and the row is marked low confidence.")
    if question.readback_required:
        lines.append("- **Say it back** in one sentence and get a yes before you write it.")
    if question.seedable:
        lines.append("- **Often already on the inventory** the room brought. Read it back for "
                     "correction rather than asking cold, and if nobody confirms it, it stays "
                     "the inventory's claim rather than becoming theirs.")
    if question.guidance:
        lines.append(f"- **Note:** {question.guidance}")
    lines.append(f"- **Goes into:** {question.written_to}")
    if question.structural_provenance == "nist":
        lines.append(f"- **NIST:** {question.nist_heading} ({question.nist_source})")
    elif question.structural_provenance == "ours":
        lines.append("- **No NIST slot.** An element this toolkit carries deliberately; the "
                     "answer in it is elicited like any other.")
    else:
        lines.append("- **These words are the toolkit's, not the room's.** They render as its "
                     "own and are never presented as something anybody in the room said: "
                     f"{question.method_statement}")
    if question.crosswalk_note:
        lines.append(f"- **Terminology:** {question.crosswalk_note}")
    lines.append("")
    return lines


def _checklist(namespaces: tuple[str, ...]) -> list[str]:
    """Every field the phase records, grouped by the section of the plan it feeds."""
    questions = _questions_for(namespaces)
    if not questions:
        return []
    lines = [
        "---",
        "",
        "## What this segment has to come away with",
        "",
        f"{len(questions)} answers, grouped by the section of the plan each one feeds. Read "
        "this before the session; the worksheet at the end is what you take into it.",
        "",
        "Every one of them leaves the room with something written against it. An answer "
        "nobody in the room could give is a **name** — whoever can — which is a result and "
        "not a failure. A blank is neither.",
        "",
    ]
    for row in dict.fromkeys(question.coverage_row for question in questions):
        lines += [f"### {row}", ""]
        for question in (entry for entry in questions if entry.coverage_row == row):
            lines += _question_block(question)
    return lines


# --------------------------------------------------------------------------- worksheets

_WORKSHEET_HEAD = "| What it records | Answer | Who said it | Sure? | What breaks at that number |"
_WORKSHEET_RULE = "|---|---|---|---|---|"
_WORKSHEET_BLANK = "|  |  | H / M / L |  |"


def _questions_for(namespaces: tuple[str, ...]) -> list[bank.Question]:
    return [entry for namespace in namespaces for entry in bank.for_namespace(namespace)]


def _worksheet(namespaces: tuple[str, ...]) -> list[str]:
    """The printable sheet: one line per answer, blank, in the order they are asked."""
    questions = _questions_for(namespaces)
    if not questions:
        return []
    lines = [
        "---",
        "",
        "## The worksheet",
        "",
        "Print this. One line per answer, filled in as it is said rather than afterwards. "
        "Never leave a cell blank: where nobody in the room can answer, write the name of "
        "somebody who can. Two columns need a word of explanation.",
        "",
        "- **Sure?** is how the answer arrived, not how plausible it sounds. H: measured, or "
        "read off a screen while you waited. M: confident from experience, never measured. "
        "L: worked out in the room just now. Ask when you cannot tell.",
        "- **What breaks at that number** is what makes a figure arguable rather than "
        "arbitrary. A duration with an empty cell beside it is a guess, and gets an L.",
        "",
        "Where two people give two answers, write both, and write whose decision it is.",
        "",
    ]
    for row in dict.fromkeys(question.coverage_row for question in questions):
        lines += [f"### {row}", ""]
        scalars = [entry for entry in questions
                   if entry.coverage_row == row and entry.kind != "rows"]
        tables = [entry for entry in questions
                  if entry.coverage_row == row and entry.kind == "rows"]
        if scalars:
            lines += [_WORKSHEET_HEAD, _WORKSHEET_RULE]
            for question in scalars:
                lines.append(f"| {question.records} (`{question.id}`) {_WORKSHEET_BLANK}")
            lines.append("")
        for question in tables:
            columns = list(question.columns) + ["Who said it", "Sure?"]
            lines += [
                f"**{question.records}** (`{question.id}`) — one row each, add as many as the "
                "room needs",
                "",
                "| " + " | ".join(columns) + " |",
                "|" + "---|" * len(columns),
            ]
            for _ in range(3):
                lines.append("| " + " | ".join([" "] * len(question.columns))
                             + " |  | H / M / L |")
            lines.append("")
    return lines


# --------------------------------------------------------------------------- by hand

def _register_worksheet() -> list[str]:
    """The register and its checks, done on a wall instead of by a validator."""
    return [
        "---",
        "",
        "## The register, on a wall",
        "",
        "One card per system, laid out left to right in recovery waves. Everything below is "
        "what a card carries and what the room checks it against. If somebody types it up "
        "afterwards the file has these same fields, and then a validator can make these same "
        "five passes for you.",
        "",
        "### Once for the organization",
        "",
        "| Ask | Write down |",
        "|---|---|",
        "| The organization's name | The name that goes on the plan |",
        "| \"You can have this many systems at each tier.\" | The tier budget. Asked without "
        "one, every owner answers tier 0 and is not wrong to |",
        "| \"How many of these can you genuinely bring up at once, with the people you would "
        "actually have at 3am on a Sunday?\" | The concurrency limit for each wave. It is a "
        "statement about people far more often than about capacity |",
        "",
        "### On each system's card",
        "",
        "| Field | What it holds |",
        "|---|---|",
        "| Name | What the business calls it, not the hostname |",
        "| Class | One of " + ", ".join(f"`{item}`" for item in portfolio.SYSTEM_CLASSES) + " |",
        "| Business owner, application owner | A system with neither is an error, not a gap: "
        "nobody can sign its recovery target |",
        "| Tier, RTO, RPO, MTD | Ranked against the other cards, never in isolation |",
        "| Wave | Which step of the recovery order it belongs to |",
        "| Where its plan lives | Blank means known about and unplanned, which is worth "
        "seeing on the wall |",
        "",
        "### On each line between cards",
        "",
        "| Field | What it holds |",
        "|---|---|",
        "| Points at | The card it needs |",
        "| Kind | One of " + ", ".join(f"`{item}`" for item in portfolio.DEPENDENCY_KINDS)
        + ". `recovery` is the one almost nobody asks for, and the one that finds the "
          "circular plans |",
        "| How badly | " + " or ".join(f"`{item}`" for item in portfolio.CRITICALITIES)
        + ". Only hard lines constrain the recovery order |",
        "| What breaks without it | The sentence that survives a reorganization. The card's "
        "name is only a pointer |",
        "",
        "### Checking the register by hand",
        "",
        "Five passes over the wall. Each one is a question you can answer by looking, and "
        "each is a check the toolkit's validator makes under the name in brackets.",
        "",
        "1. **Walk every hard line and compare the two numbers.** If a card claims to be back "
        "before something it cannot run without, that is a contradiction between two signed "
        "figures. [`rto-inversion`, an error]",
        "2. **Follow the recovery lines and see if you come back to where you started.** Two "
        "systems that each need the other recovered first is a deadlock, and neither plan can "
        "see it because each is separately reasonable. [`recovery-cycle`, an error] Do the "
        "same walk along the runtime lines: a loop there is only a warning, because mutually "
        "dependent at runtime means recover them together, which is possible. "
        "[`runtime-cycle`, a warning]",
        "3. **Check that every hard line points leftwards.** A dependency scheduled after the "
        "thing that needs it cannot execute in the order it is written. Same wave is not an "
        "error but it is unspecified, so say which goes first. [`wave-inversion`, an error; "
        "`wave-concurrency`, a warning]",
        "4. **Count the cards in each tier against the budget.** More tier 0 systems than the "
        "budget allows means the ranking has not happened yet. [`tier-budget-exceeded`]",
        "5. **Count the hard lines arriving at each card.** "
        f"{portfolio.SHARED_SERVICE_THRESHOLD} or more makes it a shared service in practice "
        "whatever it is labelled, and hiding that from the recovery order is how it ends up "
        "in the wrong wave. [`undeclared-shared-service`]",
        "",
        "**Never fix a failing check by editing a number.** The wall would agree with itself "
        "and the plan would still be impossible; you would have deleted the finding rather "
        "than the problem. Three honest outcomes: the dependency's target tightens, the "
        "dependant's relaxes, or the dependency is broken — a cached credential, a read-only "
        "mode, a queue that absorbs the gap. The third is the best answer and the one nobody "
        "reaches for unaided, so offer it.",
        "",
    ]


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
        "# The tabletop",
        "",
        _BANNER,
        "",
        "This engagement, run as a facilitated exercise: the application and infrastructure "
        "teams in one room, a printed worksheet on the table, and nothing to install. The "
        "questions are the same ones the toolkit asks, because both are generated from the "
        "same files.",
        "",
        "Two of the phases are deliberately kept out of the room. The business figures come "
        "first, on their own, because tiers agreed in front of the engineers who will have "
        "to meet them stop being the business's figures. Governance comes afterwards and "
        "needs nobody technical.",
        "",
        "Read [the method](method.md) before the first session. It is the discipline all of "
        "this runs under, and the one part that is not optional. A plan whose numbers nobody "
        "gave is worse than one with visible gaps, and the method is what keeps the two "
        "apart.",
        "",
        "## The running order",
        "",
        "| Phase | Session | Answers to come away with |",
        "|---|---|---|",
    ]
    for phase in PHASES:
        counted = len(_questions_for(phase.namespaces))
        room = phase.room.split(".")[0].strip().replace("**", "")
        outcome = f"{counted} answer{'' if counted == 1 else 's'}" if counted else ""
        if phase.produces:
            outcome = f"{outcome}, plus {phase.produces}" if outcome else phase.produces
        lines.append(f"| {_phase_link(phase)} | {room} | {outcome} |")
    lines += [
        "",
        "Phase 7 is not a document. It is the signature, and then the drill: **every duration "
        "in the plan is a design target, and none of them are commitments until a drill has "
        "measured one.** Schedule the first drill before the approval meeting ends.",
        "",
        "## What to print",
        "",
        "Each phase page ends with a worksheet sized for its session. Print the worksheet for "
        "the session you are running; read the rest of the page before it.",
        "",
        "- [The method](method.md) — how an answer is captured, and the appendix for typing "
        "the worksheets up afterwards.",
        "- [Every answer, by the document it belongs in](fields.md) — the order to write the "
        "plan in, and the full index.",
        "",
        "---",
        "",
    ]
    for heading in GETTING_STARTED_SECTIONS:
        extracted = _section(guide, heading, GETTING_STARTED)
        lines += [f"## {heading}", ""]
        if heading in GETTING_STARTED_PREFACE:
            lines += [GETTING_STARTED_PREFACE[heading], ""]
        lines += _translation_table(extracted)
        lines += [extracted, "", "---", ""]
    return "\n".join(lines).rstrip("\n") + "\n"


def _capture_sheet() -> list[str]:
    return [
        "## Capturing what the room says",
        "",
        "There is no file to write and nothing to install. The answer store is the stack of "
        "worksheets, holding what the toolkit's store holds: the answer, who gave it, how "
        "sure they were, and what breaks at that number. Columns instead of keys. Where the "
        "pages that follow say *write it to the store*, they mean the sheet in front of you.",
        "",
        "Every phase page ends with its own worksheet. They all have the same five columns:",
        "",
        _WORKSHEET_HEAD,
        _WORKSHEET_RULE,
        "| Maximum tolerable downtime for the tier 0 processes | 8h | Head of Finance Systems "
        "| M | Overnight bank file cuts at 18:00; missing it loses a day of settlement |",
        "| Who declares a disaster | *nobody in the room knew — **Ops Director** to confirm* "
        "|  |  | Raised in session, unowned |",
        "| Time to rebuild from backup | 6h | Lead engineer | L | Never measured. First drill "
        "objective |",
        "",
        "Four rules, and the first is the one that makes the other three work.",
        "",
        "1. **Never leave a cell blank.** An answer nobody has is a name, written in the "
        "answer column. A room that leaves twelve named unknowns has done more for the "
        "organization than one that leaves twelve confident inventions.",
        "2. Write it as it is said. A worksheet filled in from memory at the end of the day "
        "is a worksheet nobody can attribute.",
        "3. The Sure? column is about how the answer arrived, not how plausible it sounds. "
        "\"Is that something you have measured, or is it your best read?\" is not a rude "
        "question. It decides whether the figure can go in front of an auditor, and people "
        "are usually relieved to be asked.",
        "4. Two answers means two rows, with the name of whoever decides between them. Do "
        "not average them, and do not quietly keep the more senior one.",
        "",
    ]


def _method_page() -> str:
    record_fields = [field.name for field in dataclass_fields(store.Record)]
    undescribed = [name for name in record_fields if name not in RECORD_FIELD_NOTES]
    if undescribed:
        raise ManualError("the answer record has fields the manual does not describe: "
                          + ", ".join(undescribed))
    method_text = _embedded(METHOD_EMBEDS)
    coverage_text = _embedded(COVERAGE_EMBEDS)
    store_text = _embedded(STORE_EMBEDS)
    joined = "\n".join(text for _, _, text in method_text + coverage_text + store_text)
    lines = [
        "# The method",
        "",
        _BANNER,
        "",
        "Read this before the first session. It is the discipline every phase is run under, "
        "and it is the same file the toolkit reads: it is about how people answer, which does "
        "not change when the facilitator is a person rather than a program.",
        "",
        "---",
        "",
        *_capture_sheet(),
        "---",
        "",
        "## The elicitation discipline",
        "",
        *_translation_table(joined),
        *_sections(method_text),
        "---",
        "",
        "## What a complete plan contains",
        "",
        "The full element list, so that phase 6 is assembly rather than invention.",
        "",
        *_sections(coverage_text),
        "---",
        "",
        "## Appendix — typing the worksheets up",
        "",
        "**Optional, and not part of the exercise.** If the organization later adopts the "
        "toolkit, the worksheets transcribe into its answer store one row per record, and the "
        "cross-system checks then run for you. The columns map like this.",
        "",
        "| Store field | Worksheet |",
        "|---|---|",
        *[f"| `{name}` | {RECORD_FIELD_NOTES[name]} |" for name in record_fields],
        "",
        f"Statuses: {', '.join(f'`{status}`' for status in bank.STATUSES)}. "
        f"Confidence: {', '.join(f'`{level}`' for level in bank.CONFIDENCES)}. "
        f"Read-back: {', '.join(f'`{state}`' for state in bank.READBACKS)}.",
        "",
        "The seven roles a name may be recorded against, each of which also owes a deputy: "
        + ", ".join(f"`{role}`" for role in bank.ROLES) + ".",
        "",
        *_sections(store_text),
    ]
    return "\n".join(lines).rstrip("\n") + "\n"


def _sections(carried: list[tuple[str, str, str]]) -> list[str]:
    """Embedded sections, each under its own heading, demoted to sit under the page's."""
    lines: list[str] = []
    for _, heading, text in carried:
        if heading:
            lines.append(f"### {heading}")
            lines.append("")
        lines += [_demote(text), ""]
    return lines


def _phase_page(phase: Phase) -> str:
    carried = _embedded(phase.embeds)
    joined = "\n".join(text for _, _, text in carried)
    lines = [
        f"# Phase {phase.number} — {phase.title}",
        "",
        _BANNER,
        "",
        phase.room,
        "",
    ]
    if phase.session:
        _, body, path = _skill_body(phase.embeds[0].skill)
        lines += [
            f"**Whose answers these are:** {_bold_field(body, 'Interviewee', path)}",
            "",
            f"**How long:** {_bold_field(body, 'Time', path)}",
            "",
        ]
    lines += [
        phase.lead,
        "",
        "**Run under [the method](method.md).** Nothing enters the plan unless somebody in "
        "the room said it, an inventory shows it, or it is written down as a gap with a name "
        "against it.",
        "",
        "---",
        "",
    ]
    lines += _translation_table(joined)
    lines += ["## The technique", ""]
    for skill in dict.fromkeys(skill for skill, _, _ in carried):
        front = _frontmatter(_read(SKILLS / skill / "SKILL.md"), SKILLS / skill / "SKILL.md")
        lines += [f"*From `{front['name']}`: {front['description']}*", ""]
        lines += _sections([entry for entry in carried if entry[0] == skill])
    if phase.slug == "00-portfolio":
        lines += _register_worksheet()
    lines += _checklist(phase.namespaces)
    lines += _worksheet(phase.namespaces)
    return "\n".join(lines).rstrip("\n") + "\n"


def _skill_body(name: str) -> tuple[dict[str, str], str, Path]:
    path = SKILLS / name / "SKILL.md"
    text = _read(path)
    return _frontmatter(text, path), _body(text, path), path


def _landing_files(written_to: str) -> list[str]:
    """The files one answer belongs in, with any trailing section number dropped."""
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
        "# Every answer, and the document it belongs in",
        "",
        _BANNER,
        "",
        f"The {len(bank.QUESTIONS)} answers a first plan is built from, listed twice: by the "
        "document each one is written into, which is the order to write in, and then as a "
        "flat index. An answer feeding two documents appears under both.",
        "",
        "---",
        "",
        "## By document",
        "",
    ]
    for path in sorted(by_file):
        lines += [f"### `{path}`", "", "| Answer | What it records | Who gives it |",
                  "|---|---|---|"]
        for question in by_file[path]:
            lines.append(f"| `{question.id}` | {question.records} | {question.owner_role} |")
        lines.append("")
    lines += [
        "---",
        "",
        "## The full index",
        "",
        "| Answer | Phase | Shape | Who gives it | Section of the plan |",
        "|---|---|---|---|---|",
    ]
    for question in bank.QUESTIONS:
        phase = phase_of[question.namespace]
        lines.append(f"| `{question.id}` | [{phase.number}]({phase.slug}.md) | "
                     f"{question.kind} | {question.owner_role} | {question.coverage_row} |")
    lines += [
        "",
        f"Figures that owe a *what breaks at that number*: "
        f"{sum(q.mechanism_required for q in bank.QUESTIONS)}. "
        f"Answers to say back before writing them down: "
        f"{sum(q.readback_required for q in bank.QUESTIONS)}. "
        f"Answers the inventory usually already holds: "
        f"{sum(q.seedable for q in bank.QUESTIONS)}.",
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
