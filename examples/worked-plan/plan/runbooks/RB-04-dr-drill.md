# RB-04 Recovery drill

The exercise procedure and what evidence it has to produce.

This document is generated from the answer store. Correct it by correcting the interview, not by editing this file.

## APPENDIX J TEST AND MAINTENANCE SCHEDULE

- **The date of the last end-to-end execution and who performed it**: Never, by construction. The reference plan documents a hypothetical corporation and states that it is not validated against a live environment. Its Terraform has never been applied and plan and apply were never run. Its plan-approval statement carries the date of the last drill as an unfilled placeholder, its evidence directory is a structural placeholder, and its record of changes carries no row for a drill or an event. Nobody has run it.

## 5.9 Event Documentation

- **How a real event is written up, by whom, and where the record goes**: It has never been done, and the reference plan states plainly that it could not be. There is no after-action report template. The standard asks for one explicitly, and the repository has the inputs, the drill timing sheet, the recovery-point attestation script, the replication-state capture and the evidence directory, but no document that assembles them into a report and no defined route from a finding to a plan change beyond the record of changes. The drill runbook covers evidence and improvement for a drill; a real event is not covered. Where the record would go is stated, the timing sheet, replication-state capture and after-action narrative to the evidence directory with the record of changes updated with what the event taught, and both are exit-checklist items. Who writes it for a real event is not stated in the reference plan, beyond the assessment team contributing to the after-action record and risk and audit receiving the evidence. The record of changes carries no row for a drill or an event.

## 3.5 Plan Testing, Training, and Exercises (TT&E)

- **How often the plan is exercised, in practice**: **[MISSING — owner: governance/risk contact]**

## Supplied by the toolkit's method

An exercise proves one of three things and rarely all three: that the plan reads correctly, that the steps run, or that the business can work afterwards. The toolkit asks which level each exercise reaches and what it therefore leaves unproven, because a plan whose only evidence is a reading has never been shown to work.


**Each exercise level, what it proves and what it does not**

| level | what_it_proves | what_it_does_not_prove |
| --- | --- | --- |
| 1, component test, using the orchestration prechecks and the replication health script, with no production impact | Replication is healthy, prechecks pass, the in-guest agent is alive, and, empirically the first time it is run, what the built-in Exadata drill plan group actually does | It exercises no recovery role, so it satisfies no training requirement. Beyond that, not stated in the reference plan |
| 2, snapshot standby drill, using a Data Guard snapshot standby with the start-drill and stop-drill plans, with no production impact | The full EBS stack opens read-write in Phoenix, the application tier starts and transactions commit. This is the drill that produces a real measured tolerable downtime without an outage, and the plan calls it the workhorse | It is run with the runbook open, so it never satisfies the closed-book training standard. While it runs, the always-on BI node reads a snapshot standby that is receiving redo without applying it, so it proves the presentation tier survives a role change and not that the standby is current |
| 3, live switchover, running the switchover runbook against real production, with a planned outage | Everything, including DNS, users and partner integrations | not stated in the reference plan |


## References

Sources for every value above, as recorded when the value was given.

- **The date of the last end-to-end execution and who performed it**, recorded by document:oci-itscp/README.md
- **How a real event is written up, by whom, and where the record goes**, recorded by document:oci-itscp/docs/10-phase-reconstitution.md
- **Each exercise level, what it proves and what it does not**, recorded by document:oci-itscp/runbooks/RB-04-dr-drill.md

### Unverified statements

Engineering judgments, outstanding gaps and disagreements, labeled as such.

- **How often the plan is exercised, in practice**: **[MISSING — owner: governance/risk contact]**
