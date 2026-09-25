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


## Bounce EXP004-C01 — contract exploration checkpoint

Completed:
- refreshed transport/Wilson/chiral-channel/spin-observable literature;
- decomposed the minimum EXP-004 problem;
- pseudo-Council converged on a clean two-terminal Wilson domain-wall calibration;
- selected a periodic transverse double-wall geometry to make the compensating channel explicit;
- selected flux-mode spin expectation rather than an unqualified conserved-spin-current claim;
- ran 300,000-draw-per-scenario engineering Monte Carlo over five experiment shapes;
- selected Kwant as the **first backend qualification target**, not as physics authority.

Durable artifacts:
- `docs/EXP-004.md`
- `research/EXP004_LITERATURE_REFRESH_2026-09-25.md`
- `research/exp004_method_selection.py`
- `evidence/EXP-004/design/exp004_method_selection.json`
- `.github/workflows/exp004-contract-research.yml`

Current gate:

```text
EXP-004 Scientific Contract      DRAFT
transport implementation         NOT AUTHORIZED
Kwant backend                    NOT QUALIFIED
acceptance tolerances            NOT FROZEN
```

Next bounce: public-GitHub-Actions backend qualification and minimal
lead/scattering smoke test. No EXP-004 scientific PASS claim yet.


## Bounce EXP004-C03 — backend qualification launched

Fresh exploration confirmed that the current PyPI stable Kwant target is
`1.5.0`. Because the qualification question is deterministic, this bounce
uses a known-answer scattering test rather than Monte Carlo.

Committed:
- `research/exp004_kwant_backend_smoke.py`
- `.github/workflows/exp004-kwant-backend.yml`
- `research/EXP004_KWANT_BACKEND_QUALIFICATION_2026-09-25.md`

The workflow tests public GitHub Actions + Python 3.12 + Kwant 1.5.0 using a
single-propagating-spin-channel chain.

Current gate remains:

```text
Kwant backend QUALIFICATION RUN PENDING
EXP-004 transport implementation NOT AUTHORIZED
```
