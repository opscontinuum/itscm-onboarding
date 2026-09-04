# Risk register

The accepted risks to this plan, each with an owner and a review date.

This document is generated from the answer store. Correct it by correcting the interview, not by editing this file.

## 1.3 Assumptions


**Each stated assumption, what breaks if it is wrong, who confirms it and by when**

| assumption | impact_if_wrong | owner | confirm_by |
| --- | --- | --- | --- |
| A1: EBS 12.2.x, with the dual filesystem fs1 and fs2, WebLogic based | MATERIAL. 12.1 removes the online-patching filesystem split and simplifies the dual-filesystem design | not stated in the reference plan | not stated in the reference plan |
| A2: the database is 19c on Exadata Database Service on Dedicated Infrastructure, not Cloud at Customer | MATERIAL. Cloud at Customer changes networking, Data Guard setup, and Full Stack DR member support | not stated in the reference plan | not stated in the reference plan |
| A3: the EBS application tier runs on Windows Server x64, relinked with MKS Toolkit | Affects the script language, which is PowerShell, and the shared filesystem mount strategy | not stated in the reference plan | not stated in the reference plan |
| A4: visualization tier means the BI or reporting presentation layer | MATERIAL. If it means virtualization, that tier's design is replaced by one based on OCI VMware Solution | not stated in the reference plan | not stated in the reference plan |
| A5: the database does not use Hybrid Columnar Compression | If it does, the standby storage must be Exadata, Oracle ZFS Storage Appliance, or Pillar Axiom FS1. Whether compressed data becomes unreadable on unsupported storage is unverified | not stated in the reference plan | not stated in the reference plan |
| A6: cross-region traffic rides a Dynamic Routing Gateway and a Remote Peering Connection over the OCI backbone, not FastConnect and not the public internet | Changes the bandwidth guarantee and the redo transport tuning. No bandwidth guarantee or service level for the peering link was verified in this revision | not stated in the reference plan | not stated in the reference plan |
| A7: a single production EBS instance, with no multi-org split across regions | A multi-instance estate changes the tiering map | not stated in the reference plan | not stated in the reference plan |


## Recorded for this plan

- **Each external party, what their contract obliges, how fast, and where the contract is held**: **[MISSING — owner: governance/risk contact]**
- **Each material assumption or design risk, its owner and its review date**: **[MISSING — owner: governance/risk contact]**

## References

Sources for every value above, as recorded when the value was given.

- **Each stated assumption, what breaks if it is wrong, who confirms it and by when**, recorded by document:oci-itscp/docs/01-architecture.md

### Unverified statements

Engineering judgements, outstanding gaps and disagreements, labelled as such.

- **Each external party, what their contract obliges, how fast, and where the contract is held**: **[MISSING — owner: governance/risk contact]**
- **Each material assumption or design risk, its owner and its review date**: **[MISSING — owner: governance/risk contact]**
