"""The portfolio: the register of systems, the graph between them, and the recovery order.

An organization does not have *a* system. It has a core product suite, the applications that
read from it, the tooling those are built and deployed with, the public interfaces clients
push data into, and the websites that front all of it. NIST SP 800-34 Rev. 1 specifies a plan
for *an information system*, and it is right to: an auditor asking for the identity database's
ISCP should receive one document, not the environment. But a stack of individually correct plans is
not a portfolio plan, and the gap between the two is where real invocations fail.

Four failures live only at this level, and none of them are visible from inside a single plan:

**Recovery time inversion.** A system cannot be available before something it hard-depends on.
Order management declares two hours; the identity database it authenticates against declares
eight. Both plans are internally coherent. Together they are impossible, and because the two
were written by different people in different weeks, nothing in either document can see it.

**Recovery dependencies, as distinct from runtime ones.** Every interview asks what a system
needs in order to *run*. Almost none ask what it needs in order to be *recovered*. If the
runbooks are in the source control server, the instructions are inside the outage. If the
cloud console authenticates through the identity database, the first system that must be
recovered is the one nobody can log in to. These are circular, they are common, and they are
found during the invocation rather than during the planning.

**Wave ordering.** Recovery is sequenced, not simultaneous, and the constraint that binds is
usually people rather than infrastructure. A dependency scheduled to recover after its
dependant is a plan that cannot execute in the order it is written.

**Tier inflation.** Ask forty application owners in isolation and forty systems are Tier 0.
A tier only means something against a constrained budget, so the budget belongs here, where
the systems can be compared, rather than in any one of their plans.

This module holds the register and the checks. It reads and writes TOML with the same
hand-written emitter discipline as ``itscp_store``: ``tomllib`` reads and does not write, and
comments are regenerated rather than preserved.

Read ``skills/itscp-portfolio/SKILL.md`` for how the register is elicited and
``skills/itscp-dependencies/SKILL.md`` for how the graph is.
"""
from __future__ import annotations

import sys

if sys.version_info < (3, 11):
    raise RuntimeError(
        "itscp-author needs Python 3.11 or newer (this is "
        f"{sys.version_info.major}.{sys.version_info.minor}). The portfolio reads TOML "
        "through the standard library's tomllib, added in 3.11."
    )

import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1

#: The filename the register lives under, beside the answer store.
PORTFOLIO_FILENAME = "portfolio.toml"

#: What a system *is*, which determines what questions it deserves and roughly where in the
#: recovery order it belongs. Drawn from the shape a real environment has rather than invented:
#: a core product suite, the applications reading from it, the tooling underneath, the
#: public interfaces clients push into, and the sites that front them.
SYSTEM_CLASSES: tuple[str, ...] = (
    "shared-platform",    # identity, network, secrets, certificates: wave 0, everything needs it
    "core-data",          # the core product suite; the system of record others read
    "dependent-app",      # an application that consumes a core system
    "supporting-infra",   # source control, artefact repository, ticketing, CI
    "public-api",         # ingests data from clients; loss here may be unrecoverable by resend
    "public-web",         # public-facing site; reputational rather than transactional exposure
)

#: Why one system needs another. The distinction between the first two is the reason this
#: module exists: a runtime dependency shapes the recovery *order*, a recovery dependency can
#: make recovery *impossible*, and only one of them is ever asked about.
DEPENDENCY_KINDS: tuple[str, ...] = (
    "runtime",    # needed for the dependant to function
    "recovery",   # needed in order to RECOVER the dependant: runbooks, secrets, console login
    "data",       # exchanges data with it; an interface, not a hard prerequisite
)

#: Whether the dependant works at all without it.
CRITICALITIES: tuple[str, ...] = ("hard", "soft")

_SEVERITIES: tuple[str, ...] = ("ERROR", "WARNING")

#: A duration as people write one: 0, 30m, 4h, 2d. Parsed to minutes for comparison only;
#: the register keeps the text the interviewee actually said.
_DURATION = re.compile(r"^(?P<count>\d+(?:\.\d+)?)(?P<unit>[mhdw])?$", re.I)
_UNIT_MINUTES = {"m": 1, "h": 60, "d": 60 * 24, "w": 60 * 24 * 7}

