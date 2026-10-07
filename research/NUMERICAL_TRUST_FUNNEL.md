# Numerical-trust funnel for the high-speed research loop

**Status:** operating method / research governance  
**Authority:** method only; not physics evidence

VAL-003 adds an arithmetic falsification funnel to the existing high-speed
research loop.

## Core loop

```text
scientific question
    |
    v
cheap ordinary calculation
    |
    v
numerical kittens / parameter kittens
    |
    +---- no disagreement --------------------+
    |                                         |
    |                                         v
    |                               continue bounded sweep
    |
    +---- suspicious / decision boundary -----+
                                              |
                                              v
                                  EFT product-error capture
                                  + accurate reduction
                                              |
                           +------------------+------------------+
                           |                                     |
                           v                                     v
                  exact small oracle                    metamorphic checks
                  Fraction / CRT                        symmetry / scaling /
                                                       phase / permutation
                           |                                     |
                           +------------------+------------------+
                                              v
                                   independent native/high-
                                   precision backend when needed
                                              |
                                              v
                                       failure biopsy
                                              |
                        +---------------------+--------------------+
                        |                     |                    |
                     PHYSICS                NUMERICS           INFRA/CONTRACT
                        |                     |                    |
                        v                     v                    v
                    next model         new kitten/check       repair layer only
                        \_____________________|____________________/
                                              |
                                              v
                                      durable checkpoint
                                              |
                                              v
                                        meta-improvement
```

## Numerical kittens

A numerical kitten is a deterministic, cheap adversarial calculation designed
to search for numerical disagreement rather than physical novelty.

Candidate kitten families:

```text
cancellation
large exponent spread
near degeneracy
wall hybridization knee
coarse/fine discretization pairs
permuted reduction order
power-of-two rescaling
basis/global-phase transforms
corrupted matrices / outputs
boundary values near an acceptance threshold
```

A kitten does not vote on the truth. Its job is to produce a suspicious case
that a stronger oracle can adjudicate.

## Escalation policy

### Tier N0 — ordinary

Use NumPy/SciPy/vendor BLAS for the broadest exploration.

### Tier N1 — compensated/EFT

Use product-error capture plus accurate reduction for:

- dot products;
- norms;
- expectation values;
- residuals;
- small matrix-vector post-checks.

### Tier N2 — exact micro-oracle

Use `Fraction` or bounded CRT when:

- the object is small;
- a disagreement must be adjudicated;
- a Red Team requires an exact known answer.

### Tier N3 — independent high-precision/reproducible backend

Use MPFR / ExBLAS / OzBLAS or another separately qualified backend when:

- the object is too large for exact Python micro-oracles;
- a result is near a scientific acceptance boundary;
- a result is about to cross into canonical evidence.

Do not default to N3 for every exploratory run.

## Exact CRT policy

The CRT path must always carry an explicit capacity contract.

```text
2 * conservative absolute product bound < CRT dynamic range
```

If the inequality fails, the calculation is `INVALID`, not an approximate
answer.

Whenever practical, use one modulus not used for reconstruction as an
independent corruption check.

## Floating-point policy

Accurate summation alone is not assumed to recover information lost during
multiplication.

C01 establishes the working pattern:

```text
product
 -> product + product-error (EFT)
 -> accurate reduction
 -> exact small oracle when suspicious
```

A future FMA-optimized implementation may replace the pure-Python reference
kernel only after differential qualification.

## Metamorphic oracle policy

Prefer transformations with a known physical or algebraic output relation.
Examples:

- global complex phase must not change an expectation value;
- simultaneous inverse power-of-two scaling of dot operands must not change
  their exact dot product;
- wall reversal must reverse the expected chirality relation;
- equivalent basis transformations must preserve basis-invariant spectra;
- Hermitian operators must give real expectation values within the declared
  numerical bound.

A metamorphic test can falsify a calculation even when no closed-form numeric
answer is available.

## Meta-meta improvement

Each numerical failure is converted into reusable infrastructure.

```text
new disagreement
    -> classify failure
    -> minimize to smallest reproducer
    -> create deterministic kitten
    -> attach strongest available oracle
    -> add Red Team regression
    -> measure whether a cheaper tier can now detect it
```

The loop therefore improves not only the scientific model, but its own
verification cost curve.

Track at least:

```text
kitten cases executed
suspicious cases escalated
exact-oracle disagreements
failure classes discovered
new regression controls added
fraction of cases requiring expensive escalation
runtime per verification tier
```

The target is **higher failure-detection coverage with a lower fraction of
expensive authority-oracle calls**.

## Relationship to EXP-004 and VAL-002

```text
VAL-002 asks: is the model adequate for NdBi?
VAL-003 asks: did we compute the stated model reliably?
EXP-004 asks: what transport result follows under its frozen model/contract?
```

None of these questions can substitute for another.

## Immediate application

Before freezing EXP004-C12's economy (`10 Å / 8 xi`) or margin (`8 Å / 8 xi`)
candidate, run both through:

1. ordinary dense/Kwant path;
2. EFT residual + expectation checks;
3. exact micro-oracles on reduced blocks / adversarial reductions;
4. at least one independently qualified high-precision/reproducible backend if
   the result is being promoted.

Only disagreements relevant to the decision are escalated further.
