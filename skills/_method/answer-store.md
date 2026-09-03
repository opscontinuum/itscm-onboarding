# The answer store

One file per plan: `.itscm/answers.yaml` in the generated repository. Every interview reads
it, every interview appends to it, and every generated document renders from it.

**It is gitignored by default and must stay that way.** It accumulates names, phone numbers,
OCIDs, MTD figures, incident narratives and organisational weak points. It is the most
sensitive file the toolkit produces.

---

## Why a store at all

Three problems it solves, all of which appear within the first hour of real use:

1. **Interviews are interrupted.** A business owner gives you 40 minutes and leaves. Without a
   store you restart; with one you resume mid-question.
2. **The same fact has two askers.** The application owner and the infrastructure owner both
   know the database name. Without a store you ask twice, look disorganised, and create a
   contradiction you then have to reconcile.
3. **Regeneration must not require re-interviewing.** Fix a template, re-render, done. If the
   answers live only in the generated prose, every correction is archaeology.

---

## Shape

Flat, dotted keys. Greppable, diffable, mergeable, and readable by a human who has never seen
the toolkit.

```yaml
meta:
  schema_version: 1
  system_name: "EBS Production"
  created: "2026-09-02"
  last_updated: "2026-09-03"

facts:
  business.mtd.tier0:
    status: ANSWERED            # MISSING | ANSWERED | DEFERRED | NOT_APPLICABLE
    value: "2h"
    mechanism: "Bank payment file cuts at 18:00; missing it defers settlement one day."
    provenance: "interview:business-owner:2026-09-02"
    confidence: medium
    owner: null
    due: null
    notes: null

  business.mbco.tier0:
    status: MISSING
    value: null
    provenance: null
    confidence: null
    owner: "Head of Finance Systems"
    due: null
    notes: "What must be usable during work recovery, as opposed to fully restored.
            Business owner asked for time to consult Treasury."

  infra.standby.region:
    status: ANSWERED
    value: "us-phoenix-1"
    provenance: "oci-discovery:ListCloudVmClusters"
    confidence: high
    owner: null
```

### Field rules

| Field | Rule |
|---|---|
| `status` | Always present. Never absent, never blank |
| `value` | Present only when `status: ANSWERED`. `null` otherwise |
| `mechanism` | Required for every duration, threshold or currency figure. See the method file |
| `provenance` | Required when `ANSWERED`. Never `assistant`, never `inferred` |
| `confidence` | Required when `ANSWERED`. `high`, `medium` or `low` |
| `owner` | Required when `MISSING` or `DEFERRED`. A role, not a name, where possible |
| `due` | Required when `DEFERRED` |
| `notes` | Free text. Where the reason for `NOT_APPLICABLE` goes |
| `conflict` | Present only when two sources disagree. Never resolved silently |

### Key namespaces

| Prefix | Owned by | Feeds |
|---|---|---|
| `system.*` | `itscp-interview-application` | ISCP §1 Introduction, §2.1 System Description |
| `business.*` | `itscp-interview-business` | Appendix K BIA, MTD tiers, Appendix E workarounds |
| `app.*` | `itscp-interview-application` | §2.1, Appendix F validation, Appendix I interconnections |
| `infra.*` | `itscp-interview-infrastructure` + `itscp-discover` | Architecture, replication, Appendix C, Appendix H |
| `continuity.*` | `itscp-interview-continuity` | §2.3 roles, §3.1 activation, §3.2 notification, §3.3 assessment, §4.3 escalation |
| `governance.*` | `itscp-interview-governance` | Approval, categorization, review cadence, Appendix J TT&E |
| `discovery.*` | `itscp-discover` only | Raw inventory; never written by an interview |

A skill writes only within its own prefix. If an interview learns something outside its
prefix — and it will — it records the fact **and** notes which interview owns the key, so the
owning skill confirms it rather than inheriting it unread.

---

## Writing rules

**Write after every answer, not at the end.** An interview that ends unexpectedly must leave
the store consistent.

**Never delete a fact to change it.** Supersede in place and keep the prior value:

```yaml
  business.mtd.tier0:
    status: ANSWERED
    value: "6h"
    provenance: "interview:business-owner:2026-09-10"
    confidence: high
    superseded:
      - value: "2h"
        provenance: "interview:business-owner:2026-09-02"
        reason: "Revised after Treasury confirmed the file cut-off is 22:00, not 18:00."
```

The reference repository keeps an append-only record of changes for the same reason: a
continuity plan whose numbers move without a trail cannot be audited, and the question
"when did this become six hours, and who said so?" is asked exactly once, in the worst week.

**Never write a value the toolkit produced.** Engineering judgements belong in the generated
document's *Unverified statements* section, attributed as judgements. The store holds only
what humans and read-only APIs said.

---

## Reading rules

- On entry, load the store and report coverage before asking anything.
- Skip `ANSWERED` fields. Re-ask only when the interviewee volunteers a correction, or when a
  `conflict` needs the owner's decision.
- `DEFERRED` fields past their `due` date are surfaced to the orchestrator, not silently
  re-asked.

---

## Coverage

Coverage is `ANSWERED + NOT_APPLICABLE` over total fields in scope. `itscp-build` reports it
per section and refuses to claim a section complete below 100%.

**Coverage is not quality.** A store at 100% coverage where two thirds of the fields are
`confidence: low` describes an organisation that has guessed comprehensively. Report the
confidence distribution alongside coverage, always, and let the drill programme aim at the
low-confidence figures first.