#: How many dependants make a system shared in practice, whatever its declared class. A
#: system four others cannot run without is a concentration of risk, and calling it a
#: dependent-app hides that from the recovery order.
SHARED_SERVICE_THRESHOLD = 4


class PortfolioError(Exception):
    """The register exists but is not usable. Expected, reported, never a crash."""


# --------------------------------------------------------------------------- record shapes

@dataclass(frozen=True)
class Dependency:
    """One edge: this system needs ``on``, for ``kind`` reasons, ``criticality`` badly."""

    on: str
    kind: str = "runtime"
    criticality: str = "hard"
    notes: str = ""

    def __post_init__(self) -> None:
        if self.kind not in DEPENDENCY_KINDS:
            raise PortfolioError(
                f"dependency on {self.on!r} has kind {self.kind!r}; expected one of "
                f"{', '.join(DEPENDENCY_KINDS)}")
        if self.criticality not in CRITICALITIES:
            raise PortfolioError(
                f"dependency on {self.on!r} has criticality {self.criticality!r}; expected "
                f"one of {', '.join(CRITICALITIES)}")


@dataclass(frozen=True)
class Wave:
    """One step of the recovery order.

    ``max_concurrent`` is the number of systems the organization can actually recover at
    once in this wave. It is a statement about people far more often than about capacity,
    and it is the number that turns a wish list into a sequence.
    """

    id: int
    name: str
    purpose: str
    max_concurrent: int = 0     # 0 means unconstrained, and says so rather than implying it


@dataclass(frozen=True)
class System:
    """One row of the register: a system, its targets, its owners, and what it needs."""

    slug: str
    name: str
    system_class: str
    business_owner: str
    application_owner: str
    tier: int | None
    rto: str
    rpo: str
    mtd: str
    wave: int | None
    plan_repo: str = ""
    depends_on: tuple[Dependency, ...] = ()
    notes: str = ""

    def __post_init__(self) -> None:
        if self.system_class not in SYSTEM_CLASSES:
            raise PortfolioError(
                f"system {self.slug!r} has class {self.system_class!r}; expected one of "
                f"{', '.join(SYSTEM_CLASSES)}")


#: The recovery order a first pass starts from. Wave 0 exists because the tooling recovery
#: itself needs is the thing most often left out of the plan it is needed by.
DEFAULT_WAVES: tuple[Wave, ...] = (
    Wave(0, "Foundation",
         "Identity, network, secrets, and the tooling the recovery itself depends on", 3),
    Wave(1, "Core data",
         "The systems of record everything else reads from", 2),
    Wave(2, "Dependent applications and public interfaces",
         "Applications and client-facing interfaces built on the core", 4),
    Wave(3, "Supporting and internal tooling",
         "Development, reporting and internal tooling that can wait", 6),
)


@dataclass(frozen=True)
class Portfolio:
    """The whole register."""

    organization: str
    waves: tuple[Wave, ...] = DEFAULT_WAVES
    systems: tuple[System, ...] = ()
    #: Tier to the maximum number of systems allowed in it. Empty means nobody has set a
    #: budget yet, which is itself worth knowing and is not the same as unlimited.
    tier_budget: dict[int, int] = field(default_factory=dict)

    def by_slug(self) -> dict[str, System]:
        return {system.slug: system for system in self.systems}


@dataclass(frozen=True)
class Finding:
    """One cross-system problem, named so that it can be argued with."""

    code: str
    severity: str
    system: str
    detail: str

    def __post_init__(self) -> None:
        if self.severity not in _SEVERITIES:
            raise PortfolioError(f"finding {self.code!r} has severity {self.severity!r}")


@dataclass(frozen=True)
class Report:
    """The counts a caller needs to decide what to do."""

    findings: tuple[Finding, ...]
    errors: int
    warnings: int

    @property
    def exit_code(self) -> int:
        """0 clean, 1 warnings only, 2 any error. Shell-shaped on purpose."""
        if self.errors:
            return 2
        return 1 if self.warnings else 0


def report(findings) -> Report:
    findings = tuple(findings)
    return Report(
        findings=findings,
        errors=sum(1 for f in findings if f.severity == "ERROR"),
        warnings=sum(1 for f in findings if f.severity == "WARNING"),
    )


# ------------------------------------------------------------------------------- durations

