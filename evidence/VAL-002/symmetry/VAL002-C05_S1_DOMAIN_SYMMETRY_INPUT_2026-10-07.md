# VAL002-C05 — S1 domain-symmetry input for L1

**Date:** 2026-10-07  
**Status:** `SYMMETRY_INPUT_PARTIAL_PASS`  
**Hamiltonian coefficients:** NOT AUTHORIZED  
**Specific Pauli mass axis:** NOT FROZEN

## Selected source-conditioned slice

C05 deliberately uses the best-defined S1 slice rather than mixing the open S1/S4 quantitative-gap conflict.

```text
material              NdBi
surface               (001)
magnetic phase        AF
surface branch        D1
expansion point       surface Gamma
contexts              domain A / domain B
primary source        Honma et al., Nature Communications 14, 7396 (2023)
```

## Frozen source facts

### Paramagnetic / surface-band identity

S1 identifies:

- a single D1 surface Dirac cone around surface Gamma;
- D2/D3 surface Dirac-cone structure around surface M;
- the D1–D3 states as surface-origin states in the source analysis.

C05 uses only D1@Gamma.

### Antiferromagnetic symmetry

Ordinary time reversal `Theta` is broken in the AF phase.

The material nevertheless admits the combined operation

```text
S = Theta T_D
```

where `T_D` is translation by a vector `D` that reverses the AF spin direction.

### Domain B

S1 identifies domain B with AF stacking along an in-plane direction. The spin-reversing translation vector `D` lies in the surface.

Therefore the surface preserves the combined symmetry `S`.

Observed D1 behavior:

```text
D1 @ surface Gamma    massless / no clear Dirac gap
```

The source interprets this as `S`-symmetry protection despite broken ordinary time reversal.

### Domain A

S1 identifies domain A with AF stacking having an out-of-plane component; the topmost surface is ferromagnetically aligned in the source magnetic-structure picture.

The surface does not preserve the spin-reversing translation needed for `S`.

Observed D1 behavior:

```text
D1 @ surface Gamma    massive
source-native gap     125 ± 5 meV
```

The numerical gap value remains confined to the S1-Q1 slice and is not merged with S4's `17 ± 2 meV` spin-resolved slice.

## What this symmetry input already constrains

### Domain-B rule

For an L1 low-energy theory of D1@Gamma, the preserved antiunitary combined symmetry must forbid a constant term that would split/gap the protected D1 pair at Gamma.

In contract language:

```text
context = domain_B / S-preserving
    -> D1 Gamma mass term forbidden by the preserved protecting symmetry
```

This is stronger than manually choosing `mass=0`: the zero gap is tied to a declared symmetry context.

### Domain-A rule

When the surface breaks `S`, that protecting constraint is removed:

```text
context = domain_A / S-broken
    -> a D1 Gamma splitting/mass is symmetry-eligible
```

C05 intentionally says **eligible**, not “must equal `m sigma_z`”. `S` breaking alone does not determine the Pauli-axis representation or coefficient in the repository's future L1 basis.

## What remains insufficient

The primary paper/source extraction used here is enough to freeze the `S`-preserved versus `S`-broken mass rule, but not enough to derive a complete most-general L1 Hamiltonian.

Still required before freezing term classes:

- the surface magnetic little group for the selected domain context;
- representation matrices/actions of the preserved unitary surface symmetries on the chosen D1 basis;
- the chosen basis convention relating physical spin and effective Pauli matrices;
- whether additional symmetry-allowed anisotropy/warping/scalar-dispersion terms enter at the desired order;
- a source-backed mapping of surface inversion breaking and AF order into the same low-energy basis;
- full provenance for the S4 spin-resolved branch before attempting a unified fit.

The supplementary PDF endpoint was identified during C05 but was not available through the current retrieval path. Missing representation information is therefore recorded as `SOURCE_EXTRACTION_PENDING`, not guessed.

## C05 decision

The following L1 interface requirement is now frozen:

```text
surface_context:
    surface = (001)
    branch = D1
    trim = Gamma
    af_domain in {A, B}
    combined_S_preserved in {false, true}

constraint:
    if combined_S_preserved:
        constant_D1_gap_term_at_Gamma = FORBIDDEN
    else:
        constant_D1_gap_term_at_Gamma = ALLOWED_BY_THIS_CONSTRAINT
```

This is a context/symmetry contract, not yet a Hamiltonian implementation.

## Relation to C02/C03

C05 repairs part of the C02 T1 failure at the **contract level**:

- the missing domain variable is now explicit;
- the qualitative massive/massless relation has a source-backed symmetry rule.

It does not yet repair:

- T2 spin-split material branch identity;
- T4 surface/bulk material-oracle identity;
- T5 S4-specific surface-magnetic-order response;
- T6 q-order-wide multiplicity.

## Next gate — VAL002-C06

Acquire or reconstruct the missing surface magnetic little-group / basis-representation information required to enumerate the lowest-order L1 term classes.

C06 must prefer authoritative source/supplement/crystallographic data. If the necessary representation cannot be established, it must preserve `SOURCE_EXTRACTION_PENDING` rather than write a guessed `k.p` model.

## Claim ceiling

C05 establishes only the source-backed domain/context rule that preserves or removes D1 gap protection on NdBi (001). It does not provide a complete L1 Hamiltonian, does not identify the physical Pauli mass axis, does not resolve the 125-meV versus 17-meV source conflict, and does not authorize NdBi transport calculations.
