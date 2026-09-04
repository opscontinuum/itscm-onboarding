# Validation pack

The checks that decide whether the recovered system may be used.

This document is generated from the answer store. Correct it by correcting the interview, not by editing this file.

## APPENDIX E SYSTEM VALIDATION TEST PLAN


**Each validation check, its duration and its owner**

| check | duration | who |
| --- | --- | --- |
| V1: AppsLocalLogin loads and a test user logs in, returning HTTP 200 with a session established | not stated in the reference plan | not stated in the reference plan |
| V2: a Forms session opens on a real transaction form, renders and commits a test record | not stated in the reference plan | not stated in the reference plan |
| V3: Concurrent Managers, with all target managers at actual equals target | not stated in the reference plan | not stated in the reference plan |
| V4: submit the Active Users concurrent request and see it complete normally | not stated in the reference plan | not stated in the reference plan |
| V5: Workflow Mailer running, with a test notification delivered | not stated in the reference plan | not stated in the reference plan |
| V6: the inbound interface directory is reachable and writable, and a test file round-trips | not stated in the reference plan | not stated in the reference plan |
| V7: integration endpoints respond on their health endpoint | not stated in the reference plan | not stated in the reference plan |
| V8: reverse Data Guard, with the former primary now a standby and applying, the Broker showing success and apply lag decreasing | not stated in the reference plan | not stated in the reference plan |
| V9: the BI and visualization tier reconnected, with a report rendering | not stated in the reference plan | not stated in the reference plan |


## 5.2 Validation Data Testing


**Each data validation check, what it proves and who signs it off**

| check | what_it_proves | who_signs |
| --- | --- | --- |
| Data Guard gap check | not stated in the reference plan | not stated in the reference plan |
| System change number and lag reconciliation | not stated in the reference plan | not stated in the reference plan |
| The recovery point attestation, recording what was actually lost | What was actually lost, in seconds of transport lag. The plan calls this the honest half of the step: validation data testing asks whether the data is current, and after an unplanned failover the truthful answer is often no, by some number of seconds | not stated in the reference plan |


## References

Sources for every value above, as recorded when the value was given.

- **Each validation check, its duration and its owner**, recorded by document:oci-itscp/runbooks/RB-01-switchover.md
- **Each data validation check, what it proves and who signs it off**, recorded by document:oci-itscp/docs/10-phase-reconstitution.md

### Unverified statements

Engineering judgements, outstanding gaps and disagreements, labeled as such.

Every value in this document is traceable to a recorded source.
