# EXP004-C15 — Wilson-regulator neighborhood sensitivity

**Date:** 2026-10-07  
**Status:** RESEARCH PASS  
**Purpose:** bounded validation around frozen `r=0.5`, not re-optimization

## Question

Does the generic clean EXP-004 finite-scattering known answer remain stable
under a small Wilson-regulator neighborhood around the already selected
`r=0.5` reference?

C15 deliberately does **not** search for a better regulator value.

Fixed geometry:

```text
lattice spacing       8 Å
wall separation       8 xi
device length         ny=5
```

Sensitivity matrix:

```text
Wilson r              0.4, 0.5, 0.6
energy (eV)           -0.015, -0.005, +0.005, +0.015
```

Twelve clean scattering points are evaluated.  Each point must preserve:

- one incoming channel per lead;
- `T≈1`, `R≈0`;
- scattering unitarity;
- exactly two propagating wall-mode vectors;
- canonical-wall localization, negative-x spin, and +y velocity;
- opposite-wall localization, positive-x spin, and -y velocity.

## Authority-crossing execution

```text
workflow              exp004-c15-regulator-neighborhood
run                   37565675609
job                   112612705539
head                  89195a7c0c39d03a105a2c62a1a8fa3c4a8f606f
runner                Ubuntu 24.04
Python                3.12.14
Kwant                 1.5.1.dev68+gef12fa0d7
NumPy                 2.5.3
SciPy                 1.18.1
```

The run also introduced a cache for the pinned Kwant wheel.  The first run built
and saved the wheel under the cp312 / NumPy-2.5.3 / commit-ef12fa0d7 cache key;
subsequent compatible specialist lanes can reuse it.

## Result

All 12 neighborhood points pass.

### r = 0.4

```text
all sampled energies pass                YES
max |T(L->R)-1|                           1.1102230246251565e-15
max R(L->L)                               1.720176780690593e-28
max ||S†S-I||_2                           1.8522167284472316e-13
minimum |<sigma_x>|                       0.9999994990833196
minimum canonical-wall weight             0.9624212391067098
minimum opposite-wall weight              0.9624212391067037
```

### r = 0.5

```text
all sampled energies pass                YES
max |T(L->R)-1|                           4.440892098500626e-16
max R(L->L)                               4.789859451786691e-29
max ||S†S-I||_2                           2.3011483928537937e-13
minimum |<sigma_x>|                       0.9999992181022044
minimum canonical-wall weight             0.9623591478401919
minimum opposite-wall weight              0.9623591478401824
```

### r = 0.6

```text
all sampled energies pass                YES
max |T(L->R)-1|                           8.881784197001252e-16
max R(L->L)                               5.874519541328018e-29
max ||S†S-I||_2                           4.4433797093262943e-13
minimum |<sigma_x>|                       0.999998875448202
minimum canonical-wall weight             0.9622827248290247
minimum opposite-wall weight              0.9622827248290174
```

No decision-level change occurs over the tested neighborhood.

## Failed regulator control retained from C14

The neighborhood sensitivity must be interpreted together with the deliberately
unregularized transport control:

```text
r = 0
E = +0.005 eV
incoming channels / lead     4
T(L->R)                       4.0000000000000036
```

Thus the successful `0.4–0.6` neighborhood is not evidence that the Wilson term
is irrelevant.  Removing it entirely produces the expected low-energy doubler
contamination directly in the transport channel count.

## Decision

C15 supports the statement:

> The frozen `r=0.5` regulator choice is not a fine-tuned clean-transport point
> within the tested neighborhood.  The intended one-channel wall-mode result
> and its spin/spatial identity survive `r=0.4–0.6`, while `r=0` remains a
> clearly failed transport control.

`r=0.5` remains frozen.  C15 does not select a new optimum.

## Next gate

The bounded numerical and transport work now supports an explicit promotion
review of the **generic clean known-answer EXP-004 contract**.

The promotion review must audit the full evidence chain and the Red Team matrix,
and it must distinguish a clean calibration PASS from any claim of disorder or
material robustness.

## Claim ceiling

C15 establishes regulator-neighborhood stability only for the frozen generic
clean model and sampled energies.  It does not establish disorder robustness,
geometry robustness, interactions, dephasing, material adequacy, NdBi
transport, or a conserved spin current.
