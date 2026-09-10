# Every field, and where it lands

> **Generated file.** It is assembled from the skills, the question bank and `GETTING-STARTED.md` by `plugin/itscp_manual.py`, and an edit made here is deleted by the next regeneration. Change the source and run `python3 plugin/itscp_manual.py`.

The 82 fields of the starter plan, listed twice: by the file each one is written into, which is the order phase 6 assembles in, and then as a flat index. A field feeding two files appears under both.

---

## By file

### `README.md`

| Field | Records | Owner |
|---|---|---|
| `system.business_name` | The business-facing name for the same system | business owner |
| `system.categorization` | The impact level or data classification and where it is recorded | governance/risk contact |
| `system.impact_level` | The assigned availability impact level, which selects the template this plan is graded against | governance/risk contact |
| `governance.review_cadence` | Review frequency, the triggers, and the owner of the review | governance/risk contact |
| `governance.finding_to_change_route` | The route from a drill finding to a change in the plan | governance/risk contact |
| `governance.associated_plans` | Each related plan, who owns it and how it relates to this one | governance/risk contact |

### `checklists/contact-roster.md`

| Field | Records | Owner |
|---|---|---|
| `continuity.call_tree` | The call tree, its order, and the unreachable procedure | DR process owner |
| `continuity.bridge` | The incident bridge and its dependencies | DR process owner |
| `continuity.contact_roster` | Each role, who holds it, how they are reached and when that was last verified | DR process owner |
| `continuity.vendor_contacts` | Each vendor, what they supply, how they are reached and the reference they need | DR process owner |
| `continuity.vendor_obligations` | Each external party, what their contract obliges, how fast, and where the contract is held | governance/risk contact |
| `continuity.user_notification` | How users are told service is restored, by whom and what the message must carry | DR process owner |

### `checklists/contingency-training.md`

| Field | Records | Owner |
|---|---|---|
| `governance.training_program` | The training program, distinct from the drill program | governance/risk contact |

### `checklists/dr-authority-matrix.md`

| Field | Records | Owner |
|---|---|---|
| `business.freeze_periods` | Each period when failing over costs more than the outage, and who decides during it | business owner |
| `business.freeze_override_authority` | Who may authorize a failover inside a freeze period, and on what evidence | business owner |
| `continuity.declaration_authority` | The single individual with declaration authority, and their named deputy | DR process owner |
| `continuity.decision_time_budget` | The time budget for the declaration decision | DR process owner |
| `continuity.declaration_threshold_rule` | How the point of no return is calculated rather than what it is today | DR process owner |
| `continuity.data_loss_gate` | What happens to downstream processing when the recovery point was missed | DR process owner |

### `checklists/manual-workarounds.md`

| Field | Records | Owner |
|---|---|---|
| `business.workarounds` | Each process, the workaround used, and how long it is sustainable | business owner |
| `business.reconstruction_effort` | How long rebuilding the lost work takes, and who does it | business owner |

### `checklists/outage-assessment.md`

| Field | Records | Owner |
|---|---|---|
| `continuity.unknown_estimate_default` | The default action when the repair estimate is unknown | DR process owner |
| `continuity.assessment_procedure` | The outage assessment procedure and where the repair estimate comes from | DR process owner |
| `continuity.assessment_calibration` | How long this organization actually takes to produce a repair estimate | DR process owner |

### `checklists/risk-register.md`

| Field | Records | Owner |
|---|---|---|
| `system.assumptions` | Each stated assumption, what breaks if it is wrong, who confirms it and by when | lead engineer |
| `continuity.vendor_obligations` | Each external party, what their contract obliges, how fast, and where the contract is held | governance/risk contact |
| `governance.risk_register` | Each material assumption or design risk, its owner and its review date | governance/risk contact |

### `checklists/roles-and-responsibilities.md`

