# Research current state — 2026-10-07

**STATUS:** EXP-004 GENERIC CLEAN MILESTONE PROMOTED  
**ACTIVE PR:** #12 `research: promote generic clean EXP-004 transport calibration`  
**ACTIVE BRANCH:** `research/exp004-reentry-2026-09-25`

## Canonical program state

```text
EXP-001                         PASS / FROZEN
EXP-002                         PASS / FROZEN
EXP-003                         PASS / FROZEN CONTINUUM REFERENCE
VAL-001                         PASS / REVIEWED
Stacey/tangent                  STATIONARY SPECTRAL VALIDATOR
Wilson r=0.5                    FROZEN CLEAN-TRANSPORT REFERENCE
VAL-003                         NUMERICAL-TRUST FUNNEL QUALIFIED THROUGH C02
EXP-004                         PASS — GENERIC CLEAN KNOWN-ANSWER CALIBRATION
VAL-002                         MATERIAL-ADEQUACY CONTRACT NOT YET FROZEN
NdBi material adequacy          NOT ESTABLISHED
disorder/geometry robustness    NOT AUTHORIZED
```

## EXP-004 promoted claim

The 2026-10-07 promotion council authorizes only:

> In the frozen generic Wilson-regularized surface-Dirac model and clean
> two-terminal geometry, the separated mass-domain-wall channel reproduces the
> expected low-energy chiral transmission and mode spin polarization within the
> tested numerical convergence criteria.

The full canonical contract and claim ceiling are now in `docs/EXP-004.md`.

## Frozen generic clean geometry

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
```

## Evidence chain closed on 2026-10-07

### C10 — independent convergence oracle

A NumPy-only dense Hamiltonian independently reproduced the Kwant lead result
and mapped lattice-spacing and wall-separation/circumference regimes.

Selected strict-margin candidate after C11/C12:

```text
a = 8 Å
separation = 8 xi
r = 0.5
```

The 8 Å point costs 1.5625x matrix storage and 1.953125x under the deterministic
dense `n^3` proxy relative to 10 Å while moving away from the strict threshold
frontier.

### C13 — first finite clean scattering calibration

At `E=+0.005 eV`, `ny=5`:

```text
incoming channels / lead          1
S matrix                           2 x 2
T(L->R)                            0.9999999999999989
R(L->L)                            5.776763101803822e-29
||S†S-I||_2                        9.123866703415499e-14
canonical <sigma_x>               -0.9999992181022046
opposite <sigma_x>                +0.9999992181022048
```

The two propagating modes remain spatially assigned to opposite walls with
opposite global velocity signs.

Required negative controls also passed:

- half-period lead/device mismatch -> measurable reflection `~5.48e-4`;
- deliberate `1e-3` S-matrix corruption -> unitarity residual `~1.0005e-3`.

### C14 — acceptance surface

Clean grid:

```text
energy (eV)          -0.015, -0.010, -0.005, +0.005, +0.010, +0.015
device length ny      3, 5, 9
```

All 18 points preserve one incoming channel per lead, `T≈1`, `R≈0`, and
unitarity. At the reference length all six energies preserve wall/spin/velocity
identity.

The `r=0` transport Red Team fails strongly:

```text
incoming channels / lead          4
S matrix                           8 x 8
T(L->R)                            4.0000000000000036
```

This exposes lattice fermion doubling directly at the finite-transport level.

### C15 — regulator neighborhood

Without reopening optimization:

```text
r                    0.4, 0.5, 0.6
E (eV)              -0.015, -0.005, +0.005, +0.015
```

All 12 points preserve the one-channel clean result and the spatial/spin/
velocity identity. `r=0.5` remains frozen.

## VAL-003 numerical-trust state

The active verification funnel is:

```text
N0  NumPy / SciPy broad exploration
 -> numerical kittens
N1  fail-closed TwoProduct EFT + accurate reduction
N2  exact Fraction / bounded CRT micro-oracle
N3  MPFR / MPC 256-bit authority-boundary adjudicator
 -> failure biopsy
 -> durable regression kitten
```

C01 demonstrated bounded CRT exact micro-GEMM and cancellation-heavy EFT
post-checks.

C02 qualified:

```text
gmpy2              2.3.2
MPFR                4.2.2
MPC                 1.4.1
precision           256 bits
```

The C02 Red Team found a defect in the original lightweight EFT verifier: its
exponent-domain assumptions were documented but not enforced. The implementation
now fails closed on underflow/subnormal products, product overflow, splitter
overflow, non-finite operands, and non-finite error terms, then escalates to the
stronger oracle.

## Research-harness improvements discovered by the loop

### Current-push CI instead of cumulative-PR path matching

The long-lived draft PR exposed a GitHub Actions failure mode:
`pull_request.paths` observes the cumulative PR diff, so once a heavy specialist
file changed, unrelated later commits could keep retriggering that lane.

The branch now uses current-push path filtering for ordinary and specialist
research lanes. Documentation/evidence-only checkpoints no longer need to rerun
the full numerical stack.

### Cached pinned Kwant wheel

The C15 lane introduced a cache key for the pinned research build:

```text
Linux-x64-cp312-kwant-ef12fa0d7-numpy-2.5.3
```

The first run built and saved the wheel. Future compatible specialist runs can
reuse it instead of rebuilding Kwant from source.

## Main-branch synchronization

The research branch was previously one methodology commit behind `main`.

The Strata v0.1.39 methodological transfer note was carried into the branch and
an explicit merge commit synchronized current main.

Current ancestry state after synchronization:

```text
behind main       0
merge base         current main 6fe3b8e1c74e78e329a1b0fa229834122f22af91
```

The branch remains ahead with the EXP-004/VAL-003 research series. This Git
synchronization does not change the scientific result.

## Model-adequacy boundary

The generic model remains only the L0 known-answer reference:

```text
L0  generic 2x2 Dirac + scalar mass known answer
L1  symmetry-derived low-order surface k.p
L2  minimal spin x orbital x AFM/folding reduced model
L3  DFT+U+SOC / Wannier material oracle
```

No L1/L2 material Hamiltonian is frozen.

The next material-specific step must be `VAL002-C01`: freeze the observable
contract first, then allow model complexity only when a lower level fails that
contract.

Candidate target observables remain:

- number of surface branches;
- dispersion near the selected surface TRIM;
- magnetic Dirac gap;
- full vector spin texture versus momentum;
- magnetic-order reversal response;
- surface/bulk spectral weight;
- surface inversion-breaking sensitivity;
- q-order dependence where supported by evidence.

## Claim ceiling after EXP-004 promotion

Still not established:

- NdBi transport;
- material-specific conductance;
- disorder immunity;
- curved/slanted/junction geometry robustness;
- interactions or dephasing robustness;
- experimental 100% spin polarization;
- conserved spin current;
- real-material QAH quantization.

Clean-calibration authority must not leak into those later questions.

## Next bounded research work

### Primary: VAL002-C01

Freeze a modern NdBi material-observable target contract from current literature
and material-reference calculations. Do **not** fit or invent a larger
Hamiltonian in the same step.

### Secondary: future EXP-005

Draft a generic robustness contract with its own failure controls and claim
ceiling. A clean EXP-004 PASS is only the prerequisite calibration, not evidence
that disorder or geometry perturbations are harmless.
