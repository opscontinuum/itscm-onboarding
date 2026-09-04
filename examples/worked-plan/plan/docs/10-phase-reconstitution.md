# Phase three: reconstitution

How normal operation is restored and the plan stood down.

This document is generated from the answer store. Correct it by correcting the interview, not by editing this file.

## Supplied by the toolkit's method

Maximum tolerable downtime is recovery time plus work recovery time. The toolkit decomposes it that way so that a recovery which meets its technical target and still misses what the business can tolerate is visible on paper rather than at four in the morning.


**Each work-recovery activity, its duration, and whether it runs in parallel with bring-up**

| activity | duration | parallel_with_bringup |
| --- | --- | --- |
| Reconcile the in-flight concurrent request list captured by the scheduled job against what completed, and re-submit per the idempotency register | not stated in the reference plan | yes |
| Replay inbound interface files from the replicated Object Storage bucket for the window between the last replica and the incident | not stated in the reference plan | yes |
| Identify outbound files generated but not transmitted, and re-transmit them from the ledger | not stated in the reference plan | yes |
| Warn users of the possible Workflow Mailer duplicate-notification window | not stated in the reference plan | yes |
| Run the reconciliation report pack and obtain Finance sign-off | not stated in the reference plan | yes |
| Publish the data-loss statement | not stated in the reference plan | yes |


## 5.1 Concurrent Processing

- **Whether concurrent processing is performed, and the reason either way**: Not applicable — Not performed. A single EBS instance with one authoritative database cannot run production in two regions at once; a second writable copy would diverge, and reconciling it is worse than the outage. NIST does not require it, stating that information systems are not required to have concurrent processing capabilities.

## 5.2 Validation Data Testing


**Each data validation check, what it proves and who signs it off**

| check | what_it_proves | who_signs |
| --- | --- | --- |
| Data Guard gap check | not stated in the reference plan | not stated in the reference plan |
| System change number and lag reconciliation | not stated in the reference plan | not stated in the reference plan |
| The recovery point attestation, recording what was actually lost | What was actually lost, in seconds of transport lag. The plan calls this the honest half of the step: validation data testing asks whether the data is current, and after an unplanned failover the truthful answer is often no, by some number of seconds | not stated in the reference plan |


## Recorded for this plan

- **Each scheduled job, whether it is safe to resubmit, and what a second run does**: **[MISSING — owner: application owner]**

## 5.8 Data Backup

- **How the recovered system is protected again, when, and who confirms it**: Nothing protects the recovered system until somebody turns protection on, and the reference plan says so in as many words: this is the step most likely to be missed, because Ashburn's protection was the recovery service and Phoenix as primary is a different posture that does not inherit it. Backups are disabled on the new standby after any role change, and the failover runbook carries an explicit step to enable the recovery service on the new primary, warning that backups are not running there until somebody does. An alarm covers it: the protected-database status is checked, and a non-healthy status or no backup in twenty-six hours pages the DBA on-call. The database team owns re-protection, meaning a new standby and a fresh backup, and the plan's exit checklist will not close until a fresh full backup of the current primary exists in whatever region is now primary and a standby exists again inside the tier recovery point. No deadline in hours is stated for that first backup; the twenty-six hour figure is a monitoring threshold rather than a target. **[CONFLICT — Nothing protects the recovered system until somebody turns protection on, and the reference plan says so in as many words: this is the step most likely to be missed, because Ashburn's protection was the recovery service and Phoenix as primary is a different posture that does not inherit it. Backups are disabled on the new standby after any role change, and the failover runbook carries an explicit step to enable the recovery service on the new primary, warning that backups are not running there until somebody does. An alarm covers it: the protected-database status is checked, and a non-healthy status or no backup in twenty-six hours pages the DBA on-call. The database team owns re-protection, meaning a new standby and a fresh backup, and the plan's exit checklist will not close until a fresh full backup of the current primary exists in whatever region is now primary and a standby exists again inside the tier recovery point. No deadline in hours is stated for that first backup; the twenty-six hour figure is a monitoring threshold rather than a target. (document:oci-itscp/docs/10-phase-reconstitution.md) against Automatic backups may be enabled on a database holding the standby role in a Data Guard association, so the Phoenix standby could be backed up directly. (document:oci-itscp/docs/03-replication-matrix.md); decision owner: infrastructure owner]**

## 5.10 Deactivation

- **Who may deactivate the plan and on what evidence**: The same authority that declared the disaster announces the deactivation, to the same list that was notified at activation, because declaration and deactivation are a matched pair and an unclosed declaration leaves the organization unsure whether it is still in one. What they have to see is a ten-item exit checklist, all of it true: the recovery-point attestation filed; the functional team's signature on the validation pack; users, business owner and partners notified; drill and temporary resources torn down and the posture returned to steady state; a standby existing again with its lag inside the tier recovery point; a fresh full backup of the current primary in whatever region is now primary; the protection groups re-pointed and their plans re-validated; the timing sheet and after-action narrative written to evidence; the record of changes updated with what the event taught; and the announcement itself. Anything unticked is an open disaster, whatever the dashboards say. Deactivating does not require being back in Ashburn; it requires being protected wherever you are.

