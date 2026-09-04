"""Realisation: whether the estate the plan describes is the estate that exists.

Orthogonal to provenance, and never folded into it. Provenance answers who said it.
Realisation answers whether it is there. The two are independent, and the dangerous
combination is a fact that is perfectly attributed and describes something absent.

The case that motivates the module: a design calls for two additional racks in the standby
region. Nobody provisions them. The architecture document goes on describing them in the
present tense, correctly attributed to the person who designed them, and the tier 0 recovery
target stops being a target that might slip and becomes one that cannot be met. No reader of
the document can tell.

Four states, derived from one plan requirement and one source observation:

=============  ===============  ============  ==================================
Plan requires  Source finds     State         Meaning
=============  ===============  ============  ==================================
yes            present          conformant    As designed
yes            absent           gap           The stated recovery target is unachievable
no             present          shadow        Undocumented and unowned
yes            differing        drift         The quiet killer
=============  ===============  ============  ==================================

The default is ``unknown`` and never ``conformant``. A component nobody has checked must not
render as verified; that is the same discipline as every answer-store field starting MISSING.

The state is always derived, never asserted. :class:`Reconciliation` cannot be constructed
without a reason, so there is no way to write down "this is conformant" without saying what
made it so.

The reconciliation is modelled once and generally, over a named source. Oracle Cloud
discovery and a ServiceNow CMDB have the same three-way shape (in the source and not in the
plan, in the plan and not the source, in both but differing), so a second source is a member
of :data:`SOURCES` and an implementation of the observation, not a second copy of this logic.

**Separability.** This axis is additive beyond reproducing the reference plan, which carries
no realisation marking. Nothing here is imported by :mod:`itscp_store`, the ledger is its own
file, and ``test_realisation`` proves the answer store's bytes are unchanged by a
reconciliation running. Exact reproduction of the reference plan cannot break because of
anything in this module.
"""
from __future__ import annotations

import sys

if sys.version_info < (3, 11):
    raise RuntimeError(
        "itscp-author needs Python 3.11 or newer (this is "
        f"{sys.version_info.major}.{sys.version_info.minor}). The ledger reads TOML through "
        "the standard library's tomllib, added in 3.11. There is no pip dependency to "
        "install; run the plugin under a newer interpreter."
    )

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import itscp_questions as bank
from itscp_store import StoreError, ValidationError, toml_value

SCHEMA_VERSION = 1

#: The ledger's filename, deliberately not the answer store's. Realisation is a different
#: question about the same estate and belongs in a different file, so a plan that does not
#: use it has no trace of it.
LEDGER_FILENAME = "realisation.toml"

#: ``unknown`` is first because it is the default, and the ordering is the one a reader wants:
#: not checked, checked and fine, then the three ways it can be wrong.
REALISATION_STATES: tuple[str, ...] = ("unknown", "conformant", "gap", "shadow", "drift")

_STATE_DESCRIPTIONS: dict[str, str] = {
    "unknown": "Not checked. No source has looked, or the plan states no requirement.",
    "conformant": "The plan requires it and the source found it, matching.",
    "gap": "The plan requires it and the source did not find it. A stated recovery target "
           "depends on something that is not there.",
    "shadow": "The source found it and the plan does not require it. Undocumented, "
              "unowned, and recovered by nobody.",
    "drift": "The plan requires it and the source found something different. The failure "
             "that is hardest to see, because the component is present.",
}

#: Read-only sources that can observe an estate. Adding one is adding a member here and a
#: collector that produces :class:`SourceObservation`; the reconciliation below is unchanged.
SOURCES: tuple[str, ...] = ("oci-discovery", "servicenow-cmdb")


def state_description(state: str) -> str:
    """What one state means, in a sentence. For a renderer's legend and for error messages."""
    return _STATE_DESCRIPTIONS[state]


@dataclass(frozen=True)
class PlanRequirement:
    """What the plan says must exist, and what fails if it does not.

    ``identity`` is a source-neutral name for the thing, so two sources can be asked about
    the same component without either one's identifier scheme leaking into the model.

    ``invalidates`` is mandatory when ``required``, which is what makes a gap a finding
    rather than a note. "Two racks are missing" is documentation. "Two racks are missing, so
    the tier 0 recovery time objective cannot be met" is something somebody has to act on,
    and the owner is named beside it.
    """

    identity: str
    key: str
    required: bool
    owner: str
    invalidates: str
    expected: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if bank.question(self.key) is None:
            raise ValidationError(
                f"{self.key!r} is not a key in the question bank, so this requirement rests "
                f"on a field nobody defined.")
        if not self.required:
            return
        if not self.invalidates:
            raise ValidationError(
                f"{self.identity}: a required component requires the consequence of its "
                f"absence. A gap with no named consequence is a documentation note; one that "
                f"says which recovery target it invalidates is a finding.")
        if not self.owner:
            raise ValidationError(
                f"{self.identity}: a required component requires an owner, the role who can "
                f"close the gap.")
        if self.owner not in bank.OWNER_VOCABULARY:
            raise ValidationError(
                f"{self.identity}: owner must be a role from the roster; got {self.owner!r}")


