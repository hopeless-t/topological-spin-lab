# VAL003-C01 — Numerical Trust Pilot

**Date:** 2026-10-07  
**Status:** EXPLORATORY PASS  
**Authority:** research-only

## Question

Can a small, dependency-light verification stack detect and correct numerical
failure modes that ordinary floating-point reductions may hide, while remaining
cheap enough to insert into the high-speed research loop?

## Mechanisms exercised

- Ozaki-Scheme-II-inspired CRT exact integer micro-GEMM;
- unused-modulus corruption check;
- Dekker `TwoProduct` EFT;
- accurate final reduction with `math.fsum`;
- exact `Fraction` dot-product oracle;
- deterministic numerical-kitten adversarial cases;
- metamorphic permutation and power-of-two scaling checks;
- EFT eigenpair residual post-check;
- global-phase invariance of `<sigma_x>`.

## Result

### Exact CRT micro-oracle

```text
bounded random GEMM cases        256
exact matches                    256
capacity-overflow Red Team       PASS (rejected)
corruption Red Team              PASS (detected)
primary CRT dynamic range        1,920,875
maximum tested product bound     60,000
```

### Real cancellation kittens

```text
cases                                      1,024
vector length                                 64
NumPy correctly-rounded matches                0
fsum(rounded products) matches                 0
EFT + fsum matches                         1,024
EFT permutation failures                       0
EFT inverse-power-of-two scale failures        0
```

This demonstrates a concrete failure of the hypothesis that accurate summation
alone is enough. Once the individual products have already lost their low-order
error, `fsum` cannot recover it. C01 therefore promotes **product-error capture
before reduction** as a reusable method atom.

### Complex kittens

```text
cases                              256
vector length                       32
NumPy exact-oracle matches          63
EFT exact-oracle matches           256
```

### Wilson wall eigenpair post-check

```text
matrix dimension                            160
energy                                      0.004997923060880724 eV
ordinary residual norm                      9.99408896597437e-17
EFT residual norm                           9.950098769364557e-17
ordinary/EFT residual max component delta   1.6439679271400473e-18
EFT <sigma_x>                              -0.9999987727276152
global-phase trials                         32
max phase-induced <sigma_x> delta            1.1102230246251565e-16
```

The post-check is consistent with the existing C09/C10 wall-mode observation.
It does not independently solve the eigenproblem; it checks the returned
eigenpair and observable through a different arithmetic path.

## Failure biopsy / method improvement

### Failed assumption

```text
accurate reduction of already-rounded products
    ~= sufficient high-trust dot product
```

was falsified by the numerical kittens.

### Replacement

```text
TwoProduct EFT
    -> retain product + product error
    -> accurate reduction
    -> exact small oracle on suspicious cases
```

This becomes the default lightweight floating-point verification path proposed
by C01.

## Boundaries

The C01 CRT routine is a correctness demonstrator, not the complete published
Ozaki Scheme II. The EFT lane is not NearSum, ExBLAS, or OzBLAS. The recorded
runtime is not the repository's canonical Python 3.12 environment.

No transport, conductance, material, or model-adequacy claim follows from this
pilot.

## Next gate

**VAL003-C02**

1. rerun C01 in the repository Python 3.12 authority-crossing environment;
2. qualify a native/high-precision comparator candidate;
3. widen Red Team inputs to exponent extremes, subnormals, and clustered
   eigenvalues;
4. apply the trust stack to both EXP004 C12 economy/margin candidates;
5. define the minimum verification depth required for each observable class.
