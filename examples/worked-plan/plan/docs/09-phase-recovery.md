# Phase two: recovery

The order things are brought back, and who escalates when they are not.

This document is generated from the answer store. Correct it by correcting the interview, not by editing this file.

## 4.1 Sequence of Recovery Activities

- **The component start order and what depends on what**: The order is fixed by dependency rather than preference and both runbooks execute it the same way. Quiesce the application tier first, Concurrent Managers before anything else, because an in-flight concurrent request writing during a role transition is the hardest class of damage to reason about afterwards: stopping the writers precedes stopping the readers. Capture forensics next on an unplanned event, because evidence is destroyed by recovery. Then transition the database, because everything downstream needs a writable database with a known system change number. Then activate storage, block first, then file, then object, because the application tier mounts these, and because activating a volume group replica takes its last synced point and activating before it has caught up silently strands writes. Then scale the standby Exadata off its OCPU floor, because redo apply at the floor is not the same workload as serving production. Then start compute and then EBS. Steer traffic last, so that no user reaches a half-built stack. Work recovery runs in parallel with the last two steps rather than after them. Within the application tier: attach and mount storage and verify fs1, fs2 and fs_ne are all present before touching EBS; run cmclean with all managers down; start EBS services; start Concurrent Managers last, after web and forms are confirmed healthy; then verify that FND_NODES matches the running logical host names.

## Recorded for this plan

- **How long a full application-tier reconfiguration takes, measured**: About 20 to 40 minutes when the EBS logical host names are preserved, because application-tier recovery is then just starting the services. About 3 to 5 hours when they are not, because the documented Oracle sequence for a role transition has to run: purge FND_NODES, then AutoConfig on the database tier, then AutoConfig on both the run and patch filesystems of every application-tier node. *(low confidence; not measured)*

## 4.3 Recovery Escalation Notices/Awareness

- **The escalation thresholds, each observable**: Four triggers, each tied to something observable. Any numbered recovery step exceeding twice its drill-measured duration, or the elapsed total passing half the tier's tolerable downtime: escalate to the declaring authority, re-forecast against what remains, and consider the failover runbook's branches. A key step completing, meaning the database transitioned, traffic steered, or service declared: status to the bridge and to the business owner. Standby capacity proving insufficient, whether core scaling is blocked or Phoenix shape capacity is unavailable: escalate to the cloud account team. And measured data loss exceeding the tier's recovery point, which leaves the runbook altogether and becomes a business decision. Beyond those, a suspected cyber cause, regulatory exposure or media interest escalates to security incident response, Legal and Communications. *(low confidence; not measured)*

## References

Sources for every value above, as recorded when the value was given.

- **The component start order and what depends on what**, recorded by document:oci-itscp/docs/09-phase-recovery.md
- **How long a full application-tier reconfiguration takes, measured**, recorded by document:oci-itscp/docs/01-architecture.md; mechanism: Neither figure has been timed. The reference plan marks both as engineering judgement with no documentation found, in four separate places, and states that an unnecessary hostname-rebuild cycle adds 3 to 5 hours and turns a one-hour switchover into a multi-hour one. The 3 to 5 hour figure is built on Oracle's documented purge-and-AutoConfig sequence rather than on a rehearsal, and the whole portfolio has never been exercised end to end.
- **The escalation thresholds, each observable**, recorded by document:oci-itscp/docs/09-phase-recovery.md

### Unverified statements

Engineering judgements, outstanding gaps and disagreements, labeled as such.

- **How long a full application-tier reconfiguration takes, measured**:  *(low confidence; not measured)*
- **The escalation thresholds, each observable**:  *(low confidence; not measured)*
