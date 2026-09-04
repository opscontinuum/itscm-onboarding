"""A pass/fail reporter in the shape of ``scripts/discover/test-readonly.sh``.

Numbered sections, an ``ok`` or ``FAIL`` line per check, a ``PASS`` or ``FAIL`` summary and
a non-zero exit when anything failed. Standard library only, like everything else here.

Each test module builds one :class:`Section`, registers checks against it and calls
:meth:`Section.finish`, which is what sets the exit code.
"""
from __future__ import annotations

import sys
import traceback
from collections.abc import Callable

_INDENT = "  "
_DETAIL_INDENT = "          "


class Section:
    """One numbered group of checks, printed as it runs."""

    def __init__(self, number: str, title: str):
        self.number = number
        self.title = title
        self.failures = 0
        print(f"\n{number}. {title}")

    def check(self, name: str, assertion: Callable[[], None]) -> None:
        """Run one check. ``assertion`` raises to fail and returns to pass.

        An unexpected exception fails the check and prints its traceback rather than
        aborting the run, so one broken check does not hide the state of the others.
        """
        try:
            assertion()
        except AssertionError as failure:
            self._fail(name, str(failure))
        except Exception:  # noqa: BLE001 - a crashed check is a failed check, not a stop
            self._fail(name, traceback.format_exc().rstrip())
        else:
            print(f"{_INDENT}ok    {name}")

    def rejects(self, name: str, action: Callable[[], object], expected: str) -> None:
        """Check that ``action`` raises with ``expected`` in its message.

        The enforcement rules are all of this shape: bad input in, refusal out. Asserting on
        the message as well as the raise is what stops a rule passing because some unrelated
        error happened to fire.
        """

        def assertion() -> None:
            try:
                action()
            except Exception as refusal:  # noqa: BLE001 - any refusal type is acceptable
                message = str(refusal)
                assert expected in message, (
                    f"refused, but for the wrong reason.\n"
                    f"expected to find: {expected!r}\n"
                    f"actual message:   {message!r}"
                )
                return
            raise AssertionError(f"accepted bad input; expected a refusal mentioning {expected!r}")

        self.check(name, assertion)

    def note(self, text: str) -> None:
        """Print a measured number that is reported rather than asserted.

        A score recorded for comparison is not a check: nothing about the reference plan can
        fail this suite, and a check that could never fail would be a lie about what is
        being enforced. Notes are indented under the checks so a reader sees them in place.
        """
        print(f"{_INDENT}note  {text}")

    def _fail(self, name: str, detail: str) -> None:
        self.failures += 1
        print(f"{_INDENT}FAIL  {name}")
        for line in detail.splitlines():
            print(f"{_DETAIL_INDENT}{line}")

    def finish(self) -> None:
        """Print the summary and exit non-zero if any check in this section failed."""
        print()
        if self.failures:
            print(f"FAIL - {self.failures} check(s) failed in section {self.number}")
            sys.exit(1)
        print(f"PASS - section {self.number}: {self.title}")
        sys.exit(0)


def equal(actual: object, expected: object, subject: str) -> None:
    """Assert equality with a message that names the subject and shows both sides."""
    assert actual == expected, f"{subject}: expected {expected!r}, got {actual!r}"
