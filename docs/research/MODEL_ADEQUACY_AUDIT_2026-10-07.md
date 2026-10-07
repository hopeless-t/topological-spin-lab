# Mathematical model adequacy audit — 2026-10-07

## Status

**RESEARCH AUDIT / NO EXISTING FROZEN RESULT INVALIDATED**

This audit asks whether the mathematical model hierarchy in `topological-spin-lab`
is still adequate after the 2025–2026 NdBi and antiferromagnetic-topological-domain-wall
literature refresh.

The answer is deliberately split:

- the frozen 2x2 Dirac models remain useful and valid as **generic known-answer references**;
- they are **not an adequate material model of NdBi**;
- future material-informed work should therefore add a model hierarchy rather than mutate
  the frozen references in place.

## Current model

The trusted low-energy reference begins from

```text
H0(k) = alpha (kx sigma_y - ky sigma_x)
```

and adds a magnetic mass

```text
Hm(k) = H0(k) + m sigma_z.
```

EXP-003 promotes `m -> m(x)` to a sign-changing scalar mass wall. VAL-001 / EXP-004
then introduce a Wilson lattice regulator for numerical work.

The state vector has only the two spinor components acted on by the Pauli matrices
`sigma_i`.

## What this model is still good for

The 2x2 model remains a very strong reference for:

- the local surface-Dirac dispersion;
- spin-momentum locking in an idealized surface cone;
- opening a Dirac gap with an exchange-like mass;
- the Jackiw-Rebbi / mass-sign-change known answer;
- chirality reversal under mass-wall reversal;
- testing lattice regulators and fermion doubling;
- calibrating clean numerical transport machinery;
- constructing cheap independent analytic / dense numerical oracles.

Those uses should remain frozen.

## What changed in the scientific target

### NdBi surface spin splitting

The 2025 NdBi laser-SARPES work reports two antiferromagnetic-state surface bands with
opposite spin polarization. The measured spin polarization is antisymmetric about the
surface time-reversal-invariant momentum and is reproduced by DFT / tight binding for a
single-q antiferromagnetic structure. The interpretation requires the combination of
surface inversion-symmetry breaking and antiferromagnetic order.

A single generic 2x2 surface cone cannot independently represent:

- magnetic sublattice / q-order;
- multiple surface branches;
- orbital content;
- surface inversion-breaking terms distinct from magnetic mass;
- band-folding-generated surface states.

### NdBi magnetic Dirac gap

The September 2026 NdBi laser spin-ARPES result observes a spin-polarized topological
surface Dirac cone with a 17 +/- 2 meV gap and reports a DFT prediction of about 12 meV.
The gap is linked experimentally to surface magnetic order.

This makes `m sigma_z` a useful local phenomenological language, but it does not show that
`m` is the complete NdBi order parameter or that the rest of the NdBi spectrum can be
ignored.

### Multi-q / orbital topology

First-principles NdBi work distinguishes 1q, 2q, and 3q antiferromagnetic orders. It finds
band-folding / hybridization effects and Dirac or Weyl phases depending on magnetic order.
The published Wannier tight-binding construction retains Nd s-d-f and Bi p orbitals with
SOC rather than reducing the material to a two-component spinor.

Therefore magnetic order in future NdBi work must be an explicit model input, not merely
a sign choice for one scalar mass.

### Modern AFTI domain-wall theory

Recent antiferromagnetic-topological-insulator work shows that domain-wall topology may
depend on crystalline / mirror symmetry and the microscopic AFTI construction. Depending
on the model, a magnetic domain wall may be gapped in its interior with chiral termination
states or may itself form a two-dimensional embedded semimetal.

Therefore

```text
scalar mass sign change -> one chiral wall channel
```

is a valuable known answer, but is not a universal mathematical description of every AFTI
domain wall.

## Adequacy diagnosis

The current model is not "obsolete" in the sense of being wrong. It is obsolete only if
it is asked to carry a material-specific claim that requires degrees of freedom it does not
contain.

The central failure mode is **state-space under-resolution**, not lattice-spacing error.

Refining `a -> 0` in the existing 2x2 Wilson model cannot recover:

- missing orbitals;
- missing magnetic sublattices;
- missing 1q/2q/3q order;
- missing surface inversion asymmetry;
- missing bulk-band / surface-state hybridization.

Numerical convergence and model adequacy must therefore be separate gates.

## Proposed model ladder

### L0 — generic two-component Dirac known answer

Keep the existing frozen model:

```text
H_L0 = alpha (kx sigma_y - ky sigma_x) + m(r) sigma_z.
```

Authority:

- generic low-energy mathematics;
- numerical-regulator validation;
- clean known-answer transport calibration.

Not authorized:

- NdBi material prediction.

### L1 — symmetry-derived surface k.p model

Construct the most general low-order surface Hamiltonian allowed by the selected surface
and magnetic little group, rather than adding terms by taste.

Generic bookkeeping form:

```text
H_L1(k) = epsilon0(k) I + d_x(k) sigma_x + d_y(k) sigma_y + d_z(k) sigma_z
```

where the allowed functions `d_i(k)` are determined by symmetry.

Candidate effects to test for necessity include:

- anisotropic velocity tensor;
- particle-hole / scalar dispersion;
- exchange-vector orientation;
- symmetry-allowed higher-order warping;
- surface-inversion-breaking spin splitting.

This level is still a phenomenological surface theory. It must not be called an NdBi model
until fitted / validated against a material reference.

### L2 — minimal multi-sector AFM surface model

Introduce the minimum additional pseudospin sectors required by the data, e.g. orbital and
magnetic-sublattice / folded-band sectors in addition to real spin.

Schematic state space:

```text
|psi> in spin x orbital x (optional AFM-sublattice / folded-band) space
```

with Pauli families kept distinct, e.g.

```text
sigma : real spin
tau   : orbital / inverted-band sector
rho   : AFM sublattice or folding sector, only if required
```

The actual Hamiltonian terms must be derived from the magnetic space group / little group
or downfolded from a material tight-binding model. They must not be invented from analogy.

Acceptance targets should include both energy dispersion and vector spin texture.

### L3 — NdBi material-reference tight binding

Use a DFT+U+SOC-derived Wannier / tight-binding model as the material oracle.

The existing literature provides precedent for a model retaining Nd s-d-f and Bi p orbitals
and explicitly distinguishing magnetic q-order.

L3 does not need to become the default transport engine. Its role can be:

```text
material oracle
    -> downfold / fit
L2 reduced model
    -> low-cost exploration / transport
L0-L1 known answers
    -> analytic and numerical falsification
```

This preserves consumer-PC accessibility while keeping a traceable path to the material.

## Domain-wall model upgrade

A future material-aware domain wall should promote the order parameter beyond a scalar
`m(x)` where evidence requires it.

Conceptually:

```text
m(x)                       scalar reference (L0)
M(r)                       exchange vector / texture
N_AFM(r)                   staggered AFM order parameter
q / domain label           magnetic-order sector
surface termination        boundary-condition input
```

The exact coupling matrices belong to the L2/L3 derivation and are not frozen by this
audit.

This allows the repository to distinguish:

- mass-amplitude suppression without sign reversal;
- exchange-vector rotation;
- AFM domain reversal;
- q-domain boundaries;
- surface-step / termination defects.

These are physically different defects and should not all be serialized as one scalar
`tanh` wall.

## Proposed validation lane — VAL-002

Before any NdBi-specific transport claim, add a model-adequacy validation lane.

Candidate question:

> What is the smallest model that reproduces the experimentally / material-reference
> required low-energy NdBi surface observables without sacrificing the frozen generic
> known answers?

Candidate comparison:

```text
L0 generic 2x2
L1 symmetry-complete 2x2 surface k.p
L2 minimal multi-sector AFM model
L3 DFT/Wannier material reference
```

Compare at minimum:

- number of surface branches;
- energy dispersion near the selected TRIM;
- direct magnetic gap;
- spin-polarization vector versus momentum;
- response to reversing the relevant magnetic order;
- surface / bulk localization or spectral weight;
- sensitivity to surface termination / inversion breaking;
- magnetic-q-order dependence where available.

Use complexity penalties so that a larger model is accepted only when a lower level fails a
predefined observable gate.

## Model-selection rule

Adopt the smallest adequate model, not the newest or largest model.

```text
L0 survives target observables -> keep L0
L0 fails, L1 survives          -> promote L1
L1 fails, L2 survives          -> promote L2
L2 is checked against L3       -> material-informed claim may become eligible
```

Failure of a lower-level model is itself useful evidence and should be serialized.

## Interaction with EXP-004

Do not retroactively invalidate EXP-004's clean generic calibration.

Instead separate two questions:

```text
EXP-004A: does the frozen generic Wilson-Dirac wall transport correctly?
VAL-002:  is that reduced model adequate for the material question?
EXP-004B or later: transport in the smallest material-adequate model
```

This prevents material complexity from destroying a clean numerical known answer while
also preventing the known answer from being overclaimed as NdBi.

## Immediate recommendation

1. Finish C12 only as a generic L0 transport-calibration decision.
2. In parallel, start VAL-002 as a **model adequacy** lane; do not wait for disorder / curved
   walls.
3. Treat the 2025 single-q spin-splitting data and 2026 magnetic-gap data as the first L1/L2
   target observables.
4. Recover / reconstruct a reproducible material-reference L3 target from published
   DFT/Wannier results before fitting a reduced NdBi model.
5. Only after VAL-002 promote geometry, disorder, and network experiments to a
   material-informed lane.

## Claim ceiling

This audit does not provide a new NdBi Hamiltonian and intentionally does not guess
symmetry-allowed coupling matrices. It establishes that the existing 2x2 model is a generic
reference, identifies the missing degrees of freedom, and defines a falsifiable route to the
smallest material-adequate model.
