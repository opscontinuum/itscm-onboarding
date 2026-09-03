# Coverage map — every ISCP section, the skill that elicits it, the file it lands in

The authoritative list of what a complete plan contains. `itscp-build` reports against this
table and `itscp-audit` checks it. If a row has no skill, the toolkit does not yet cover it
and says so rather than quietly producing an incomplete plan.

Structure follows NIST SP 800-34 Rev. 1 Appendix A (Sample ISCP Templates) and §4.1–§4.5.

---

## Front matter

| ISCP element | Elicited by | Written to |
|---|---|---|
| Plan Approval statement | `itscp-interview-governance` | `docs/00-plan-approval.md` |
| Record of Changes | `itscp-build` (from git log) | `docs/00-record-of-changes.md` |

## 1. Introduction

| ISCP element | Elicited by | Written to |
|---|---|---|
| 1.1 Background — why the plan exists, its objectives | `itscp-interview-governance` | `README.md`, `docs/00-plan-approval.md` |
| 1.2 Scope — FIPS 199 impact level, RTOs, alternate site and storage | `itscp-interview-governance` + `itscp-interview-business` | `README.md`, `docs/02-mtd-tiers.md` |
| 1.3 Assumptions — including what is explicitly *not* covered | `itscp-interview-infrastructure` | `docs/01-architecture.md` §1 |

## 2. Concept of Operations

| ISCP element | Elicited by | Written to |
|---|---|---|
| 2.1 System description — architecture, locations, I/O and architecture diagrams | `itscp-interview-application` + `itscp-discover` | `docs/01-architecture.md` §2 |
| 2.2 Overview of the three phases | `itscp-build` (renders from the runbook set) | `docs/08`, `docs/09`, `docs/10` |
| 2.3 Roles and responsibilities — team structure, hierarchy, coordination | `itscp-interview-continuity` | `checklists/roles-and-responsibilities.md` |

## 3. Activation and Notification

| ISCP element | Elicited by | Written to |
|---|---|---|
| 3.1 Activation criteria and procedure; who may activate | `itscp-interview-continuity` | `runbooks/RB-02-failover.md` §0, `checklists/dr-authority-matrix.md` |
| 3.2 Notification — call tree, methods, unreachable procedure | `itscp-interview-continuity` | `checklists/contact-roster.md` |
| 3.3 Outage assessment — procedure and the repair estimate | `itscp-interview-continuity` | `checklists/outage-assessment.md` |

## 4. Recovery

| ISCP element | Elicited by | Written to |
|---|---|---|
| 4.1 Sequence of recovery activities, ordered by BIA priority | `itscp-interview-infrastructure` | `runbooks/RB-01`, `RB-02`, `docs/09` §3 |
| 4.2 Recovery procedures — step by step, nothing assumed | `itscp-interview-infrastructure` + `itscp-interview-application` | `runbooks/`, `scripts/` |
| 4.3 Recovery escalation and notification — triggers and thresholds | `itscp-interview-continuity` | `docs/09` §5 |

## 5. Reconstitution

| ISCP element | Elicited by | Written to |
|---|---|---|
| 5.1 Concurrent processing (or a stated reason it is not performed) | `itscp-interview-application` | `docs/10` §3 |
| 5.2 Validation data testing | `itscp-interview-application` | `docs/10` §3, `runbooks/RB-01` §5 |
| 5.3 Validation functionality testing — the business's own pass list | `itscp-interview-business` | `docs/10` §3, validation pack |
| 5.4 Recovery declaration | `itscp-interview-continuity` | `docs/10` §4.2 |
| 5.5 User notification | `itscp-interview-continuity` | `checklists/contact-roster.md` |
| 5.6 Cleanup | `itscp-interview-infrastructure` | `docs/10` §4, `runbooks/RB-05` |
| 5.7 Offsite data storage (or stated not applicable) | `itscp-interview-infrastructure` | `docs/10` §4 |
| 5.8 Data backup after reconstitution | `itscp-interview-infrastructure` | `docs/10` §4.1 |
| 5.9 Event documentation and after-action report | `itscp-interview-governance` | `evidence/`, after-action template |
| 5.10 Deactivation | `itscp-interview-continuity` | `docs/10` §4.2 |

## Appendices

| ISCP appendix | Elicited by | Written to |
|---|---|---|
| A. Personnel contact information | `itscp-interview-continuity` | `checklists/contact-roster.md` §2 |
| B. Vendor contacts, offsite storage and alternate site POCs | `itscp-interview-infrastructure` | `checklists/contact-roster.md` §5 |
| C. Alternate site, storage and telecommunications | `itscp-interview-infrastructure` | `docs/01` §5, `docs/03` |
| D. Detailed recovery procedures and checklists | `itscp-interview-infrastructure` | `runbooks/`, `checklists/pre-failover-precheck.md` |
| E. Alternate mission/business processing — manual workarounds | `itscp-interview-business` | `checklists/manual-workarounds.md` |
| F. System validation test plan | `itscp-interview-application` | `checklists/validation-pack.md` |
| G. Diagrams — architecture and I/O | `itscp-discover` + `itscp-interview-infrastructure` | `docs/01` §2, `docs/diagrams/` |
| H. Hardware, software and firmware inventory | `itscp-discover` | `docs/11-inventory.md` |
| I. System interconnections | `itscp-discover` + `itscp-interview-application` | `docs/12-interconnections.md` |
| J. Test, training and exercise documentation | `itscp-interview-governance` | `checklists/contingency-training.md`, `runbooks/RB-04` |
| K. Business impact analysis | `itscp-interview-business` | `docs/02-mtd-tiers.md`, `checklists/tier-assignment-workshop.md` |
| L. Vendor SLAs and reciprocal agreements | `itscp-interview-governance` | `checklists/contact-roster.md` §5 |

---

## Beyond NIST

Not required by SP 800-34, included because the reference repository demonstrates their value
and because auditors working to ISO 22301 ask for them.

| Element | Elicited by | Written to | Why |
|---|---|---|---|
| Minimum business continuity objective per tier | `itscp-interview-business` | `docs/02-mtd-tiers.md` | MTD says *when* service returns; MBCO says *how much of it* is acceptable meanwhile |
| Risk register | `itscp-interview-governance` | `checklists/risk-register.md` | Material assumptions and design risks, owned and reviewed rather than scattered |
| Plan review and maintenance cadence | `itscp-interview-governance` | `README.md` | Continuity plans decay; nothing else states when this one is reviewed |
| Cost model and posture economics | `itscp-interview-infrastructure` | `docs/05-cost-and-teardown.md` | Standby cost drives the tier the business can actually have |
| Citation and unverified-statement discipline | every skill | every document | The property that makes a generated plan auditable |

---

## Not yet covered

Stated so the toolkit does not imply completeness it lacks.

| Gap | Consequence |
|---|---|
| No elicitation for platform types other than Oracle EBS on OCI | The runbook templates assume Oracle Data Guard and OCI replication primitives. Other stacks get the structure but must supply their own procedures |
| No automated import of an existing plan | An organisation with a plan in Word starts from interviews, not from its own document |
| Discovery covers OCI only | AWS, Azure, GCP and on-premises inventories are manual |
