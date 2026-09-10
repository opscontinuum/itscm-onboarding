"""The browser worksheet: still what the bank generates, and still self-contained.

``docs/manual/worksheet.html`` is the file a facilitator opens in a meeting room, so the two
properties that matter are that it holds the current questions and that it needs nothing from
the network. Both are checked here from Python, with no dependency beyond the standard
library, like the rest of this suite.

Behaviour is a different problem. The page is JavaScript, and asserting that typing an answer
reaches storage means running it. ``worksheet-behaviour.js`` does exactly that against a
minimal DOM, and this section runs it **when a JavaScript runtime happens to be installed**
and says so plainly when one is not. A skipped check is reported as skipped rather than
passed: a suite that quietly counts an unrun check as a pass is worse than one that admits it
could not run.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import itscp_manual as manual
import itscp_questions as bank
import itscp_worksheet as worksheet
from harness import Section, equal

SHEET = manual.OUTPUT_DIR / "worksheet.html"
BEHAVIOUR = Path(__file__).resolve().parent / "worksheet-behaviour.js"

#: Runtimes that can execute the behaviour harness, in the order they are tried. Any of them
#: is enough; none of them is required.
RUNTIMES: tuple[str, ...] = ("bun", "node", "deno")

#: Anything that would make the page reach off the machine it is opened on. A worksheet that
#: needs the network is a worksheet that fails in the room it was written for.
_REACHES_OUT = re.compile(
    r"""(?:src|href)\s*=\s*["'](?!\#)[^"']+["']"""
    r"""|\bfetch\s*\(|XMLHttpRequest|WebSocket|@import|url\(\s*['"]?https?:""")

#: The embedded bank, which is the page's whole reason for being generated rather than written.
_BANK = re.compile(r'<script id="bank" type="application/json">\n(?P<data>.*?)\n</script>', re.S)


def main() -> None:
    section = Section("12", "the browser worksheet")

    section.check("the worksheet exists", _exists)
    section.check("it is what the bank generates now", _matches_the_bank)
    section.check("it asks every question the manual asks", _asks_everything)
    section.check("it reaches out to nothing", _self_contained)
    section.check("every phase of the manual is in it", _phases_match)
    section.check("a figure carries its follow-up question", _mechanisms_present)
    _behaviour(section)

    section.finish()


def _exists() -> None:
    assert SHEET.exists(), f"{SHEET} is missing; run python3 plugin/itscp_manual.py"


def _matches_the_bank() -> None:
    generated = worksheet.render(manual.PHASES)
    committed = SHEET.read_text(encoding="utf-8")
    if committed == generated:
        return
    raise AssertionError(
        "docs/manual/worksheet.html is not what the bank generates now. Regenerate with "
        "python3 plugin/itscp_manual.py.")


def _embedded() -> dict:
    match = _BANK.search(SHEET.read_text(encoding="utf-8"))
    assert match is not None, "the page carries no embedded question bank"
    return json.loads(match.group("data").replace("<\\/", "</"))


def _asks_everything() -> None:
    asked = {question["id"] for phase in _embedded()["phases"]
             for question in phase["questions"]}
    equal(sorted(asked), sorted(bank.STARTER_KEYS),
          "the questions the worksheet carries against the bank")


def _self_contained() -> None:
    found = sorted({match.group(0) for match in _REACHES_OUT.finditer(
        SHEET.read_text(encoding="utf-8"))})
    assert not found, (
        "the worksheet would reach off the machine: " + ", ".join(found)
        + ". It is opened from a file in a room with no wifi; everything it needs is inside "
          "it or it does not work.")


def _phases_match() -> None:
    embedded = [phase["number"] for phase in _embedded()["phases"]]
    equal(embedded, [phase.number for phase in manual.PHASES],
          "the phases the worksheet carries")


def _mechanisms_present() -> None:
    """Every figure that owes an explanation asks for one on the page too."""
    owed = {question.id for question in bank.QUESTIONS if question.mechanism_required}
    carried = {question["id"] for phase in _embedded()["phases"]
               for question in phase["questions"] if question.get("mechanism")}
    equal(sorted(carried), sorted(owed),
          "the questions the worksheet asks a mechanism for")


def _runtime() -> str | None:
    for name in RUNTIMES:
        found = shutil.which(name)
        if found:
            return found
    return None


def _behaviour(section: Section) -> None:
    """Run the page and assert what it does, if anything here can run JavaScript."""
    runtime = _runtime()
    if runtime is None:
        section.note("behaviour not exercised: none of "
                     + ", ".join(RUNTIMES) + " is installed. The page is checked as text "
                     "only, which cannot tell you whether typing an answer records it.")
        return
    result = subprocess.run([runtime, str(BEHAVIOUR), str(SHEET)],
                            capture_output=True, text=True, timeout=120)
    for line in result.stdout.splitlines():
        stripped = line.strip()
        if stripped.startswith("ok    "):
            section.check(stripped[6:], lambda: None)
        elif stripped.startswith("FAIL  "):
            detail = result.stdout.split(stripped, 1)[1].splitlines()
            message = detail[1].strip() if len(detail) > 1 else ""
            section.check(stripped[6:], _fails(message))
    if result.returncode not in (0, 1):
        section.check("the behaviour harness ran",
                      _fails(result.stderr.strip()[:400] or "no output"))


def _fails(message: str):
    def assertion() -> None:
        raise AssertionError(message)
    return assertion


if __name__ == "__main__":
    main()
