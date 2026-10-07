# VAL002-C04 — NdBi Dirac-gap source reconciliation gate

**Date:** 2026-10-07  
**Status:** `SOURCE_CONFLICT_OPEN`  
**Model fitting across the conflicting slices:** BLOCKED

## Discovery

The VAL-002 source review exposes two peer-reviewed NdBi Dirac-gap observations
whose numerical values must not be silently merged.

### S1 — Honma et al. 2023

For the NdBi `(001)` surface, the paper explicitly identifies the D1 surface
Dirac cone around surface `Gamma`.

In the AF phase:

```text
domain A / S-broken surface
D1 @ surface Gamma
Dirac gap from EDC       125 ± 5 meV

domain B / S-preserving surface
D1 @ surface Gamma
no clear Dirac gap
```

The paper associates the domain contrast with the combined antiferromagnetic
symmetry

```text
S = Theta T_D
```

where `T_D` translates by a vector that reverses the spin direction.  When `D`
lies in the surface (domain B), `S` is preserved and D1 remains massless; domain
A breaks the surface `S` symmetry and D1 is massive.

### S4 — Fukushima et al. 2026

High-resolution 7 eV spin-ARPES reports:

```text
spin-polarized topological surface Dirac gap     17 ± 2 meV
DFT reference                                     ~12 meV
```

The work explicitly separates the targeted surface Dirac cone from bulk-derived
states and links gap opening to surface magnetic order through temperature and
controlled-contamination tests.

## Why this is a hard research gate

The intervals

```text
S1: [120, 130] meV
S4: [15, 19] meV
```

are not alternative noisy measurements of an obviously common scalar target.

The repository currently lacks sufficient source-native mapping to assert that
they correspond to the same combination of:

- surface termination;
- AF domain / `S`-symmetry class;
- surface Dirac branch identifier;
- momentum/TRIM;
- sample/surface preparation;
- spectral-component assignment;
- measurement matrix elements / photon-energy sensitivity.

Therefore **no model is allowed to minimize a joint loss against 125 meV and
17 meV as though they were measurements of one parameter**.

## Non-exclusive hypotheses to investigate

These are reconciliation hypotheses, not conclusions:

1. the experiments probe different surface/domain/termination contexts;
2. the targeted surface Dirac feature is not the same branch in the two source
   analyses;
3. the earlier EDC peak separation contains additional reconstruction,
   hybridization, or unresolved bulk/surface spectral contributions;
4. photon-energy / matrix-element sensitivity changes the component isolated by
   the measurement;
5. surface preparation, contamination, or magnetic surface order changes the
   relevant low-energy state;
6. the 2026 spin-resolved experiment isolates an intrinsic surface gap that is
   not numerically identical to the larger domain-dependent 2023 spectral
   separation.

C04 does not select among these hypotheses without source evidence.

## Contract repair

VAL-002 now treats quantitative observations as **source-conditioned slices**.

### Slice Q1 — S1 domain-symmetry slice

Use S1 for:

- `(001)` surface;
- D1 around surface Gamma;
- domain-A massive versus domain-B massless contrast;
- the source-native `125 ± 5 meV` domain-A spectral gap only inside that S1
  slice.

### Slice Q2 — S4 spin-resolved intrinsic-gap slice

Use S4 for:

- the spin-resolved surface Dirac feature isolated from bulk-derived states;
- `17 ± 2 meV` as the quantitative target inside the S4 slice;
- surface-magnetic-order sensitivity.

### Prohibited operation

```text
Q1 gap + Q2 gap
-> average / compromise / shared scalar-mass fit
```

is prohibited until the source identity relation is established.

## Impact on model ladder

This conflict makes **context explicitness more important, not less**.

A model that can reproduce one numerical gap only by a free scalar mass is not
material-adequate.  A future reduced model must say which source-conditioned
slice it is modeling and why.

L1 symmetry derivation may proceed first on the well-defined S1 domain contrast,
because S1 supplies explicit surface, TRIM, domain, and combined-symmetry
information.

A quantitative S4 fit must remain a separate target slice until its full
surface/domain/branch identity has been extracted with sufficient provenance.

## Next bounded gate

`VAL002-C05` — derive the symmetry input for the S1 `(001)`, D1@Gamma,
domain-A/domain-B slice without fitting coefficients.

In parallel, a later source-extraction task must map the S4 spin-resolved feature
onto the repository context schema before any unified material fit is eligible.

## Claim ceiling

C04 establishes a source-conditioned conflict and prevents an invalid joint fit.
It does not say that either measurement is wrong, does not choose one value as
universally correct, and does not provide a new NdBi Hamiltonian.
