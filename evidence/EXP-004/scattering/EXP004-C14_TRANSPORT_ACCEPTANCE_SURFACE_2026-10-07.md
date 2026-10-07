# EXP004-C14 — Clean transport acceptance surface

**Date:** 2026-10-07  
**Status:** RESEARCH PASS  
**Scope:** generic clean Wilson-domain-wall model only

## Question

C13 passed at one energy and one device length.  C14 asks whether that result is
structural rather than a tuned numerical point.

The fixed C12 discretization is retained:

```text
lattice spacing       8 Å
wall separation       8 xi
Wilson r              0.5
```

C14 varies only:

```text
energies (eV)         -0.015, -0.010, -0.005, +0.005, +0.010, +0.015
device lengths (ny)   3, 5, 9
```

This produces 18 clean finite-scattering points.  At the reference length
`ny=5`, each energy also receives an explicit wall/spin/velocity mode-identity
check.

A Wilson-off `r=0` transport control is evaluated separately at `E=0.005 eV`.

## Authority-crossing execution

```text
workflow              exp004-c14-transport-surface
run                   37565279689
job                   112611438264
head                  5342981f864b30092152e28686a9250eca724289
runner                Ubuntu 24.04
Python                3.12.15
Kwant                 1.5.1.dev68+gef12fa0d7
NumPy                 2.5.3
SciPy                 1.18.1
```

The Python 3.12 micro-version changed from C13 (`3.12.14`) to C14 (`3.12.15`)
without changing the decision-level result, providing a small incidental runtime
reproducibility cross-check.

## Clean acceptance surface

All 18 clean `(energy, device length)` points pass simultaneously:

- exactly one incoming channel per lead;
- `T(L->R) ≈ T(R->L) ≈ 1`;
- `R(L->L) ≈ R(R->R) ≈ 0`;
- 2x2 scattering matrix;
- unitarity residual far below the C13 tolerance.

Representative points:

```text
ny=3, E=-0.015 eV
    T(L->R)               1.0000000000000009
    R(L->L)               2.278194527345744e-31
    ||S†S-I||_2           8.078397918932878e-14

ny=5, E=+0.005 eV
    T(L->R)               0.9999999999999989
    R(L->L)               5.776763101803822e-29
    ||S†S-I||_2           9.123866703415499e-14

ny=9, E=+0.015 eV
    T(L->R)               0.9999999999999996
    R(L->L)               7.372491890365803e-32
    ||S†S-I||_2           3.5503269335960453e-14
```

Across the full grid the observed unitarity residual remains of order
`1e-13` or smaller.

## Device-length metamorphic check

For an identical clean device, changing only the number of repeated y cells may
change scattering phase but must not change the transmission magnitude.

Maximum minus minimum `T(L->R)` across `ny={3,5,9}`:

```text
E=-0.015 eV        8.881784197001252e-16
E=-0.010 eV        2.220446049250313e-15
E=-0.005 eV        6.661338147750939e-16
E=+0.005 eV        1.9984014443252818e-15
E=+0.010 eV        6.661338147750939e-16
E=+0.015 eV        8.881784197001252e-16
```

The clean transmission result is therefore invariant under the tested device
lengths down to floating-point noise.

## Mode identity across energy

At all six energies for `ny=5`, the right lead contains exactly two propagating
mode vectors and both pass the spatial/spin/velocity identity gate.

For the canonical wall at x=0:

- wall weight remains approximately `0.96236–0.96255`;
- `<sigma_x>` remains essentially `-1`;
- global velocity remains positive, approximately `+0.1241–+0.1249`;
- momentum changes sign with energy, as expected for one chiral branch.

For the opposite wall at x=400 Å:

- wall weight remains approximately `0.96236–0.96255`;
- `<sigma_x>` remains essentially `+1`;
- global velocity remains negative, approximately `-0.1241–-0.1249`;
- momentum mirrors the canonical-wall branch.

Endpoint examples:

```text
canonical wall, E=-0.015 eV
    momentum             -0.12028988177612127
    velocity             +0.12409672688227177
    <sigma_x>            -0.9999999948816766
    wall weight           0.9623591478401918

canonical wall, E=+0.015 eV
    momentum             +0.12028988177612111
    velocity             +0.12409672688227223
    <sigma_x>            -0.9999999948816766
    wall weight           0.962359147840196
```

This is stronger than a transmission-only result: the same physical channel
identity survives across the sampled in-gap energy window.

## Wilson-off transport Red Team

At `r=0`, `E=0.005 eV`, and the same clean geometry:

```text
left incoming channels             4
right incoming channels            4
propagating mode vectors / lead    8
S matrix shape                      8 x 8
T(L->R)                             4.0000000000000036
T(R->L)                             3.9999999999999982
||S†S-I||_2                         4.084183125023295e-13
```

The naive lattice remains perfectly clean and nearly reflectionless, but it
carries **four incoming low-energy channels instead of one**.  This directly
exposes the fermion-doubler contamination at the transport level.

Therefore the Wilson regulator is not merely improving a plot at the
Brillouin-zone edge; it is required to recover the intended low-energy channel
count in this finite-scattering experiment.

## C14 decision

All four C14 gates pass:

```text
all clean grid points pass                  YES
all sampled-energy mode identities pass     YES
device-length transmission metamorphic      YES
Wilson-off adds extra transport channels     YES
```

C14 therefore upgrades C13 from a single-point calibration to a bounded clean
**acceptance surface**.

## Remaining gate before generic scientific promotion

The EXP-004 contract also requires regulator sensitivity around the frozen
`r=0.5` reference without reopening regulator optimization.

The next bounded experiment should vary only a small neighborhood around 0.5,
retain representative positive/negative in-gap energies, and verify that the
one-channel clean result plus mode identity is stable while `r=0` remains the
explicit failed control.

That experiment is EXP004-C15.

## Claim ceiling

C14 establishes clean generic Wilson-model transport consistency only over the
sampled energy/device-length surface.  It does not establish disorder
robustness, arbitrary geometry robustness, interactions, dephasing, NdBi
material adequacy, experimental spin current, or a material-specific
conductance plateau.
