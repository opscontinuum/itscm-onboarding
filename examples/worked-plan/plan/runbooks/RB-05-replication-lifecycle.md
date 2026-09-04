# RB-05 Replication lifecycle

Building, holding and tearing down the standby posture.

This document is generated from the answer store. Correct it by correcting the interview, not by editing this file.

## Supplied by the toolkit's method

A standby is held in one of a small number of postures, and the posture is a decision about cost against readiness rather than a property of the environment. The toolkit asks what is done to the standby when nothing is happening, what is done when there is warning, and who may change it. A posture nobody may change is a cost nobody may reduce; a posture anybody may change is a recovery nobody can rely on.

- **The standby's steady-state posture and who may change it**: Warm is the steady state: Phoenix compute stopped, the Exadata VM cluster held at its OCPU floor, and all replication running. The governing rule is stated as tearing down compute and never tearing down replication, and the BI node is the exception to stopped, always on and reading the standby, which is what keeps the standby continuously proven. Hot exists for the days when there is warning, a storm track or an announced regional maintenance window. Drill is a third posture for a non-disruptive exercise. Who may change it is written down: moving warm to hot is the infrastructure on-call with the DR Coordinator as deputy and FinOps notified; moving hot back to warm is the DR Coordinator with the Infra Manager as deputy; deleting replication needs the Infra Manager and the risk function, both in writing; and scaling the Exadata cluster below its OCPU floor may be done by nobody, because the tooling refuses it.

## Recorded for this plan

- **How long it takes to move the standby to its warned state**: **[MISSING — owner: infrastructure owner]**

## References

Sources for every value above, as recorded when the value was given.

- **The standby's steady-state posture and who may change it**, recorded by document:oci-itscp/runbooks/RB-05-replication-lifecycle.md

### Unverified statements

Engineering judgements, outstanding gaps and disagreements, labeled as such.

- **How long it takes to move the standby to its warned state**: **[MISSING — owner: infrastructure owner]**
