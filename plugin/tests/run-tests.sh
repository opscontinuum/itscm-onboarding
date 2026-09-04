#!/usr/bin/env bash
# run-tests.sh - the itscp-author data layer, proved.
#
# Nine sections, each a Python module printing its own ok/FAIL lines. Any one
# failing fails the suite:
#   1. The question bank is internally consistent (unit).
#   2. Every store rule refuses bad input, and the emitter round-trips
#      through tomllib (unit + property).
#   3. The session transcript is append only and records read-backs.
#   4. Realization state is derived, defaults to unknown, and cannot change
#      the answer store's bytes.
#   5. The shipped starter store is what the bank generates, and its key
#      count is the denominator itscp-build reports against.
#   6. Every byte the renderer writes is structural text, a recorded answer,
#      markup or an annotation drawn from a closed vocabulary.
#   7. Both reference diagrams are generated from their data, and an
#      unsourced figure is marked in three channels that survive greyscale.
#   8. Acceptance, end to end: a scripted answer set in, a plan repository
#      out, graded on structure, provenance and quoted-standard fidelity.
#   9. The two committed examples under examples/ are still what the build
#      step writes from their own answer stores.
#  10. The portfolio holds: recovery time inversions, dependency cycles and
#      wave ordering are caught above the level of any single plan.
#
# Check 2's round trip is the one that matters over time. The emitter is hand
# written and tomllib is the standard library's parser; without a property
# test comparing what went in to what comes back, a TOML quoting bug shows up
# as a silently corrupted answer in somebody's continuity plan rather than as
# a failing build.
#
# Standard library only, no pip, no test framework. Python 3.11 or newer,
# because tomllib landed there.

set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

PYTHON="${PYTHON:-python3}"
# No .pyc files: the repo has no ignore rule for them and a test run should not
# leave the working tree dirty for whoever looks at git status next.
export PYTHONDONTWRITEBYTECODE=1
FAILS=0

if ! "$PYTHON" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'; then
    printf 'FAIL - %s is older than 3.11; tomllib is not available\n' "$PYTHON"
    exit 1
fi

for module in test_questions test_store test_session test_realization test_example \
              test_render test_diagrams test_acceptance test_examples test_portfolio; do
    if ! "$PYTHON" "${module}.py"; then
        FAILS=$((FAILS + 1))
    fi
done

printf '\n'
if [ "$FAILS" -eq 0 ]; then
    printf 'PASS - itscp-author holds, and the scripted plan is acceptable\n'; exit 0
else
    printf 'FAIL - %s section(s) failed\n' "$FAILS"; exit 1
fi
