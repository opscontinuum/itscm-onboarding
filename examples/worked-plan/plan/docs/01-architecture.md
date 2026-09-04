# Architecture

The environment this plan recovers, and the assumptions the design rests on.

This document is generated from the answer store. Correct it by correcting the interview, not by editing this file.

## 2.1 System Description

- **The system's technical name, as the plan's title and throughout**: Oracle E-Business Suite on Exadata Database Service, with Windows application, concurrent-processing and visualization tiers

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
| A7: a single production EBS instance, with no multi-org split across regions | A multi-instance environment changes the tiering map | not stated in the reference plan | not stated in the reference plan |


## Recorded for this plan

- **The words this organization uses for its own components, and what each one means**: The reference plan defines three of its own terms and leaves one of them unresolved. Visualization tier is taken to mean the BI or reporting presentation layer, and that reading is marked MATERIAL: if it means virtualization instead, the design for that tier is replaced by one based on OCI VMware Solution. Physical host name means the per-region, per-availability-domain computer name, unique everywhere. Logical host name means the neutral name EBS itself is configured with, the same in both regions and resolved region-locally, and it is the distinction the whole naming design rests on. The replication matrix states that it uses the vendor's own product and feature names verbatim so that every row is searchable in Oracle documentation.

## 2.1 System Description

- **The release of each major component, and any upgrade in flight**: EBS 12.2.x, with the dual filesystem fs1 and fs2, on Oracle Database 19c running on Exadata Database Service on Dedicated Infrastructure. Both are stated as assumptions, A1 and A2, both marked MATERIAL and to be confirmed or corrected before build, rather than as confirmed facts. No upgrade in flight is recorded. *(low confidence; not measured)*
- **The operating system of each tier, and what that constrains**: The EBS application, concurrent-processing and visualization tiers run on Windows Server x64, relinked with MKS Toolkit. That is stated as assumption A3, and the plan records its consequence directly: the recovery scripts are PowerShell, and the shared-filesystem strategy has to work around EBS 12.2 on Windows having no shared application-tier file system. The database tier is Exadata Database Service on Dedicated Infrastructure.
- **Whether the production environment is one instance or several, and how they are split**: One production EBS instance, with no multi-org split across regions. The reference plan states this as assumption A7 and records that a multi-instance environment would change the tiering map. It is not marked MATERIAL. *(low confidence; not measured)*
- **The primary region**: us-ashburn-1

## APPENDIX F ALTERNATE STORAGE, SITE, AND TELECOMMUNICATIONS

- **The standby region**: us-phoenix-1

## Recorded for this plan

- **Which names are region-locked and what changing them costs in recovery time**: The design deliberately removes the region lock, and the reference plan calls that the single biggest recovery-time lever in the document. Physical computer names are unique per region and per availability domain, each machine a distinct directory account. EBS itself is configured with logical host names that are the same in both regions and resolved region-locally, through a hosts file or a region-scoped private DNS view, so that context files, FND_NODES, WebLogic configuration and profile options do not change at failover. TNS aliases resolve region-locally for the same reason, so the service access names differ per region and Data Guard needs no shared names. The two virtual networks must use different address ranges, because both have to be routable at once for Data Guard. Drill instances get the same logical names in a drill-only resolution view, and the plan warns that without that view a drill silently falls into the slow rebuild branch.

## 2.1 System Description

- **The availability domains in use, and where any arbitrator sits**: Production spans Ashburn AD-1 and AD-2: the primary database in AD-1, the synchronous standby in AD-2, and the Windows application, concurrent-processing and visualization tiers split across both behind one load balancer that spans them. The split is deliberate, so that after an automatic local failover there is an application node that can still reach the promoted database. The Fast-Start Failover observer sits in Ashburn AD-3, on a host separate from both the primary and the standby, which the plan takes from Oracle's best practice of siting it in a third location. Which Phoenix availability domains the standby environment occupies is not stated in the reference plan.

## Recorded for this plan

- **How the two regions are joined and what is committed in writing**: A Dynamic Routing Gateway with a Remote Peering Connection over the OCI backbone, not FastConnect and not the public internet. The plan records that Oracle requires remote virtual network peering for cross-region Data Guard on this database service, so the choice is constrained rather than free. Nothing is committed in writing: the plan states that no bandwidth guarantee or service level for the peering link was verified in this revision, and that the one gigabit per second in its worked example is illustrative rather than a guarantee. It records the consequence rather than hiding it, that a peering-link incident is a single event which degrades every cross-region replication tier at once, and that an alternate path is warranted only if measured transport lag at period-close redo rates breaches the tier 0 target.

## 2.1 System Description

- **What lives on shared storage and how it is reached**: Less than a reader would expect, and the plan is explicit about why. EBS 12.2 on Windows has no shared application-tier file system, so the run, patch and non-editioned filesystems live on each node's own replicated block volumes rather than on a share, and the replicated copy is the Phoenix application tier. What is genuinely shared is the inbound and outbound interface landing directories that every application node must see, custom file drops written by integrations such as bank files, EDI and scanned documents, and the concurrent output archive if one is kept on a share rather than per node. Those are reached over NFS version 3, which is the protocol the File Storage service supports, using the Windows client for NFS with anonymous user and group mapping. The plan records that whether that configuration is EBS-certified for Windows was not found in any source it read.

## References

Sources for every value above, as recorded when the value was given.

- **The system's technical name, as the plan's title and throughout**, recorded by document:oci-itscp/docs/01-architecture.md
- **Each stated assumption, what breaks if it is wrong, who confirms it and by when**, recorded by document:oci-itscp/docs/01-architecture.md
- **The words this organization uses for its own components, and what each one means**, recorded by document:oci-itscp/docs/01-architecture.md
- **The release of each major component, and any upgrade in flight**, recorded by document:oci-itscp/docs/01-architecture.md
- **The operating system of each tier, and what that constrains**, recorded by document:oci-itscp/docs/01-architecture.md
- **Whether the production environment is one instance or several, and how they are split**, recorded by document:oci-itscp/docs/01-architecture.md
- **The primary region**, recorded by document:oci-itscp/docs/01-architecture.md
- **The standby region**, recorded by document:oci-itscp/docs/01-architecture.md
- **Which names are region-locked and what changing them costs in recovery time**, recorded by document:oci-itscp/docs/01-architecture.md
- **The availability domains in use, and where any arbitrator sits**, recorded by document:oci-itscp/docs/01-architecture.md
- **How the two regions are joined and what is committed in writing**, recorded by document:oci-itscp/docs/01-architecture.md
- **What lives on shared storage and how it is reached**, recorded by document:oci-itscp/docs/01-architecture.md

### Unverified statements

Engineering judgements, outstanding gaps and disagreements, labeled as such.

- **The release of each major component, and any upgrade in flight**:  *(low confidence; not measured)*
- **Whether the production environment is one instance or several, and how they are split**:  *(low confidence; not measured)*
