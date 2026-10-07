# Numerical-trust method delta — 2026-10-07

> Methods only. These sources do not provide physics evidence for EXP-004.

## Why this refresh matters

The existing high-speed loop already preferred cheap independent oracles before
remote CI. The missing piece was a clearer arithmetic trust ladder for cases in
which ordinary binary64 reductions disagree near a decision boundary.

The current source delta suggests a layered approach rather than immediately
switching every computation to arbitrary precision.

## [M-OZAKI-II-2026] Ozaki, Uchino, Imamura

Katsuhisa Ozaki, Yuki Uchino, Toshiyuki Imamura.

"Ozaki scheme II: A GEMM-oriented emulation of floating-point matrix
multiplication using an integer modular technique."

International Journal of High Performance Computing Applications, OnlineFirst,
2026.

DOI: https://doi.org/10.1177/10943420261467787

Method atom used here:

- modular integer products can serve as exact matrix-multiplication kernels;
- CRT reconstruction can recover the signed result when the dynamic-range
  contract is explicit;
- capacity must be treated as a fail-closed precondition.

VAL-003 C01 uses only a tiny correctness-oriented CRT micro-oracle. It is not a
performance implementation of the full method.

## [M-OZAKI-FMA-2026] Ozaki and Koizumi

Katsuhisa Ozaki and Toru Koizumi.

"Fast and accurate algorithms for matrix multiplication using fused
multiply-add and their rounding error analysis."

Japan Journal of Industrial and Applied Mathematics 43, 59 (2026), published
2026-08-26.

DOI: https://doi.org/10.1007/s13160-026-00816-8

Method atoms:

- error-free transformations such as `TwoSum` and `TwoProductFMA` remain useful
  building blocks around fast floating-point kernels;
- there is a continuum between ordinary precision, compensated/pair or
  double-word arithmetic, and GEMM-oriented high-accuracy schemes;
- a cheaper FMA-based middle tier can be valuable when full multiple precision
  is unnecessary.

Candidate implication: after C01, benchmark a hardware-FMA middle tier against
EFT+exact oracles before adopting a heavier native high-precision backend.

## [M-FP64-EMU-2026] FP64 emulation on AI-oriented tensor hardware

"DGEMM using FP64 Arithmetic Emulation and FP8 Tensor Cores with Ozaki Scheme."

SCA/HPCAsiaWS 2026, published January 2026.

DOI: https://doi.org/10.1145/3784828.3785017

Method atom:

- the surrounding FP64 work can itself be emulated on hardware optimized for
  lower-precision arithmetic;
- therefore high-trust arithmetic does not necessarily imply dependence on
  native high-throughput FP64 hardware.

This is future infrastructure guidance only; current consumer-PC experiments do
not require Tensor Cores.

## [M-OZAKI-NEARSUM] Error-free products + correctly rounded summation

The earlier Tensor-Core Ozaki work explicitly separates:

```text
splitting
-> error-free partial matrix products
-> final summation
```

and notes that a correctly rounded summation method such as NearSum can recover
a correctly rounded final result once the partial products themselves are
error-free.

Method implication for VAL-003:

**accurate summation is downstream of product accuracy.**

C01's numerical kittens directly reinforce that distinction: `math.fsum` over
already-rounded products did not reproduce the exact dot oracle, while
TwoProduct error capture followed by accurate reduction did for all bounded C01
cases.

## [M-EXBLAS] ExBLAS / reproducible BLAS lineage

ExBLAS combines floating-point expansions, EFTs such as `TwoSum`/`TwoProd`, and
long accumulators to preserve low-order information until the final rounding.
Its design goal includes results independent of computation order, data
partition, scheduling, or reduction tree.

Project: https://github.com/riakymch/exblas

Method implication:

A native ExBLAS/OzBLAS-style backend is a strong candidate for VAL003-C02, but
C01 deliberately starts with a dependency-light Python reference path so that
we can first prove what failure classes need to be detected.

## Method synthesis for this repository

```text
Tier 0  ordinary NumPy/SciPy
Tier 1  EFT product-error capture + accurate reduction
Tier 2  exact small oracle (Fraction / bounded CRT)
Tier 3  native reproducible/high-precision backend
Tier 4  only when necessary: arbitrary/multiple precision authority oracle
```

The important change is not "use higher precision everywhere." It is:

> use the cheapest arithmetic path that can falsify the current decision, then
> escalate only suspicious or authority-crossing cases.

This keeps the numerical-trust lane compatible with the repository's
high-speed autonomous research loop.
