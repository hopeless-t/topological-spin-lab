# EXP004-C13 — Minimal clean finite scattering calibration

**Date:** 2026-10-07  
**Status:** RESEARCH PASS  
**Scientific transport PASS:** not yet promoted at C13 alone

## Question

Does the C12-selected generic Wilson discretization reproduce the EXP-003/C09
known-answer domain-wall channel in an actual finite two-terminal scattering
problem, while retaining explicit wall identity, propagation direction, and mode
spin polarization?

Frozen parameters:

```text
alpha                 1.0 eV·Å
m0                    0.020 eV
wall width            50 Å
xi                    50 Å
lattice spacing       8 Å
transverse sites      100
circumference         800 Å
wall separation       400 Å = 8 xi
Wilson r              0.5
device length         5 y cells
energy                +0.005 eV
```

The device and both leads use the same clean Hamiltonian and mass texture.

## Authority-crossing execution

```text
workflow              exp004-c13-clean-scattering
run                   37565013203
job                   112610612204
head                  5f49f7e651abfbe5ccb0419decd1bf6fbfe31300
runner                Ubuntu 24.04
Python                3.12.14
Kwant                 1.5.1.dev68+gef12fa0d7
NumPy                 2.5.3
SciPy                 1.18.1
```

Kwant reported that MUMPS was unavailable and used its SciPy solver fallback.
This is a performance/runtime fact, not a physics acceptance criterion.

## Clean scattering result

```text
left incoming channels             1
right incoming channels            1
S matrix shape                      2 x 2
T(L -> R)                           0.9999999999999989
T(R -> L)                           1.0
R(L -> L)                           5.776763101803822e-29
R(R -> R)                           9.681097245055433e-27
||S†S-I||_2                         9.123866703415499e-14
```

The clean finite device therefore reproduces the single-forward-channel known
answer to numerical precision.

## Propagating-mode identity

The +y-oriented right lead contains exactly two propagating mode vectors: one
for each oppositely oriented wall.

### Canonical wall at x = 0 Å

```text
momentum                             +0.04001064305302394
velocity                             +0.12489982549665449
<sigma_x>                            -0.9999992181022046
<sigma_y>                            -1.3551340720034628e-13
<sigma_z>                            -1.4787538080275422e-05
weight within 2 xi of x=0            0.9625477420242844
weight near opposite wall            1.7526379095715182e-05
```

### Opposite wall at x = 400 Å

```text
momentum                             -0.040010643053025825
velocity                             -0.12489982549665302
<sigma_x>                            +0.9999992181022048
<sigma_y>                            +1.1356859249210067e-14
<sigma_z>                            -1.4787538067323091e-05
weight within 2 xi of x=400          0.9625477420242736
weight near canonical wall           1.7526379095713762e-05
```

Thus C13 does not rely on `T≈1` alone.  The transmitting channel is connected to
the expected wall, direction, and EXP-003 spin orientation.

## Required Red Teams

### Lead/device mass-texture mismatch

The finite device mass texture was shifted by half the transverse period while
keeping the leads unchanged.

```text
mass shift                            400 Å
R(L -> L)                             5.478677971242005e-4
R(R -> R)                             5.478677971314022e-4
T(L -> R)                             0.9994521322028727
||S†S-I||_2                           1.5405824540762552e-13
```

The detector therefore distinguishes clean matching from a deliberately broken
lead/device interface.  The mismatch remains unitary; the signal is physical
reflection rather than a solver-integrity failure.

### S-matrix corruption

One S-matrix element was deliberately perturbed by `1e-3`.

```text
corrupted ||S†S-I||_2                 0.001000500125086313
```

The unitarity gate detects the corruption with very large margin relative to the
clean residual.

## C13 decision

All C13 checks pass:

- one incoming channel per lead;
- clean `T≈1`, `R≈0`;
- unitary scattering matrix;
- exactly two spatially separated propagating wall modes;
- canonical wall has negative-x spin and +y velocity;
- opposite wall has positive-x spin and -y velocity;
- lead/device mismatch produces detectable reflection;
- deliberate S-matrix corruption fails the unitarity invariant.

C13 is therefore a **finite-device research PASS**.

## Why C13 alone is not the final scientific PASS

A single energy and device length can still hide a tuned operating point.  The
next gate must demonstrate an acceptance surface rather than a single-point
success and must expose the Wilson-off transport doubler directly.

That gate is EXP004-C14.

## Claim ceiling

C13 supports only a generic clean Wilson-regularized domain-wall calibration.
It does not establish NdBi transport, disorder immunity, arbitrary geometry
robustness, a conserved spin current, or a material-specific conductance.
