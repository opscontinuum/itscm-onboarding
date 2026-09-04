---
name: itscp-dependencies
description: Use when mapping what one system needs from another, when the recovery order across several systems has to be established, when checking whether recovery targets are consistent between a system and the things it depends on, or when working out what is needed in order to recover a system as opposed to run it.
---

# itscp-dependencies

Builds the dependency graph in `portfolio.toml`, and it is one question that makes it worth
doing separately from everything else:

> **What does this system need in order to be *recovered*, as distinct from what it needs in
> order to *run*?**

Every interview in every continuity toolkit asks the second. Almost none ask the first. The
gap between them is where real invocations fail.

**Read first:** `itscp-method-interview`. Run after `itscp-portfolio` has the register and
before or alongside the per-system interviews.

**Interviewee:** the application owner and the infrastructure owner for each system, together
where possible. Runtime dependencies are usually known; recovery dependencies usually are not,
and the conversation that surfaces them needs both people in it.

**Time:** 20–30 minutes per system, faster once the pattern is understood.

---

## Three kinds of edge

| Kind | Means | Found by asking |
|---|---|---|
| `runtime` | Needed for the system to function | "What does this call, read from or authenticate against?" |
| `recovery` | Needed in order to **recover** the system | "Walk me through recovering this. What do you open, log into, or pull from?" |
| `data` | Exchanges data with it; an interface, not a prerequisite | "Who sends you files, and who is waiting on yours?" |

Plus a criticality: `hard` means it does not work at all without it; `soft` means degraded but
functional. Only hard edges constrain the recovery order.

---

## Eliciting recovery dependencies

Do not ask "what are your recovery dependencies". Nobody has a list. Walk them through the
recovery and catch the tools they mention in passing:

> "It's 3am, the region is gone, and you're recovering this. Talk me through the first ten
> minutes. What do you open first?"

Then the four follow-ups that catch what the walkthrough missed:

1. **"Where is the runbook you'd be following?"** If it is in the source control server, and
   that server is in the failed region, the instructions are inside the outage.
2. **"How do you log in to the cloud console to do any of this?"** If it federates through
   the identity system, and identity is a system on the register, the first thing to recover
   is the thing you cannot authenticate to.
3. **"Where do the credentials and certificates come from?"** A secrets store is a recovery
   dependency of everything that holds a credential, which is everything.
4. **"If you had to rebuild rather than fail over, where do the artefacts come from?"** The
   artefact repository becomes a hard recovery dependency the moment the answer is "rebuild".

**These four find something in almost every engagement.** They are not exotic; they are the
ordinary consequence of tooling being used to build the systems it also has to recover.

### The trap they exist to catch

Two systems each needing the other to be recovered first is a deadlock, and neither plan can
see it because each is separately reasonable. The validator raises `recovery-cycle` as an
error. **The fix is never to reorder the pair** — it is to put what one of them needs (a
runbook copy, a break-glass credential, console access that does not federate) somewhere
outside the cycle.

---

## Checking the graph

```bash
python3 itscp_portfolio.py portfolio.toml
```

| Finding | Severity | Means |
|---|---|---|
| `rto-inversion` | ERROR | A system claims to be back before something it cannot run without |
| `recovery-cycle` | ERROR | Systems that each need the other recovered first. Nothing can start |
| `wave-inversion` | ERROR | A hard dependency scheduled after its dependant |
| `unknown-dependency` | ERROR | An edge pointing at a system not in the register |
| `runtime-cycle` | WARNING | Mutually dependent at runtime. Recoverable together, not in an order |
| `wave-concurrency` | WARNING | A hard dependency in the same wave. Ordering inside a wave is unspecified |
| `undeclared-shared-service` | WARNING | Four or more systems hard-depend on it, but it is classed as an ordinary app |

### Handling an inversion

An RTO inversion is a contradiction between two signed figures, so it is **not yours to
resolve.** Take it back:

> "Order management is signed at four hours. It cannot log in without the identity database,
> which is signed at eight. One of those two numbers has to move. Which, and who signs it?"

Three legitimate outcomes: the dependency's target tightens, the dependant's relaxes, or the
dependency is broken (a cached credential, a read-only mode, a queue that absorbs the gap).
The third is the best answer and the one nobody reaches for unaided — offer it.

**Never resolve an inversion by editing a number.** The register would validate and the plan
would still be impossible; you would have deleted the finding rather than the problem.

---

## What to record

Per edge: `on`, `kind`, `criticality`, and a note saying *what breaks* without it. The note is
what survives a re-organisation; the slug is just a pointer.

Keep `soft` honest. "Degraded but functional" must mean somebody can still do their job, not
that the system technically starts. If the answer is "it comes up but nobody can use it",
that edge is `hard`.

---

## Red flags

| Thought | Reality |
|---|---|
| "They listed their integrations, the graph is done" | Integrations are `data` edges. You have not asked what recovery needs |
| "The runbook location is a documentation detail" | It is a hard recovery dependency. It decides whether the plan is readable during the outage |
| "Everything depends on identity, that's not worth recording" | Recording it is what puts identity in wave 0 and catches the login circularity |
| "This dependency is soft, they can work around it" | Ask whether anyone can do their job. If not, it is hard |
| "I'll relax the RTO to clear the inversion" | Two owners signed those figures. Deleting the finding is not fixing the problem |
| "A recovery cycle just means recover them together" | If each needs the other *first*, together does not help. Break it from outside |
