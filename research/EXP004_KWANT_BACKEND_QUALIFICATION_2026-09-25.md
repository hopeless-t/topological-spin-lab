# EXP004-C03 — Kwant backend qualification design

**STATUS:** BACKEND QUALIFICATION SPIKE / NO EXP-004 PHYSICS CLAIM

## Fresh exploration

Current PyPI stable Kwant is `1.5.0` and is distributed there as a source
tarball. The current Kwant development documentation also makes clear that a
native compiler/scientific build stack is part of source installation on
Linux.

Therefore the first qualification question is deliberately operational:

> Can public GitHub-hosted Ubuntu + Python 3.12 build/import Kwant 1.5.0 and
> reproduce a tiny deterministic scattering known answer?

## Why no Monte Carlo in this bounce

The decision uncertainty was already addressed in EXP004-C01.

This bounce has a deterministic capability question. A known-answer test is
stronger than random sampling here, so the Catfood simulation asset is not
admitted for this subproblem.

The existing numerical-compute discipline is reused:

```text
known answer
+ numerical residual
+ explicit tolerance
+ external execution evidence
```

## Smoke model

A clean one-dimensional chain with two local orbitals:

- spin-up onsite = 0;
- spin-down onsite = +5;
- hopping = `-I`;
- energy = 0.

At E=0 only the spin-up band propagates.

Known answer:

```text
left propagating modes  = 1
right propagating modes = 1
T(L->R)                 = 1
R(L->L)                 = 0
S†S                     = I
<sigma_z>               = +1
```

This tests:
- Kwant build/import;
- lead modes;
- scattering matrix;
- transmission/reflection;
- wave-function access;
- multi-orbital spin expectation.

It does **not** test the Wilson domain wall.

## Pseudo-Council

**Transport:** use the smallest exact scattering problem before importing the
EXP-004 Hamiltonian.

**Numerics:** include S-matrix unitarity, not only T≈1.

**Spin:** include a two-orbital mode so the backend must preserve orbital/spin
structure.

**Reproducibility:** pin Kwant stable version and Python major/minor; record
NumPy/SciPy runtime versions in evidence.

**Minimalism:** do not add Kwant to `pyproject.toml` yet. Qualification comes
before making it a project dependency.

Council converged.

## Gate

PASS means only:

> Kwant 1.5.0 is usable on the selected public GitHub Actions substrate for the
> minimal capabilities needed to start an EXP-004 implementation spike.

PASS does not authorize EXP-004 scientific acceptance.