def duration_minutes(text: str) -> float | None:
    """Minutes, or ``None`` when the text is not a duration this can compare.

    Returning ``None`` rather than raising is deliberate. An unparseable recovery target is a
    gap in the register, and the checks below skip comparisons they cannot make instead of
    refusing the whole file. A register that will not load teaches nobody anything.
    """
    if not isinstance(text, str):
        return None
    stripped = text.strip().lower()
    if not stripped:
        return None
    match = _DURATION.match(stripped)
    if not match:
        return None
    unit = match.group("unit") or "m"
    return float(match.group("count")) * _UNIT_MINUTES[unit]


# ------------------------------------------------------------------------------ validation

def validate(portfolio: Portfolio) -> tuple[Finding, ...]:
    """Every cross-system check, in one pass. Order is stable so output diffs are readable."""
    findings: list[Finding] = []
    known = portfolio.by_slug()

    findings.extend(_check_edges_resolve(portfolio, known))
    findings.extend(_check_rto_inversions(portfolio, known))
    findings.extend(_check_cycles(portfolio, known))
    findings.extend(_check_waves(portfolio, known))
    findings.extend(_check_register_completeness(portfolio))
    findings.extend(_check_tier_budget(portfolio))
    findings.extend(_check_shared_services(portfolio, known))
    return tuple(findings)


def _check_edges_resolve(portfolio: Portfolio, known: dict[str, System]) -> list[Finding]:
    findings = []
    for system in portfolio.systems:
        for edge in system.depends_on:
            if edge.on == system.slug:
                findings.append(Finding(
                    "self-dependency", "ERROR", system.slug,
                    f"{system.slug} depends on itself"))
            elif edge.on not in known:
                findings.append(Finding(
                    "unknown-dependency", "ERROR", system.slug,
                    f"{system.slug} depends on {edge.on!r}, which is not in the register. "
                    "Either add it as a system or correct the slug; an edge to nothing "
                    "cannot be sequenced or checked."))
    return findings


def _check_rto_inversions(portfolio: Portfolio, known: dict[str, System]) -> list[Finding]:
    """A system cannot be back before something it cannot run without."""
    findings = []
    for system in portfolio.systems:
        mine = duration_minutes(system.rto)
        if mine is None:
            continue
        for edge in system.depends_on:
            if edge.criticality != "hard" or edge.kind == "data":
                continue
            other = known.get(edge.on)
            if other is None:
                continue
            theirs = duration_minutes(other.rto)
            if theirs is None or theirs <= mine:
                continue
            findings.append(Finding(
                "rto-inversion", "ERROR", system.slug,
                f"{system.slug} declares an RTO of {system.rto} but hard-depends on "
                f"{other.slug}, which declares {other.rto}. {system.slug} cannot be "
                f"available before {other.slug} is. One of the two figures is wrong, and "
                f"the business owners of both have to agree which."))
    return findings


def _edges_of_kind(portfolio: Portfolio, kinds: tuple[str, ...],
                   hard_only: bool) -> dict[str, set[str]]:
    graph: dict[str, set[str]] = {system.slug: set() for system in portfolio.systems}
    for system in portfolio.systems:
        for edge in system.depends_on:
            if edge.kind not in kinds:
                continue
            if hard_only and edge.criticality != "hard":
                continue
            if edge.on in graph:
                graph[system.slug].add(edge.on)
    return graph


def _find_cycle(graph: dict[str, set[str]]) -> list[str] | None:
    """One cycle if the graph has any, as the path that closes it. Iterative depth-first."""
    WHITE, GREY, BLACK = 0, 1, 2
    color = dict.fromkeys(graph, WHITE)
    for root in sorted(graph):
        if color[root] != WHITE:
            continue
        stack = [(root, iter(sorted(graph[root])))]
        path = [root]
        color[root] = GREY
        while stack:
            node, children = stack[-1]
            advanced = False
            for child in children:
                if color.get(child, BLACK) == GREY:
                    return path[path.index(child):] + [child]
                if color.get(child, BLACK) == WHITE:
                    color[child] = GREY
                    path.append(child)
                    stack.append((child, iter(sorted(graph[child]))))
                    advanced = True
                    break
            if not advanced:
                color[node] = BLACK
                stack.pop()
                path.pop()
    return None


