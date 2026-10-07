# EXP004-C05 — Kwant compatibility matrix

**STATUS:** BACKEND QUALIFICATION MATRIX / NO SCIENTIFIC CHANGE

## Trigger

Two deterministic public-CI build failures narrowed the problem:

1. ordinary isolated `pip install kwant==1.5.0` could not see NumPy headers;
2. `--no-build-isolation` exposed the headers, but stable Kwant 1.5.0 then
   failed against NumPy 2.5.x because its generated C code still accesses a
   NumPy descriptor field removed from the NumPy 2 API.

The second failure is consistent with upstream Kwant's later NumPy-2
compatibility work. Current upstream development has explicitly dropped
NumPy<2 support and migrated build machinery.

## Atomic alternatives

### Lane A — stable_numpy1

```text
Python 3.12
Kwant 1.5.0 (stable)
NumPy 1.26.4
SciPy 1.14.1
```

Question: does the released Kwant package pass the required transport primitives
in a deliberately isolated legacy numerical environment?

### Lane B — dev_numpy2

```text
Python 3.12
Kwant development snapshot @ ef12fa0d7
NumPy 2.x
SciPy 1.x
```

Question: does a pinned upstream development snapshot pass the same primitive
test while staying aligned with this repository's NumPy-2 numerical stack?

## Pseudo-Council

**Reproducibility:** do not silently downgrade the whole repository to NumPy 1
just to make one transport backend install.

**Stability:** do not silently adopt an unreleased dependency simply because it
builds against NumPy 2.

**Numerics:** test both environments against the *same* exact known-answer
scattering problem before making a dependency decision.

**Architecture:** backend isolation is acceptable if its evidence boundary is
explicit; the physics model must not depend on package-version folklore.

Council converged on an empirical two-lane qualification matrix.

## Why no Monte Carlo

This is a compatibility truth table, not an uncertain preference problem.
Deterministic external execution dominates Monte Carlo here.

If both lanes pass, a later Council can compare stable-release provenance
against stack alignment and maintenance burden.

If only one passes, that fact constrains the next design.
