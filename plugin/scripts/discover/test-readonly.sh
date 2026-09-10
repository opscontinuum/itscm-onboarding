#!/usr/bin/env bash
# test-readonly.sh - run every environment's own read-only proof.
#
# Discovery is organized one directory per environment, and each one carries the
# proof that its own walk cannot write: see README.md for the contract. This
# script finds those proofs rather than listing them, so an environment added
# tomorrow is covered by the suite the moment its directory exists, and an
# environment whose proof is missing fails here instead of being skipped
# silently.
#
# Run it before pointing any discovery script at a live environment.

set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

FAILS=0
FOUND=0

for environment in */; do
    name="${environment%/}"
    [ "$name" = "discovery-output" ] && continue
    [ -d "$name" ] || continue
    FOUND=$((FOUND + 1))

    if [ ! -f "$name/test-readonly.sh" ]; then
        printf '\nFAIL - %s has no test-readonly.sh. Every environment owes one; see README.md\n' "$name"
        FAILS=$((FAILS + 1))
        continue
    fi

    printf '\n=== %s ===\n' "$name"
    if ! bash "$name/test-readonly.sh"; then
        FAILS=$((FAILS + 1))
    fi
done

printf '\n'
if [ "$FOUND" -eq 0 ]; then
    printf 'FAIL - no environment directories found under scripts/discover\n'
    exit 1
fi
if [ "$FAILS" -eq 0 ]; then
    printf 'PASS - %s environment(s) proved read-only\n' "$FOUND"
    exit 0
fi
printf 'FAIL - %s of %s environment(s) failed\n' "$FAILS" "$FOUND"
exit 1
