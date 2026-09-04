# Cost and teardown

What the standby posture costs and what changing it costs.

This document is generated from the answer store. Correct it by correcting the interview, not by editing this file.

## Recorded for this plan

- **The monthly standby cost floor**: **[MISSING — owner: infrastructure owner]**
- **Storage features that constrain what the standby may be built on**: One feature decides what the standby may be built on. The plan assumes the database does not use Hybrid Columnar Compression, and records that if it does, the standby storage must be Exadata, Oracle ZFS Storage Appliance or Pillar Axiom FS1, so the cheap non-Exadata standby is ruled out. It ships a check to run before sizing the standby and says to run it first. It also marks as unverified whether compressed data actually becomes unreadable on unsupported storage, and tells the reader to validate before assuming the downgrade path is closed. Two licensing constraints sit alongside: redo transport compression on the Phoenix leg needs the Advanced Compression option, and real-time apply with a readable standby needs the Active Data Guard option.

## Supplied by the toolkit's method

A standby is held in one of a small number of postures, and the posture is a decision about cost against readiness rather than a property of the estate. The toolkit asks what is done to the standby when nothing is happening, what is done when there is warning, and who may change it. A posture nobody may change is a cost nobody may reduce; a posture anybody may change is a recovery nobody can rely on.

- **The standby's steady-state posture and who may change it**: Warm is the steady state: Phoenix compute stopped, the Exadata VM cluster held at its OCPU floor, and all replication running. The governing rule is stated as tearing down compute and never tearing down replication, and the BI node is the exception to stopped, always on and reading the standby, which is what keeps the standby continuously proven. Hot exists for the days when there is warning, a storm track or an announced regional maintenance window. Drill is a third posture for a non-disruptive exercise. Who may change it is written down: moving warm to hot is the infrastructure on-call with the DR Coordinator as deputy and FinOps notified; moving hot back to warm is the DR Coordinator with the Infra Manager as deputy; deleting replication needs the Infra Manager and the risk function, both in writing; and scaling the Exadata cluster below its OCPU floor may be done by nobody, because the tooling refuses it.

## Recorded for this plan


**Each optional feature the design needs, whether it is licensed and where that is recorded**

| feature | licensed | where_it_is_recorded |
| --- | --- | --- |
| Oracle Active Data Guard, for real-time apply and a readable standby, and for a Far Sync instance if one is ever used | nobody knows | not stated in the reference plan |
| Oracle Advanced Compression, for Data Guard redo transport compression on the Phoenix leg | nobody knows | not stated in the reference plan |
| Real-time redo transport to the backup service, which the plan records as an extra-cost option | nobody knows | not stated in the reference plan |
| EBS entitlement for a snapshot standby opened read-write each quarter for the drill | nobody knows | not stated in the reference plan |


## References

Sources for every value above, as recorded when the value was given.

- **Storage features that constrain what the standby may be built on**, recorded by document:oci-itscp/docs/01-architecture.md
- **The standby's steady-state posture and who may change it**, recorded by document:oci-itscp/runbooks/RB-05-replication-lifecycle.md
- **Each optional feature the design needs, whether it is licensed and where that is recorded**, recorded by document:oci-itscp/checklists/cost-model-template.md

### Unverified statements

Engineering judgements, outstanding gaps and disagreements, labelled as such.

- **The monthly standby cost floor**: **[MISSING — owner: infrastructure owner]**
