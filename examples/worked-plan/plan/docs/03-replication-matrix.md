# Replication matrix

What is replicated, by which mechanism, and which choices cannot be reversed.

This document is generated from the answer store. Correct it by correcting the interview, not by editing this file.

## APPENDIX F ALTERNATE STORAGE, SITE, AND TELECOMMUNICATIONS

- **The standby region**: us-phoenix-1

## Recorded for this plan

- **Measured inter-region round-trip time in milliseconds**: **[MISSING — owner: lead engineer]**

## 3.4.1 Backup and Recovery


**Per tier: the replication mechanism, whether it is synchronous, measured lag, failover behavior, whether reversal needs a re-baseline, and whether it is one-way**

| tier | mechanism | sync | measured_lag | what_breaks_at_that_lag | failover_behavior | rebaseline_on_reversal | one_way |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Tier 0, Platinum | Oracle Active Data Guard, synchronous within the region and asynchronous to Phoenix, with real-time apply and Fast-Start Failover on the local leg; Block Volume Group Replication running continuously; File Storage replication at its shortest supported interval of fifteen minutes; Object Storage replication policy | yes within the region, no across regions | target under 30 seconds across regions; the measured figure is not stated in the reference plan | Recovery point zero stops being true once the configuration falls unsynchronized, and fast-start failover cannot occur while the target standby is unsynchronized, so the local automatic-failover story stops working in exactly the double-fault case tier 0 exists to cover | A pre-approved Full Stack DR failover plan | yes for block, file and object storage; no for Data Guard, which reinstates the former primary through Flashback Database | yes for block, file and object storage |
| Tier 1, Gold | Oracle Active Data Guard, asynchronous, with real-time apply; Volume Group Replication running continuously; File Storage replication; Object Storage replication policy. Phoenix instances exist but are stopped on a schedule | no | not stated in the reference plan | not stated in the reference plan | A Full Stack DR plan plus change approval | yes for block, file and object storage; no for Data Guard | yes for block, file and object storage |
| Tier 2, Silver | Oracle Data Guard managed recovery with the VM cluster at its OCPU floor; Volume Group Replication; File Storage replication on a long interval; Object Storage replication policy; custom images and volume group replicas only for compute | no | not stated in the reference plan | not stated in the reference plan | A Full Stack DR plan plus manual staging | yes for block, file and object storage | yes for block, file and object storage |
| Tier 3, Bronze | Autonomous Recovery Service in-region backup with RMAN restore; scheduled cross-region block volume backup copy; a File Storage snapshot exported to Object Storage; rebuild from a custom image | no | not stated in the reference plan | not stated in the reference plan | Manual rebuild | no rebaseline; there is no standing replication to reverse | no |


## Recorded for this plan

- **Storage features that constrain what the standby may be built on**: One feature decides what the standby may be built on. The plan assumes the database does not use Hybrid Columnar Compression, and records that if it does, the standby storage must be Exadata, Oracle ZFS Storage Appliance or Pillar Axiom FS1, so the cheap non-Exadata standby is ruled out. It ships a check to run before sizing the standby and says to run it first. It also marks as unverified whether compressed data actually becomes unreadable on unsupported storage, and tells the reader to validate before assuming the downgrade path is closed. Two licensing constraints sit alongside: redo transport compression on the Phoenix leg needs the Advanced Compression option, and real-time apply with a readable standby needs the Active Data Guard option.

## Supplied by the toolkit's method

Some decisions in a continuity design cost a change ticket to undo and some cannot be undone at all without rebuilding from nothing. The toolkit separates the two and costs the second kind before it is taken, because otherwise the moment a one-way door is noticed is the moment somebody has already walked through it to save money.


**Each decision that cannot be cheaply reversed, what reversing it costs and who may take it**

| decision | cost_to_reverse | who_may_take_it |
| --- | --- | --- |
| Disable Volume Group Replication to save the replica storage line | Disabling deletes the replica, and re-enabling starts the replication process from scratch with an initial sync that can take hours. The cheapest line item is traded for a multi-hour unprotected window | Nobody. The posture tooling refuses it outright |
| Export a File Storage replication target to make it writable at failover | Once a target has been exported, re-establishing replication requires a full base copy; a target that was never exported can be reused without one | The failover runbook, and only with an explicit confirmation flag and a change or incident ticket |
| Delete the source Object Storage replication policy | A new policy does not replicate objects that already exist in the source bucket, so a bulk copy has to run before the reverse policy. Deleting the source policy is permanent | The failover runbook, and only with an explicit confirmation flag and a change or incident ticket |
| Execute a cross-region failover to Phoenix | There is no fast undo. The return trip is a project-managed failback measured in days to weeks, mostly waiting on full baseline copies of every storage tier | The DR Commander, under the delegation in the authority matrix, without waiting for the change advisory board |
| Scale the Phoenix Exadata VM cluster to zero cores to save money | Redo apply stops. Tier 1 silently becomes tier 3 while the documentation still claims the old recovery point | Nobody. Refused by the tooling |
| Delete replication to decommission the DR site | Protection is removed outright, deliberately | The Infra Manager and the risk function, with written sign-off from both |


## 5.7 Offsite Data Storage


**Each backup copy, where it is held, how long it is kept and how it is retrieved**

