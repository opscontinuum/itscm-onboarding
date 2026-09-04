# Test environments

What each tier of testing proves, and what it does not.

This document is generated from the answer store. Correct it by correcting the interview, not by editing this file.

## Supplied by the toolkit's method

An exercise proves one of three things and rarely all three: that the plan reads correctly, that the steps run, or that the business can work afterwards. The toolkit asks which level each exercise reaches and what it therefore leaves unproven, because a plan whose only evidence is a reading has never been shown to work.


**Each exercise level, what it proves and what it does not**

| level | what_it_proves | what_it_does_not_prove |
| --- | --- | --- |
| 1, component test, using the orchestration prechecks and the replication health script, with no production impact | Replication is healthy, prechecks pass, the in-guest agent is alive, and, empirically the first time it is run, what the built-in Exadata drill plan group actually does | It exercises no recovery role, so it satisfies no training requirement. Beyond that, not stated in the reference plan |
| 2, snapshot standby drill, using a Data Guard snapshot standby with the start-drill and stop-drill plans, with no production impact | The full EBS stack opens read-write in Phoenix, the application tier starts and transactions commit. This is the drill that produces a real measured tolerable downtime without an outage, and the plan calls it the workhorse | It is run with the runbook open, so it never satisfies the closed-book training standard. While it runs, the always-on BI node reads a snapshot standby that is receiving redo without applying it, so it proves the presentation tier survives a role change and not that the standby is current |
| 3, live switchover, running the switchover runbook against real production, with a planned outage | Everything, including DNS, users and partner integrations | not stated in the reference plan |


## References

Sources for every value above, as recorded when the value was given.

- **Each exercise level, what it proves and what it does not**, recorded by document:oci-itscp/runbooks/RB-04-dr-drill.md

### Unverified statements

Engineering judgements, outstanding gaps and disagreements, labelled as such.

Every value in this document is traceable to a recorded source.
