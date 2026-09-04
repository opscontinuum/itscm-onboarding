"""The starter answer store shipped as an example, checked against the pinned denominator.

``plugin/answers.example.toml`` is the TOML successor to
``templates/answers.example.yaml``. It is generated from the question bank, so the two
cannot drift: this suite regenerates it and fails if the committed file differs, which makes
a stale example a failing test rather than a thing somebody notices later.

The denominator matters because ``skills/itscp-build/SKILL.md`` reports coverage against the
starter field set and pins it at 82. A plan that adds fields reports against its own counted
total, but the example is the starter set and has to be the number the skill quotes.
"""
from __future__ import annotations

import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import itscp_questions as bank
import itscp_store as store
from harness import Section, equal

EXAMPLE = Path(__file__).resolve().parent.parent / "answers.example.toml"

#: The denominator itscp-build reports against, quoted in its coverage section.
PINNED_DENOMINATOR = 82


def main() -> None:
    section = Section("5", "the starter answer store")

    section.check("the example exists", lambda: _assert_exists(EXAMPLE))
    section.check("the example is what the bank generates", _example_matches_the_bank)
    section.check("the example parses as TOML", _example_parses)
    section.check("the example round trips", _example_round_trips)
    section.check("its key count is the pinned denominator", _key_count_is_the_denominator)
    section.check("every key is a question in the bank", _every_key_is_in_the_bank)
    section.check("every field starts MISSING with a named owner", _every_field_starts_missing)
    section.check("no field carries a value", _no_field_carries_a_value)
    section.check("coverage of the example is zero", _coverage_is_zero)
    section.check("the example warns that it is sensitive", _example_warns)
    section.check("the example carries no real identifiers", _no_real_identifiers)

    section.finish()


def _assert_exists(path: Path) -> None:
    assert path.exists(), f"{path} is missing; run itscp_store.starter_document through emit"


def _example_matches_the_bank() -> None:
    equal(EXAMPLE.read_text(encoding="utf-8"), store.emit(store.starter_document()),
          "the committed example against what the bank generates now")


def _parsed() -> dict:
    return tomllib.loads(EXAMPLE.read_text(encoding="utf-8"))


def _example_parses() -> None:
    assert "facts" in _parsed(), "the example has no [facts] table"


def _example_round_trips() -> None:
    document = store.load_document(_parsed())
    equal(store.as_comparable(store.load_document(tomllib.loads(store.emit(document)))),
          store.as_comparable(document), "the example after a round trip")


def _key_count_is_the_denominator() -> None:
    equal(len(_parsed()["facts"]), PINNED_DENOMINATOR, "keys in the example")
    equal(len(bank.STARTER_KEYS), PINNED_DENOMINATOR, "keys in the starter set")


def _every_key_is_in_the_bank() -> None:
    unknown = [key for key in _parsed()["facts"] if key not in bank.BY_ID]
    assert not unknown, f"keys in the example that no question defines: {unknown}"


def _every_field_starts_missing() -> None:
    for key, table in _parsed()["facts"].items():
        equal(table["status"], "MISSING", f"status of {key}")
        assert table.get("owner") in bank.OWNER_VOCABULARY, (
            f"{key} starts MISSING with owner {table.get('owner')!r}, which is not a role")


def _no_field_carries_a_value() -> None:
    valued = [key for key, table in _parsed()["facts"].items() if "value" in table]
    assert not valued, (
        f"the starter store carries values: {valued}. Every field starts MISSING; a value "
        f"here would be a plausible default, which is the failure the toolkit prevents.")


def _coverage_is_zero() -> None:
    coverage = store.coverage(store.load_document(_parsed()))
    equal(coverage.percent, 0, "coverage of the starter store")
    equal(coverage.missing, PINNED_DENOMINATOR, "missing in the starter store")


def _example_warns() -> None:
    assert "GITIGNORED" in EXAMPLE.read_text(encoding="utf-8"), (
        "the example does not warn that a real store must not be committed")


def _no_real_identifiers() -> None:
    text = EXAMPLE.read_text(encoding="utf-8")
    for forbidden in ("ocid1.", "@", "+44", "+1 ", "http://", "https://"):
        assert forbidden not in text, (
            f"the example contains {forbidden!r}, which looks like a real identifier")


if __name__ == "__main__":
    main()
