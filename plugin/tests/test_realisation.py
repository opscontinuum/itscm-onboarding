"""The realisation axis: does the estate the plan describes actually exist?

Orthogonal to provenance, and the two must not be folded together. Provenance answers who
said it. Realisation answers whether it is there. A fact can be perfectly attributed by a
named person on a named date and describe two Exadata racks nobody ever provisioned, and
until something reconciles the plan against the estate, the document says they are there in
the present tense and the stated recovery target is not a target that might slip. It is
unachievable, and no reader can tell.

The last two checks are the separability ones. This axis is additive beyond reproducing the
reference plan, which carries no such marking, so it must be impossible for realisation data
to change a byte of the answer store's output.
"""
from __future__ import annotations

import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import itscp_realisation as realisation
import itscp_store as store
from harness import Section, equal

RACKS = "exadata-rack:standby-region:pair"
OBSERVED_AT = "2026-09-03"
DISCOVERY = "oci-discovery"
CMDB = "servicenow-cmdb"


def _requirement(**overrides) -> realisation.PlanRequirement:
    fields = {
        "identity": RACKS,
        "key": "infra.replication",
        "required": True,
        "expected": {"count": "2", "shape": "quarter rack"},
        "owner": "infrastructure owner",
        "invalidates": "the tier 0 recovery time objective",
    }
    fields.update(overrides)
    return realisation.PlanRequirement(**fields)


def _observation(**overrides) -> realisation.SourceObservation:
    fields = {
        "source": DISCOVERY,
        "identity": RACKS,
        "present": True,
        "observed": {"count": "2", "shape": "quarter rack"},
        "observed_at": OBSERVED_AT,
        "operation": "ListExadataInfrastructures",
    }
    fields.update(overrides)
    return realisation.SourceObservation(**fields)


def main() -> None:
    section = Section("4", "realisation state")

    section.check("the default is unknown, not conformant", _default_is_unknown)
    section.check("required and present and matching is conformant", _conformant)
    section.check("required and absent is a gap", _gap)
    section.check("not required and present is shadow", _shadow)
    section.check("required and present but differing is drift", _drift)
    section.check("drift names the attributes that differ", _drift_names_the_attributes)
    section.check("no observation leaves the state unknown", _no_observation_is_unknown)
    section.check("an unknown state carries a recoverable reason", _unknown_reason_is_recoverable)
    section.check("a gap carries its owner and its consequence", _gap_carries_the_consequence)

    section.rejects(
        "a requirement with no consequence is refused",
        lambda: _requirement(invalidates=""),
        "requires the consequence")

    section.rejects(
        "a requirement with no owner is refused",
        lambda: _requirement(owner=""),
        "requires an owner")

    section.rejects(
        "a requirement owned outside the roster is refused",
        lambda: _requirement(owner="the platform team"),
        "must be a role from the roster")

    section.rejects(
        "a requirement against an unknown key is refused",
        lambda: _requirement(key="infra.invented"),
        "is not a key in the question bank")

    section.rejects(
        "an observation from an unknown source is refused",
        lambda: _observation(source="a spreadsheet"),
        "source must be one of")

    section.rejects(
        "a state cannot be asserted by hand",
        lambda: realisation.Reconciliation(
            identity=RACKS, source=DISCOVERY, state="conformant", reason="",
            differing=(), owner="infrastructure owner", consequence=""),
        "reason")

    section.check("two sources reconcile independently", _two_sources_reconcile_independently)
    section.check("a second source needs no new code", _a_second_source_reuses_the_shape)
    section.check("every state has a label a renderer can print", _every_state_has_a_label)
    section.check("a ledger round trips through tomllib", _ledger_round_trips)

    section.check("realisation cannot change the answer store's bytes", _store_output_is_untouched)
    section.check("the ledger is a separate file", _ledger_is_a_separate_file)

    section.finish()


def _default_is_unknown() -> None:
    equal(realisation.REALISATION_STATES[0], "unknown", "the first state")
    equal(realisation.reconcile(None, None).state, "unknown", "state with neither input")


