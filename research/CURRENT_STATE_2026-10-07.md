# Research current state — 2026-10-07

**STATUS:** ACTIVE RESTART / RESEARCH ONLY  
**ACTIVE PR:** #12 `research: restart EXP-004 through convergence-gate review`  
**ACTIVE BRANCH:** `research/exp004-reentry-2026-09-25`

This checkpoint restarts the physics program after attention shifted to other implementations.
It preserves the existing scientific boundary and adds a literature delta, a cheaper
independent oracle, a compact convergence pilot, threshold sensitivity, and an explicit
mathematical-model adequacy lane.

## What was already complete

Verified state at restart:

- EXP-001 — implemented + frozen;
- EXP-002 — implemented + frozen;
- EXP-003 — implemented + frozen continuum domain-wall reference;
- VAL-001 — implemented + reviewed;
- Stacey/tangent — stationary spectral validator;
- Wilson `r=0.5` — conventional-lattice transport candidate;
- Kwant primitive backend qualification — complete;
- EXP004-C09 Wilson lead-mode physical bridge — PASS;
- finite scattering device — **NOT AUTHORIZED**.

C09 reported for the canonical `a = 10 Å`, `wall separation = 8 xi` lead:

```text
E(+k)                    +0.0049979231 eV
<sigma_x>                -0.999998773
wall weight               0.96926
Wilson r=0.5 pi gap       0.08119 eV
r=0 Red Team pi gap      ~0
```

The next recorded gate was a compact convergence pilot.

## Main/branch drift

`main` subsequently gained a methodology note transferring regime/knee/topology measurement
discipline from Strata. That change is process input, not physics evidence.

Before merge/promotion, the research branch should be synchronized with current `main`.
This restart does not treat Git ancestry drift as a scientific disagreement.

## 2026-10-07 source refresh

See:

- `docs/research/LITERATURE_DELTA_2026-10-07.md`

Materially relevant additions include:

- 2025 NdBi laser-SARPES spin-splitting work;
- 2024 magnetic-TI nanoribbon domain-wall transport;
- 2025 magnetic-TI domain-wall snake-state transport;
- 2025 AFTI domain-wall topology with explicit crystalline / mirror-symmetry dependence;
- 2025 direct / zero-field chiral edge transport in MnBi2Te4;
- the September 2026 NdBi spin-polarized Dirac-gap result as a model-adequacy constraint for later material-informed work.

The refresh does **not** change the frozen generic EXP-001/002/003 parameters.

## EXP004-C10 — independent dense-oracle convergence pilot

A NumPy-only dense Bloch Hamiltonian was constructed independently from Kwant using the same
C09 Wilson lead Hamiltonian.

Artifacts:

- `research/exp004_convergence_pilot.py`
- `evidence/EXP-004/convergence/exp004_convergence_pilot_2026-10-07.json`
- `evidence/EXP-004/convergence/EXP004-C10_INDEPENDENT_CONVERGENCE_PILOT_2026-10-07.md`

### Independent reproduction

At the C09 canonical point, the independent oracle returns:

```text
E                         0.004997923060880724 eV
<sigma_x>                -0.9999987727276153
wall weight               0.9692577462762243
dE/dky                    0.9987485671342482 eV·Å
Wilson pi gap             0.08118689392021403 eV
naive r=0 pi gap          3.44e-17 eV
```

The energy, spin, localization, and Wilson doubler gap reproduce the previously recorded
C09 values without using Kwant.

### Separation sweep at `a = 10 Å`

```text
separation       hybridization gap
4 xi             1.44395e-4 eV
6 xi             4.20629e-5 eV
8 xi             8.57475e-6 eV
10 xi            1.54395e-6 eV
```

### Lattice-refinement sweep at `8 xi`

```text
a           velocity relative error      hybridization gap
20 Å        5.003e-3                     1.746e-5 eV
12.5 Å      1.955e-3                     1.076e-5 eV
10 Å        1.251e-3                     8.575e-6 eV
8 Å         8.010e-4                     6.845e-6 eV
5 Å         3.129e-4                     4.268e-6 eV
```

The C09 point lies on the convergent side of both the lattice-resolution and wall-separation
knees for the tested observables.

## EXP004-C11 — threshold sensitivity review

C11 applied strict, nominal, and relaxed threshold families to the C10 matrix.

Result:

```text
10 Å / 8 xi   strict FAIL, nominal PASS, relaxed PASS
8 Å / 8 xi    strict PASS, nominal PASS, relaxed PASS
```

This means the historical C09 point is useful but not threshold-insensitive.

C11 separates the gate into three classes:

```text
CONVERGENCE
    continuum energy error
    group-velocity error
    wall-wall hybridization
    refinement stability

IDENTITY
    wall localization
    spin sign / magnitude
    wall assignment

REGULATOR / RED TEAM
    Wilson Brillouin-edge gap
    r=0 doubler detection
```

Artifacts:

- `evidence/EXP-004/convergence/exp004_gate_sensitivity_2026-10-07.json`
- `evidence/EXP-004/convergence/EXP004-C11_GATE_SENSITIVITY_2026-10-07.md`

## Mathematical-model adequacy audit

