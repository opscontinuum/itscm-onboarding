# Inventory

The hardware and software this plan depends on.

This document is generated from the answer store. Correct it by correcting the interview, not by editing this file.

## 2.1 System Description

- **The release of each major component, and any upgrade in flight**: EBS 12.2.x, with the dual filesystem fs1 and fs2, on Oracle Database 19c running on Exadata Database Service on Dedicated Infrastructure. Both are stated as assumptions, A1 and A2, both marked MATERIAL and to be confirmed or corrected before build, rather than as confirmed facts. No upgrade in flight is recorded. *(low confidence; not measured)*
- **The operating system of each tier, and what that constrains**: The EBS application, concurrent-processing and visualization tiers run on Windows Server x64, relinked with MKS Toolkit. That is stated as assumption A3, and the plan records its consequence directly: the recovery scripts are PowerShell, and the shared-filesystem strategy has to work around EBS 12.2 on Windows having no shared application-tier file system. The database tier is Exadata Database Service on Dedicated Infrastructure.

## APPENDIX H HARDWARE AND SOFTWARE INVENTORY

- **Whether a discovery walk has run, and when**: **[MISSING — owner: infrastructure owner]**

## References

Sources for every value above, as recorded when the value was given.

- **The release of each major component, and any upgrade in flight**, recorded by document:oci-itscp/docs/01-architecture.md
- **The operating system of each tier, and what that constrains**, recorded by document:oci-itscp/docs/01-architecture.md

### Unverified statements

Engineering judgements, outstanding gaps and disagreements, labeled as such.

- **The release of each major component, and any upgrade in flight**:  *(low confidence; not measured)*
- **Whether a discovery walk has run, and when**: **[MISSING — owner: infrastructure owner]**
