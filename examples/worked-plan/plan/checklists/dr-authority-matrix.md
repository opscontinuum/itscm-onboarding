# Recovery authority matrix

Who may declare, who may spend, and how long they have to decide.

This document is generated from the answer store. Correct it by correcting the interview, not by editing this file.

## Recorded for this plan


**Each period when failing over costs more than the outage, and who decides during it**

| period | why | who_decides |
| --- | --- | --- |
| Period close | not stated in the reference plan in terms of what it costs; the plan states the rule as no cross-region failover during close unless the business explicitly accepts it, and requires the close-reconciliation checklist if it is forced | The CFO or their delegate, whose sign-off is mandatory |
| An open EBS online patching cycle | If an online patching cycle is open when disaster strikes, the failover runbook has to take an abort and filesystem-clone branch, and an open cycle is fixed after service is restored rather than during the outage | not stated in the reference plan |

- **Who may authorize a failover inside a freeze period, and on what evidence**: The CFO or their delegate, and that decision is theirs alone: sign-off is mandatory before any cross-region failover during period close, and the pre-failover precheck carries the line as not in period close, or Finance has signed off. What the CFO has to be shown before saying yes is not stated in the reference plan.

## 4.2.1 Activation Criteria and Procedure

- **The single individual with declaration authority, and their named deputy**: The DR Commander, and that decision only: the same document is explicit that the Commander declares and the DR Coordinator recovers, because the person weighing the repair estimate against the remaining budget should not also be running the storage sequence. One person holds declaration authority at any moment. The Deputy DR Commander is the named alternate and the plan is careful that they are not a second decision-maker but the same box when the first is silent. The business owner is consulted if reachable within fifteen minutes and the gate does not wait beyond that, and the declaration does not wait for the change advisory board.

## Recorded for this plan

- **The time budget for the declaration decision**: 10
- **How the point of no return is calculated rather than what it is today**: Computed from what is left of the budget, explicitly not a fixed number of hours. The rule is that estimated repair time greater than the remaining tolerable downtime means declare, where remaining means the tier's tolerable downtime minus the time already elapsed on the gate minus the roughly sixty-minute failover recovery time, and not a flat two-hour figure. The plan states the counterpart out loud, that the gate exists to be used and that one should not wait for certainty, and it requires the DR Commander to be able to state the rule from memory in a closed-book assessment.
- **What happens to downstream processing when the recovery point was missed**: Downstream processing stays stopped. If the recovery point is breached the Concurrent Managers stay down until Finance clears them, because automated batch processing on incomplete data is far harder to unwind than a longer outage. The decision to proceed when data loss exceeds the tier recovery point belongs to the business owner together with the CFO delegate and their involvement is mandatory. Finance convenes before any batch processing runs, and clearing the Concurrent Managers is a Finance duty rather than a DBA or functional one, though the EBS functional lead is the role that actually starts them, last, and not at all after a breach until Finance has cleared it. The rule appears in four separate documents including both closed-book role cards, which is what makes it a decision taken in daylight rather than at speed.

## References

Sources for every value above, as recorded when the value was given.

- **Each period when failing over costs more than the outage, and who decides during it**, recorded by document:oci-itscp/checklists/dr-authority-matrix.md
- **Who may authorize a failover inside a freeze period, and on what evidence**, recorded by document:oci-itscp/checklists/dr-authority-matrix.md
- **The single individual with declaration authority, and their named deputy**, recorded by document:oci-itscp/checklists/dr-authority-matrix.md
- **The time budget for the declaration decision**, recorded by document:oci-itscp/checklists/outage-assessment.md; mechanism: Ten minutes end to end, phased: reachability triage in the first minute, evidence capture running in parallel through minute four, blast radius from two to six, the estimate with a confidence band from five to eight, and the hand-off to the DR Commander and the gate decision from eight to ten. What is happening to the outage meanwhile is that the budget is being spent at a known rate against an unknown duration, and the clock does not stop while succession runs, so ten minutes spent failing to reach the Commander is ten minutes of the tolerable downtime. Overrunning the budget is itself an input: if no estimate exists by minute eight, the estimate is unknown and the unknown rule applies.
- **How the point of no return is calculated rather than what it is today**, recorded by document:oci-itscp/checklists/dr-authority-matrix.md
- **What happens to downstream processing when the recovery point was missed**, recorded by document:oci-itscp/checklists/dr-authority-matrix.md

### Unverified statements

Engineering judgements, outstanding gaps and disagreements, labeled as such.

Every value in this document is traceable to a recorded source.
