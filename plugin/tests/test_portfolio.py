"""The portfolio: many systems, the dependencies between them, and the order they recover in.

A per-system plan is coherent on its own and can still be impossible in company. The order
management application declares a two hour recovery time objective; the identity database it
cannot authenticate against declares eight. Both documents are internally consistent. Read
together they are a lie, and nothing in a single-system toolkit can see it, because the two
were written by different people in different weeks.

That is what this module checks: the findings that only exist above the level of one plan.
The sharpest is the distinction between a runtime dependency and a recovery dependency. Every
interview asks what a system needs in order to run. Almost none ask what it needs in order to
be recovered, which is how an organisation discovers during an invocation that its runbooks
are in the source control server that is inside the outage.

Standard library only, like everything else here.
"""
from __future__ import annotations

import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import itscp_portfolio as portfolio
from harness import Section, equal


def _system(slug: str, **overrides) -> portfolio.System:
    fields = {
        "slug": slug,
        "name": slug.replace("-", " ").title(),
        "system_class": "dependent-app",
        "business_owner": "business owner",
        "application_owner": "application owner",
        "tier": 1,
        "rto": "4h",
        "rpo": "1h",
        "mtd": "8h",
        "wave": 2,
        "plan_repo": f"https://example.invalid/{slug}",
        "depends_on": (),
    }
    fields.update(overrides)
    return portfolio.System(**fields)


def _depends(on: str, kind: str = "runtime", criticality: str = "hard") -> portfolio.Dependency:
    return portfolio.Dependency(on=on, kind=kind, criticality=criticality)


def _portfolio(*systems: portfolio.System, **overrides) -> portfolio.Portfolio:
    fields = {
        "organisation": "Example Corp",
        "waves": portfolio.DEFAULT_WAVES,
        "systems": tuple(systems),
        "tier_budget": {},
    }
    fields.update(overrides)
    return portfolio.Portfolio(**fields)


def _codes(findings) -> tuple[str, ...]:
    return tuple(sorted({finding.code for finding in findings}))


def main() -> None:
    section = Section("10", "the portfolio: cross-system coherence")

    section.check("a durationless portfolio of one system is clean", _one_clean_system)
    section.check("a dependency on an unknown system is refused", _unknown_dependency)
    section.check("a system may not depend on itself", _self_dependency)

    section.check("a shorter RTO than a hard dependency is an inversion", _rto_inversion)
    section.check("an equal RTO to a hard dependency is not an inversion", _rto_equal_is_clean)
    section.check("a soft dependency does not raise an inversion", _soft_dependency_no_inversion)
    section.check("the inversion names both systems and both figures", _inversion_message)

    section.check("a recovery dependency cycle is an error", _recovery_cycle)
    section.check("the runbook-in-source-control trap is caught", _runbook_circularity)
    section.check("a runtime cycle is a warning, not an error", _runtime_cycle_warns)

    section.check("a hard dependency in a later wave is an error", _wave_inversion)
    section.check("a hard dependency in the same wave warns", _same_wave_warns)
    section.check("more systems in a wave than it can recover warns", _wave_overload)

    section.check("a system with no owner is an error", _orphan_system)
    section.check("a system with no plan repository warns", _no_plan_repo)
    section.check("more tier 0 systems than the budget allows warns", _tier_budget)
    section.check("a heavily depended-on system not marked shared warns", _undeclared_shared)

    section.check("errors and warnings are separated by severity", _severity_split)
    section.check("a realistic five-class portfolio round-trips through TOML", _round_trip)
    section.check("the shipped example portfolio parses and validates", _example_portfolio)

    section.finish()


# ------------------------------------------------------------------ the graph is well formed

def _one_clean_system() -> None:
    findings = portfolio.validate(_portfolio(_system("payroll")))
    equal(_codes(findings), (), "findings for a single well-formed system")


def _unknown_dependency() -> None:
    result = portfolio.validate(_portfolio(
        _system("payroll", depends_on=(_depends("ghost-system"),))))
    assert "unknown-dependency" in _codes(result), _codes(result)


def _self_dependency() -> None:
    result = portfolio.validate(_portfolio(
        _system("payroll", depends_on=(_depends("payroll"),))))
    assert "self-dependency" in _codes(result), _codes(result)


