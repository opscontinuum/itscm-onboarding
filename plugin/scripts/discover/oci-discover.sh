#!/usr/bin/env bash
# oci-discover.sh — read-only walk of an OCI tenancy for ISCP Appendix H and I.
#
# Every call goes through ro_oci() in lib/readonly-guard.sh, which refuses any
# operation that is not a list or a get. See the itscp-discover skill.
#
#   ./oci-discover.sh --compartment <ocid> --regions us-ashburn-1,us-phoenix-1 --out discovery-output/
#   ./oci-discover.sh --compartment <ocid> --regions us-ashburn-1 --dry-run
#
# --dry-run prints every command without executing. Show a customer the dry run
# before the real run; it turns "an AI will look at production" into a list they
# can review.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/readonly-guard.sh
source "$SCRIPT_DIR/lib/readonly-guard.sh"

COMPARTMENT=""
REGIONS=""
OUT="discovery-output"
SUBTREE="true"

usage() {
    sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'
    exit "${1:-0}"
}

while [ $# -gt 0 ]; do
    case "$1" in
        --compartment) COMPARTMENT="$2"; shift 2 ;;
        --regions)     REGIONS="$2"; shift 2 ;;
        --out)         OUT="$2"; shift 2 ;;
        --no-subtree)  SUBTREE="false"; shift ;;
        --dry-run)     RO_DRY_RUN=1; shift ;;
        -h|--help)     usage 0 ;;
        *) printf 'unknown argument: %s\n' "$1" >&2; usage 1 ;;
    esac
done

[ -n "$COMPARTMENT" ] || { printf 'error: --compartment is required\n' >&2; usage 1; }
[ -n "$REGIONS" ]     || { printf 'error: --regions is required\n' >&2; usage 1; }

if ! command -v oci >/dev/null 2>&1; then
    printf 'error: the oci CLI is not on PATH. Install it and run `oci setup config`.\n' >&2
    exit 1
fi

HAVE_JQ=0
command -v jq >/dev/null 2>&1 && HAVE_JQ=1
if [ "$HAVE_JQ" -eq 0 ]; then
    printf 'warning: jq not found. Raw JSON is still written; the rendered inventory will be sparse.\n' >&2
fi

