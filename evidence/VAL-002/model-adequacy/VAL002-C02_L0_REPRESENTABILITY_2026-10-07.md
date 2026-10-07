# VAL002-C02 — L0 representability falsification

**Date:** 2026-10-07  
**Status:** `L0_MATERIAL_INADEQUATE`  
**Parameter fitting:** not performed  
**L1 Hamiltonian terms:** not proposed

## Question

Can the frozen generic L0 model interface satisfy the material-observable
representability contract frozen in `docs/VAL-002.md` without adding state-space
or context variables?

The tested implementation is:

`src/topological_spin_lab/models/magnetic_surface_dirac.py`

with

```text
H = alpha (kx sigma_y - ky sigma_x) + mass sigma_z
```

and explicit inputs:

```text
kx, ky, alpha, mass
```

The Hamiltonian is a 2x2 complex matrix.

## Why this is a representability audit rather than a fit

A parameter fit can change values inside a model's existing state space. It
cannot create missing variables or sectors.

C02 therefore asks, target by target:

> Could this interface even express the required comparison if its four inputs
> were tuned perfectly?

This avoids the specific failure mode of choosing `mass ≈ 8.5 meV`, reproducing
a `17 meV` two-level gap, and incorrectly promoting the generic model to an NdBi
model.

## Machine-readable evidence

See:

- `evidence/VAL-002/model-adequacy/val002_c02_l0_representability_2026-10-07.json`

## Target audit

### T1 — domain / combined-symmetry response

**NOT_REPRESENTABLE**

L0 has no explicit surface/domain/combined-symmetry coordinate. The caller may
manually choose `mass=0` or `mass!=0`, but there is no model rule connecting an
AF domain or combined-symmetry class to the gap response.

This is a **missing context/coupling structure**, not a bad scalar parameter.

### T2 — AF surface branch + spin structure

**CONTEXT_MISSING**

L0 can compute a vector spin expectation for a two-component spinor. That is a
real capability and must not be discarded.

However, it has no explicit:

- AF-domain context;
- surface inversion-breaking mechanism distinct from the mass;
- orbital/folded-band identity;
- material branch identifier.

Therefore matching an abstract spin texture does not identify the experimentally
observed NdBi AF surface-band pair as a material state class.

### T3 — quantitative spin-polarized Dirac gap

**REPRESENTABLE**

At `k=0`, the L0 gap is:

```text
gap = 2 * |mass|
```

so a `17 meV` two-level gap can be represented numerically by approximately
`|mass| = 8.5 meV`.

This is deliberately recorded as a **positive result**: L0 understands the
mathematics of a magnetic Dirac gap.

It is not evidence that its `mass` parameter is the complete NdBi order
parameter or that the rest of the material spectrum is represented.

### T4 — surface / bulk identity

**NOT_REPRESENTABLE**

L0 contains only the surface spinor. There is no:

- bulk sector;
- layer coordinate;
- orbital projection;
- surface spectral-weight operator;
- surface/bulk hybridization channel.

Therefore it cannot reproduce the source-level act of separating the targeted
surface cone from bulk-derived states.

### T5 — surface magnetic-order sensitivity

**CONTEXT_MISSING**

Again, the caller can manually change `mass`, but L0 has no explicit surface
magnetic-order variable or coupling rule saying what happens when surface order
is suppressed.

Manual parameter switching is not a material response model.

### T6 — q-order / surface-state multiplicity

**NOT_REPRESENTABLE**

L0 has no q-order coordinate and no orbital/folding/magnetic-sublattice sectors.
It cannot generate the 1q/2q/3q-dependent branch multiplicities or bulk
Dirac/Weyl distinctions discussed by the material reference.

### T7 — termination-dependent 1D edge state

**NOT_APPLICABLE_AT_THIS LEVEL**

C01 deliberately deferred this boundary observable. It does not affect the
first uniform-surface decision.

## Failure biopsy

The required C01 targets divide into three classes:

```text
already representable in L0
    T3  two-level magnetic Dirac gap magnitude

observable mathematics exists but material context is missing
    T2  vector spin / branch identity
    T5  magnetic-order response

requires context/state-space not present in L0
    T1  AF domain / combined symmetry
    T4  surface-vs-bulk identity
    T6  q-order / folded-sector multiplicity
```

This distinction matters because not every failure licenses a larger Hilbert
space. Some may first be repaired by an explicit symmetry/context contract at
L1; others may require L2 sectors or an L3 oracle.

## Decision

L0 remains frozen and trusted for:

- generic surface-Dirac mathematics;
- magnetic mass-gap known answers;
- domain-wall known answers;
- regulator validation;
- the promoted generic clean EXP-004 transport calibration.

It is **not eligible for an NdBi material-adequacy PASS**.

No amount of fitting `alpha` and `mass` repairs the missing material contexts and
state-space sectors identified above.

## Next gate

`VAL002-C03` must classify each C02 failure by the **minimum additional model
structure required**:

```text
explicit context only
symmetry-derived 2x2 surface term/interface
additional orbital/folding/AFM sector
external L3 material-oracle projection
```

C03 may define requirements for L1/L2. It may not invent coupling matrices or
fit coefficients.

## Claim ceiling

C02 establishes structural inadequacy of the current L0 interface for the frozen
NdBi material contract. It does not identify the correct L1/L2 Hamiltonian and
does not predict any NdBi transport observable.
