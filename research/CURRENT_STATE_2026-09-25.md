# Research Current State — 2026-09-25

**STATUS:** RECOVERY CHECKPOINT / RESEARCH ONLY  
**MAINLINE AUTHORITY:** NONE  
**BASE MAIN:** `e7c0d437b5d96040efd874c4dbe6eb4c0115030d`  
**ACTIVE BRANCH:** `research/exp004-reentry-2026-09-25`

## Why this checkpoint exists

A 2026-09-25 research session was accidentally continued in `hopeless-t/DDS_Vault` under a Decision Archaeology research branch instead of this public physics repository.

That work is **not** imported here because it belongs to a different research domain and would contaminate the scientific lineage of `topological-spin-lab`.

This checkpoint restores the baton to the correct repository and records the exact restart point.

## Verified repository state

Main currently ends at:

```text
e7c0d437b5d96040efd874c4dbe6eb4c0115030d
val001: implement regulator cross-check
```

The reviewed state at that commit is:

- EXP-001 — implemented and frozen reference;
- EXP-002 — implemented and frozen reference;
- EXP-003 — implemented and frozen continuum domain-wall reference;
- VAL-001 — implemented and reviewed;
- Stacey/tangent — selected as stationary spectral validator for the frozen benchmark;
- Wilson `r=0.5` — selected as conventional-lattice transport **candidate**;
- transport authorization — **false**;
- EXP-004 — deferred pending a separate Scientific Contract.

No 2026-09-25 physics result predating this checkpoint is claimed.

## Research boundary

Do not copy Decision Archaeology / Jev-Cua artifacts from `DDS_Vault` into this repository merely to preserve session continuity.

Only reusable **process discipline** may be borrowed when useful, such as:

- short multi-bounce checkpoints;
- source/claim provenance;
- explicit claim ceilings;
- fail-closed research contracts;
- externalized Monte Carlo / numerical computation;
- GitHub-based durable evidence.

Those process patterns are not physics evidence.

## Execution substrate

This repository is public and already contains:

```text
.github/workflows/ci.yml
on:
  push:
  pull_request:
```

The CI uses GitHub-hosted `ubuntu-latest` and currently runs:

- pytest;
- EXP-001;
- EXP-002;
- EXP-003;
- VAL-001;
- VAL-001 threshold-sensitivity analysis.

For this repository, GitHub Actions should be treated as the preferred remote compute/verification substrate when the workload fits GitHub-hosted-runner limits.

## Multi-bounce operating rule

Each meaningful bounce should be short:

```text
fresh read / exploration
  -> atomic decomposition
  -> pseudo-Council until convergence
  -> external calculation / Monte Carlo when useful
  -> durable Git checkpoint
  -> user progress report
  -> stop / refresh context
```

Do not continue multiple long research legs without a visible checkpoint/report.

## Next eligible research question

The repository itself points to EXP-004 as the next physical lane, but VAL-001 explicitly keeps transport unauthorized.

Therefore the next eligible bounce is **not transport implementation**.

It is:

> Explore and freeze the Scientific Contract for EXP-004 spin-resolved transport, including the minimum physical question, observables, known-answer checks, regulator usage, failure modes, literature lineage, and authorization boundary.

Before implementation:

1. refresh relevant transport / Dirac / Wilson / spin-resolved literature;
2. decompose the proposed experiment into physics assumptions, numerical assumptions, observables, and falsification checks;
3. run a pseudo-Council until the contract converges;
4. use Monte Carlo / sensitivity only for engineering-design choices, never as physical evidence;
5. commit the contract as a separate short bounce;
6. only then decide whether EXP-004 implementation is authorized.

## Recovery invariant

```text
correct repository
+ pinned source state
+ explicit scientific boundary
+ visible Git checkpoint
= valid baton
```

This file is a recovery/status artifact, not a new scientific result.
