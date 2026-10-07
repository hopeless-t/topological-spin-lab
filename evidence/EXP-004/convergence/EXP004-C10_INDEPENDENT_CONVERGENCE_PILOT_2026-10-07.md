# EXP004-C10 — independent convergence pilot

**Date:** 2026-10-07  
**Status:** EXPLORATORY PASS  
**Authority:** research-only; candidate thresholds are not frozen  
**Finite scattering device:** not authorized

## Purpose

C09 demonstrated that the Wilson `r=0.5` lead reproduces the expected low-energy wall mode
and gaps the y-direction fermion doubler.

C10 asks the next narrower question:

> Is the C09 canonical discretization (`a = 10 Å`, wall separation `8 xi`) inside a
> numerically converged regime for the lead-mode observables that matter before a finite
> scattering device is constructed?

The calculation is intentionally independent of Kwant. It reconstructs the same finite
transverse Bloch Hamiltonian directly with NumPy dense diagonalization.

## Model

The inherited lattice model is

```text
H(k) = alpha/a [sin(kx a) sigma_y - sin(ky a) sigma_x]
     + {m(x) + r alpha/a [(1-cos(kx a)) + (1-cos(ky a))]} sigma_z
```

with the periodic two-wall profile inherited from C09.

Frozen inherited parameters for this pilot:

```text
alpha = 1.0 eV Å
m0 = 0.020 eV
w = 50 Å
xi = alpha/m0 = 50 Å
r = 0.5
probe ky = 0.005 Å^-1
```

Sweep:

```text
a = {20, 12.5, 10, 8, 5} Å
wall separation = {4, 6, 8, 10} xi
```

## Independent C09 reproduction

At `a = 10 Å`, separation `8 xi`:

```text
canonical wall E           +0.004997923060880724 eV
opposite wall E            -0.004997923060880719 eV
canonical <sigma_x>        -0.9999987727276153
opposite <sigma_x>         +0.9999987727276152
canonical wall weight       0.9692577462762243
dE/dky                      0.9987485671342482 eV Å
Wilson pi gap               0.08118689392021403 eV
naive r=0 pi gap            3.4431e-17 eV
```

These values reproduce the previously recorded C09 lead smoke without using Kwant.

That is an implementation-independence check, not a new physical result.

## Wall-separation regime at `a = 10 Å`

| separation | zero-k wall-wall hybridization | velocity relative error |
|---:|---:|---:|
| `4 xi` | `1.44395e-4 eV` | `1.760e-3` |
| `6 xi` | `4.20629e-5 eV` | `1.291e-3` |
| `8 xi` | `8.57475e-6 eV` | `1.251e-3` |
| `10 xi` | `1.54395e-6 eV` | `1.250e-3` |

The finite-size effect drops strongly between `6 xi` and `8 xi` and continues to decrease
at `10 xi`.

## Lattice-resolution regime at `8 xi`

| `a` | continuum-energy abs. error | velocity relative error | hybridization | Wilson pi gap |
|---:|---:|---:|---:|---:|
| `20 Å` | `8.304e-6 eV` | `5.003e-3` | `1.746e-5 eV` | `0.03189 eV` |
| `12.5 Å` | `3.245e-6 eV` | `1.955e-3` | `1.076e-5 eV` | `0.06136 eV` |
| `10 Å` | `2.077e-6 eV` | `1.251e-3` | `8.575e-6 eV` | `0.08119 eV` |
| `8 Å` | `1.329e-6 eV` | `8.010e-4` | `6.845e-6 eV` | `0.10604 eV` |
| `5 Å` | `5.193e-7 eV` | `3.129e-4` | `4.268e-6 eV` | `0.18082 eV` |

The C09 point is not the most refined point, but the tested low-energy observables continue
smoothly toward the continuum expectation under refinement.

## Candidate gate

C10 proposes the following gate for review:

```text
a = 10 Å
wall separation >= 8 xi
hybridization gap <= 1e-5 eV
continuum energy relative error <= 1e-3
group velocity relative error <= 2e-3
|<sigma_x>| >= 0.999
wall weight >= 0.95
Wilson pi gap >= 0.05 eV
r=0 pi gap <= 1e-10 eV
```

The canonical C09 point passes all candidate checks.

## Why the thresholds are not frozen here

This run was used to **discover the regime and achievable error scale**.

Freezing thresholds in the same step that discovers them risks post-hoc tuning. The next
bounce must therefore:

1. review whether each threshold corresponds to a physically/numerically meaningful error;
2. run threshold sensitivity;
3. reproduce the matrix in the selected authority-crossing environment.

Only then may the convergence contract be promoted.

## Red Team

The `r=0` y-Brillouin-edge control remains essentially gapless throughout the tested
lattice spacings, while the Wilson `r=0.5` model is gapped.

At the canonical point:

```text
Wilson r=0.5 pi gap = 8.1187e-2 eV
naive r=0 pi gap    = 3.44e-17 eV
```

The regulator distinction therefore remains visible across the convergence exercise.

## Claim ceiling

This pilot supports only:

> The previously chosen C09 lead discretization appears to lie inside a stable convergence
> regime for the tested lead-mode observables, and a concrete candidate convergence gate
> can now be reviewed independently.

It does **not** establish:

- a finite-device S matrix;
- transmission `T = 1`;
- quantized conductance;
- disorder robustness;
- curved-wall invariance;
- material-specific NdBi transport.
