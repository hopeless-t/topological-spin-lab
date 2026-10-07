# Research current state — 2026-10-07

**STATUS:** ACTIVE RESTART / RESEARCH ONLY  
**ACTIVE PR:** #12 `research: restart EXP-004 with model and numerical trust gates`  
**ACTIVE BRANCH:** `research/exp004-reentry-2026-09-25`

This checkpoint records the restarted physics program after the 2026-10-07
literature/model refresh, convergence work, and numerical-trust program.

## Preserved baseline

- EXP-001 — implemented + frozen;
- EXP-002 — implemented + frozen;
- EXP-003 — implemented + frozen continuum domain-wall reference;
- VAL-001 — implemented + reviewed;
- Stacey/tangent — stationary spectral validator;
- Wilson `r=0.5` — conventional-lattice transport candidate;
- Kwant primitive backend qualification — complete;
- EXP004-C09 Wilson lead-mode bridge — PASS;
- EXP-004 scientific finite-device PASS — **NO**.

The frozen generic model remains a useful L0 known-answer model:

```text
H = alpha (kx sigma_y - ky sigma_x) + m(r) sigma_z
```

It is not promoted as an adequate modern NdBi material model.

## Literature and model-adequacy delta

See:

- `docs/research/LITERATURE_DELTA_2026-10-07.md`
- `docs/research/MODEL_ADEQUACY_AUDIT_2026-10-07.md`

The restart now separates:

```text
L0  generic 2x2 Dirac + scalar mass known answer
L1  symmetry-derived surface k.p candidate
L2  minimal spin x orbital x AFM/folding reduced model candidate
L3  DFT+U+SOC / Wannier NdBi material oracle
```

No speculative L1/L2 Hamiltonian is frozen. A proposed VAL-002 lane must first
freeze the NdBi observable/model-adequacy contract.

## EXP004-C10 — independent convergence pilot

A NumPy-only dense Bloch oracle independently reproduced C09 and swept lattice
spacing plus wall separation.

At `8 xi` wall separation:

```text
a           velocity relative error      hybridization gap
20 Å        5.003e-3                     1.746e-5 eV
12.5 Å      1.955e-3                     1.076e-5 eV
10 Å        1.251e-3                     8.575e-6 eV
8 Å         8.010e-4                     6.845e-6 eV
5 Å         3.129e-4                     4.268e-6 eV
```

## EXP004-C11 — threshold sensitivity

```text
10 Å / 8 xi   strict FAIL, nominal PASS, relaxed PASS
8 Å / 8 xi    strict PASS, nominal PASS, relaxed PASS
```

The gate remains separated into convergence, identity, and regulator/Red-Team
classes.

## VAL-003 — numerical trust / multi-oracle verification

See:

- `docs/VAL-003.md`
- `research/NUMERICAL_TRUST_FUNNEL.md`
- `docs/research/NUMERICAL_TRUST_DELTA_2026-10-07.md`

The working funnel is now:

```text
ordinary calculation
-> numerical kittens
-> suspicious cases
-> fail-closed EFT product-error capture + accurate reduction
-> exact small oracle (Fraction / bounded CRT)
-> MPFR/MPC authority-boundary adjudicator
-> failure biopsy
-> durable regression kitten
```

The verifier is a falsification system, not a majority vote.

### VAL003-C01 — lightweight trust pilot

C01 added:

- Dekker `TwoProduct` EFT;
- accurate `math.fsum` reduction;
- exact `Fraction` real/complex dot oracles;
- Ozaki-Scheme-II-inspired bounded CRT exact micro-GEMM;
- independent unused-modulus corruption check;
- deterministic cancellation kittens;
- metamorphic permutation, scaling, and global-phase checks;
- EFT eigenpair residual / spin post-check.

Python 3.12 CI reproduced:

```text
CRT bounded GEMM                  256 / 256 exact
capacity overflow                rejected
corrupted reconstruction         detected
real kittens EFT                1024 / 1024 exact-oracle matches
real NumPy dot                      0 / 1024 on adversarial kittens
fsum(rounded products)              0 / 1024 on adversarial kittens
complex kittens EFT               256 / 256 exact-oracle matches
complex NumPy dot                  63 / 256 on adversarial kittens
```

C01 falsified the shortcut assumption that accurate summation can recover bits
already discarded during multiplication. The cheap trust path therefore starts
with product-error capture.

### VAL003-C02 — MPFR/MPC qualification

C02 qualified a scoped 256-bit `gmpy2` / MPFR / MPC lane on GitHub Actions:

```text
run       37563577740
job       112606121293
Python    3.12.14
gmpy2     2.3.2
MPFR      4.2.2
MPC       1.4.1
precision 256 bits
status    QUALIFICATION PASS
```

Safe-domain adversarial results:

```text
normal exponent kittens [-20,+20]    EFT 512 / 512 matches MPFR
wide exponent kittens   [-400,+400]  EFT 512 / 512 matches MPFR
```

C02 also discovered and repaired a verifier defect: the original pure-Python
Dekker lane documented its exponent assumptions but did not enforce them. The
current `TwoProduct` now fails closed on non-finite inputs, product overflow,
subnormal/underflowed products, splitter overflow, or non-finite error terms.

Boundary Red Teams such as `2^-800 * 2^-300`, `2^-1022 * 0.5`,
`2^1000 * 2^-1000`, and `2^900 * 2^200` are now rejected by the cheap EFT lane
and remain adjudicable by MPFR.

The C12 margin eigenpair was also independently post-checked:

```text
EFT residual norm     1.644776539676223e-16
MPFR residual norm    1.6447765396762231742992037899966785312382e-16
EFT <sigma_x>        -0.9999992176075575
MPFR <sigma_x>       -0.9999992176075576
```

Frozen numerical-trust policy:

```text
N0  NumPy/SciPy                    broad exploration
N1  fail-closed EFT                cheap suspicious-case check
N2  Fraction / bounded CRT         exact small oracle
N3  MPFR/MPC 256-bit               authority-boundary adjudicator
```

ExBLAS/OzBLAS remain optional future differential/performance lanes, not a
blocker for the next bounded physics step.

## EXP004-C12 — cost + trust selection

C12 compared only the two C11 candidates on Python 3.12 CI and applied VAL-003
post-checks.

### Economy — `10 Å / 8 xi`

```text
matrix dimension              160
energy relative error         4.154e-4
velocity relative error       1.251e-3
hybridization gap             8.575e-6 eV
EFT residual                  9.602e-17
nominal                       PASS
strict                        FAIL
```

### Margin — `8 Å / 8 xi`

```text
matrix dimension              200
energy relative error         2.659e-4
velocity relative error       8.010e-4
hybridization gap             6.845e-6 eV
EFT residual                  1.645e-16
nominal                       PASS
strict                        PASS
```

Deterministic cost ratios, margin / economy:

```text
transverse sites              1.25
matrix elements / storage     1.5625
dense n^3 proxy               1.953125
same-extent 2D sites proxy    1.5625
```

The same-run eigensolver median ratio was ~1.34, but runtime is descriptive and
is not the selection authority.

### Frozen C12 engineering selection

For the generic clean EXP-004 calibration lane:

```text
lattice spacing      a = 8 Å
wall separation      8 xi
Wilson parameter     r = 0.5
```

is now the preferred frozen discretization candidate. `10 Å / 8 xi` remains an
economy/reference point for exploration.

C12 authorizes implementation of the **minimal clean finite scattering
calibration only**. This is not a transport-result PASS.

The implementation must inherit the frozen discretization and record at least:

- scattering unitarity;
- transmission/reflection;
- propagating mode count;
- spatial mode identity;
- mode spin polarization;
- lead/device mismatch Red Team;
- deliberate S-matrix/unitarity corruption detection.

No disorder, curved-wall, robustness, or material-specific NdBi claim is
authorized by C12.

## CI / research-loop efficiency

The normal PR CI no longer duplicates branch push CI. Push CI is restricted to
`main`, and concurrency cancels obsolete in-flight PR runs.

The higher-cost MPFR lane is separately scoped to numerical-trust changes, so
ordinary short research checkpoints do not install or run it unnecessarily.

## Current authority map

```text
EXP-001/002/003 frozen references          PASS
VAL-001 regulator cross-check              PASS
EXP004-C09 lead bridge                     PASS
EXP004-C10 convergence exploration         PASS
EXP004-C11 threshold review                COMPLETE
EXP004-C12 discretization selection        RESEARCH PASS
frozen generic discretization              8 Å / 8 xi / r=0.5
minimal clean device implementation        AUTHORIZED
finite-device scientific transport PASS    NO
VAL-002 NdBi model adequacy                 NOT ESTABLISHED
VAL-003 C01 lightweight verifier            REPRODUCED
VAL-003 C02 MPFR/MPC comparator             QUALIFIED
```

## Next bounded physics bounce

**EXP004-C13 — minimal clean finite scattering calibration**

Implement only the clean known-answer device already defined by the EXP-004
Scientific Contract using `a = 8 Å`, `8 xi`, `r = 0.5`.

The result must remain research-only until its scattering, mode-identity, spin,
Red-Team, and VAL-003 evidence are reviewed.

In parallel, VAL002-C01 may freeze the modern NdBi material-observable target
contract, but it must not silently alter the generic EXP-004 model.

## Claim ceiling

The restart now establishes a stronger research process, a frozen generic
numerical discretization candidate, and a qualified multi-oracle numerical
trust ladder. It does not yet establish finite-device transmission, quantized
conductance, disorder/geometry robustness, or a material-specific NdBi
transport prediction.
