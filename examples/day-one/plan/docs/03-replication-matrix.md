# Replication matrix

What is replicated, by which mechanism, and which choices cannot be reversed.

This document is generated from the answer store. Correct it by correcting the interview, not by editing this file.

## APPENDIX F ALTERNATE STORAGE, SITE, AND TELECOMMUNICATIONS

- **The standby region**: **[MISSING — owner: infrastructure owner]**

## Recorded for this plan

- **Measured inter-region round-trip time in milliseconds**: **[MISSING — owner: lead engineer]**

## 3.4.1 Backup and Recovery

- **Per tier: the replication mechanism, whether it is synchronous, measured lag, failover behavior, whether reversal needs a re-baseline, and whether it is one-way**: **[MISSING — owner: infrastructure owner]**

## Recorded for this plan

- **Storage features that constrain what the standby may be built on**: **[MISSING — owner: lead engineer]**

## Supplied by the toolkit's method

Some decisions in a continuity design cost a change ticket to undo and some cannot be undone at all without rebuilding from nothing. The toolkit separates the two and costs the second kind before it is taken, because otherwise the moment a one-way door is noticed is the moment somebody has already walked through it to save money.

- **Each decision that cannot be cheaply reversed, what reversing it costs and who may take it**: **[MISSING — owner: lead engineer]**

## 5.7 Offsite Data Storage

- **Each backup copy, where it is held, how long it is kept and how it is retrieved**: **[MISSING — owner: infrastructure owner]**

## 5.8 Data Backup

- **How the recovered system is protected again, when, and who confirms it**: **[MISSING — owner: infrastructure owner]**
- **What protects each part of the system, and which loss each protection answers**: **[MISSING — owner: infrastructure owner]**
- **Each backup policy: its mechanism, the kind of copy it makes, its rhythm and where it lands**: **[MISSING — owner: infrastructure owner]**
- **Each thing that needs protecting, what it is, which policy covers it and why anything uncovered is uncovered**: **[MISSING — owner: infrastructure owner]**

## Recorded for this plan

- **How long a restore of the largest component takes, end to end**: **[MISSING — owner: lead engineer]**
- **The copy that cannot be deleted or encrypted by a compromised administrator, and who holds access to it**: **[MISSING — owner: infrastructure owner]**

## References

Sources for every value above, as recorded when the value was given.

No value in this document has a recorded source yet.

### Unverified statements

Engineering judgments, outstanding gaps and disagreements, labeled as such.

- **The standby region**: **[MISSING — owner: infrastructure owner]**
- **Measured inter-region round-trip time in milliseconds**: **[MISSING — owner: lead engineer]**
- **Per tier: the replication mechanism, whether it is synchronous, measured lag, failover behavior, whether reversal needs a re-baseline, and whether it is one-way**: **[MISSING — owner: infrastructure owner]**
- **Storage features that constrain what the standby may be built on**: **[MISSING — owner: lead engineer]**
- **Each decision that cannot be cheaply reversed, what reversing it costs and who may take it**: **[MISSING — owner: lead engineer]**
- **Each backup copy, where it is held, how long it is kept and how it is retrieved**: **[MISSING — owner: infrastructure owner]**
- **How the recovered system is protected again, when, and who confirms it**: **[MISSING — owner: infrastructure owner]**
- **What protects each part of the system, and which loss each protection answers**: **[MISSING — owner: infrastructure owner]**
- **Each backup policy: its mechanism, the kind of copy it makes, its rhythm and where it lands**: **[MISSING — owner: infrastructure owner]**
- **Each thing that needs protecting, what it is, which policy covers it and why anything uncovered is uncovered**: **[MISSING — owner: infrastructure owner]**
- **How long a restore of the largest component takes, end to end**: **[MISSING — owner: lead engineer]**
- **The copy that cannot be deleted or encrypted by a compromised administrator, and who holds access to it**: **[MISSING — owner: infrastructure owner]**