mkdir -p "$OUT/raw"
export RO_GAPS_FILE="$OUT/gaps.md"
: > "$RO_GAPS_FILE"
{
    printf '# Discovery gaps\n\n'
    printf 'Everything the walk could not read, with the reason. **Absence here is absence of\n'
    printf 'evidence, not evidence of absence** — a resource class listed below may well exist.\n\n'
    printf 'Started: %s\n\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} >> "$RO_GAPS_FILE"

# save NAME REGION ARGS... — run a read, store raw JSON, echo the path.
save() {
    local name="$1" region="$2"; shift 2
    local file="$OUT/raw/${region}.${name}.json"
    local body
    body="$(ro_try "$name ($region)" "$@" --region "$region")"
    if [ "$body" = "NOT_DISCOVERED" ] || [ -z "$body" ]; then
        printf '{"data":[]}' > "$file"
    else
        printf '%s' "$body" > "$file"
    fi
    printf '%s' "$file"
}

jqr() {  # jqr FILE FILTER  -> empty string when jq is absent or filter fails
    [ "$HAVE_JQ" -eq 1 ] || return 0
    jq -r "$2" "$1" 2>/dev/null || true
}

IFS=',' read -r -a REGION_LIST <<< "$REGIONS"

printf 'Discovering compartment %s across %s\n' "$COMPARTMENT" "$REGIONS"
[ "$RO_DRY_RUN" = "1" ] && printf '(dry run: no calls will be executed)\n'
printf '\n'

for REGION in "${REGION_LIST[@]}"; do
    printf '== %s\n' "$REGION"

    printf '  identity and network\n'
    save compartments        "$REGION" iam compartment list --compartment-id "$COMPARTMENT" --compartment-id-in-subtree "$SUBTREE" --all >/dev/null
    save availability-domains "$REGION" iam availability-domain list --compartment-id "$COMPARTMENT" >/dev/null
    save vcns                "$REGION" network vcn list --compartment-id "$COMPARTMENT" --all >/dev/null
    save subnets             "$REGION" network subnet list --compartment-id "$COMPARTMENT" --all >/dev/null
    save drgs                "$REGION" network drg list --compartment-id "$COMPARTMENT" --all >/dev/null
    save nsgs                "$REGION" network nsg list --compartment-id "$COMPARTMENT" --all >/dev/null

    printf '  database\n'
    save exa-infrastructure  "$REGION" db cloud-exa-infra list --compartment-id "$COMPARTMENT" --all >/dev/null
    save vm-clusters         "$REGION" db cloud-vm-cluster list --compartment-id "$COMPARTMENT" --all >/dev/null
    save db-systems          "$REGION" db system list --compartment-id "$COMPARTMENT" --all >/dev/null
    save autonomous-dbs      "$REGION" db autonomous-database list --compartment-id "$COMPARTMENT" --all >/dev/null

    printf '  compute and storage\n'
    save instances           "$REGION" compute instance list --compartment-id "$COMPARTMENT" --all >/dev/null
    save volume-groups       "$REGION" bv volume-group list --compartment-id "$COMPARTMENT" --all >/dev/null
    save boot-volumes        "$REGION" bv boot-volume list --compartment-id "$COMPARTMENT" --all >/dev/null
    save volume-backup-policies "$REGION" bv volume-backup-policy list --compartment-id "$COMPARTMENT" --all >/dev/null
    save mount-targets       "$REGION" fs mount-target list --compartment-id "$COMPARTMENT" --all >/dev/null

    printf '  edge and orchestration\n'
    save load-balancers      "$REGION" lb load-balancer list --compartment-id "$COMPARTMENT" --all >/dev/null
    save network-lbs         "$REGION" nlb network-load-balancer list --compartment-id "$COMPARTMENT" --all >/dev/null
    save dns-zones           "$REGION" dns zone list --compartment-id "$COMPARTMENT" --all >/dev/null
    save steering-policies   "$REGION" dns steering-policy list --compartment-id "$COMPARTMENT" --all >/dev/null
    save http-monitors       "$REGION" health-checks http-monitor list --compartment-id "$COMPARTMENT" --all >/dev/null
    save drpgs               "$REGION" disaster-recovery dr-protection-group list --compartment-id "$COMPARTMENT" --all >/dev/null
    save protected-databases "$REGION" recovery protected-database list --compartment-id "$COMPARTMENT" --all >/dev/null
    save alarms              "$REGION" monitoring alarm list --compartment-id "$COMPARTMENT" --all >/dev/null

    # Per-AD resources: file systems and volume-group replicas are AD-scoped.
    if [ "$HAVE_JQ" -eq 1 ] && [ "$RO_DRY_RUN" != "1" ]; then
        printf '  per-availability-domain resources\n'
        while IFS= read -r AD; do
            [ -n "$AD" ] || continue
            save "file-systems.$AD"  "$REGION" fs file-system list --compartment-id "$COMPARTMENT" --availability-domain "$AD" --all >/dev/null
            save "fs-replications.$AD" "$REGION" fs replication list --compartment-id "$COMPARTMENT" --availability-domain "$AD" --all >/dev/null
            save "vg-replicas.$AD"   "$REGION" bv volume-group-replica list --compartment-id "$COMPARTMENT" --availability-domain "$AD" --all >/dev/null
        done < <(jqr "$OUT/raw/${REGION}.availability-domains.json" '.data[].name')
    fi

    # Object Storage: namespace, then buckets, then per-bucket replication policy.
    if [ "$RO_DRY_RUN" != "1" ]; then
        printf '  object storage\n'
        NS="$(ro_try "object storage namespace ($REGION)" os ns get --region "$REGION" 2>/dev/null | tr -d '"' | tr -d ' \n')"
        NS="${NS#*:}"
        if [ -n "$NS" ] && [ "$NS" != "NOT_DISCOVERED" ]; then
            save buckets "$REGION" os bucket list --compartment-id "$COMPARTMENT" --namespace-name "$NS" --all >/dev/null
            if [ "$HAVE_JQ" -eq 1 ]; then
                while IFS= read -r B; do
                    [ -n "$B" ] || continue
                    save "replication.$B" "$REGION" os replication list-replication-policies \
                        --namespace-name "$NS" --bucket-name "$B" >/dev/null
                done < <(jqr "$OUT/raw/${REGION}.buckets.json" '.data[].name')
            fi
        fi
    fi
done

MADE="$(ro_made)"; REFUSED="$(ro_refused)"
printf '\nCalls made: %s   refused by guard: %s\n' "$MADE" "$REFUSED"

if [ "$REFUSED" -ne 0 ]; then
    printf '\nERROR: the guard refused %s call(s). A mutating call was attempted.\n' "$REFUSED" >&2
    printf 'This is a defect in this script, not a condition to work around.\n' >&2
    exit 4
fi

if [ "$RO_DRY_RUN" = "1" ]; then
    printf '\nDry run complete. Nothing was executed and nothing was written.\n'
    exit 0
fi

"$SCRIPT_DIR/emit-inventory.sh" --in "$OUT" --regions "$REGIONS" --out "$OUT/inventory.md"
"$SCRIPT_DIR/emit-dr-resources-env.sh" --in "$OUT" --regions "$REGIONS" --out "$OUT/dr-resources.env"

printf '\nWrote:\n'
printf '  %s/inventory.md         ISCP Appendix H\n' "$OUT"
printf '  %s/dr-resources.env     resource file for runbook scripts\n' "$OUT"
printf '  %s/gaps.md              what could not be read, and who to ask\n' "$OUT"
printf '  %s/raw/                 raw JSON, for re-rendering without re-walking\n' "$OUT"
printf '\nAll of these are gitignored. inventory.md is a complete map of a production environment.\n'
