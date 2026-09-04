# Contact roster

Who is called, in what order, and on what bridge.

This document is generated from the answer store. Correct it by correcting the interview, not by editing this file.

## 3.2 Notification

- **The call tree, its order, and the unreachable procedure**: Each box calls the boxes below it and only those; nobody telephones the whole roster. The first responder, infrastructure or DBA on-call, detects and escalates to the DR Commander, who runs the decision gate and declares, with the Deputy taking the tree if the Commander is unreachable. The Commander then calls the DR Coordinator as technical execution lead and the business owner, who is consulted within fifteen minutes and not waited for beyond it. The Coordinator calls the Infra Manager, the DBA on-call and the EBS functional lead. The Infra Manager calls infrastructure on-call, network on-call and FinOps, who are notified rather than consulted. The DBA calls a second DBA and Oracle Support at severity one. The functional lead calls their alternate and the interface partner contacts. The business owner calls the CFO delegate, mandatory during period close or after a recovery-point breach, and Risk. When somebody does not pick up: try cell, then work, then home, leaving a voicemail at each that states the bridge details and that this is a DR notification and nothing more. Move on after five minutes without a spoken or typed acknowledgement and ring the alternate, who then holds the position for the duration rather than handing it back mid-runbook. If both primary and alternate are silent after ten minutes the branch collapses upward: the caller takes over that box's list, continues down the tree, and tells the Commander which position is unfilled. Email and chat do not count as reached, because there is no way to ensure receipt and acknowledgement. Log every attempt with time, number tried and outcome.

## Recorded for this plan

- **The incident bridge and its dependencies**: **[MISSING — owner: DR process owner]**

## APPENDIX A PERSONNEL CONTACT LIST

- **Each role, who holds it, how they are reached and when that was last verified**: **[MISSING — owner: DR process owner]**

## APPENDIX B VENDOR CONTACT LIST


**Each vendor, what they supply, how they are reached and the reference they need**

| organization | what_they_supply | reached_by | reference_to_quote |
| --- | --- | --- | --- |
| Oracle Support, severity one | Support on the database and application stack during an incident | a fictitious placeholder in the reference plan | A customer support identifier and a service-request template pre-registered against the primary and standby databases; the identifier itself is a fictitious placeholder in the reference plan |
| The cloud account team | Capacity and platform escalation, and the destination for procurement escalation because no procurement team is staffed for this plan | a fictitious placeholder in the reference plan | The tenancy name, itself a fictitious placeholder in the reference plan |
| The bank payment-file interchange partner | The outbound payment-file interchange, replayed from the ledger during work recovery | a fictitious placeholder in the reference plan | An interface identifier, itself a fictitious placeholder in the reference plan |


## Recorded for this plan

- **Each external party, what their contract obliges, how fast, and where the contract is held**: **[MISSING — owner: governance/risk contact]**

## 5.5 Notifications (users)

- **How users are told service is restored, by whom and what the message must carry**: A service-restored notice goes to users, the business owner, and every interconnected partner who was told during activation, sent through the call tree and partner contact lists rather than through the recovered environment, and the exit checklist will not close until it has gone. What the message has to carry is not stated in the reference plan: the reference plan has a what-to-say table and it belongs to the activation notification, covering the nature of the outage, the repair estimate, the runbook step and the bridge details. There is no restoration template, nobody is named as drafting it, and the warning about possibly duplicated workflow notifications appears only as a work-recovery task and not as something the restoration message must repeat to users.

## References

Sources for every value above, as recorded when the value was given.

- **The call tree, its order, and the unreachable procedure**, recorded by document:oci-itscp/checklists/contact-roster.md
- **Each vendor, what they supply, how they are reached and the reference they need**, recorded by document:oci-itscp/checklists/contact-roster.md
- **How users are told service is restored, by whom and what the message must carry**, recorded by document:oci-itscp/docs/10-phase-reconstitution.md

### Unverified statements

Engineering judgments, outstanding gaps and disagreements, labeled as such.

- **The incident bridge and its dependencies**: **[MISSING — owner: DR process owner]**
- **Each role, who holds it, how they are reached and when that was last verified**: **[MISSING — owner: DR process owner]**
- **Each external party, what their contract obliges, how fast, and where the contract is held**: **[MISSING — owner: governance/risk contact]**
