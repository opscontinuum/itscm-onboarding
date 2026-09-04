#!/usr/bin/env bash
# readonly-guard.sh — structural enforcement that discovery never mutates.
#
# Source this file and call OCI commands ONLY through ro_oci(). The guard
# inspects the operation token and refuses anything that is not a read.
#
# It fails CLOSED: an operation it cannot parse is refused, not allowed.
#
#   source lib/readonly-guard.sh
#   ro_oci compute instance list --compartment-id "$C"     # runs
#   ro_oci compute instance terminate --instance-id "$I"   # refused, exit 3
#
# Self-test:  bash lib/readonly-guard.sh --self-test

set -o pipefail

# Operations permitted. An OCI operation is a read if and only if it begins
# with "list" or "get" (list, list-replication-policies, get, get-namespace).
# Allowlist, not denylist: a service added tomorrow with a novel destructive
# verb is refused by default rather than discovered in production.
readonly RO_ALLOWED_PATTERN='^(list|get)(-[a-z0-9-]+)?$'

RO_DRY_RUN="${RO_DRY_RUN:-0}"

# Counters live in files, not variables: ro_oci is routinely called inside a
# command substitution, and a variable incremented in a subshell never reaches
# the parent. A guard whose refusal count is silently lost is not a guard.
RO_STATE_DIR="${RO_STATE_DIR:-$(mktemp -d "${TMPDIR:-/tmp}/roguard.XXXXXX")}"
: > "$RO_STATE_DIR/made"
: > "$RO_STATE_DIR/refused"

ro_count()  { printf 'x' >> "$RO_STATE_DIR/$1"; }
ro_made()    { wc -c < "$RO_STATE_DIR/made" | tr -d ' '; }
ro_refused() { wc -c < "$RO_STATE_DIR/refused" | tr -d ' '; }

# ro_extract_operation ARGS... -> echoes the operation token, or empty.
# The operation is the last positional token before the first flag.
ro_extract_operation() {
    local last=""
    local tok
    for tok in "$@"; do
        case "$tok" in
            -*) break ;;
            *)  last="$tok" ;;
        esac
    done
    printf '%s' "$last"
}

ro_oci() {
    local op
    op="$(ro_extract_operation "$@")"

    if [ -z "$op" ]; then
        ro_count refused
        printf 'READONLY GUARD: refused - no operation token found in: oci %s\n' "$*" >&2
        return 3
    fi

    if ! printf '%s' "$op" | grep -Eq "$RO_ALLOWED_PATTERN"; then
        ro_count refused
        printf 'READONLY GUARD: refused mutating operation "%s"\n' "$op" >&2
        printf '  full command: oci %s\n' "$*" >&2
        printf '  Discovery is read-only. This is not a flag to widen; it is a finding to report.\n' >&2
        return 3
    fi

    if [ "$RO_DRY_RUN" = "1" ]; then
        # stderr, not stdout: callers capture stdout, and a dry run whose
        # command list is swallowed by a command substitution shows nothing.
        printf '    oci %s\n' "$*" >&2
        ro_count made
        return 0
    fi

    ro_count made
    command oci "$@"
}

# ro_try NAME ARGS... — run a read, and on failure record a gap rather than
# aborting the walk. A CLI too old to know a service must not stop discovery.
# Writes the gap line to the file named by RO_GAPS_FILE, if set.
ro_try() {
    local name="$1"; shift
    local out rc

    # In a dry run, let the guard's command line reach the terminal instead of
    # being captured into $out and discarded by the caller.
    if [ "$RO_DRY_RUN" = "1" ]; then
        ro_oci "$@" >/dev/null
        printf 'DRY_RUN'
        return 0
    fi

    out="$(ro_oci "$@" 2>&1)"; rc=$?
    if [ $rc -eq 0 ]; then
        printf '%s' "$out"
        return 0
    fi
    if [ -n "${RO_GAPS_FILE:-}" ]; then
        {
            printf 'NOT DISCOVERED: %s\n' "$name"
            printf '  command: oci %s\n' "$*"
            printf '  exit: %s\n' "$rc"
            printf '  reason: %s\n' "$(printf '%s' "$out" | head -3 | tr '\n' ' ')"
            printf '  action: confirm with the infrastructure owner during itscp-interview-infrastructure\n\n'
        } >> "$RO_GAPS_FILE"
    fi
    printf 'NOT_DISCOVERED'
    return 0
}

ro_self_test() {
    local fails=0 rc
    printf 'readonly-guard self-test\n\n'

    _expect_allow() {
        RO_DRY_RUN=1 ro_oci "$@" >/dev/null 2>&1; rc=$?
        if [ $rc -eq 0 ]; then printf '  ok    allow: oci %s\n' "$*"
        else printf '  FAIL  should allow: oci %s\n' "$*"; fails=$((fails+1)); fi
    }
    _expect_refuse() {
        RO_DRY_RUN=1 ro_oci "$@" >/dev/null 2>&1; rc=$?
        if [ $rc -eq 3 ]; then printf '  ok    refuse: oci %s\n' "$*"
        else printf '  FAIL  should refuse (rc=%s): oci %s\n' "$rc" "$*"; fails=$((fails+1)); fi
    }

    _expect_allow compute instance list --compartment-id ocid1.test
    _expect_allow db cloud-vm-cluster get --cloud-vm-cluster-id ocid1.test
    _expect_allow os replication list-replication-policies --bucket-name b
    _expect_allow iam compartment list --compartment-id-in-subtree true
    _expect_allow os ns get

    _expect_refuse compute instance terminate --instance-id ocid1.test
    _expect_refuse compute instance action --action STOP
    _expect_refuse db cloud-vm-cluster update --cpu-core-count 8
    _expect_refuse bv volume-group-replica create
    _expect_refuse disaster-recovery dr-plan-execution create
    _expect_refuse network vcn delete --vcn-id ocid1.test
    _expect_refuse db database switchover --database-id ocid1.test
    _expect_refuse db database failover --database-id ocid1.test
    _expect_refuse os object put --name x
    _expect_refuse --help

    printf '\n'
    if [ $fails -eq 0 ]; then printf 'all guard tests passed\n'; return 0
    else printf '%s guard test(s) FAILED\n' "$fails"; return 1; fi
}

if [ "${1:-}" = "--self-test" ]; then
    ro_self_test
    exit $?
fi
