# Tier assignment workshop

The session that turns business impact into a recovery tier.

This document is generated from the answer store. Correct it by correcting the interview, not by editing this file.

## 3.2.1 Determine Business Processes and Recovery Criticality


**Each business process and what its outage costs at one hour, four hours, a day and a week**

| name | impact_1h | impact_4h | impact_1d | impact_1w |
| --- | --- | --- | --- | --- |
| Order entry and booking | not stated in the reference plan | not stated in the reference plan | not stated in the reference plan | not stated in the reference plan |
| Shipping and fulfilment | not stated in the reference plan | not stated in the reference plan | not stated in the reference plan | not stated in the reference plan |
| AP payment runs | not stated in the reference plan | not stated in the reference plan | not stated in the reference plan | not stated in the reference plan |
| AR cash application | not stated in the reference plan | not stated in the reference plan | not stated in the reference plan | not stated in the reference plan |
| GL and period close | not stated in the reference plan | not stated in the reference plan | not stated in the reference plan | not stated in the reference plan |
| Procurement | not stated in the reference plan | not stated in the reference plan | not stated in the reference plan | not stated in the reference plan |
| Payroll and HR self-service | not stated in the reference plan | not stated in the reference plan | not stated in the reference plan | not stated in the reference plan |
| Reporting and BI | not stated in the reference plan | not stated in the reference plan | not stated in the reference plan | not stated in the reference plan |
| Partner and EDI integrations | not stated in the reference plan | not stated in the reference plan | not stated in the reference plan | not stated in the reference plan |


## 3.2.3 Identify System Resource Recovery Priorities


**Each business process, the tier it is assigned to, and the argument for it**

| process | tier | rationale |
| --- | --- | --- |
| Core financials: GL, AP, AR and FA; Order Management and Inventory transactions; the EBS database itself | 0 | Revenue-recognition and cash-application paths. Data loss is not recoverable by re-keying. |
| Full production application tier: Concurrent Managers, Workflow, Workflow Mailer, iProcurement, self-service HR, integration endpoints | 1 | The business can absorb a few hours; most work re-queues rather than being lost. |
| Visualization, BI and reporting tier, ad-hoc analytics, data extracts, non-critical inbound integrations | 2 | Reporting can wait a day. If the BI tier reads the Active Data Guard standby it is effectively available first. |
| Non-production: Dev, Test, UAT and sandbox clones; archive and long-tail file shares | 3 | Rebuild from backup. Do not pay for warm capacity here. |


## References

Sources for every value above, as recorded when the value was given.

- **Each business process and what its outage costs at one hour, four hours, a day and a week**, recorded by document:oci-itscp/checklists/tier-assignment-workshop.md
- **Each business process, the tier it is assigned to, and the argument for it**, recorded by document:oci-itscp/docs/02-mtd-tiers.md

### Unverified statements

Engineering judgements, outstanding gaps and disagreements, labelled as such.

Every value in this document is traceable to a recorded source.