| Field | Records | Owner |
|---|---|---|
| `continuity.succession` | The ordered line of succession and what each hand-off waits for | DR process owner |
| `continuity.decision_and_recovery_roles` | Each duty in a recovery, the role that holds it and the deputy behind them | DR process owner |
| `continuity.people_unavailable` | Who could execute the plan if the disruption also removed the primary team | DR process owner |
| `governance.breach_disclosure_clock` | Who owns the disclosure clock when the cause is an attack, and how fast it runs | governance/risk contact |

### `checklists/tier-assignment-workshop.md`

| Field | Records | Owner |
|---|---|---|
| `business.processes` | Each business process and what its outage costs at one hour, four hours, a day and a week | business owner |
| `business.tier_assignment` | Each business process, the tier it is assigned to, and the argument for it | business owner |

### `checklists/validation-pack.md`

| Field | Records | Owner |
|---|---|---|
| `app.validation_pack` | Each validation check, its duration and its owner | application owner |
| `app.validation_data_tests` | Each data validation check, what it proves and who signs it off | application owner |

### `docs/00-plan-approval.md`

| Field | Records | Owner |
|---|---|---|
| `system.business_name` | The business-facing name for the same system | business owner |
| `governance.signing_authority` | The signatory and the alternate signatory | signing authority |
| `governance.plan_custody` | Where the approved plan is held, and where it is held when the environment is unavailable | signing authority |

### `docs/00-record-of-changes.md`

| Field | Records | Owner |
|---|---|---|
| `governance.event_documentation` | How a real event is written up, by whom, and where the record goes | governance/risk contact |

### `docs/01-architecture.md`

| Field | Records | Owner |
|---|---|---|
| `system.name` | The system's technical name, as the plan's title and throughout | application owner |
| `system.assumptions` | Each stated assumption, what breaks if it is wrong, who confirms it and by when | lead engineer |
| `system.component_terms` | The words this organization uses for its own components, and what each one means | application owner |
| `system.releases` | The release of each major component, and any upgrade in flight | application owner |
| `system.operating_systems` | The operating system of each tier, and what that constrains | infrastructure owner |
| `system.instances` | Whether the production environment is one instance or several, and how they are split | application owner |
| `infra.primary_region` | The primary region | infrastructure owner |
| `infra.standby_region` | The standby region | infrastructure owner |
| `infra.region_locked_naming` | Which names are region-locked and what changing them costs in recovery time | infrastructure owner |
| `infra.availability_domains` | The availability domains in use, and where any arbitrator sits | infrastructure owner |
| `infra.inter_region_transport` | How the two regions are joined and what is committed in writing | infrastructure owner |
| `infra.shared_storage` | What lives on shared storage and how it is reached | infrastructure owner |

### `docs/02-mtd-tiers.md`

| Field | Records | Owner |
|---|---|---|
| `system.categorization` | The impact level or data classification and where it is recorded | governance/risk contact |
| `system.impact_level` | The assigned availability impact level, which selects the template this plan is graded against | governance/risk contact |
| `system.instances` | Whether the production environment is one instance or several, and how they are split | application owner |
| `business.processes` | Each business process and what its outage costs at one hour, four hours, a day and a week | business owner |
| `business.mtd.tier0` | Maximum tolerable downtime for the tier 0 processes | business owner |
| `business.rpo.tier0` | Recovery point objective for the tier 0 processes | business owner |
| `business.mbco.tier0` | The minimum service level that must be available during work recovery | business owner |
| `business.tier_signoff` | Whether the tier assignment is signed, and by whom, or who owes it | business owner |
| `business.tier_targets` | Per tier: maximum tolerable downtime, recovery time, work recovery time, recovery point and the minimum service that counts as trading | business owner |
| `business.tier_assignment` | Each business process, the tier it is assigned to, and the argument for it | business owner |
| `business.reconstruction_effort` | How long rebuilding the lost work takes, and who does it | business owner |

### `docs/03-replication-matrix.md`

