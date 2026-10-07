# Research current state — 2026-10-07

**STATUS:** ACTIVE RESTART / RESEARCH ONLY  
**ACTIVE PR:** #12 `research: restore physics research baton for EXP-004`  
**ACTIVE BRANCH OBSERVED AT RESTART:** `research/exp004-reentry-2026-09-25`  
**OBSERVED HEAD BEFORE THIS RESTART:** `e076dd709991a7df4b0525e86c133090fdb03da7`

This checkpoint restarts the physics program after attention shifted to other implementations.
It preserves the existing scientific boundary and adds a literature delta, a cheaper
independent oracle, and a compact convergence pilot.

## What was already complete

The recovered branch had already progressed beyond the original EXP-004 contract draft.

Verified state:

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
- 2025 direct / zero-field chiral edge transport in MnBi2Te4;
- the existing September 2026 NdBi spin-polarized Dirac-gap result reinterpreted as a
  model-adequacy constraint for later material-informed work.

The refresh does **not** change the frozen generic EXP-001/002/003 parameters.

## EXP004-C10 — independent dense-oracle convergence pilot

A NumPy-only dense Bloch Hamiltonian was constructed independently from Kwant using the same
C09 Wilson lead Hamiltonian.

Artifact:

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

This exposes a clear wall-separation regime rather than treating `8 xi` as an arbitrary
drawing choice.

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

## Candidate convergence gate

The exploratory pilot proposes, but does not yet canonically freeze:

```text
canonical a                         10 Å
minimum wall separation             8 xi
hybridization gap                  <= 1e-5 eV
continuum energy relative error    <= 1e-3
group-velocity relative error      <= 2e-3
|<sigma_x>|                        >= 0.999
wall weight                        >= 0.95
Wilson pi gap                      >= 0.05 eV
r=0 Red Team pi gap                <= 1e-10 eV
```

The canonical C09 point passes all of these candidate gates in the independent pilot.

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
finite scattering device           NOT AUTHORIZED
EXP-004 scientific PASS            NO
```

No transport implementation is promoted by this checkpoint.

## New research axes discovered

The source refresh identifies four downstream lanes:

1. **geometry/path topology** — straight, slanted, curved, transverse walls;
2. **mass amplitude vs sign** — true sign-changing wall versus same-sign magnetic-gap
   suppression as a null/control geometry;
3. **mixed-channel leakage** — preserve channel identity when trivial/bulk-like transport
   coexists;
4. **NdBi model adequacy** — determine the minimum model required before any
   material-informed claim.

These remain downstream of the clean EXP-004 calibration.

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

## EXP004-C11 — threshold sensitivity review

C11 applied strict, nominal, and relaxed threshold families to the C10 matrix.

Result:

```text
10 Å / 8 xi   strict FAIL, nominal PASS, relaxed PASS
8 Å / 8 xi    strict PASS, nominal PASS, relaxed PASS
```

This means the historical C09 point is useful but not threshold-insensitive.

C11 also separates the gate into three classes:

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

## Next bounded bounce

**EXP004-C12 — economy-versus-margin cost qualification**

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
5. only then make an explicit transport-implementation authorization decision.

Do not begin curved-wall, disorder, leakage, or NdBi-specific transport work before this
gate is resolved.

## Claim ceiling

This restart establishes a stronger research process and a candidate convergence regime.
It does not establish finite-device transmission, quantized conductance, disorder
robustness, or a material-specific NdBi transport prediction.