@dataclass(frozen=True)
class SourceObservation:
    """What one read-only source reports about one identity, and when it looked.

    ``observed_at`` matters as much as ``observed``: a reconciliation against a walk from
    three months ago is a reconciliation against a memory of the estate.
    """

    source: str
    identity: str
    present: bool
    observed_at: str
    operation: str = ""
    observed: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.source not in SOURCES:
            raise ValidationError(
                f"{self.identity}: source must be one of {', '.join(SOURCES)}; "
                f"got {self.source!r}")


@dataclass(frozen=True)
class Reconciliation:
    """One derived state, for one identity, according to one source.

    Cannot be constructed without a reason, so there is no way to record a state without
    recording what produced it. That is what "derived, never asserted" means in practice.
    """

    identity: str
    source: str
    state: str
    reason: str
    owner: str
    consequence: str
    differing: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.state not in REALISATION_STATES:
            raise ValidationError(
                f"{self.identity}: state must be one of {', '.join(REALISATION_STATES)}; "
                f"got {self.state!r}")
        if not self.reason:
            raise ValidationError(
                f"{self.identity}: a realisation state carries the reason it was derived. "
                f"A state with no reason is an assertion, and this axis has none.")

    @property
    def label(self) -> str:
        """The literal text a renderer prints beside the shape.

        Text, not colour. Colour alone fails for colour-blind readers and in greyscale
        print, so the state is always spelled out and the consequence travels with a gap.
        """
        if self.state == "gap":
            return f"gap: {self.consequence} is unachievable"
        if self.state == "drift":
            return f"drift: {', '.join(self.differing)} differs"
        return self.state


def reconcile(requirement: PlanRequirement | None,
              observation: SourceObservation | None) -> Reconciliation:
    """Derive one state from one requirement and one observation.

    Either may be absent, and absence of either is ``unknown`` with a reason that says which
    half was missing, so an unknown can always be chased to the thing that would resolve it.
    """
    if requirement is None and observation is None:
        return _unknown("", "", "the plan states no requirement and no source has looked")
    if requirement is None:
        return _reconcile_without_a_requirement(observation)
    if observation is None:
        return _unknown(requirement.identity, "",
                        f"the plan requires this and no source has looked for it. Owner: "
                        f"{requirement.owner}", requirement)
    return _reconcile_both(requirement, observation)


def _reconcile_without_a_requirement(observation: SourceObservation) -> Reconciliation:
    if not observation.present:
        return _unknown(observation.identity, observation.source,
                        "the plan states no requirement and the source did not find it")
    return Reconciliation(
        identity=observation.identity, source=observation.source, state="shadow",
        reason=f"{observation.source} found this on {observation.observed_at} and the plan "
               f"states no requirement for it",
        owner="", consequence="")


def _reconcile_both(requirement: PlanRequirement,
                    observation: SourceObservation) -> Reconciliation:
    if not requirement.required:
        return _reconcile_without_a_requirement(observation)
    if not observation.present:
        return Reconciliation(
            identity=requirement.identity, source=observation.source, state="gap",
            reason=f"the plan requires this and {observation.source} did not find it on "
                   f"{observation.observed_at}",
            owner=requirement.owner, consequence=requirement.invalidates)
    differing = _differing_attributes(requirement.expected, observation.observed)
    if differing:
        return Reconciliation(
            identity=requirement.identity, source=observation.source, state="drift",
            reason=f"{observation.source} found this on {observation.observed_at} with "
                   f"{', '.join(differing)} differing from what the plan states",
            owner=requirement.owner, consequence=requirement.invalidates,
            differing=differing)
    return Reconciliation(
        identity=requirement.identity, source=observation.source, state="conformant",
        reason=f"{observation.source} found this on {observation.observed_at} matching what "
               f"the plan states",
        owner=requirement.owner, consequence="")


