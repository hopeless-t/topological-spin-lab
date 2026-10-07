# EXP004-C06 — Compatibility-matrix midpoint

**STATUS:** STABLE LANE PASS / DEVELOPMENT LANE BUILD-ENV CORRECTION

Public Actions run `36116861955` produced two useful facts.

## stable_numpy1

PASS:

```text
Python 3.12.14
Kwant 1.5.0
NumPy 1.26.4
SciPy 1.14.1

propagating modes L/R = 1 / 1
T(L->R)              = 1.0
R(L->L)              = 0.0
||S†S-I||_2           = 0.0
<sigma_z>             = 1.0
```

Actions artifact:
- id: `10855650978`
- zip digest:
  `sha256:340b36303d9f95af3253785af941b2d38e6eb1126bc9ed5674790609ccf3107c`

This proves the required Kwant transport primitives are available on public
GitHub Actions in a stable upstream environment.

## dev_numpy2

The pinned upstream commit was resolved successfully:

```text
ef12fa0d7
Kwant 1.5.1.dev68+gef12fa0d7
```

The build then failed because pip's isolated build environment did not contain
SciPy's Cython declaration file:

```text
scipy/linalg/cython_lapack.pxd not found
```

The selected outer environment already contains SciPy 1.18.1.

Correction: build the pinned development snapshot with
`--no-build-isolation`, matching the current upstream development installation
guidance to reuse the explicitly prepared NumPy/SciPy build environment.

No known-answer expectation changes.

## Council midpoint

**Stability:** stable Kwant is already qualified for the primitive test.

**Stack alignment:** NumPy-2 compatibility is still unresolved; do not choose
the stable NumPy-1 lane as the project dependency yet.

**Reproducibility:** the development source revision is now verified to resolve
to the expected exact commit/version.

**Minimalism:** one more deterministic build attempt is justified. No Monte
Carlo is needed.

Gate:
- stable backend primitive: PASS;
- canonical NumPy-2-aligned backend: PENDING.