| copy | where_it_is_held | retention | how_it_is_retrieved |
| --- | --- | --- | --- |
| Autonomous Recovery Service backup of the primary, with retention lock for immutability | In whichever region is primary, replicated across availability domains within that region | A minimum fourteen-day delay before the retention period locks permanently, and a maximum retention of ninety-five days | Restorable to any availability domain, zone or region, over the network. No physical media is involved anywhere in this plan |
| A customer-scheduled RMAN backup of the Phoenix standby | An Object Storage bucket, with a retention rule on the bucket | not stated in the reference plan; the plan records that a specific retention duration was not sourced in this revision | RMAN restore from the Phoenix copy, followed by enabling the backup service on the new primary |
| A periodic long-term RMAN keep backup, taken ahead of any standby decommission | Object Storage, with a cross-region copy | not stated in the reference plan as a duration; the plan states only that the recovery service is not a long-term retention mechanism because its lock accepts at most ninety-five days, while an ERP records-retention schedule is measured in years | Restored and verified restorable |


## 5.8 Data Backup

- **How the recovered system is protected again, when, and who confirms it**: Nothing protects the recovered system until somebody turns protection on, and the reference plan says so in as many words: this is the step most likely to be missed, because Ashburn's protection was the recovery service and Phoenix as primary is a different posture that does not inherit it. Backups are disabled on the new standby after any role change, and the failover runbook carries an explicit step to enable the recovery service on the new primary, warning that backups are not running there until somebody does. An alarm covers it: the protected-database status is checked, and a non-healthy status or no backup in twenty-six hours pages the DBA on-call. The database team owns re-protection, meaning a new standby and a fresh backup, and the plan's exit checklist will not close until a fresh full backup of the current primary exists in whatever region is now primary and a standby exists again inside the tier recovery point. No deadline in hours is stated for that first backup; the twenty-six hour figure is a monitoring threshold rather than a target. **[CONFLICT — Nothing protects the recovered system until somebody turns protection on, and the reference plan says so in as many words: this is the step most likely to be missed, because Ashburn's protection was the recovery service and Phoenix as primary is a different posture that does not inherit it. Backups are disabled on the new standby after any role change, and the failover runbook carries an explicit step to enable the recovery service on the new primary, warning that backups are not running there until somebody does. An alarm covers it: the protected-database status is checked, and a non-healthy status or no backup in twenty-six hours pages the DBA on-call. The database team owns re-protection, meaning a new standby and a fresh backup, and the plan's exit checklist will not close until a fresh full backup of the current primary exists in whatever region is now primary and a standby exists again inside the tier recovery point. No deadline in hours is stated for that first backup; the twenty-six hour figure is a monitoring threshold rather than a target. (document:oci-itscp/docs/10-phase-reconstitution.md) against Automatic backups may be enabled on a database holding the standby role in a Data Guard association, so the Phoenix standby could be backed up directly. (document:oci-itscp/docs/03-replication-matrix.md); decision owner: infrastructure owner]**

## References

Sources for every value above, as recorded when the value was given.

- **The standby region**, recorded by document:oci-itscp/docs/01-architecture.md
- **Per tier: the replication mechanism, whether it is synchronous, measured lag, failover behavior, whether reversal needs a re-baseline, and whether it is one-way**, recorded by document:oci-itscp/docs/02-mtd-tiers.md
- **Storage features that constrain what the standby may be built on**, recorded by document:oci-itscp/docs/01-architecture.md
- **Each decision that cannot be cheaply reversed, what reversing it costs and who may take it**, recorded by document:oci-itscp/docs/03-replication-matrix.md
- **Each backup copy, where it is held, how long it is kept and how it is retrieved**, recorded by document:oci-itscp/runbooks/RB-05-replication-lifecycle.md
- **How the recovered system is protected again, when, and who confirms it**, recorded by document:oci-itscp/docs/10-phase-reconstitution.md

### Unverified statements

Engineering judgements, outstanding gaps and disagreements, labeled as such.

- **Measured inter-region round-trip time in milliseconds**: **[MISSING — owner: lead engineer]**
- **How the recovered system is protected again, when, and who confirms it**:  **[CONFLICT — Nothing protects the recovered system until somebody turns protection on, and the reference plan says so in as many words: this is the step most likely to be missed, because Ashburn's protection was the recovery service and Phoenix as primary is a different posture that does not inherit it. Backups are disabled on the new standby after any role change, and the failover runbook carries an explicit step to enable the recovery service on the new primary, warning that backups are not running there until somebody does. An alarm covers it: the protected-database status is checked, and a non-healthy status or no backup in twenty-six hours pages the DBA on-call. The database team owns re-protection, meaning a new standby and a fresh backup, and the plan's exit checklist will not close until a fresh full backup of the current primary exists in whatever region is now primary and a standby exists again inside the tier recovery point. No deadline in hours is stated for that first backup; the twenty-six hour figure is a monitoring threshold rather than a target. (document:oci-itscp/docs/10-phase-reconstitution.md) against Automatic backups may be enabled on a database holding the standby role in a Data Guard association, so the Phoenix standby could be backed up directly. (document:oci-itscp/docs/03-replication-matrix.md); decision owner: infrastructure owner]**