| Field | Records | Owner |
|---|---|---|
| `infra.standby_region` | The standby region | infrastructure owner |
| `infra.measured_rtt_ms` | Measured inter-region round-trip time in milliseconds | lead engineer |
| `infra.replication` | Per tier: the replication mechanism, whether it is synchronous, measured lag, failover behavior, whether reversal needs a re-baseline, and whether it is one-way | infrastructure owner |
| `infra.storage_constraints` | Storage features that constrain what the standby may be built on | lead engineer |
| `infra.irreversible_choices` | Each decision that cannot be cheaply reversed, what reversing it costs and who may take it | lead engineer |
| `infra.offsite_storage` | Each backup copy, where it is held, how long it is kept and how it is retrieved | infrastructure owner |
| `infra.post_recovery_backup` | How the recovered system is protected again, when, and who confirms it | infrastructure owner |

### `docs/04-monitoring.md`

| Field | Records | Owner |
|---|---|---|
| `infra.silent_failures` | The failures this environment does not notice, and what would have shown them | lead engineer |

### `docs/05-cost-and-teardown.md`

| Field | Records | Owner |
|---|---|---|
| `infra.standby_cost_floor` | The monthly standby cost floor | infrastructure owner |
| `infra.storage_constraints` | Storage features that constrain what the standby may be built on | lead engineer |
| `infra.standby_posture` | The standby's steady-state posture and who may change it | infrastructure owner |
| `infra.licensing` | Each optional feature the design needs, whether it is licensed and where that is recorded | infrastructure owner |

### `docs/06-test-environments.md`

| Field | Records | Owner |
|---|---|---|
| `governance.drill_levels` | Each exercise level, what it proves and what it does not | governance/risk contact |

### `docs/07-standards-alignment.md`

| Field | Records | Owner |
|---|---|---|
| `system.impact_level` | The assigned availability impact level, which selects the template this plan is graded against | governance/risk contact |
| `governance.associated_plans` | Each related plan, who owns it and how it relates to this one | governance/risk contact |
| `governance.availability_boundary` | Where day-to-day availability ends and continuity begins, and who owns each side | governance/risk contact |

### `docs/08-phase-activation.md`

| Field | Records | Owner |
|---|---|---|
| `business.freeze_periods` | Each period when failing over costs more than the outage, and who decides during it | business owner |
| `governance.breach_disclosure_clock` | Who owns the disclosure clock when the cause is an attack, and how fast it runs | governance/risk contact |

### `docs/09-phase-recovery.md`

| Field | Records | Owner |
|---|---|---|
| `app.start_order` | The component start order and what depends on what | lead engineer |
| `app.reconfiguration_duration` | How long a full application-tier reconfiguration takes, measured | lead engineer |
| `continuity.escalation_thresholds` | The escalation thresholds, each observable | DR process owner |

### `docs/10-phase-reconstitution.md`

| Field | Records | Owner |
|---|---|---|
| `app.wrt_activities` | Each work-recovery activity, its duration, and whether it runs in parallel with bring-up | application owner |
| `app.concurrent_processing` | Whether concurrent processing is performed, and the reason either way | application owner |
| `app.validation_data_tests` | Each data validation check, what it proves and who signs it off | application owner |
| `app.unsafe_reruns` | Each scheduled job, whether it is safe to resubmit, and what a second run does | application owner |
| `infra.post_recovery_backup` | How the recovered system is protected again, when, and who confirms it | infrastructure owner |
| `continuity.deactivation_authority` | Who may deactivate the plan and on what evidence | DR process owner |
| `continuity.recovery_declaration` | Who declares recovery complete and the evidence they need first | DR process owner |
| `continuity.user_notification` | How users are told service is restored, by whom and what the message must carry | DR process owner |
| `continuity.cleanup` | What is dismantled after the event, and who is responsible for each of it | DR process owner |

### `docs/11-inventory.md`

| Field | Records | Owner |
|---|---|---|
| `system.releases` | The release of each major component, and any upgrade in flight | application owner |
| `system.operating_systems` | The operating system of each tier, and what that constrains | infrastructure owner |
| `discovery.completed` | Whether a discovery walk has run, and when | infrastructure owner |