def _differing_attributes(expected: dict[str, str],
                          observed: dict[str, str]) -> tuple[str, ...]:
    """Attributes the plan states that the source reports differently. Sorted, so stable."""
    return tuple(sorted(name for name, value in expected.items()
                        if observed.get(name) != value))


def _unknown(identity: str, source: str, reason: str,
             requirement: PlanRequirement | None = None) -> Reconciliation:
    return Reconciliation(
        identity=identity, source=source, state="unknown", reason=reason,
        owner=requirement.owner if requirement else "",
        consequence=requirement.invalidates if requirement else "")


def reconcile_all(requirements, observations) -> tuple[Reconciliation, ...]:
    """Reconcile every identity every source has an opinion about, one result per pair.

    One result per source rather than one merged verdict: two sources disagreeing about the
    same component is itself the finding, and merging them would hide it.
    """
    by_identity = {requirement.identity: requirement for requirement in requirements}
    seen = set()
    results = []
    for observation in observations:
        seen.add(observation.identity)
        results.append(reconcile(by_identity.get(observation.identity), observation))
    for identity, requirement in by_identity.items():
        if identity not in seen:
            results.append(reconcile(requirement, None))
    return tuple(results)


# --------------------------------------------------------------------------- the ledger

def new_ledger(system_name: str) -> dict:
    """An empty realisation ledger for one system."""
    return {
        "meta": {"schema_version": SCHEMA_VERSION, "system_name": system_name},
        "reconciliations": (),
    }


def record_all(ledger: dict, results) -> dict:
    """A copy of ``ledger`` with these reconciliations appended."""
    return {**ledger,
            "reconciliations": tuple(ledger["reconciliations"]) + tuple(results)}


def gaps(ledger: dict) -> list[Reconciliation]:
    """Every gap, which is the list somebody has to act on before the plan can be signed."""
    return [result for result in ledger["reconciliations"] if result.state == "gap"]


def emit(ledger: dict) -> str:
    """The whole ledger as TOML, with the state legend regenerated as comments."""
    lines = ["\n".join(f"# {line}".rstrip() for line in _ledger_notice()),
             "", "[meta]"]
    lines.extend(f"{name} = {toml_value(value)}" for name, value in ledger["meta"].items())
    for result in ledger["reconciliations"]:
        lines.append("")
        lines.append("[[reconciliations]]")
        lines.extend(f"{name} = {toml_value(value)}"
                     for name, value in vars(result).items()
                     if value != "" and value != ())
    return "\n".join(lines) + "\n"


def _ledger_notice() -> tuple[str, ...]:
    legend = tuple(f"  {state}: {state_description(state)}" for state in REALISATION_STATES)
    return (
        "Realisation: whether the estate the plan describes is the estate that exists.",
        "",
        "Derived, never asserted. Every state below carries the reason it was derived and",
        "the observation date it rests on. Generated by itscp_realisation.emit; editing a",
        "state here has no effect, because the next reconciliation recomputes it.",
        "",
        "States:",
    ) + legend


def load_ledger(parsed: dict) -> dict:
    """Turn a parsed TOML mapping back into reconciliations. The inverse of :func:`emit`."""
    return {
        "meta": dict(parsed.get("meta", {})),
        "reconciliations": tuple(
            Reconciliation(
                identity=table.get("identity", ""), source=table.get("source", ""),
                state=table.get("state", "unknown"), reason=table.get("reason", ""),
                owner=table.get("owner", ""), consequence=table.get("consequence", ""),
                differing=tuple(table.get("differing", ())),
            ) for table in parsed.get("reconciliations", ())),
    }


def as_comparable(ledger: dict) -> dict:
    """``ledger`` reduced to plain data, for comparing a round trip to its original."""
    return {
        "meta": dict(ledger["meta"]),
        "reconciliations": [
            {name: value for name, value in vars(result).items() if value not in ("", ())}
            for result in ledger["reconciliations"]],
    }


class RealisationLedger:
    """The ledger as a file: read it, write it atomically, never silently reset it."""

    def __init__(self, path: Path):
        self.path = path

    def read(self) -> dict:
        """The stored ledger, or an empty one. A corrupt file is reported, never reset."""
        if not self.path.exists():
            return new_ledger("")
        try:
            parsed = tomllib.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as failure:
            raise StoreError(
                f"{self.path} is not readable as TOML ({failure}). Fix or move it; nothing "
                f"has been overwritten."
            ) from failure
        return load_ledger(parsed)

    def write(self, ledger: dict) -> None:
        """Replace the file atomically."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_name(self.path.name + ".tmp")
        temporary.write_text(emit(ledger), encoding="utf-8")
        os.replace(temporary, self.path)