def _conformant() -> None:
    equal(realisation.reconcile(_requirement(), _observation()).state, "conformant", "state")


def _gap() -> None:
    equal(realisation.reconcile(_requirement(), _observation(present=False)).state,
          "gap", "state")


def _shadow() -> None:
    equal(realisation.reconcile(None, _observation()).state, "shadow", "state")
    equal(realisation.reconcile(_requirement(required=False), _observation()).state,
          "shadow", "state")


def _drift() -> None:
    differing = _observation(observed={"count": "1", "shape": "quarter rack"})
    equal(realisation.reconcile(_requirement(), differing).state, "drift", "state")


def _drift_names_the_attributes() -> None:
    differing = _observation(observed={"count": "1", "shape": "eighth rack"})
    result = realisation.reconcile(_requirement(), differing)
    equal(sorted(result.differing), ["count", "shape"], "differing attributes")
    assert "count" in result.reason, f"the reason does not name what differs: {result.reason}"


def _no_observation_is_unknown() -> None:
    equal(realisation.reconcile(_requirement(), None).state, "unknown", "state")


def _unknown_reason_is_recoverable() -> None:
    result = realisation.reconcile(_requirement(), None)
    assert "no source has looked" in result.reason, (
        f"unknown with no recoverable reason: {result.reason!r}")


def _gap_carries_the_consequence() -> None:
    result = realisation.reconcile(_requirement(), _observation(present=False))
    equal(result.owner, "infrastructure owner", "owner")
    equal(result.consequence, "the tier 0 recovery time objective", "consequence")
    assert result.consequence in result.label, (
        f"the label does not carry the consequence: {result.label!r}")


def _two_sources_reconcile_independently() -> None:
    results = realisation.reconcile_all(
        (_requirement(),),
        (_observation(), _observation(source=CMDB, present=False, operation="")))
    equal({result.source: result.state for result in results},
          {DISCOVERY: "conformant", CMDB: "gap"}, "state per source")


def _a_second_source_reuses_the_shape() -> None:
    equal(sorted(realisation.SOURCES), sorted((DISCOVERY, CMDB)), "known sources")
    for source in realisation.SOURCES:
        equal(realisation.reconcile(_requirement(), _observation(source=source, present=False)).state,
              "gap", f"gap detection for {source}")


def _every_state_has_a_label() -> None:
    for state in realisation.REALISATION_STATES:
        assert realisation.state_description(state), f"{state} has no description"


def _ledger_round_trips() -> None:
    ledger = realisation.new_ledger("Payments")
    ledger = realisation.record_all(ledger, realisation.reconcile_all(
        (_requirement(), _requirement(identity="drg:standby", key="infra.standby_region",
                                      expected={}, invalidates="the failover path")),
        (_observation(), _observation(identity="drg:standby", present=False, observed={}))))
    text = realisation.emit(ledger)
    reread = realisation.load_ledger(tomllib.loads(text))
    equal(realisation.as_comparable(reread), realisation.as_comparable(ledger),
          f"ledger after a round trip\n--- emitted ---\n{text}")


def _store_output_is_untouched() -> None:
    document = store.put(store.new_document("Payments"), store.Record(
        "infra.replication", "ANSWERED",
        value=[{"tier": "0", "mechanism": "Data Guard", "sync": "true", "measured_lag": "0s",
                "failover_behaviour": "automatic", "rebaseline_on_reversal": "false",
                "one_way": "false"}],
        provenance="oci-discovery:ListVolumeGroupReplicas", confidence="high"))
    before = store.emit(document)
    realisation.record_all(realisation.new_ledger("Payments"),
                           realisation.reconcile_all((_requirement(),), (_observation(),)))
    equal(store.emit(document), before, "the store's bytes after a reconciliation ran")
    assert "realisation" not in before, "the answer store emitted a realisation field"


def _ledger_is_a_separate_file() -> None:
    assert realisation.LEDGER_FILENAME != "answers.toml", (
        "the ledger shares the answer store's filename")


if __name__ == "__main__":
    main()
