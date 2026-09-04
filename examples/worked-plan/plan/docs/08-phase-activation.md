# Phase one: activation and notification

How an incident becomes a declared disaster, and who is told.

This document is generated from the answer store. Correct it by correcting the interview, not by editing this file.

## Recorded for this plan


**Each period when failing over costs more than the outage, and who decides during it**

| period | why | who_decides |
| --- | --- | --- |
| Period close | not stated in the reference plan in terms of what it costs; the plan states the rule as no cross-region failover during close unless the business explicitly accepts it, and requires the close-reconciliation checklist if it is forced | The CFO or their delegate, whose sign-off is mandatory |
| An open EBS online patching cycle | If an online patching cycle is open when disaster strikes, the failover runbook has to take an abort and filesystem-clone branch, and an open cycle is fixed after service is restored rather than during the outage | not stated in the reference plan |

- **Who owns the disclosure clock when the cause is an attack, and how fast it runs**: **[MISSING — owner: governance/risk contact]**

## References

Sources for every value above, as recorded when the value was given.

- **Each period when failing over costs more than the outage, and who decides during it**, recorded by document:oci-itscp/checklists/dr-authority-matrix.md

### Unverified statements

Engineering judgements, outstanding gaps and disagreements, labelled as such.

- **Who owns the disclosure clock when the cause is an attack, and how fast it runs**: **[MISSING — owner: governance/risk contact]**