def _check_cycles(portfolio: Portfolio, known: dict[str, System]) -> list[Finding]:
    findings = []

    recovery_cycle = _find_cycle(_edges_of_kind(portfolio, ("recovery",), hard_only=False))
    if recovery_cycle:
        findings.append(Finding(
            "recovery-cycle", "ERROR", recovery_cycle[0],
            "recovery dependencies form a cycle: " + " -> ".join(recovery_cycle) + ". "
            "Each of these needs another to be recovered first, so none of them can be "
            "recovered at all. Break it by putting whatever one of them needs -- the "
            "runbooks, the credentials, the console access -- somewhere outside the cycle."))

    runtime_cycle = _find_cycle(_edges_of_kind(portfolio, ("runtime",), hard_only=False))
    if runtime_cycle:
        findings.append(Finding(
            "runtime-cycle", "WARNING", runtime_cycle[0],
            "runtime dependencies form a cycle: " + " -> ".join(runtime_cycle) + ". "
            "Mutually dependent systems can still be recovered together, but they cannot be "
            "recovered in an order, so they belong in one wave and probably in one plan."))
    return findings


def _check_waves(portfolio: Portfolio, known: dict[str, System]) -> list[Finding]:
    findings = []
    waves = {wave.id: wave for wave in portfolio.waves}

    for system in portfolio.systems:
        if system.wave is None:
            continue
        for edge in system.depends_on:
            if edge.criticality != "hard" or edge.kind == "data":
                continue
            other = known.get(edge.on)
            if other is None or other.wave is None:
                continue
            if other.wave > system.wave:
                findings.append(Finding(
                    "wave-inversion", "ERROR", system.slug,
                    f"{system.slug} recovers in wave {system.wave} but hard-depends on "
                    f"{other.slug}, which recovers in wave {other.wave}. The plan cannot "
                    f"execute in the order it is written."))
            elif other.wave == system.wave:
                findings.append(Finding(
                    "wave-concurrency", "WARNING", system.slug,
                    f"{system.slug} and its hard dependency {other.slug} are both in wave "
                    f"{system.wave}. Ordering within a wave is unspecified, so state the "
                    f"order explicitly or move {other.slug} earlier."))

    counts: dict[int, int] = {}
    for system in portfolio.systems:
        if system.wave is not None:
            counts[system.wave] = counts.get(system.wave, 0) + 1
    for wave_id, count in sorted(counts.items()):
        wave = waves.get(wave_id)
        if wave is None:
            findings.append(Finding(
                "unknown-wave", "ERROR", "",
                f"{count} system(s) are assigned to wave {wave_id}, which is not defined."))
            continue
        if wave.max_concurrent and count > wave.max_concurrent:
            findings.append(Finding(
                "wave-overload", "WARNING", "",
                f"wave {wave_id} ({wave.name}) holds {count} systems but states it can "
                f"recover {wave.max_concurrent} at once. Either the wave splits, or the "
                f"later systems in it wait, and their recovery targets have to say so."))
    return findings


def _check_register_completeness(portfolio: Portfolio) -> list[Finding]:
    findings = []
    for system in portfolio.systems:
        missing = [label for label, value in (
            ("business owner", system.business_owner),
            ("application owner", system.application_owner),
        ) if not str(value).strip()]
        if missing:
            findings.append(Finding(
                "orphan-system", "ERROR", system.slug,
                f"{system.slug} has no {' and no '.join(missing)}. A system with no named "
                f"owner has nobody who can sign a recovery target, and no amount of "
                f"documentation fixes that."))
        if not str(system.plan_repo).strip():
            findings.append(Finding(
                "no-plan", "WARNING", system.slug,
                f"{system.slug} is in the register with no plan repository. It is a system "
                f"the organization knows it has and has not planned for."))
    return findings


def _check_tier_budget(portfolio: Portfolio) -> list[Finding]:
    if not portfolio.tier_budget:
        return []
    findings = []
    counts: dict[int, int] = {}
    for system in portfolio.systems:
        if system.tier is not None:
            counts[system.tier] = counts.get(system.tier, 0) + 1
    for tier, allowed in sorted(portfolio.tier_budget.items()):
        actual = counts.get(tier, 0)
        if actual > allowed:
            findings.append(Finding(
                "tier-budget-exceeded", "WARNING", "",
                f"{actual} systems are tier {tier} against a budget of {allowed}. Asked in "
                f"isolation every owner says tier 0; a tier only means something when the "
                f"systems are ranked against each other."))
    return findings