# ---------------------------------------------------------------------------- RTO inversion

def _inverted() -> portfolio.Portfolio:
    """Order management back in two hours, on an identity database back in eight."""
    return _portfolio(
        _system("order-management", rto="2h", wave=2,
                depends_on=(_depends("id-database"),)),
        _system("id-database", system_class="core-data", rto="8h", wave=1),
    )


def _rto_inversion() -> None:
    assert "rto-inversion" in _codes(portfolio.validate(_inverted()))


def _rto_equal_is_clean() -> None:
    clean = _portfolio(
        _system("order-management", rto="8h", wave=2, depends_on=(_depends("id-database"),)),
        _system("id-database", system_class="core-data", rto="8h", wave=1),
    )
    assert "rto-inversion" not in _codes(portfolio.validate(clean))


def _soft_dependency_no_inversion() -> None:
    soft = _portfolio(
        _system("order-management", rto="2h", wave=2,
                depends_on=(_depends("reporting", criticality="soft"),)),
        _system("reporting", rto="24h", wave=3),
    )
    assert "rto-inversion" not in _codes(portfolio.validate(soft))


def _inversion_message() -> None:
    finding = next(f for f in portfolio.validate(_inverted()) if f.code == "rto-inversion")
    for expected in ("order-management", "id-database", "2h", "8h"):
        assert expected in finding.detail, (
            f"the inversion message omits {expected!r}: {finding.detail!r}")


# ------------------------------------------------------------------------------ circularity

def _recovery_cycle() -> None:
    cycle = _portfolio(
        _system("alpha", depends_on=(_depends("beta", kind="recovery"),)),
        _system("beta", depends_on=(_depends("alpha", kind="recovery"),)),
    )
    assert "recovery-cycle" in _codes(portfolio.validate(cycle))


def _runbook_circularity() -> None:
    """The runbooks live in the source control server, which is recovered using the runbooks."""
    trap = _portfolio(
        _system("gitlab", system_class="supporting-infra", wave=0,
                depends_on=(_depends("gitlab-runbooks-are-in-gitlab", kind="recovery"),)),
        _system("gitlab-runbooks-are-in-gitlab", system_class="supporting-infra", wave=0,
                depends_on=(_depends("gitlab", kind="recovery"),)),
    )
    assert "recovery-cycle" in _codes(portfolio.validate(trap))


def _runtime_cycle_warns() -> None:
    cycle = _portfolio(
        _system("alpha", wave=2, depends_on=(_depends("beta", criticality="soft"),)),
        _system("beta", wave=2, depends_on=(_depends("alpha", criticality="soft"),)),
    )
    findings = portfolio.validate(cycle)
    runtime = [f for f in findings if f.code == "runtime-cycle"]
    assert runtime, _codes(findings)
    equal(runtime[0].severity, "WARNING", "the severity of a runtime cycle")


# ------------------------------------------------------------------------------------ waves

def _wave_inversion() -> None:
    later = _portfolio(
        _system("app", wave=1, rto="8h", depends_on=(_depends("platform"),)),
        _system("platform", system_class="shared-platform", wave=3, rto="8h"),
    )
    findings = portfolio.validate(later)
    assert "wave-inversion" in _codes(findings), _codes(findings)
    assert any(f.code == "wave-inversion" and f.severity == "ERROR" for f in findings)


def _same_wave_warns() -> None:
    same = _portfolio(
        _system("app", wave=2, rto="8h", depends_on=(_depends("platform"),)),
        _system("platform", system_class="shared-platform", wave=2, rto="8h"),
    )
    findings = [f for f in portfolio.validate(same) if f.code == "wave-concurrency"]
    assert findings, _codes(portfolio.validate(same))
    equal(findings[0].severity, "WARNING", "the severity of a same-wave hard dependency")


def _wave_overload() -> None:
    waves = (portfolio.Wave(id=2, name="Applications", purpose="apps", max_concurrent=2),)
    crowded = _portfolio(*(_system(f"app-{n}", wave=2) for n in range(5)), waves=waves)
    findings = [f for f in portfolio.validate(crowded) if f.code == "wave-overload"]
    assert findings, "five systems in a wave that can recover two raised nothing"
    assert "2" in findings[0].detail and "5" in findings[0].detail, findings[0].detail


