# VAL003-C01 — CI reproduction confirmation

**Date:** 2026-10-07  
**Status:** CI REPRODUCTION PASS / RESEARCH ONLY  
**PR:** #12  
**Branch head:** `925e67672c277bd2399c37915b70da4f9b476040`  
**GitHub Actions run:** `37562840318`  
**Job:** `112603843747`

## Environment

```text
runner image     Ubuntu 24.04
Python           3.12.14
NumPy            2.5.3
SciPy            1.18.1
pytest           9.1.1
```

## Repository regression status

```text
pytest                         82 passed
EXP-001                        PASS
EXP-002                        PASS
EXP-003                        PASS
VAL-001                        PASS
VAL-001 threshold sensitivity completed
VAL-003 C01 pilot             EXPLORATORY_PASS
```

The VAL-003 addition therefore did not break the frozen baseline experiments or
VAL-001 validation lane in this run.

## VAL-003 reproduced observations

### CRT micro-oracle

```text
bounded integer GEMM exact matches       256 / 256
capacity-overflow Red Team               rejected
corrupted reconstruction Red Team        detected
CRT dynamic range                        1,920,875
maximum tested absolute product bound    60,000
```

### Real numerical kittens

```text
cases                                     1,024
length                                       64
NumPy exact-oracle matches                    0
fsum(rounded products) matches                0
EFT + accurate reduction matches          1,024
EFT permutation failures                      0
EFT inverse-power-of-two scale failures       0
```

### Complex numerical kittens

```text
cases                                       256
length                                       32
NumPy exact-oracle matches                   63
EFT exact-oracle matches                    256
```

### Wilson wall post-check

```text
matrix dimension                           160
energy                                     0.004997923060880724 eV
ordinary residual norm                     9.581176755113525e-17
EFT residual norm                          9.601961333961899e-17
max residual-vector delta                  1.7314580629624672e-18
EFT <sigma_x>                             -0.9999987727276152
global-phase trials                        32
max phase-induced <sigma_x> delta          1.1102230246251565e-16
```

The small residual difference relative to the earlier exploratory local run is
expected environment/backend variation and remains far below the current C01
post-check bound. The decision-level conclusions are unchanged.

## Authority boundary

This confirmation establishes reproducibility of the **C01 exploratory
verification mechanism** on the repository's Python 3.12 CI substrate.

It does not yet promote VAL-003 to canonical numerical authority because an
independent native/high-precision backend has not been qualified and the Red
Team has not yet been widened to exponent extremes, subnormals, and clustered
eigenproblems.

## Next gate

`VAL003-C02` should qualify an independent native/high-precision backend and
cross-check the lightweight EFT/exact-oracle lane before canonical promotion.

`EXP004-C12` should apply the now-reproduced VAL-003 post-checks to the economy
`10 Å / 8 xi` and margin `8 Å / 8 xi` candidates while measuring their actual
compute-cost frontier.
