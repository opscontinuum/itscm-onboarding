# Monitoring and attestation

The alarms that prove the recovery point objective is being met.

This document is generated from the answer store. Correct it by correcting the interview, not by editing this file.

## Recorded for this plan

- **The failures this estate does not notice, and what would have shown them**: The reference plan carries a catalogue of them and says why: an estate that is not monitored is not a DR estate, it is an assumption. Data Guard apply can stop while transport keeps running, so the standby falls arbitrarily far behind while the console still looks connected. The configuration can fall unsynchronized, at which point recovery point zero stops being true and fast-start failover can no longer occur, so the local automatic-failover story stops working in exactly the case tier 0 exists for. Volume group replication can stall silently, leaving the replica frozen at an old point in time that is discovered only at failover. File storage replication can miss its interval repeatedly and leave files hours or days stale. The in-guest agent that runs every orchestrated step can stop on a Windows node, so every user-defined step fails mid plan. Backup protection can fail to be re-enabled on the new primary after a role change, so the region that is now primary is not being backed up at all. The fast recovery area can fill, which stalls apply and fails drills. The Phoenix cluster can be scaled to zero cores by a cost-cutting change, which stops redo apply and silently turns tier 1 into tier 3 while the documentation still claims the old recovery point. And configuration can drift between the regions, so failover succeeds and the application misbehaves. The governing rule the plan draws from this is to alarm on the absence of signal and not only on bad values, because several of these show up as silence rather than as a bad number.

## References

Sources for every value above, as recorded when the value was given.

- **The failures this estate does not notice, and what would have shown them**, recorded by document:oci-itscp/docs/04-monitoring.md

### Unverified statements

Engineering judgements, outstanding gaps and disagreements, labelled as such.

Every value in this document is traceable to a recorded source.