def _check_shared_services(portfolio: Portfolio, known: dict[str, System]) -> list[Finding]:
    dependants: dict[str, int] = {}
    for system in portfolio.systems:
        for edge in system.depends_on:
            if edge.criticality == "hard" and edge.on in known:
                dependants[edge.on] = dependants.get(edge.on, 0) + 1

    findings = []
    for slug, count in sorted(dependants.items()):
        system = known[slug]
        if count < SHARED_SERVICE_THRESHOLD:
            continue
        if system.system_class in ("shared-platform", "core-data"):
            continue
        findings.append(Finding(
            "undeclared-shared-service", "WARNING", slug,
            f"{count} systems hard-depend on {slug}, but it is classed as "
            f"{system.system_class}. In practice it is a shared service, and a concentration "
            f"of risk its class hides from the recovery order."))
    return findings


# ------------------------------------------------------------------------------ TOML shape

def load(parsed: dict) -> Portfolio:
    """A parsed TOML document as a :class:`Portfolio`."""
    try:
        systems = tuple(_load_system(table) for table in parsed.get("system", ()))
        waves = tuple(
            Wave(id=int(table["id"]), name=str(table.get("name", "")),
                 purpose=str(table.get("purpose", "")),
                 max_concurrent=int(table.get("max_concurrent", 0)))
            for table in parsed.get("wave", ())
        ) or DEFAULT_WAVES
        budget = {int(k): int(v) for k, v in (parsed.get("tier_budget") or {}).items()}
    except PortfolioError:
        raise
    except (KeyError, TypeError, ValueError) as bad:
        raise PortfolioError(f"the portfolio register is malformed: {bad}") from bad
    return Portfolio(
        organization=str(parsed.get("organization", "")),
        waves=waves, systems=systems, tier_budget=budget)


def _load_system(table: dict) -> System:
    return System(
        slug=str(table["slug"]),
        name=str(table.get("name", "")),
        system_class=str(table.get("class", "dependent-app")),
        business_owner=str(table.get("business_owner", "")),
        application_owner=str(table.get("application_owner", "")),
        tier=_optional_int(table.get("tier")),
        rto=str(table.get("rto", "")),
        rpo=str(table.get("rpo", "")),
        mtd=str(table.get("mtd", "")),
        wave=_optional_int(table.get("wave")),
        plan_repo=str(table.get("plan_repo", "")),
        notes=str(table.get("notes", "")),
        depends_on=tuple(
            Dependency(on=str(edge["on"]), kind=str(edge.get("kind", "runtime")),
                       criticality=str(edge.get("criticality", "hard")),
                       notes=str(edge.get("notes", "")))
            for edge in table.get("depends_on", ())
        ),
    )


def _optional_int(value: Any) -> int | None:
    return None if value is None or value == "" else int(value)


