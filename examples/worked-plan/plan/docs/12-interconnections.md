# Interconnections

Every system this one exchanges data with, and who to call about each.

This document is generated from the answer store. Correct it by correcting the interview, not by editing this file.

## APPENDIX I INTERCONNECTIONS TABLE

- **Each interconnection, its direction, transport, contact and whether it is replayable**: **[MISSING — owner: application owner]**

## Recorded for this plan

- **Where inbound interface data lands today and whether that location is replicated**: Two landing places, both replicated. Inbound and outbound interface landing directories and custom file drops that every application node must see sit on OCI File Storage, replicated across regions on a snapshot-delta basis at a minimum interval of fifteen minutes and sixty by default, which is what bounds their loss. Batch interchange lands in Object Storage under a cross-region replication policy, and the failover runbook replays inbound files from the replicated bucket. The plan states that the Object Storage path, not the share, is the primary recovery path for interface files, and it presents landing all inbound files in Object Storage before processing as the single highest-leverage change on its work-recovery table, which is the language of a change to make rather than a description of what is in place. Whether the pattern is already in place, and the actual paths, share names and mount points, are not stated in the reference plan.

## References

Sources for every value above, as recorded when the value was given.

- **Where inbound interface data lands today and whether that location is replicated**, recorded by document:oci-itscp/docs/01-architecture.md

### Unverified statements

Engineering judgements, outstanding gaps and disagreements, labeled as such.

- **Each interconnection, its direction, transport, contact and whether it is replayable**: **[MISSING — owner: application owner]**
