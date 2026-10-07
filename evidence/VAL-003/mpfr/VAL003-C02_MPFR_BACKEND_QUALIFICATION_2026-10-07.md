# VAL003-C02 — MPFR/MPC backend qualification

**Date:** 2026-10-07  
**Status:** QUALIFICATION PASS  
**Authority:** independent numerical adjudication lane for tested operations/ranges

## Purpose

C01 established a dependency-light numerical-trust path:

```text
TwoProduct EFT
-> accurate reduction
-> exact Fraction / bounded CRT oracle on small suspicious cases
```

C02 asks whether an independent multiple-precision backend can adjudicate both
that safe lane and cases deliberately outside its validity range.

## Authority-crossing run

```text
workflow              val003-mpfr
GitHub Actions run    37563577740
job                   112606121293
head                  054d0bf74c31d2e0836569b58397f35cb7497535
runner                Ubuntu 24.04
Python                3.12.14
NumPy                 2.5.3
gmpy2                 2.3.2
MPFR                  4.2.2
MPC                   1.4.1
precision             256 bits
```

The scoped workflow installed `gmpy2==2.3.2` only for this qualification lane;
it is not added to the ordinary experiment dependency path.

## Safe-range numerical kittens

### Normal exponent family

```text
cases                         512
exponent range                [-20, +20]
EFT rejected                    0
EFT matches 256-bit MPFR      512 / 512
NumPy matches MPFR              0 / 512
max |EFT - rounded MPFR|        0
```

### Wide exponent family

```text
cases                         512
exponent range                [-400, +400]
EFT rejected                    0
EFT matches 256-bit MPFR      512 / 512
NumPy matches MPFR              0 / 512
max |EFT - rounded MPFR|        0
```

These are cancellation-heavy adversarial kittens, not a general statement that
ordinary NumPy dot products are defective.

## Boundary Red Team

C02 deliberately probes cases where the pure-Python Dekker splitter is not a
safe authority path.

### Product underflow to zero

```text
a = 2^-800
b = 2^-300
binary64 product lane     rejected by EFT
MPFR result               7.3621518290228626754e-332 (nonzero)
```

### Subnormal product

```text
a = 2^-1022
b = 0.5
binary64 EFT lane         rejected
MPFR result               1.1125369292536006915e-308
```

### Splitter overflow

```text
a = 2^1000
b = 2^-1000
ordinary mathematical product  1
Dekker splitter lane            rejected
MPFR result                     1 exactly
```

### Ordinary binary64 product overflow

```text
a = 2^900
b = 2^200
EFT lane                   rejected
MPFR result                1.3582985290493858493e+331
```

All dangerous C02 cases were **rejected fail-closed by the cheap EFT lane** and
remained finite/adjudicable by MPFR.

This closes a verifier defect discovered during the C02 Red Team: the original
C01 `TwoProduct` reference documented its bounded exponent assumption but did
not enforce it. The implementation now rejects non-finite operands, product
overflow, subnormal/underflowed products, splitter overflow, and non-finite
error terms.

## C12 margin-candidate post-check

The frozen generic EXP-004 candidate `a = 8 Å`, `8 xi`, `r = 0.5` was
post-checked independently at 256-bit precision.

```text
matrix dimension                 200
energy                           0.004998670684251443 eV
EFT residual norm                1.644776539676223e-16
MPFR residual norm               1.6447765396762231742992037899966785312382e-16
binary64 residual-norm delta     0
EFT <sigma_x>                   -0.9999992176075575
MPFR <sigma_x>                  -0.9999992176075576
|spin delta|                     1.1102230246251565e-16
```

The MPFR lane does not independently solve the eigensystem; it independently
recomputes critical reductions and the returned eigenpair residual from the
binary64 matrix/eigenpair.

## Frozen numerical-trust decision

For current generic topological-spin experiments:

```text
N0  NumPy/SciPy                      broad exploration
N1  fail-closed EFT + accurate sum   cheap suspicious-case post-check
N2  Fraction / bounded CRT           exact small oracle
N3  MPFR/MPC 256-bit                 authority-boundary adjudicator
```

Escalation rule:

> If N1 rejects an input or disagrees at a decision boundary, do not repair the
> number heuristically. Escalate the calculation to N2/N3.

ExBLAS and OzBLAS remain useful future differential/performance lanes, but they
are not required to block the next minimal clean EXP-004 implementation.

## Scientific boundary

C02 qualifies a numerical backend relationship. It does not establish:

- correctness or adequacy of the physical model;
- a high-precision independent eigensolver;
- finite-device transmission or conductance;
- disorder/geometry robustness;
- material-specific NdBi behavior.

Those remain separate contracts.