## 5.4 Recovery Declaration

- **Who declares recovery complete and the evidence they need first**: The reference plan has two moments where this plan's question expects one, and it does not name a speaker for the first. Service is declared available to users once the validation pack passes, at which point the plan is explicit that the system is functional and not validated, because validation belongs to reconstitution. Later the business owner accepts service restoration, the functional team signs the validation pack and the DBA does not, and the declaring authority announces deactivation. The evidence required is the validation pack, the recovery-point attestation, and the data-loss statement produced during the failover. Who tells the business at the first moment is not stated in the reference plan.

## 5.5 Notifications (users)

- **How users are told service is restored, by whom and what the message must carry**: A service-restored notice goes to users, the business owner, and every interconnected partner who was told during activation, sent through the call tree and partner contact lists rather than through the recovered environment, and the exit checklist will not close until it has gone. What the message has to carry is not stated in the reference plan: the reference plan has a what-to-say table and it belongs to the activation notification, covering the nature of the outage, the repair estimate, the runbook step and the bridge details. There is no restoration template, nobody is named as drafting it, and the warning about possibly duplicated workflow notifications appears only as a work-recovery task and not as something the restoration message must repeat to users.

## 5.6 Cleanup

- **What is dismantled after the event, and who is responsible for each of it**: Tear down drill-only resources, release the activated volume-group clones, retire the temporary DNS answers, and return the posture to steady state, which for Phoenix compute means back to pilot light. The DR Coordinator owns the exit checklist, the application tier team carries drift reconciliation and cleanup, and the network team retires the temporary answers. Nothing is returned physically: there is no media, backups sit in the recovery service and Object Storage, and the plan marks offsite media return as not applicable rather than leaving it blank. The thing that must deliberately not be torn down is replication, and the plan's governing rule says exactly that: tear down compute, never tear down replication. The exit checklist will not close until a standby exists again with its lag inside the tier recovery point.

## References

Sources for every value above, as recorded when the value was given.

- **Each work-recovery activity, its duration, and whether it runs in parallel with bring-up**, recorded by document:oci-itscp/runbooks/RB-02-failover.md
- **Each data validation check, what it proves and who signs it off**, recorded by document:oci-itscp/docs/10-phase-reconstitution.md
- **How the recovered system is protected again, when, and who confirms it**, recorded by document:oci-itscp/docs/10-phase-reconstitution.md
- **Who may deactivate the plan and on what evidence**, recorded by document:oci-itscp/docs/10-phase-reconstitution.md
- **Who declares recovery complete and the evidence they need first**, recorded by document:oci-itscp/docs/10-phase-reconstitution.md
- **How users are told service is restored, by whom and what the message must carry**, recorded by document:oci-itscp/docs/10-phase-reconstitution.md
- **What is dismantled after the event, and who is responsible for each of it**, recorded by document:oci-itscp/docs/10-phase-reconstitution.md

### Unverified statements

Engineering judgments, outstanding gaps and disagreements, labeled as such.

- **Whether concurrent processing is performed, and the reason either way**: Not applicable — Not performed. A single EBS instance with one authoritative database cannot run production in two regions at once; a second writable copy would diverge, and reconciling it is worse than the outage. NIST does not require it, stating that information systems are not required to have concurrent processing capabilities.
- **Each scheduled job, whether it is safe to resubmit, and what a second run does**: **[MISSING — owner: application owner]**
- **How the recovered system is protected again, when, and who confirms it**:  **[CONFLICT — Nothing protects the recovered system until somebody turns protection on, and the reference plan says so in as many words: this is the step most likely to be missed, because Ashburn's protection was the recovery service and Phoenix as primary is a different posture that does not inherit it. Backups are disabled on the new standby after any role change, and the failover runbook carries an explicit step to enable the recovery service on the new primary, warning that backups are not running there until somebody does. An alarm covers it: the protected-database status is checked, and a non-healthy status or no backup in twenty-six hours pages the DBA on-call. The database team owns re-protection, meaning a new standby and a fresh backup, and the plan's exit checklist will not close until a fresh full backup of the current primary exists in whatever region is now primary and a standby exists again inside the tier recovery point. No deadline in hours is stated for that first backup; the twenty-six hour figure is a monitoring threshold rather than a target. (document:oci-itscp/docs/10-phase-reconstitution.md) against Automatic backups may be enabled on a database holding the standby role in a Data Guard association, so the Phoenix standby could be backed up directly. (document:oci-itscp/docs/03-replication-matrix.md); decision owner: infrastructure owner]**
