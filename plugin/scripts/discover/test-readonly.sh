#!/usr/bin/env bash
# test-readonly.sh — proves discovery cannot mutate.
#
# Three independent checks. Any one failing fails the suite:
#   1. The guard refuses mutating operations and allows reads (unit).
#   2. No source file calls the oci CLI outside the guard (static tripwire).
#   3. Every command a full dry run would issue is a list or a get (end to end).
#
# Check 2 is the one that matters over time. The guard is only protective if
# every call goes through it, and a future edit that adds a direct `oci` call
# would bypass it silently. This fails CI instead.

set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
FAILS=0
pass() { printf '  ok    %s\n' "$1"; }
fail() { printf '  FAIL  %s\n' "$1"; FAILS=$((FAILS + 1)); }

printf '\n1. guard unit tests\n'
if bash lib/readonly-guard.sh --self-test >/dev/null 2>&1; then
    pass 'guard allows reads and refuses mutations'
else
    fail 'guard self-test failed - run: bash lib/readonly-guard.sh --self-test'
fi

printf '\n2. static tripwire: no direct CLI calls outside the guard\n'
# `command oci` inside readonly-guard.sh is the single sanctioned call site.
# Scan the discovery scripts only. This test file necessarily mentions the
# string it is looking for, and lib/readonly-guard.sh holds the one sanctioned
# call site (`command oci`).
STRAY="$(grep -nE '(^|[^_a-zA-Z-])oci ' oci-discover.sh emit-inventory.sh emit-dr-resources-env.sh 2>/dev/null \
        | grep -v 'ro_oci' \
        | grep -v 'ocid1' \
        | grep -v '^\s*#' \
        | grep -vE '^[^:]+:[0-9]+:\s*#' \
        | grep -vE "printf|command -v oci|'oci|\\\"oci" || true)"
if [ -z "$STRAY" ]; then
    pass 'no direct oci invocations in discovery scripts'
else
    fail 'direct oci invocation found outside the guard:'
    printf '%s\n' "$STRAY" | sed 's/^/          /'
fi

printf '\n3. end to end: every dry-run command is a read\n'
DRY="$(./oci-discover.sh --compartment ocid1.compartment.oc1..test \
        --regions us-ashburn-1,us-phoenix-1 --dry-run 2>&1 \
        | grep -E '^\s+oci ' || true)"
COUNT="$(printf '%s\n' "$DRY" | grep -c 'oci ' || true)"
if [ "$COUNT" -lt 20 ]; then
    fail "dry run emitted only $COUNT commands; expected the full walk"
else
    pass "$COUNT commands emitted"
fi

BAD=0
while IFS= read -r line; do
    [ -n "$line" ] || continue
    # operation = last positional token before the first flag
    op="$(printf '%s' "$line" | sed 's/^\s*oci //' | awk '{for(i=1;i<=NF;i++){if($i ~ /^-/) break; last=$i} print last}')"
    if ! printf '%s' "$op" | grep -Eq '^(list|get)(-[a-z0-9-]+)?$'; then
        printf '          non-read operation "%s" in: %s\n' "$op" "$line"
        BAD=$((BAD + 1))
    fi
done <<< "$DRY"
if [ "$BAD" -eq 0 ]; then
    pass 'all emitted operations are list or get'
else
    fail "$BAD non-read operation(s) found"
fi

printf '\n'
if [ "$FAILS" -eq 0 ]; then
    printf 'PASS - discovery is read-only by construction\n'; exit 0
else
    printf 'FAIL - %s check(s) failed\n' "$FAILS"; exit 1
fi