def emit(portfolio: Portfolio) -> str:
    """The register as TOML, with its guidance regenerated as comments.

    Hand written for the same reason ``itscp_store.emit`` is: ``tomllib`` reads and does not
    write, and it discards comments, so the file is a projection of schema plus data and the
    guidance is always current.
    """
    lines = [
        "# portfolio.toml - the register of systems, what they need, and the order they",
        "# recover in. Generated and regenerated by itscp-portfolio; comments come from the",
        "# schema, so edits to them are overwritten on the next write.",
        "#",
        "# A per-system plan can be correct on its own and impossible in company. This file",
        "# is where that is checked: run itscp_portfolio.validate to find recovery time",
        "# inversions, dependency cycles and wave ordering the individual plans cannot see.",
        "",
        f"schema_version = {SCHEMA_VERSION}",
        f"organization = {_toml_string(portfolio.organization)}",
        "",
    ]

    if portfolio.tier_budget:
        lines += [
            "# How many systems each tier may hold. Asked in isolation every owner says",
            "# tier 0; the budget is what makes the ranking comparative.",
            "[tier_budget]",
        ]
        lines += [f'"{tier}" = {allowed}' for tier, allowed in sorted(portfolio.tier_budget.items())]
        lines.append("")

    lines += [
        "# The recovery order. max_concurrent is how many of a wave's systems can actually",
        "# be recovered at once, which is a statement about people more often than capacity.",
        "",
    ]
    for wave in portfolio.waves:
        lines += [
            "[[wave]]",
            f"id = {wave.id}",
            f"name = {_toml_string(wave.name)}",
            f"purpose = {_toml_string(wave.purpose)}",
            f"max_concurrent = {wave.max_concurrent}",
            "",
        ]

    lines += [
        "# One block per system. class is one of: " + ", ".join(SYSTEM_CLASSES) + ".",
        "# depends_on.kind is one of: " + ", ".join(DEPENDENCY_KINDS) + ". A recovery",
        "# dependency is what the system needs in order to BE recovered, which is the",
        "# question almost nobody asks and the one that finds circular plans.",
        "",
    ]
    for system in portfolio.systems:
        lines += [
            "[[system]]",
            f"slug = {_toml_string(system.slug)}",
            f"name = {_toml_string(system.name)}",
            f"class = {_toml_string(system.system_class)}",
            f"business_owner = {_toml_string(system.business_owner)}",
            f"application_owner = {_toml_string(system.application_owner)}",
            f"tier = {system.tier if system.tier is not None else '\"\"'}",
            f"rto = {_toml_string(system.rto)}",
            f"rpo = {_toml_string(system.rpo)}",
            f"mtd = {_toml_string(system.mtd)}",
            f"wave = {system.wave if system.wave is not None else '\"\"'}",
            f"plan_repo = {_toml_string(system.plan_repo)}",
        ]
        if system.notes:
            lines.append(f"notes = {_toml_string(system.notes)}")
        lines.append("")
        for edge in system.depends_on:
            lines += [
                "[[system.depends_on]]",
                f"on = {_toml_string(edge.on)}",
                f"kind = {_toml_string(edge.kind)}",
                f"criticality = {_toml_string(edge.criticality)}",
            ]
            if edge.notes:
                lines.append(f"notes = {_toml_string(edge.notes)}")
            lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def _toml_string(text: str) -> str:
    escaped = (str(text).replace("\\", "\\\\").replace('"', '\\"')
               .replace("\n", "\\n").replace("\t", "\\t"))
    return f'"{escaped}"'


def read(path: Path) -> Portfolio:
    """Load a register from disk, reporting a missing or malformed file rather than crashing."""
    try:
        return load(tomllib.loads(Path(path).read_text()))
    except FileNotFoundError as missing:
        raise PortfolioError(
            f"no portfolio register at {path}. Run the itscp-portfolio skill to build one; "
            "without it the plans cannot be checked against each other.") from missing
    except tomllib.TOMLDecodeError as bad:
        raise PortfolioError(f"the portfolio register at {path} is not valid TOML: {bad}") from bad


def format_report(portfolio: Portfolio, findings) -> str:
    """The findings as text, errors first, each naming what to do about it."""
    summary = report(findings)
    lines = [
        f"Portfolio: {portfolio.organization}",
        f"Systems: {len(portfolio.systems)}   "
        f"Errors: {summary.errors}   Warnings: {summary.warnings}",
    ]
    if not summary.findings:
        lines.append("")
        lines.append("No cross-system findings. Every plan's targets are consistent with "
                     "the plans it depends on.")
        return "\n".join(lines)
    for severity in _SEVERITIES:
        rows = [f for f in summary.findings if f.severity == severity]
        if not rows:
            continue
        lines.append("")
        lines.append(f"{severity} ({len(rows)})")
        for finding in rows:
            where = f" [{finding.system}]" if finding.system else ""
            lines.append(f"  {finding.code}{where}")
            lines.append(f"    {finding.detail}")
    return "\n".join(lines)


# ------------------------------------------------------------------------------ entry point

def _main(argv: list[str]) -> int:
    """``python3 itscp_portfolio.py <portfolio.toml>`` - validate a register and report.

    Exit code is the report's: 0 clean, 1 warnings only, 2 any error. That makes it usable
    from a pre-commit hook or a pipeline without parsing the text.
    """
    if len(argv) != 2 or argv[1] in ("-h", "--help"):
        print(f"usage: {Path(argv[0]).name} <{PORTFOLIO_FILENAME}>", file=sys.stderr)
        print("  exit 0 clean, 1 warnings only, 2 one or more errors", file=sys.stderr)
        return 64
    try:
        loaded = read(Path(argv[1]))
    except PortfolioError as refusal:
        print(str(refusal), file=sys.stderr)
        return 65
    findings = validate(loaded)
    print(format_report(loaded, findings))
    return report(findings).exit_code


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
