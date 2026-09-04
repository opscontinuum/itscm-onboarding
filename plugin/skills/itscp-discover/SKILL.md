---
name: itscp-discover
description: Use when building a continuity plan for a workload running in Oracle Cloud Infrastructure and the environment is not yet documented, when someone says they are unsure what their estate actually contains, or when a hardware and software inventory or interconnection list is needed for an appendix of an IT service continuity plan.
---

# itscp-discover

Walks an OCI tenancy **read-only** and turns "I have a vague idea of my environment" into an
inventory, a gap list, and a populated resource file the runbook scripts consume.

This is usually the highest-value hour of the whole engagement. It is also the only phase that
touches a live production tenancy, so it is the phase with a hard safety rule.

---

## The hard rule: discovery never mutates

> **Every OCI call this skill makes is a `list` or a `get`. There are no exceptions, and there
> is no flag that adds one.**

`itscp_discover_oci` is the only way this skill reaches a tenancy, and it enforces the rule: the
wrapper it runs behind rejects any invocation whose operation is not `list*` or `get*`, before
the call reaches the CLI. It fails closed.

The reference repository's Terraform is apply-locked because authoring against a hypothetical
estate is a different risk posture from touching a real one. This skill touches real ones. The
guard is structural rather than a convention because a convention is one hurried edit from
being gone.

**Do not work around the guard.** If discovery needs data only a mutating call can produce,
that is a finding to report, not a guard to widen. Rationalisations that mean stop:

| Thought | Reality |
|---|---|
| "A `start` on a stopped test instance is harmless" | It is a mutation, it is billable, and it is not discovery |
| "I'll just tag resources so they're easier to find" | Tagging is a write. Record what you found instead |
| "The customer said I could" | They authorised a read-only inventory. Widening scope needs a new conversation |
| "`terraform import` is read-only" | It writes state. Emit `import` blocks for a human to run |

---

## Prerequisites

Confirm before running, and stop if any is unmet:

1. `oci` CLI installed and configured — `oci --version`, `oci iam region list`.
2. The profile's permissions are **read-only**, or the operator has confirmed they accept
   running with wider ones. Say the risk out loud; do not assume.
3. A named compartment (or root) to walk, and the regions in scope.
4. Written confirmation from the operator that a tenancy walk is authorised. Enumerating a
   production estate is a legitimate action with an audit trail; get consent on the record.

---

## Running it

`itscp_discover_oci compartment=<ocid> regions=us-ashburn-1,us-phoenix-1 dry_run=true` first,
then the same call with `dry_run=false`. Add `out=<directory>` to write somewhere other than
`discovery-output`, and `subtree=false` to stop at the named compartment.

`dry_run=true` prints every command it would issue without executing any, and needs no
credentials. **Show a customer the dry run before the real run.** It converts "an AI is
going to look at our production tenancy" into a reviewable list, and it has never once
been a wasted five minutes.

---

## One walk, many systems

**Discovery is portfolio-wide; plans are per-system.** Walk the tenancy once, then
*attribute* what you found to the systems in `portfolio.toml`. Walking once per plan
re-reads the same estate N times and produces N inventories that disagree at the edges.

Attribution is a question, not an inference:

> "Here is everything in the compartment. Which of these belongs to the identity database,
> which to the HR suite, and which to neither?"

**A resource nobody claims is a finding, and one of the most useful a first engagement
produces.** Record it as unattributed rather than assigning it to whichever system looks
closest; an unowned production resource is either a system missing from the register or a
system nobody is maintaining, and both are worth knowing.

Feed the register back the other way too: a system in `portfolio.toml` with no discovered
resources either lives somewhere this walk did not reach, or does not exist.

## What it collects, and why each matters to the plan

