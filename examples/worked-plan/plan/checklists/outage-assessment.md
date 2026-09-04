# Outage assessment

How long the repair will take, and what to do when nobody can say.

This document is generated from the answer store. Correct it by correcting the interview, not by editing this file.

## Recorded for this plan

- **The default action when the repair estimate is unknown**: declare

## 3.3 Outage Assessment

- **The outage assessment procedure and where the repair estimate comes from**: The assessment team, led by infrastructure on-call, produces exactly one number: the estimated time to restore service in Ashburn. The failover gate compares that number against the remaining tolerable downtime and the comparison decides whether a disaster is declared. Four steps. First, establish reachability and role state using the Data Guard and replication health scripts. Second, capture evidence, and the plan says to run this even if you expect not to declare, because recovery destroys it. Third, establish the blast radius: is this the database, the availability domain, or the region? Fourth, produce the estimate, which for a regional event means asking the cloud operator, because their own estimate is the only credible input to a repair time, and writing down what was said and when, because an estimate with no timestamp is worthless twenty minutes later. The output form is fixed: give a band and a confidence, never a point estimate, because a point estimate implies a precision nobody has and invites the Commander to treat it as fact. Safety takes precedence over the procedure: an assessor in a disrupted location is not an assessor, and passes to their alternate saying why. The plan carries a closed-book fallback of five questions for when the document is not to hand.

## Recorded for this plan

- **How long this organization actually takes to produce a repair estimate**: **[MISSING — owner: DR process owner]**

## References

Sources for every value above, as recorded when the value was given.

- **The default action when the repair estimate is unknown**, recorded by document:oci-itscp/checklists/outage-assessment.md; mechanism: The rule is conditioned: declare when the radius is regional and no credible repair estimate exists. The plan's reasoning is that the honest reading of unknown is not wait and see, but that the budget is being spent at a known rate against an unknown duration. It records the rule, and the judgement that a late declaration is worse than an unnecessary failover, as its own engineering judgement, noting that NIST requires an estimated time to restore and does not say what to do when none can be produced.
- **The outage assessment procedure and where the repair estimate comes from**, recorded by document:oci-itscp/checklists/outage-assessment.md

### Unverified statements

Engineering judgements, outstanding gaps and disagreements, labeled as such.

- **How long this organization actually takes to produce a repair estimate**: **[MISSING — owner: DR process owner]**
