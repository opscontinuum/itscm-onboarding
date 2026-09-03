# Generated repository scaffold

The tree `itscp-build` creates, and which skill fills each file. Structure follows the
reference example so that anyone who has read one plan can navigate any other.

```
<your-org>-itscp-<suite>/
├── README.md                          scope, how to read, plan maintenance
├── .gitignore                         answer store, evidence, resource files
├── .itscm/
│   └── answers.yaml                   the answer store (gitignored)
├── docs/
│   ├── 00-plan-approval.md            governance      signature, attestation
│   ├── 00-record-of-changes.md        build           derived from git log
│   ├── 01-architecture.md             infrastructure  design, assumptions, diagrams
│   ├── 02-mtd-tiers.md                business        BIA output, tiers, MBCO
│   ├── 03-replication-matrix.md       infrastructure  mechanisms, one-way doors
│   ├── 04-monitoring.md               infrastructure  alarms, RPO attestation
│   ├── 05-cost-and-teardown.md        infrastructure  posture economics
│   ├── 06-test-environments.md        infrastructure  what each test tier proves
│   ├── 07-standards-alignment.md      governance      NIST / ITIL / ISO crosswalk
│   ├── 08-phase-activation.md         build           ISCP phase 1 routing
│   ├── 09-phase-recovery.md           build           ISCP phase 2 routing
│   ├── 10-phase-reconstitution.md     build           ISCP phase 3 routing
│   ├── 11-inventory.md                discovery       Appendix H
│   ├── 12-interconnections.md         discovery + app Appendix I
│   ├── references.md                  build           consolidated citation index
│   └── compliance-audit.md            audit           adversarial audit output
├── runbooks/
│   ├── RB-01-switchover.md            infrastructure  planned role transition
│   ├── RB-02-failover.md              infra + continuity  unplanned, with the gate
│   ├── RB-03-failback.md              infrastructure  the return trip
│   ├── RB-04-dr-drill.md              governance      exercise procedure
│   └── RB-05-replication-lifecycle.md infrastructure  build, posture, teardown
├── checklists/
│   ├── roles-and-responsibilities.md  continuity      §2.3, teams, succession
│   ├── contact-roster.md              continuity      Appendix A + B, call tree
│   ├── outage-assessment.md           continuity      §3.3, the repair estimate
│   ├── dr-authority-matrix.md         continuity      decision rights
│   ├── tier-assignment-workshop.md    business        the BIA session
│   ├── manual-workarounds.md          business        Appendix E
│   ├── validation-pack.md             application     Appendix F
│   ├── pre-failover-precheck.md       infrastructure  Appendix D
│   ├── drill-timing-sheet.md          governance      evidence capture
│   ├── contingency-training.md        governance      Appendix J
│   └── risk-register.md               governance      owned risks
├── scripts/                           infrastructure  recovery automation
├── evidence/                          governance      drill results, attestations
└── terraform/                         infrastructure  estate as code (apply-locked)
```

## Rendering rules

Applied by `itscp-build` when it writes any of the above.

| Answer-store state | Renders as |
|---|---|
| `ANSWERED`, confidence high or medium | The value, plainly |
| `ANSWERED`, confidence low | `4 hours *(low confidence; not measured)*` |
| `MISSING` | `**[MISSING — owner: Head of Finance Systems]**` |
| `DEFERRED` | `**[DEFERRED to 2026-10-01 — owner: Treasury]**` |
| `NOT_APPLICABLE` | `Not applicable — <the recorded reason>` |
| `conflict` present | Both values, both sources, and the named decision owner |

**A missing value never renders as blank, and never as a plausible default.** The whole point
of the toolkit is that a reader can tell, at a glance, which parts of the plan are known and
which are outstanding.

## Sections every generated document carries

- `## References` — sources for any claim about product behaviour or a standard.
- `### Unverified statements` — engineering judgements the toolkit or the author made,
  labelled as judgements. This is where anything not traceable to a person or an API goes.

The second section is not optional. It is what keeps a generated document honest about the
difference between what was elicited and what was reasoned.