# --------------------------------------------------------------------- register completeness

def _orphan_system() -> None:
    result = portfolio.validate(_portfolio(_system("payroll", business_owner="")))
    assert "orphan-system" in _codes(result), _codes(result)
    assert any(f.code == "orphan-system" and f.severity == "ERROR" for f in result)


def _no_plan_repo() -> None:
    findings = [f for f in portfolio.validate(_portfolio(_system("payroll", plan_repo="")))
                if f.code == "no-plan"]
    assert findings, "a system with no plan repository raised nothing"
    equal(findings[0].severity, "WARNING", "the severity of a missing plan repository")


def _tier_budget() -> None:
    over = _portfolio(*(_system(f"app-{n}", tier=0) for n in range(4)), tier_budget={0: 2})
    findings = [f for f in portfolio.validate(over) if f.code == "tier-budget-exceeded"]
    assert findings, "four tier 0 systems against a budget of two raised nothing"


def _undeclared_shared() -> None:
    depended_on = _portfolio(
        _system("common", system_class="dependent-app", wave=1, rto="1h"),
        *(_system(f"app-{n}", wave=2, depends_on=(_depends("common"),)) for n in range(4)),
    )
    assert "undeclared-shared-service" in _codes(portfolio.validate(depended_on))


# ------------------------------------------------------------------------------- the report

def _severity_split() -> None:
    findings = portfolio.validate(_inverted())
    report = portfolio.report(findings)
    equal(report.errors, sum(1 for f in findings if f.severity == "ERROR"), "the error count")
    assert report.exit_code == 2, "an inversion did not produce the error exit code"
    equal(portfolio.report(()).exit_code, 0, "the exit code of a clean portfolio")


def _round_trip() -> None:
    """Every class in the brief: core data, dependants, supporting tooling, API, website."""
    original = _portfolio(
        _system("id-database", system_class="core-data", wave=1, rto="1h", tier=0),
        _system("hr-portal", wave=2, rto="4h", depends_on=(_depends("id-database"),)),
        _system("gitlab", system_class="supporting-infra", wave=0, rto="30m"),
        _system("client-ingest-api", system_class="public-api", wave=2, rto="4h",
                depends_on=(_depends("id-database"), _depends("gitlab", kind="recovery"))),
        _system("www", system_class="public-web", wave=3, rto="8h"),
    )
    text = portfolio.emit(original)
    reloaded = portfolio.load(tomllib.loads(text))
    equal(portfolio.emit(reloaded), text, "the portfolio's bytes after a round trip")
    equal(len(reloaded.systems), 5, "the system count after a round trip")
    ingest = next(s for s in reloaded.systems if s.slug == "client-ingest-api")
    equal(len(ingest.depends_on), 2, "the dependency count after a round trip")
    equal({d.kind for d in ingest.depends_on}, {"runtime", "recovery"},
          "the dependency kinds after a round trip")


def _example_portfolio() -> None:
    path = Path(__file__).resolve().parent.parent / "portfolio.example.toml"
    assert path.exists(), f"the shipped example portfolio is missing: {path}"
    loaded = portfolio.load(tomllib.loads(path.read_text()))
    assert len(loaded.systems) >= 8, (
        f"the example portfolio has only {len(loaded.systems)} systems; it is meant to show "
        "an estate, not a system")
    classes = {system.system_class for system in loaded.systems}
    for expected in ("core-data", "dependent-app", "supporting-infra", "public-api",
                     "public-web"):
        assert expected in classes, f"the example portfolio has no {expected} system"
    kinds = {d.kind for system in loaded.systems for d in system.depends_on}
    assert "recovery" in kinds, (
        "the example portfolio declares no recovery dependency, so it does not demonstrate "
        "the distinction the model exists for")
    findings = portfolio.validate(loaded)
    errors = [f for f in findings if f.severity == "ERROR"]
    equal(errors, [], "errors in the shipped example portfolio")


if __name__ == "__main__":
    main()
