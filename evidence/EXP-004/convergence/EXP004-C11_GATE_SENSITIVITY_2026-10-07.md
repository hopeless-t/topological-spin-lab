# EXP004-C11 — convergence-gate sensitivity review

**Date:** 2026-10-07  
**Status:** REVIEW COMPLETE / RESEARCH ONLY  
**Convergence contract:** not frozen  
**Finite scattering device:** not authorized

## Question

C10 discovered a candidate gate and showed that the historical C09 point
`a = 10 Å, separation = 8 xi` passes it.

C11 asks:

> Does that conclusion survive reasonable tightening/relaxation of the candidate thresholds,
> or was the gate effectively tuned around the historical point?

## Threshold families

Three deterministic threshold families were applied to the C10 matrix.

### Strict

```text
hybridization gap              <= 7.5e-6 eV
energy relative error          <= 5e-4
velocity relative error        <= 1e-3
|<sigma_x>|                    >= 0.9999
wall weight                    >= 0.95
Wilson pi gap                  >= 0.075 eV
r=0 pi gap                     <= 1e-10 eV
```

Passing points `(a Å, separation/xi)`:

```text
(8, 8), (8, 10), (5, 8), (5, 10)
```

### Nominal

```text
hybridization gap              <= 1e-5 eV
energy relative error          <= 1e-3
velocity relative error        <= 2e-3
|<sigma_x>|                    >= 0.999
wall weight                    >= 0.95
Wilson pi gap                  >= 0.05 eV
r=0 pi gap                     <= 1e-10 eV
```

Passing points:

```text
(12.5, 10),
(10, 8), (10, 10),
(8, 8), (8, 10),
(5, 8), (5, 10)
```

### Relaxed

```text
hybridization gap              <= 2e-5 eV
energy relative error          <= 2e-3
velocity relative error        <= 5e-3
|<sigma_x>|                    >= 0.995
wall weight                    >= 0.90
Wilson pi gap                  >= 0.03 eV
r=0 pi gap                     <= 1e-10 eV
```

Passing points:

```text
(20, 10),
(12.5, 8), (12.5, 10),
(10, 8), (10, 10),
(8, 8), (8, 10),
(5, 8), (5, 10)
```

## Result

The historical C09 point:

```text
a = 10 Å
separation = 8 xi
```

passes nominal and relaxed gates but does **not** pass the strict family.

The nearby point:

```text
a = 8 Å
separation = 8 xi
```

passes strict, nominal, and relaxed families.

Therefore C10 supports the statement that C09 is in a useful convergence regime, but C11
rejects the stronger statement that `10 Å / 8 xi` is insensitive to the threshold choice.

## Council review

### Theorist

The primary low-energy question is continuum wall-mode recovery. Energy and group velocity
therefore belong in the convergence gate.

The finite wall-wall splitting at `ky = 0` is also physical/numerical contamination of the
intended isolated-wall limit and should remain a convergence observable.

### Numerical analyst

`wall_weight` is not monotonic under lattice refinement because it is measured inside a
fixed `2 xi` aperture on a changing discrete grid. It is valuable for **channel identity**
but is a poor primary convergence coordinate.

Likewise, the Wilson Brillouin-edge gap is primarily a **regulator-adequacy** check, not a
continuum low-energy convergence error.

### Red Team

The `r = 0` doubler remains essentially gapless across the matrix. The Wilson-vs-naive
contrast is robust and should remain a mandatory Red Team gate.

### Reproducibility reviewer

A final contract should separate three gate classes:

```text
CONVERGENCE
    energy error
    group-velocity error
    wall-wall hybridization
    refinement stability

IDENTITY
    wall localization
    spin sign / magnitude
    orientation assignment

REGULATOR / RED TEAM
    Wilson pi gap
    r=0 doubler detection
```

This is clearer than treating every check as the same type of threshold.

## Candidate decision frontier

Two points should be carried into the next bounded decision:

### Economy candidate

```text
a = 10 Å
separation = 8 xi
a/xi = 0.20
```

Advantages:

- already qualified in C09;
- lower site count for later finite devices;
- passes the nominal gate.

Risk:

- limited margin under stricter velocity/hybridization thresholds.

### Margin candidate

```text
a = 8 Å
separation = 8 xi
a/xi = 0.16
```

Advantages:

- passes strict/nominal/relaxed families;
- smaller continuum velocity error;
- smaller wall-wall hybridization;
- larger Wilson doubler gap.

Cost:

- finer lattice; a same-size 2D device will contain more sites.

## Next gate

Do **not** freeze `a = 10 Å` simply because it was the historical smoke-test point.

The next bounded decision is:

> Measure reproducible compute cost for the economy (`10 Å`) and margin (`8 Å`) candidates,
> then freeze the cheapest point that preserves the selected accuracy margin.

That is an engineering selection step. It does not require constructing the full scientific
scattering experiment.

## Claim ceiling

C11 establishes only that the canonical discretization choice has a measurable
accuracy-margin tradeoff and that `8 Å / 8 xi` is a stronger convergence candidate.

It does not establish transmission, conductance, disorder robustness, curved-wall behavior,
or NdBi-specific physics.
