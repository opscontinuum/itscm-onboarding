# RB-01 Switchover

A planned transition of the production role, rehearsed and reversible.

This document is generated from the answer store. Correct it by correcting the interview, not by editing this file.

## 4.1 Sequence of Recovery Activities

- **The component start order and what depends on what**: The order is fixed by dependency rather than preference and both runbooks execute it the same way. Quiesce the application tier first, Concurrent Managers before anything else, because an in-flight concurrent request writing during a role transition is the hardest class of damage to reason about afterwards: stopping the writers precedes stopping the readers. Capture forensics next on an unplanned event, because evidence is destroyed by recovery. Then transition the database, because everything downstream needs a writable database with a known system change number. Then activate storage, block first, then file, then object, because the application tier mounts these, and because activating a volume group replica takes its last synced point and activating before it has caught up silently strands writes. Then scale the standby Exadata off its OCPU floor, because redo apply at the floor is not the same workload as serving production. Then start compute and then EBS. Steer traffic last, so that no user reaches a half-built stack. Work recovery runs in parallel with the last two steps rather than after them. Within the application tier: attach and mount storage and verify fs1, fs2 and fs_ne are all present before touching EBS; run cmclean with all managers down; start EBS services; start Concurrent Managers last, after web and forms are confirmed healthy; then verify that FND_NODES matches the running logical host names.

## 4.2 Recovery Procedures

- **The recovery procedure at the level of what is actually typed, in order**: # Manual fallback if Full Stack DR is unavailable. Run in this order, do not reorder.

# 1. Quiesce the application tier (IAD), Concurrent Managers FIRST
powershell -File scripts/windows/Stop-EBSAppTier.ps1 -Node ALL -Drain

# 2. Switch the database (protection mode already downgraded and FSFO disabled)
dgmgrl sys/****@EBSPROD_IAD "switchover to EBSPROD_PHX"

# 3. Wait for the volume group replica to catch up to (approximately) the current
#    write rate before activating it. Activation takes the replica's LAST synced
#    point, so activating early strands changes written after that point.
oci bv volume-group-replica get --volume-group-replica-id <replica-ocid> --region us-phoenix-1 \
  | jq -r '.data["time-last-synced"]'   # repeat until within one replication cycle

# 4. Bring up Phoenix storage, then compute, then EBS.
#    All three take their OCIDs and region from terraform/dr-resources.env; all refuse
#    without --confirm and a --ticket. Add --dry-run to any of them to print the exact
#    OCI calls without issuing one; do that first.
./scripts/oci/activate-volume-group.sh --vg-replica <replica-ocid> --region us-phoenix-1 --confirm --ticket "<change-ref>"
./scripts/oci/fss-failover.sh --replication <replication-ocid> --region us-phoenix-1 --lossless --confirm --ticket "<change-ref>"
./scripts/oci/scale-exadata-ocpu.sh --cluster EBSPROD_PHX --ocpu-per-node 16
powershell -File scripts/windows/Start-EBSAppTier.ps1 -Node ALL -RunCmClean

# 5. Steer traffic
./scripts/oci/steer-traffic.sh --target phoenix

## Recorded for this plan

- **How long a full application-tier reconfiguration takes, measured**: About 20 to 40 minutes when the EBS logical host names are preserved, because application-tier recovery is then just starting the services. About 3 to 5 hours when they are not, because the documented Oracle sequence for a role transition has to run: purge FND_NODES, then AutoConfig on the database tier, then AutoConfig on both the run and patch filesystems of every application-tier node. *(low confidence; not measured)*

## References

Sources for every value above, as recorded when the value was given.

- **The component start order and what depends on what**, recorded by document:oci-itscp/docs/09-phase-recovery.md
- **The recovery procedure at the level of what is actually typed, in order**, recorded by document:oci-itscp/runbooks/RB-01-switchover.md
- **How long a full application-tier reconfiguration takes, measured**, recorded by document:oci-itscp/docs/01-architecture.md; mechanism: Neither figure has been timed. The reference plan marks both as engineering judgement with no documentation found, in four separate places, and states that an unnecessary hostname-rebuild cycle adds 3 to 5 hours and turns a one-hour switchover into a multi-hour one. The 3 to 5 hour figure is built on Oracle's documented purge-and-AutoConfig sequence rather than on a rehearsal, and the whole estate has never been exercised end to end.

### Unverified statements

Engineering judgements, outstanding gaps and disagreements, labelled as such.

- **How long a full application-tier reconfiguration takes, measured**:  *(low confidence; not measured)*