### `docs/12-interconnections.md`

| Field | Records | Owner |
|---|---|---|
| `app.interconnections` | Each interconnection, its direction, transport, contact and whether it is replayable | application owner |
| `app.interface_landing` | Where inbound interface data lands today and whether that location is replicated | lead engineer |

### `runbooks/RB-01-switchover.md`

| Field | Records | Owner |
|---|---|---|
| `app.start_order` | The component start order and what depends on what | lead engineer |
| `app.recovery_procedures` | The recovery procedure at the level of what is actually typed, in order | lead engineer |
| `app.reconfiguration_duration` | How long a full application-tier reconfiguration takes, measured | lead engineer |

### `runbooks/RB-02-failover.md`

| Field | Records | Owner |
|---|---|---|
| `app.recovery_procedures` | The recovery procedure at the level of what is actually typed, in order | lead engineer |
| `app.unsafe_reruns` | Each scheduled job, whether it is safe to resubmit, and what a second run does | application owner |
| `continuity.declaration_authority` | The single individual with declaration authority, and their named deputy | DR process owner |
| `continuity.activation_criteria` | The activation criteria, each one observable | DR process owner |

### `runbooks/RB-04-dr-drill.md`

| Field | Records | Owner |
|---|---|---|
| `infra.last_end_to_end_execution` | The date of the last end-to-end execution and who performed it | lead engineer |
| `governance.event_documentation` | How a real event is written up, by whom, and where the record goes | governance/risk contact |
| `governance.drill_cadence` | How often the plan is exercised, in practice | governance/risk contact |
| `governance.drill_levels` | Each exercise level, what it proves and what it does not | governance/risk contact |

### `runbooks/RB-05-replication-lifecycle.md`

| Field | Records | Owner |
|---|---|---|
| `infra.standby_posture` | The standby's steady-state posture and who may change it | infrastructure owner |
| `infra.warned_posture_time` | How long it takes to move the standby to its warned state | infrastructure owner |

---

## The full index

