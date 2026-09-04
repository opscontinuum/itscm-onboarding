# RB-02 Failover

An unplanned transition, and the decision gate in front of it.

This document is generated from the answer store. Correct it by correcting the interview, not by editing this file.

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

- **Each scheduled job, whether it is safe to resubmit, and what a second run does**: **[MISSING — owner: application owner]**

## 4.2.1 Activation Criteria and Procedure

- **The single individual with declaration authority, and their named deputy**: The DR Commander, and that decision only: the same document is explicit that the Commander declares and the DR Coordinator recovers, because the person weighing the repair estimate against the remaining budget should not also be running the storage sequence. One person holds declaration authority at any moment. The Deputy DR Commander is the named alternate and the plan is careful that they are not a second decision-maker but the same box when the first is silent. The business owner is consulted if reachable within fifteen minutes and the gate does not wait beyond that, and the declaration does not wait for the change advisory board.

## 3.1 Activation Criteria and Procedure

- **The activation criteria, each one observable**: Four observable questions inside a ten-minute gate, and the plan treats not activating as a first-class outcome. Is the primary database reachable and openable? If it is, this is not a failover, and the answer is to troubleshoot in place. Is a drill in progress? Did the local fast-start failover already promote the in-region standby, and if it did, is the second availability domain's application tier serving requests? Is the whole Ashburn region or the Exadata infrastructure lost? And finally, is the estimated repair time greater than the maximum tolerable downtime minus the time already spent on this gate minus the roughly sixty-minute failover recovery time? If it is, declare and execute the failover plan. The plan is emphatic that the fourth threshold is dynamic rather than the flat two-hour tier 0 figure, and that declaring late burns the margin a cross-region failover needs to land inside the tolerable downtime at all.

## References

Sources for every value above, as recorded when the value was given.

- **The recovery procedure at the level of what is actually typed, in order**, recorded by document:oci-itscp/runbooks/RB-01-switchover.md
- **The single individual with declaration authority, and their named deputy**, recorded by document:oci-itscp/checklists/dr-authority-matrix.md
- **The activation criteria, each one observable**, recorded by document:oci-itscp/runbooks/RB-02-failover.md

### Unverified statements

Engineering judgements, outstanding gaps and disagreements, labeled as such.

- **Each scheduled job, whether it is safe to resubmit, and what a second run does**: **[MISSING — owner: application owner]**
