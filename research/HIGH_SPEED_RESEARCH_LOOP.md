# High-speed autonomous research loop

**Status:** operating method / research governance  
**Applies to:** exploratory work in `topological-spin-lab`  
**Does not override:** frozen experiment contracts, canonical evidence, or claim ceilings

The purpose of this loop is to increase research velocity **without allowing velocity to
become scientific authority**.

## Core invariant

```text
fast exploration
+ independent falsification
+ explicit claim ceiling
+ durable checkpoint
!= automatic promotion to evidence
```

Promotion is a separate gate.

## Artifact ladder

Every research bounce should know which rung it is producing.

```text
SOURCE_DELTA
    External information that may change a question or boundary.

QUESTION
    A falsifiable bounded question.

CONTRACT
    Model, assumptions, observables, acceptance checks, Red Team controls.

PILOT
    Cheap calculation used to discover regimes and achievable tolerances.

RED_TEAM
    Deliberately broken/control case that the harness must reject.

EVIDENCE
    Reproducible structured observation generated under a frozen contract.

FAILURE_BIOPSY
    Why an attempted gate failed: physics, numerics, infrastructure, or contract.

PROMOTION
    Explicit review deciding whether a result may become canonical.
```

A useful result on a lower rung must not silently jump to a higher rung.

## One bounce

### 1. Refresh only the relevant source delta

Search for:

- direct predecessors;
- contradictory results;
- newer measurements;
- newer numerical failure modes;
- newer methods that could provide an independent oracle.

Do not turn literature collection into an unbounded survey.

Output: a short source delta with a statement of **what changes**.

### 2. Atomize the question

Split the proposed work into:

```text
physical assumption
numerical assumption
observable
acceptance criterion
known answer / oracle
Red Team control
claim ceiling
```

If two assumptions can fail independently, they should normally be tested independently.

### 3. Pseudo-Council

Run at least four roles mentally or computationally:

- **Theorist** — what physical statement is actually being tested?
- **Numerical analyst** — what discretization/finite-size/solver artifact can mimic it?
- **Red Team** — what intentionally wrong model should fail?
- **Reproducibility reviewer** — what must be serialized so another run can be compared?

Council convergence means disagreements have become explicit tests or documented
uncertainties. It does not mean every role “agrees.”

### 4. Cheapest independent oracle first

Before spending remote CI/compute budget, prefer the smallest independent calculation that
can falsify the current implementation.

Examples:

- analytic spectrum;
- direct dense diagonalization;
- alternate regulator;
- symmetry identity;
- finite-difference residual;
- exact small-system enumeration.

The independent oracle should avoid sharing unnecessary implementation machinery with the
candidate under test.

### 5. Bounded regime sweep

Sweep only variables capable of changing the current decision.

Prefer dimensionless control parameters where possible:

```text
a / xi
wall separation / xi
E / |m|
disorder / |m|
```

Search for knees/regime transitions rather than assuming linear convergence.

Monte Carlo is useful for:

- design selection;
- threshold sensitivity;
- robustness of an engineering decision.

Monte Carlo is **not** a substitute for a physical derivation or experimental observation.

### 6. Red Team before promotion

A positive result is incomplete until at least one relevant broken case is rejected.

Examples for the current transport lane:

- `r = 0` fermion doubler;
- insufficient wall separation;
- mismatched lead/device Hamiltonian;
- reversed wall orientation;
- perturbed/non-unitary scattering matrix.

### 7. Freeze the smallest useful checkpoint

Checkpoint contents:

```text
source state / commit
question
code/spec
structured result
checks
claim ceiling
next gate
```

Rendered figures are optional projections. Numerical/structured evidence remains the
authority.

### 8. Failure biopsy

Classify failure before changing anything:

```text
PHYSICS
    The hypothesized effect was absent or contradicted.

NUMERICS
    Discretization, finite size, conditioning, or solver behavior failed.

INFRASTRUCTURE
    Build/runtime/CI/tooling failed before valid evaluation.

CONTRACT
    The question or acceptance rule was underspecified or self-contradictory.
```

Then change only the layer implicated by the biopsy.

### 9. Meta-improvement

At the end of each bounce, record one of:

- a reusable check;
- a cheaper oracle;
- a better dimensionless parameterization;
- a new Red Team control;
- a removed redundant step;
- a reason the current loop is already minimal.

This is the self-improvement step. The output is a method delta, not physics evidence.

## Compute policy

Use a two-tier compute strategy.

### Tier 1 — exploratory / cheap

Use local or lightweight deterministic calculations for:

- regime discovery;
- tolerance estimation;
- failure localization;
- source-independent oracles.

### Tier 2 — authority crossing

Use the repository's reproducible CI/remote substrate when:

- freezing a reference;
- qualifying a backend/environment;
- promoting candidate evidence;
- verifying a result intended to survive future implementation changes.

Do not spend authoritative CI runs on questions a small local oracle can answer.

## Parallelism rule

Parallelize **independent falsifiers**, not dependent stages.

Good:

```text
literature delta
dense oracle
Red Team derivation
```

in parallel.

Bad:

```text
freeze tolerance
implement device
claim transport
```

before the convergence pilot has established the tolerance.

## Current application to EXP-004

The current boundary is:

```text
C09 Wilson lead-mode bridge       PASS
independent dense reproduction    PASS (research-only)
compact convergence pilot         exploratory PASS
candidate convergence gate        available for review
finite scattering device          NOT AUTHORIZED
```

The next useful promotion step is therefore:

1. review/freeze convergence criteria;
2. reproduce the C10 sweep in the selected reproducible environment;
3. only if the gate survives, authorize a **minimal clean finite scattering calibration**;
4. keep geometry/disorder/material-specific extensions downstream.

## Stop rule

A bounce stops when it has produced a durable decision-relevant checkpoint.

Do not continue merely because more computation is possible.