| Area | Feeds |
|---|---|
| Compartments, regions, availability domains | §2.1 System description; the primary/standby pair |
| Exadata / DB systems, VM clusters, databases | The recovery target; the Exadata cost floor conversation |
| Data Guard associations, roles, protection modes | Whether an RPO 0 claim is even available |
| Compute instances, shapes, lifecycle states | Appendix H inventory; what is pilot-light versus running |
| Block volumes, volume groups, replicas | Storage recovery sequence; re-baseline exposure |
| File systems, mount targets, replications | Shared filesystem recovery |
| Object Storage buckets and replication policies | Interface file interchange; batch recovery |
| Load balancers, backend sets, health checks | The external entry point |
| DNS zones and steering policies | Traffic failover mechanism |
| VCNs, DRGs, remote peering connections | Cross-region path; a material assumption in most designs |
| Full Stack DR protection groups and plans | Existing orchestration, if any |
| Recovery Service protected databases, backup policies | The immutable copy, and whether one exists |
| Monitoring alarms | What currently pages, versus what the plan will need |

## What it deliberately does not collect

| Not collected | Why |
|---|---|
| Secrets, vault contents, key material | Never needed for a plan. A discovery tool that reads secrets becomes a credential-exfiltration tool |
| Database contents or row counts | Out of scope; volume comes from the application owner |
| IAM policy statements verbatim | Records *that* authority exists, not the rules. Policies are sensitive and change often |
| Cost and billing data | Useful, but a separate authorisation. Ask before extending |

---

## Handling commands that do not exist

The OCI CLI moves. Services get renamed, subcommands change, and a customer's installed
version may predate a service entirely.

**A missing command is recorded, never fatal.** The step writes:

```
NOT DISCOVERED: Full Stack DR protection groups
  reason: `oci disaster-recovery dr-protection-group list` not available in CLI 3.44.1
  action: confirm with infrastructure owner during itscp-interview-infrastructure
```

The inventory then carries a *known-incomplete* marker rather than implying the estate lacks
what the tool could not see. **Absence of evidence is not evidence of absence, and the
inventory must say which one it is recording.** This distinction is the difference between an
inventory an auditor can use and one that quietly misleads.

---

## Output

| File | Contents |
|---|---|
| `discovery-output/inventory.md` | Appendix H — every resource, with OCID, region, shape, state |
| `discovery-output/dr-resources.env` | Populated resource file the runbook scripts read |
| `discovery-output/raw/*.json` | Raw API responses, for re-rendering without re-walking |
| `discovery-output/gaps.md` | Everything NOT DISCOVERED, with the reason and who to ask |

That is the whole list. `itscp_discover_oci` writes those four things and nothing else. All are
gitignored by default, and `inventory.md` is a complete map of a production estate.

Then write `discovery.*` keys into the answer store with provenance
`oci-discovery:<operation>`, and hand `gaps.md` to `itscp-build` as interview input.

### Not produced yet: Appendix I

**There is no `discovery-output/interconnections.md`.** The buckets, load balancers, DNS zones,
steering policies and peering connections that would populate Appendix I are collected into
`raw/*.json` by the walk and left unrendered. Nothing turns them into an interconnection list.

**The consequence, and say it to the operator rather than letting the appendix look
pre-populated:** Appendix I is built entirely from `itscp-interview-application`. The half of
the register discovery could have pre-filled is instead recalled in a meeting, which is exactly
the condition under which an interface gets missed, and a missed interface is the most damaging
single omission this toolkit has. Budget the interview time accordingly and treat the
interconnection section as the one with no safety net under it.

Writing the renderer is separate work and is not attempted here.

---

## What discovery cannot tell you

Say this to the operator when you hand over the inventory, because the inventory looks more
complete than it is:

- **What any of it is for.** An instance named `prd-app-04` has no business meaning until the
  application owner supplies one.
- **Whether replication is working.** It reports that a policy exists, not that it is current.
  Lag comes from monitoring, not from a resource listing.
- **What is missing.** Discovery enumerates what exists. The absence of a standby is invisible
  to it unless somebody expected one.
- **Whether the estate matches its documentation.** That comparison is the infrastructure
  interview's job, and it is usually where the first real finding appears.
