# VAL002-C03 — Minimum structure classification

**Date:** 2026-10-07  
**Status:** CLASSIFICATION COMPLETE / NO NEW HAMILTONIAN AUTHORIZED  
**Coefficient fitting:** prohibited

## Question

Given the L0 failures serialized by C02, what is the **minimum kind of added
structure** that could make each target representable?

C03 does not write coupling matrices. It prevents the next stage from treating
every failure as permission to enlarge the Hilbert space.

## Structure classes

```text
C0  existing L0 capability
C1  explicit experimental/material context variable
C2  symmetry-derived term/interface within a 2x2 surface theory
C3  additional orbital / folded-band / AFM-sublattice sector
C4  external material-oracle projection / L3 comparison
```

The ordering is a complexity ladder, not a statement that every target can be
solved by the lowest numbered class.

## Target classification

### T1 — domain / combined-symmetry response

**Minimum candidate structure: C1 + C2**

Required new information:

- explicit surface/domain/symmetry-class input;
- a symmetry-derived rule deciding which terms are allowed in that context;
- a gap response that follows from those allowed terms rather than an arbitrary
  manual `mass` switch.

A larger orbital sector is **not yet earned** by T1 alone.

### T2 — AF surface branch + spin structure

**Minimum candidate structure: C1 + C2; C3 only if branch identity cannot be
represented after the symmetry-derived 2x2 attempt.**

L0 already has Pauli spin observables. The missing first step is to separate:

- AF order;
- surface inversion breaking;
- the declared source branch/context.

A symmetry-derived L1 surface theory is therefore eligible to try T2.

However, if the source-observed band pair requires independent folded/orbital
sectors rather than the two eigenbranches of one surface spinor, that failure
must be serialized and only then may C3 be introduced.

### T3 — quantitative spin-polarized Dirac gap

**Minimum structure: C0**

The two-level gap itself is already representable by L0. No new Hilbert-space
sector is licensed by the `17 ± 2 meV` number alone.

L1/L2 may change the mechanism and fitted value, but T3 cannot be used as an
argument that a larger model is automatically necessary.

### T4 — surface / bulk identity

**Minimum validation structure: C4**

A purely surface effective Hamiltonian may call its states “surface states” by
construction, but this does not reproduce the experimental/material act of
discriminating the targeted state from bulk-derived states.

Therefore any reduced L1/L2 candidate needs an external material-oracle
comparison exposing at least one of:

- layer-resolved spectral weight;
- surface projection;
- orbital/layer-resolved localization;
- an equivalent L3 material quantity.

Adding arbitrary internal states to a reduced model does not by itself satisfy
T4.

### T5 — surface magnetic-order sensitivity

**Minimum candidate structure: C1 + C2**

Required:

- an explicit surface magnetic-order context/order parameter;
- a preregistered coupling rule from that context to the low-energy surface
  Hamiltonian;
- comparison of ordered and suppressed/absent-order contexts.

This is initially a symmetry/context problem, not automatically a new-sector
problem.

### T6 — q-order / surface-state multiplicity

**Two different authorities are required.**

For a **single preregistered q-order slice**:

```text
minimum context requirement      C1
```

An L1 model may be tested as a local effective description of that one slice if
all claims remain explicitly slice-limited.

For **intrinsic q-order-dependent multiplicity / material-wide authority**:

```text
minimum candidate structure      C3 + C4
```

A single context-free 2x2 surface spinor cannot internally generate the
1q/2q/3q band-folding multiplicity hierarchy or verify its bulk Dirac/Weyl
context. Folded/orbital/AFM sectors and an L3 material reference become eligible.

This distinction prevents a narrow L1 fit from silently becoming a universal
NdBi model.

### T7 — termination-dependent 1D edge state

**Deferred.**

When activated, T7 will require at minimum explicit termination/boundary context
(C1), a gapped surface theory consistent with that termination (C2 or higher),
and a spatial boundary problem. It remains outside the current uniform-surface
fit gate.

## C03 decision matrix

```text
target   existing   context   2x2 symmetry   extra sectors   L3 oracle
T1                  REQUIRED  REQUIRED
T2        partial   REQUIRED  TRY FIRST       IF FAILURE
T3        YES
T4                                                    REQUIRED
T5                  REQUIRED  REQUIRED
T6 slice             REQUIRED
T6 wide              REQUIRED                 REQUIRED        REQUIRED
T7        deferred
```

## Architectural consequence

The next material lane is **not**:

```text
L0 failed -> immediately build a large L2 Hamiltonian
```

Instead:

```text
L0 retained as known-answer control

source-conditioned context schema
    -> symmetry-derived L1 attempt for T1/T2/T3/T5 on one frozen slice
    -> compare reduced result against L3 surface/bulk projection for T4
    -> only if L1 fails a preregistered representability/observable gate,
       introduce the smallest C3 sector required
    -> material-wide q-order authority remains downstream
```

This preserves consumer-PC accessibility while keeping a traceable material
oracle.

## What C03 explicitly refuses to invent

Not frozen here:

- magnetic little-group representation matrices;
- allowed `k`-dependent L1 terms;
- exchange-vector couplings;
- surface inversion-breaking coefficient;
- warping coefficients;
- orbital Pauli matrices;
- AFM-sublattice/folding Pauli matrices;
- any numerical fit.

Those must come from a symmetry derivation or a material downfolding step.

## Next gate — VAL002-C04

Freeze the **L1 symmetry derivation input** for one source-conditioned surface
slice.

C04 must identify, from an authoritative crystallographic/magnetic-symmetry
source:

1. the selected surface and momentum expansion point;
2. the declared AF domain/order context;
3. the symmetries preserved and broken at that surface;
4. the representation/action of those symmetries on the low-energy basis, or an
   explicit statement that this information is still unavailable;
5. only after 1–4, the most general low-order 2x2 term classes that are allowed.

If the representation data are insufficient, C04 must return
`SOURCE_EXTRACTION_PENDING` rather than guessing terms.

## Claim ceiling

C03 classifies how much structure each failed target can legitimately request.
It does not establish that L1 will pass, does not authorize an L2 Hamiltonian,
and makes no NdBi transport prediction.
