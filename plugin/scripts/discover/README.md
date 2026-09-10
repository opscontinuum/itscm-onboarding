# Discovery, one directory per environment

Discovery answers a narrow question: what is actually running, so that the interviews start
from a list instead of a blank page. How you answer it depends entirely on where the workload
lives, so each environment gets its own directory and its own scripts.

```
discover/
├── README.md          this file: the contract every environment meets
├── test-readonly.sh   runs each environment's own read-only proof
└── oci/               Oracle Cloud Infrastructure (implemented)
    ├── discover.sh
    ├── emit-inventory.sh
    ├── emit-dr-resources-env.sh
    ├── test-readonly.sh
    └── lib/readonly-guard.sh
```

**Only `oci/` exists today.** AWS, Azure, VMware and Kubernetes are the obvious next ones and
none of them are written. That is a gap this file names rather than hides: a plan for a
workload on any of them is built from what the teams bring to the room, which is the ordinary
case anyway and is what [the tabletop](../../../docs/manual/01-discovery.md) assumes.

## What an environment directory provides

Four things, and the fourth is not optional.

**`discover.sh`** — the entry point. It takes the scope to walk, the locations to walk it in,
and `--out <directory>`, and it supports `--dry-run`, which prints every command it would run
without running any of them. The dry run is what you show a customer before you point anything
at their production estate.

**An inventory** written into `--out`, in Markdown, listing what was found. This becomes
Appendix H of the plan.

**A gap list** written into `--out`, saying what the walk could not determine. This matters
more than the inventory. A resource nobody can name and a standby that was supposed to exist
are the questions the technical sessions exist to answer, and a walk that reports only what it
found is quietly claiming the rest is absent.

**`test-readonly.sh`** — the proof that the whole thing is read-only, runnable by anybody
before they trust it against a live environment. The OCI one checks three things, and a new
environment should check the same three:

1. the guard refuses a write verb, proved by a self-test rather than by inspection;
2. no script calls the provider's CLI outside the guard, proved by grepping the sources;
3. every command a dry run emits is a read.

## The rule that does not vary

**Discovery never changes anything.** Every call is a list or a get, and the guard is what
makes that structural instead of aspirational: scripts do not call the provider's CLI
directly, they call the guard, and the guard refuses any verb that is not a read. A reviewer
checks one file to know the blast radius.

This is the part to copy first when adding an environment. The verbs differ (`aws ... describe`,
`kubectl get`, `govc ls`) and the shape does not.

## Adding one

Copy `oci/`, replace the guard's allowed verbs and the walk itself, keep the four outputs, and
add the directory. `test-readonly.sh` at this level finds it without being told: it runs the
proof in every environment directory it can see, so a new environment is covered by the suite
the moment it exists.
