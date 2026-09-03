---
name: itscp-audit
description: Use when a continuity plan or ISCP needs checking against NIST SP 800-34 or the SP 800-53 contingency planning controls, when someone asks whether their plan is complete or audit-ready, or before submitting a plan for approval or external review.
---

# itscp-audit

Audits a generated plan against the standard. Adversarial by construction: every requirement
starts REFUTED and only a quoted sentence from a file in the plan moves it.

Descended from `skills/itscp-compliance-audit` in the reference repository, generalised to
audit *your* plan rather than that one.

**Read first:** `skills/_method/coverage-map.md`.

---

## The rule that makes this an audit rather than a review

> **A requirement PASSES only when the report quotes the sentence that satisfies it, with file
> path and section heading.**

"The runbooks cover this" is not evidence. "The plan clearly intends" is not evidence. If you
cannot paste the sentence, the verdict is not PASS.

## Verdicts

Exactly one per requirement, from this list:

| Verdict | Means | The row must carry |
|---|---|---|
| PASS | A sentence in the plan satisfies the whole requirement | Path, section, verbatim quote |
| PARTIAL | Part is satisfied, or the artefact exists but is a blank template | Path, section, quote, and the missing part named |
| REFUTED | Nothing in the plan satisfies it | Where you looked, and the closest thing found (or "nothing") |
| NOT APPLICABLE | The standard or the plan's stated scope excludes it | The sentence that excludes it — never the auditor's opinion |
| INACCESSIBLE | The requirement text could not be read | Source, wall type, date attempted, and the fallback used |

**There is no "not assessed".** A requirement you did not reach is a requirement the audit did
not cover, and the summary must say so by count so the reader can reject the audit.

## Coverage-derived findings

Because the plan was generated from an answer store, the audit has evidence a normal audit
does not. Report all four:

| Finding class | Source |
|---|---|
| Sections below 100% coverage | Answer store status counts |
| Values with `confidence: low` | These are guesses in a signed document. List every one |
| Unresolved `conflict` entries | Two sources disagreed and nobody decided |
| `DEFERRED` fields past their due date | Someone promised an answer and the date passed |

**Low-confidence values in an approved plan are the highest-value finding this audit
produces.** They are the numbers most likely to be wrong, in the document most likely to be
believed, and they are invisible to any auditor without the store.

## Scope

Audit the plan repository: every document, runbook and checklist. Scripts and configuration
are evidence only where a document points at them.

State which standard editions you read and which you could not. If a source is paywalled or
login-gated, say so with the date attempted and what you used instead. **Never paraphrase a
standard from memory** — an audit whose requirements are remembered rather than read is an
opinion with a table around it.

## Output

`docs/compliance-audit.md`, containing:

1. Method, and the rule above, stated explicitly.
2. Sources read, with access status per instrument.
3. Per-requirement table with verdicts and quotes.
4. Summary counts by verdict, including anything not covered.
5. The four coverage-derived finding classes.
6. Remediation list, ordered by what blocks approval.

## Red flags

| Thought | Reality |
|---|---|
| "The intent is clearly met" | Then quote the sentence. If you cannot, it is not PASS |
| "This section is thorough, PASS" | Thorough is not a verdict. Which requirement, which sentence |
| "Not applicable — it's a cloud estate" | Quote the scope statement that excludes it, or ask for one |
| "I know what SP 800-53 CP-2 says" | Read it. Remembered requirements are how audits go wrong quietly |
| "I ran out of time, I'll report what I checked" | Report the uncovered count too, so the reader can judge the audit |
| "Coverage is high so the plan is good" | Print the confidence split. Comprehensive guessing is still guessing |