| Field | Phase | Answer | Owner | Section of the plan |
|---|---|---|---|---|
| `system.name` | [3a](03a-application.md) | text | application owner | 2.1 System description |
| `system.business_name` | [3a](03a-application.md) | text | business owner | 1.1 Background |
| `system.categorization` | [3a](03a-application.md) | text | governance/risk contact | 1.2 Scope |
| `system.impact_level` | [3a](03a-application.md) | enum | governance/risk contact | 1.2 Scope |
| `system.assumptions` | [3a](03a-application.md) | rows | lead engineer | 1.3 Assumptions |
| `system.component_terms` | [3a](03a-application.md) | narrative | application owner | 2.1 System description |
| `system.releases` | [3a](03a-application.md) | text | application owner | 2.1 System description |
| `system.operating_systems` | [3a](03a-application.md) | text | infrastructure owner | 2.1 System description |
| `system.instances` | [3a](03a-application.md) | narrative | application owner | 2.1 System description |
| `business.processes` | [2](02-business.md) | rows | business owner | K. Business impact analysis |
| `business.mtd.tier0` | [2](02-business.md) | duration | business owner | K. Business impact analysis |
| `business.rpo.tier0` | [2](02-business.md) | duration | business owner | K. Business impact analysis |
| `business.mbco.tier0` | [2](02-business.md) | text | business owner | Minimum business continuity objective per tier |
| `business.workarounds` | [2](02-business.md) | rows | business owner | E. Alternate mission/business processing - manual workarounds |
| `business.tier_signoff` | [2](02-business.md) | enum | business owner | Citation and unverified-statement discipline |
| `business.tier_targets` | [2](02-business.md) | rows | business owner | K. Business impact analysis |
| `business.tier_assignment` | [2](02-business.md) | rows | business owner | K. Business impact analysis |
| `business.freeze_periods` | [2](02-business.md) | rows | business owner | Periods when recovery is more expensive than the outage |
| `business.freeze_override_authority` | [2](02-business.md) | text | business owner | Periods when recovery is more expensive than the outage |
| `business.reconstruction_effort` | [2](02-business.md) | duration | business owner | Minimum business continuity objective per tier |
| `app.start_order` | [3a](03a-application.md) | narrative | lead engineer | 4.1 Sequence of recovery activities |
| `app.interconnections` | [3a](03a-application.md) | rows | application owner | I. System interconnections |
| `app.validation_pack` | [3a](03a-application.md) | rows | application owner | F. System validation test plan |
| `app.wrt_activities` | [3a](03a-application.md) | rows | application owner | Minimum business continuity objective per tier |
| `app.concurrent_processing` | [3a](03a-application.md) | narrative | application owner | 5.1 Concurrent processing |
| `app.recovery_procedures` | [3a](03a-application.md) | code | lead engineer | 4.2 Recovery procedures |
| `app.validation_data_tests` | [3a](03a-application.md) | rows | application owner | 5.2 Validation data testing |
| `app.interface_landing` | [3a](03a-application.md) | narrative | lead engineer | Interface landing and replication of inbound data |
| `app.unsafe_reruns` | [3a](03a-application.md) | rows | application owner | Interface landing and replication of inbound data |
| `app.reconfiguration_duration` | [3a](03a-application.md) | duration | lead engineer | Measured durations on the recovery critical path |
| `infra.primary_region` | [3b](03b-infrastructure.md) | text | infrastructure owner | 2.1 System description |
| `infra.standby_region` | [3b](03b-infrastructure.md) | text | infrastructure owner | C. Alternate site, storage and telecommunications |
| `infra.measured_rtt_ms` | [3b](03b-infrastructure.md) | number | lead engineer | Cost model and posture economics |
| `infra.replication` | [3b](03b-infrastructure.md) | rows | infrastructure owner | 4.2 Recovery procedures |
| `infra.standby_cost_floor` | [3b](03b-infrastructure.md) | currency | infrastructure owner | Cost model and posture economics |
| `infra.region_locked_naming` | [3b](03b-infrastructure.md) | narrative | infrastructure owner | Cost model and posture economics |
| `infra.last_end_to_end_execution` | [3b](03b-infrastructure.md) | date | lead engineer | J. Test, training and exercise documentation |
| `infra.availability_domains` | [3b](03b-infrastructure.md) | text | infrastructure owner | 2.1 System description |
| `infra.inter_region_transport` | [3b](03b-infrastructure.md) | narrative | infrastructure owner | Cost model and posture economics |
| `infra.storage_constraints` | [3b](03b-infrastructure.md) | narrative | lead engineer | Cost model and posture economics |
| `infra.shared_storage` | [3b](03b-infrastructure.md) | narrative | infrastructure owner | 2.1 System description |
| `infra.standby_posture` | [3b](03b-infrastructure.md) | narrative | infrastructure owner | Cost model and posture economics |
| `infra.warned_posture_time` | [3b](03b-infrastructure.md) | duration | infrastructure owner | Cost model and posture economics |
| `infra.silent_failures` | [3b](03b-infrastructure.md) | narrative | lead engineer | Alert catalog |
| `infra.irreversible_choices` | [3b](03b-infrastructure.md) | rows | lead engineer | Reversibility and one-way doors |
| `infra.licensing` | [3b](03b-infrastructure.md) | rows | infrastructure owner | Cost model and posture economics |
| `infra.offsite_storage` | [3b](03b-infrastructure.md) | rows | infrastructure owner | 5.7 Offsite data storage |
| `infra.post_recovery_backup` | [3b](03b-infrastructure.md) | narrative | infrastructure owner | 5.8 Data backup |
| `continuity.declaration_authority` | [4](04-continuity.md) | text | DR process owner | 3.1 Activation criteria and procedure; who may activate |
| `continuity.succession` | [4](04-continuity.md) | rows | DR process owner | 2.3 Roles and responsibilities |
| `continuity.activation_criteria` | [4](04-continuity.md) | narrative | DR process owner | 3.1 Activation criteria and procedure; who may activate |
| `continuity.decision_time_budget` | [4](04-continuity.md) | duration | DR process owner | 3.1 Activation criteria and procedure; who may activate |
| `continuity.unknown_estimate_default` | [4](04-continuity.md) | enum | DR process owner | 3.3 Outage assessment |
| `continuity.call_tree` | [4](04-continuity.md) | narrative | DR process owner | 3.2 Notification |
| `continuity.bridge` | [4](04-continuity.md) | text | DR process owner | 3.2 Notification |
| `continuity.assessment_procedure` | [4](04-continuity.md) | narrative | DR process owner | 3.3 Outage assessment |
| `continuity.escalation_thresholds` | [4](04-continuity.md) | narrative | DR process owner | 4.3 Recovery escalation and notification |
| `continuity.deactivation_authority` | [4](04-continuity.md) | text | DR process owner | 5.10 Deactivation |
| `continuity.contact_roster` | [4](04-continuity.md) | rows | DR process owner | A. Personnel contact list |
| `continuity.vendor_contacts` | [4](04-continuity.md) | rows | DR process owner | B. Vendor contact list |
| `continuity.vendor_obligations` | [4](04-continuity.md) | rows | governance/risk contact | Vendor obligations during a recovery |
| `continuity.decision_and_recovery_roles` | [4](04-continuity.md) | rows | DR process owner | 2.3 Roles and responsibilities |
| `continuity.people_unavailable` | [4](04-continuity.md) | narrative | DR process owner | 2.3 Roles and responsibilities |
| `continuity.assessment_calibration` | [4](04-continuity.md) | duration | DR process owner | 3.3 Outage assessment |
| `continuity.declaration_threshold_rule` | [4](04-continuity.md) | narrative | DR process owner | 3.1 Activation criteria and procedure; who may activate |
| `continuity.data_loss_gate` | [4](04-continuity.md) | narrative | DR process owner | 3.1 Activation criteria and procedure; who may activate |
| `continuity.recovery_declaration` | [4](04-continuity.md) | narrative | DR process owner | 5.4 Recovery declaration |
| `continuity.user_notification` | [4](04-continuity.md) | narrative | DR process owner | 5.5 Notification (users) |
| `continuity.cleanup` | [4](04-continuity.md) | narrative | DR process owner | 5.6 Cleanup |
| `governance.signing_authority` | [5](05-governance.md) | text | signing authority | Plan Approval statement |
| `governance.review_cadence` | [5](05-governance.md) | text | governance/risk contact | J. Test, training and exercise documentation |
| `governance.training_program` | [5](05-governance.md) | narrative | governance/risk contact | J. Test, training and exercise documentation |
| `governance.finding_to_change_route` | [5](05-governance.md) | narrative | governance/risk contact | Plan review and maintenance cadence |
| `governance.risk_register` | [5](05-governance.md) | rows | governance/risk contact | Risk register |
| `governance.event_documentation` | [5](05-governance.md) | narrative | governance/risk contact | 5.9 Event documentation |
| `governance.associated_plans` | [5](05-governance.md) | rows | governance/risk contact | K. Associated plans and procedures |
| `governance.drill_cadence` | [5](05-governance.md) | duration | governance/risk contact | J. Test, training and exercise documentation |
| `governance.drill_levels` | [5](05-governance.md) | rows | governance/risk contact | Drill levels and what each proves |
| `governance.availability_boundary` | [5](05-governance.md) | narrative | governance/risk contact | Plan review and maintenance cadence |
| `governance.plan_custody` | [5](05-governance.md) | narrative | signing authority | Plan Approval statement |
| `governance.breach_disclosure_clock` | [5](05-governance.md) | narrative | governance/risk contact | Risk register |
| `discovery.completed` | [1](01-discovery.md) | date | infrastructure owner | H. Hardware, software and firmware inventory |

Figures owing a mechanism: 10. Answers to read back before recording: 48. Fields discovery may prefill: 5.
