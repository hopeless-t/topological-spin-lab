# EXP004-C12 — Economy-versus-margin cost + numerical-trust selection

**Date:** 2026-10-07  
**Status:** RESEARCH PASS / DISCRETIZATION CANDIDATE FROZEN  
**Scientific transport PASS:** NO

## Question

C11 carried forward two bounded candidates:

```text
economy: a = 10 Å, wall separation = 8 xi
margin:  a =  8 Å, wall separation = 8 xi
```

C12 asks whether the stricter numerical margin of `8 Å / 8 xi` is worth its
additional computational cost when both candidates are checked in the same
Python 3.12 CI environment and post-checked through the VAL-003 EFT lane.

## Authority-crossing run

```text
GitHub Actions run    37563173107
job                  112605033806
head                  c288fbbbe383fa353233c79bec362f804b143da7
Python                3.12.14
NumPy                 2.5.3
```

The run also passed the frozen EXP-001/002/003 baseline, VAL-001, and VAL-003
C01 before executing C12.

## Economy candidate — 10 Å / 8 xi

```text
matrix dimension                160
nx                               80
E                               0.004997923060880724 eV
energy relative error           4.153878238552858e-4
velocity                        0.9987485671342482 eV·Å
velocity relative error         1.2514328657518003e-3
<sigma_x> EFT                  -0.9999987727276152
wall weight                     0.9692577462762242
hybridization gap               8.574754644204381e-6 eV
Wilson pi gap                   0.08118689392021403 eV
r=0 pi gap                      3.443101746981668e-17 eV
EFT eigenpair residual norm     9.601961333961899e-17
nominal gate                    PASS
strict gate                     FAIL
```

Descriptive same-run dense eigensolver timing:

```text
median  5.664433 ms
min     4.972673 ms
max     9.317761 ms
```

## Margin candidate — 8 Å / 8 xi

```text
matrix dimension                200
nx                              100
E                               0.004998670684251443 eV
energy relative error           2.65863149711415e-4
velocity                        0.9991990280582788 eV·Å
velocity relative error         8.009719417212402e-4
<sigma_x> EFT                  -0.9999992176075575
wall weight                     0.9625477428011343
hybridization gap               6.8445973165133076e-6 eV
Wilson pi gap                   0.10604403226491933 eV
r=0 pi gap                      5.341531182848012e-19 eV
EFT eigenpair residual norm     1.644776539676223e-16
nominal gate                    PASS
strict gate                     PASS
```

Descriptive same-run dense eigensolver timing:

```text
median  7.588878 ms
min     6.781951 ms
max     7.748075 ms
```

## Deterministic cost frontier

The timing measurements are descriptive only. The deterministic structural
cost ratios are the selection authority:

```text
margin / economy transverse sites          1.25
margin / economy dense matrix elements     1.5625
margin / economy complex128 matrix bytes   1.5625
margin / economy dense n^3 proxy           1.953125
same-extent 2D site-count proxy             1.5625
same-run timed eigensolver median ratio     1.3397418594  (descriptive)
```

Thus the margin candidate preserves the strict C11 gate and the VAL-003
post-check at a deterministic dense spectral cost increase below 2x.

## Council decision

### Theorist

Both candidates recover the intended low-energy wall mode, but `8 Å` has lower
energy/velocity error and lower wall-wall hybridization.

### Numerical analyst

`10 Å` remains useful for cheap exploration but sits close enough to the strict
velocity/hybridization frontier that it is a weaker canonical discretization.
The `8 Å` point survives strict, nominal, and relaxed families.

### Red Team

Both candidates continue to detect the `r=0` doubler control while the Wilson
candidate remains gapped at the Brillouin-zone edge.

### Verification reviewer

Both eigenpairs survive the independent VAL-003 EFT residual post-check. C12
does not replace the pending VAL003-C02 independent MPFR/native-backend lane.

### Cost reviewer

The strict-margin candidate costs less than 2x under the deterministic dense
`n^3` proxy and 1.5625x in same-extent 2D site-count proxy. This is an acceptable
price for moving away from the observed threshold boundary.

## Frozen engineering decision

For the **generic EXP-004 clean calibration lane**:

```text
lattice spacing       a = 8 Å
wall separation       8 xi
Wilson parameter      r = 0.5
```

is now the frozen **discretization candidate**.

`10 Å / 8 xi` remains an economy/reference point for exploratory sweeps, not the
preferred authority-crossing discretization.

## Authorization boundary after C12

C12 is sufficient to authorize implementation of the **minimal clean finite
scattering calibration** defined by the EXP-004 Scientific Contract, provided
that:

- the finite-device implementation inherits `a = 8 Å`, `8 xi`, `r = 0.5`;
- it preserves the known-answer clean geometry only;
- it records scattering unitarity, transmission/reflection, mode identity, and
  mode spin polarization;
- it includes the contract's lead/device mismatch and S-matrix/unitarity Red
  Teams;
- it remains research-only until its own acceptance evidence is reviewed;
- no disorder, curved-wall, material-specific NdBi, or robustness claim is
  added under this authorization.

This is **implementation authorization**, not a transport-result PASS.

## Remaining numerical-trust gate

VAL003-C02 should still qualify an independent MPFR/MPC or comparable native
high-precision backend before a finite-device result is promoted to canonical
scientific evidence.

## Claim ceiling

C12 establishes a bounded engineering choice of discretization and authorizes
the next minimal implementation step. It does not establish finite-device
transmission, conductance quantization, disorder immunity, geometry robustness,
or material-specific NdBi transport.
