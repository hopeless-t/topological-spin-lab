# EXP-004 promotion council — 2026-10-07

**Decision:** **PROMOTE**  
**Promoted status:** `PASS — GENERIC CLEAN KNOWN-ANSWER TRANSPORT CALIBRATION`  
**Material-specific authority:** NO  
**Disorder / geometry robustness authority:** NO

## Question before the council

Has the frozen generic Wilson-regularized surface-Dirac model now satisfied the
EXP-004 Scientific Contract strongly enough to promote the narrow clean
known-answer transport claim?

The council is **not** deciding whether a real material is protected, whether
NdBi carries this current, whether disorder is harmless, or whether a physical
spin current is conserved.

## Evidence chain

```text
EXP-003
    frozen continuum domain-wall known answer

VAL-001
    Stacey stationary spectral validator
    Wilson r=0.5 conventional-lattice transport candidate

C09
    Wilson lead-mode physical bridge

C10
    independent NumPy dense oracle
    lattice-spacing + wall-separation/circumference convergence
    r=0 Brillouin-edge doubler control

C11
    threshold-family sensitivity

C12
    freeze a=8 Å, separation=8 xi, r=0.5
    VAL-003 residual post-check

VAL003-C01/C02
    EFT / exact-oracle / MPFR numerical-trust funnel

C13
    first finite clean S matrix
    T/R + mode identity + spin + direction
    lead/device mismatch Red Team
    corrupted-S Red Team

C14
    18-point energy x device-length acceptance surface
    transport-level r=0 doubler: 4 incoming channels / lead

C15
    r={0.4,0.5,0.6} neighborhood x four energies
    all 12 points pass without regulator re-optimization
```

## Contract audit

### Required convergence axes

| Contract axis | Evidence | Council result |
|---|---|---|
| transverse lattice spacing | C10/C11/C12 | satisfied |
| wall separation in `xi` | C10/C11 | satisfied |
| transverse circumference | C10 changes circumference as `2 x wall separation` | satisfied |
| in-gap energy sampling | C14 | satisfied |
| Wilson `r` near 0.5 | C15 | satisfied |
| finite-device length metamorphic | C14, extra beyond minimum | satisfied |

C10's construction explicitly sets

```text
circumference = 2 * wall separation
```

so its `4,6,8,10 xi` separation sweep is also a `8,12,16,20 xi`
circumference sweep.  These axes are coupled in that pilot rather than claimed
as independent two-dimensional scans.

### Numerical vs physical/finite-size errors

The evidence separates:

- continuum energy / velocity discretization error;
- finite wall-wall hybridization;
- Wilson regulator adequacy;
- exact/EFT/high-precision post-check error;
- scattering unitarity error;
- physical lead/device mismatch reflection.

The Kwant SciPy fallback is a direct sparse-solver path rather than an iterative
solver with a user-tuned convergence tolerance.  The council therefore does not
pretend that an iterative `tol` sweep was performed.  Numerical acceptance is
instead bounded by S-matrix unitarity, independent lead/convergence oracles, and
the VAL-003 reduction/residual checks.

### Required Red Teams

#### 1. Wilson disabled

**Satisfied.**  C14 directly observes at `r=0`, `E=0.005 eV`:

```text
incoming channels / lead       4
S matrix                        8 x 8
T(L->R)                         4.0000000000000036
```

versus one incoming channel per lead for the frozen Wilson model.

#### 2. Wall separation reduced until hybridization fails the gate

**Satisfied at the convergence layer.**  C10 measures:

```text
4 xi     hybridization 1.44395e-4 eV
6 xi     hybridization 4.20629e-5 eV
8 xi     hybridization 8.57475e-6 eV
10 xi    hybridization 1.54395e-6 eV
```

The intentionally under-separated points fail the later strict convergence
threshold; they are not silently admitted into the finite-scattering authority
geometry.

#### 3. Opposite wall orientation reverses direction/spin assignment

**Satisfied structurally by the required periodic double-wall geometry.**  The
finite lead contains both orientations simultaneously.  Across C13/C14/C15:

```text
canonical wall      <sigma_x> ~ -1, global velocity > 0
opposite wall       <sigma_x> ~ +1, global velocity < 0
```

This is the finite-device realization of the EXP-003 wall-orientation reversal.
A separate global `m -> -m` run would be redundant for the narrow assignment
claim and is not required for promotion.

#### 4. Lead/device mismatch

**Satisfied.**  C13's half-period central-region mass shift changes
`R(L->L)` from approximately `5.8e-29` to `5.48e-4` while the S matrix remains
unitary.  The harness therefore distinguishes physical mismatch reflection from
solver corruption.

#### 5. S-matrix corruption

**Satisfied.**  A `1e-3` perturbation to one S-matrix element produces

```text
||S†S-I||_2 ~ 1.0005e-3
```

and fails the clean unitarity gate by many orders of magnitude.

## Pseudo-Council

### Continuum / topology reviewer

**PASS.**  The finite-lattice branch retains the EXP-003 wall orientation,
localization, chiral velocity sign, and spin assignment over the tested domain.
The compensating opposite wall is explicit rather than hidden at a boundary.

### Numerical analyst

**PASS with a narrow interpretation.**  Lattice spacing, finite-size
hybridization, energy, device length, and regulator neighborhood have all been
probed.  The numerical-trust funnel provides independent checks of critical
reductions and returned eigenpair residuals.

The clean `T=1` value itself is not treated as deep evidence: identical leads and
device make ballistic perfect transmission the known answer.  The stronger
numerical evidence is that the correct **single channel**, wall identity, spin,
and velocity survive while broken controls are detected.

### Transport reviewer

**PASS for calibration.**  The S matrix is unitary, the clean device has one
incoming channel per lead, and `T≈1/R≈0` survives an energy and device-length
surface.  This qualifies the transport implementation against its intended
known answer.

It does not establish protection against a nontrivial scatterer.

### Red Team

**PASS.**  Every mandatory failure class has an observed detector response:
fermion doubling, wall-wall hybridization, opposite orientation assignment,
lead/device mismatch, and S-matrix corruption.

### Reproducibility reviewer

**PASS.**  C13/C14/C15 use the same pinned Kwant commit
`ef12fa0d7`, NumPy 2.5.3, and SciPy 1.18.1.  C13/C15 ran on Python 3.12.14 while
C14 ran on 3.12.15 with the same decision-level outcome.  Specialist Actions
are path-scoped, and the pinned Kwant wheel is now cacheable for later runs.

### Claim auditor

**PASS only at the contract's exact ceiling.**  The following statement is now
supported:

> In the frozen generic Wilson-regularized surface-Dirac model and clean
> two-terminal geometry, the separated mass-domain-wall channel reproduces the
> expected low-energy chiral transmission and mode spin polarization within the
> tested numerical convergence criteria.

No stronger material, disorder, device, or conserved-spin-current statement is
licensed by this review.

## Promotion decision

The council therefore changes EXP-004 from contract/research qualification to:

```text
EXP-004
PASS — GENERIC CLEAN KNOWN-ANSWER TRANSPORT CALIBRATION
```

This closes the minimal clean transport milestone.

It does **not** close the broader research program.

## Authority boundary after promotion

Still unauthorized as consequences of EXP-004 alone:

- disorder robustness;
- curved/slanted/junction geometry robustness;
- interactions or dephasing;
- material-specific NdBi transport;
- experimental spin polarization claims;
- conserved spin-current claims;
- QAH quantization in a real material.

`VAL-002` remains the independent gate for material adequacy.

Any disorder/geometry experiment must receive its own contract and claim
ceiling rather than inheriting authority silently from this PASS.

## Next research decision

Two independent continuations are now eligible:

1. `VAL002-C01` — freeze the modern NdBi observable target contract before any
   larger material-inspired Hamiltonian is fitted;
2. draft the next generic robustness contract (future EXP-005) without yet
   assuming that clean calibration implies robustness.