See:

- `docs/research/MODEL_ADEQUACY_AUDIT_2026-10-07.md`

### Diagnosis

The existing model

```text
H = alpha (kx sigma_y - ky sigma_x) + m(r) sigma_z
```

is still a valid and useful **generic two-component known-answer model**. It should remain
frozen as an analytic / numerical reference.

It is not, however, a sufficient material model of modern NdBi evidence.

The problem is not merely discretization error. The two-component state space cannot
independently represent:

- NdBi orbital content;
- magnetic sublattice / q-order;
- the observed pair of spin-split surface bands;
- surface inversion-symmetry breaking distinct from a magnetic scalar mass;
- AFM band folding / hybridization;
- 1q / 2q / 3q-dependent Dirac / Weyl structure.

Taking `a -> 0` in the Wilson model cannot recover missing state-space dimensions.

### Model ladder

The restart therefore adopts a candidate model hierarchy:

```text
L0  frozen generic 2x2 Dirac + scalar mass known answer
L1  symmetry-derived low-order surface k.p model
L2  minimal multi-sector spin x orbital x AFM/folding reduced model
L3  DFT+U+SOC / Wannier NdBi material-reference tight binding
```

The intended flow is:

```text
L3 material oracle
    -> downfold / fit
L2 smallest material-adequate reduced model
    -> low-cost transport / exploration
L1 symmetry tests
    -> term necessity / failure localization
L0 frozen known answers
    -> analytic and numerical falsification
```

No L1/L2 coupling matrix is frozen yet. Terms must be symmetry-derived or downfolded, not
invented by analogy.

### Proposed VAL-002

Before any material-specific NdBi transport claim, add a **model adequacy** validation lane.

Candidate target observables:

- number of surface branches;
- dispersion near the chosen surface TRIM;
- magnetic Dirac gap;
- full vector spin texture versus momentum;
- magnetic-order reversal response;
- surface / bulk spectral weight;
- surface inversion-breaking sensitivity;
- q-order dependence where available.

Use the smallest model that passes predefined observable gates. Failure of a lower-order
model is evidence, not a reason to silently add complexity.

## Scientific boundary after restart

```text
EXP-004 contract                    DRAFT
Kwant primitive qualification      PASS
Wilson lead-mode bridge            PASS
independent dense reproduction     PASS (research-only)
convergence pilot                  EXPLORATORY PASS
threshold sensitivity review       COMPLETE
convergence criteria               CANDIDATE / NOT FROZEN
economy candidate                  a=10 Å, 8 xi
margin candidate                   a=8 Å, 8 xi
L0 generic model                   VALID / FROZEN REFERENCE
NdBi material adequacy             NOT ESTABLISHED
VAL-002 model-adequacy lane        PROPOSED
finite scattering device           NOT AUTHORIZED
EXP-004 scientific PASS            NO
```

## New research axes discovered

The source refresh identifies downstream lanes:

1. **geometry/path topology** — straight, slanted, curved, transverse walls;
2. **mass amplitude vs sign** — true sign-changing wall versus same-sign magnetic-gap suppression as a null/control geometry;
3. **mixed-channel leakage** — preserve channel identity when trivial/bulk-like transport coexists;
4. **NdBi model adequacy** — determine the minimum model required before any material-informed claim;
5. **AFM order-parameter topology** — distinguish scalar mass walls from vector exchange textures, q-domain boundaries, and symmetry-protected AFTI defects.

The last two are now elevated because model inadequacy cannot be repaired by finer numerical convergence.

## Updated high-speed loop

See `research/HIGH_SPEED_RESEARCH_LOOP.md`.

The key efficiency change is:

```text
cheap independent oracle
-> bounded regime sweep
-> Red Team
-> candidate gate
-> reproducible authority-crossing run
```

rather than sending every exploratory question directly to remote CI.

The model lane adds:

```text
observable target
-> smallest candidate state space
-> symmetry/downfold derivation
-> failure against material oracle
-> complexity only when earned
```

## Next bounded bounces

### EXP004-C12 — economy-versus-margin cost qualification

Compare only:

```text
economy: a = 10 Å, separation = 8 xi
margin:  a = 8 Å,  separation = 8 xi
```

Required:

1. reproduce both candidates in the selected authority-crossing environment;
2. measure deterministic runtime/resource cost with the same physical geometry;
3. keep the gate classes separated;
4. freeze the cheapest candidate that preserves the chosen accuracy margin;
5. only then make an explicit generic finite-transport authorization decision.

### VAL-002-C01 — model-target contract

In parallel, define a material-adequacy contract from the 2025–2026 NdBi observations and
material-reference calculations. Do not yet fit a speculative Hamiltonian.

First freeze:

- selected surface / TRIM;
- magnetic-order assumption;
- target branch count;
- energy-window and gap observables;
- spin-vector observables;
- surface spectral-weight observables;
- claim ceiling.

## Claim ceiling

This restart establishes a stronger research process, a candidate convergence regime, and a
formal diagnosis of the reduced model boundary. It does not establish finite-device
transmission, quantized conductance, disorder robustness, or a material-specific NdBi
transport prediction.
