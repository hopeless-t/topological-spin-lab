# Research Repository Pattern v0.1

> **Status:** PROTOTYPE / REUSABLE PATTERN  
> **Origin:** extracted from the working structure of `topological-spin-lab`  
> **Scientific authority:** NONE  
> **Mainline implementation authority:** NONE

This document records a reusable repository skeleton for small computational
research projects.

It is intentionally **not** a framework and **not** a rule that every project
must have every directory from day one.

The pattern exists to keep research repositories readable, falsifiable, and
reproducible as they grow.

## Core idea

A research repository should make this path visible:

~~~text
Question
  ↓
Experiment Spec
  ↓
Model
  ↓
Calculation
  ↓
Observable
  ↓
Acceptance
  ↓
Evidence
~~~

A successful program execution is not automatically a successful experiment.

A convincing plot is not evidence by itself.

A plan is not a result.

A cited paper is not a reproduced result.

## Prototype skeleton

~~~text
research-project/
│
├── README.md
├── specs/
│   └── EXP-001.json
├── src/
│   └── project_name/
│       ├── models/
│       ├── analytic/
│       ├── observables/
│       ├── experiments/
│       ├── spec.py
│       ├── results.py
│       ├── evidence.py
│       ├── provenance.py
│       └── plotting.py
├── tests/
├── evidence/
│   └── EXP-001/
│       └── reference/
├── research/
│   └── decision-support/
├── docs/
│   ├── REFERENCES.md
│   ├── LITERATURE_MAP.md
│   ├── VISUALS.md
│   ├── EXP-001.md
│   └── VAL-001.md
└── .github/
    └── workflows/
~~~

This is a **shape**, not an instruction to create empty directories.

Only create a component when a real experiment requires it.

## Stable responsibilities

### specs/

Records what was intended.

A spec should be machine-readable, strict, and fail-closed.

Unknown fields, invalid types, impossible values, and unsupported experiment
IDs should fail before scientific execution begins.

### models/

Contains the physical, mathematical, or algorithmic assumptions being tested.

Models should not own filesystem, network, Git, clock, UI, or provenance logic.

### analytic/

Contains independent known-answer references when they exist.

The numerical implementation should not silently use the same code path as its
reference check.

### observables/

Defines what is measured from a model or execution.

This layer should answer:

> What quantity is actually being compared?

### experiments/

Maps a validated experiment spec to a deterministic result.

Prefer a functional core:

~~~text
validated spec
    ↓
pure experiment execution
    ↓
typed result
~~~

### results.py

Defines typed observations, metrics, checks, and experiment states.

Recommended state vocabulary:

~~~text
PASS
FAIL
INVALID
ERROR
~~~

These states should not be conflated.

### evidence.py

Serializes an already-computed result.

Evidence serialization should not recompute the science.

Canonical evidence should contain structured numerical data and provenance.
Rendered figures should normally remain human-inspection artifacts unless an
experiment contract explicitly makes them authoritative.

### provenance.py

Records enough execution context to identify the source calculation.

Typical fields:

~~~text
source commit
spec hash
runtime version
numerical-library version
platform
~~~

Avoid circular provenance: evidence should identify the commit that generated
it, not pretend to contain the hash of the later commit that stores it.

### tests/

Tests should cover more than successful examples.

A useful research repository deliberately tests:

~~~text
known-answer success
invalid specs
intentional broken models
scientific FAIL paths
evidence serialization
canonical-reference regression
~~~

The harness is incomplete if it can demonstrate PASS but cannot reliably
detect a broken implementation.

### evidence/

Contains reviewed canonical references.

A canonical reference is a historical comparison anchor, not just an output
directory.

A useful reference contract records:

~~~text
immutable source commit
spec identity
structured observations
acceptance metrics
provenance
reproduction rule
authority boundary
~~~

Cross-platform reproduction should usually mean scientific agreement within
declared tolerances, not byte-identical floating-point output or identical
rendered images.

### research/

Contains research-process artifacts that are useful but are not scientific
results.

Examples:

~~~text
method-selection Monte Carlo
value-of-information estimates
prior-art comparison
sampling-design studies
decision sensitivity analysis
~~~

These outputs must clearly distinguish engineering priors from physical
probabilities.

### docs/

Contains the human-readable scientific and architectural contracts.

Useful documents include:

~~~text
REFERENCES.md
LITERATURE_MAP.md
VISUALS.md
EXP-xxx.md
VAL-xxx.md
~~~

Primary literature should be preferred for scientific claims.

A literature map should distinguish:

~~~text
SOURCE
OBSERVATION
INFERENCE
EXPERIMENT IMPACT
~~~

## Research lanes

Do not force every activity into an EXP number.

Suggested lanes:

| Prefix | Purpose |
| --- | --- |
| `EXP-xxx` | scientific or physical experiment |
| `VAL-xxx` | numerical or methodological validation |
| `BENCH-xxx` | performance comparison |
| `RQ-xxx` | open research question |
| `REF-xxx` | named reference object when needed |

A validation lane may sit between experiments without pretending to add a new
physical claim.

Example:

~~~text
EXP-003
canonical continuum result
      ↓
VAL-001
numerical-regulator validation
      ↓
EXP-004
new physical experiment
~~~

## Fixed pattern vs project-specific content

### Good candidates to standardize

~~~text
Spec → Execution → Observation → Acceptance → Evidence
functional core + thin imperative shell
PASS / FAIL / INVALID / ERROR
strict fail-closed validation
known-answer-first development
intentional failure injection
canonical reference evidence
provenance
primary-source lineage
explicit scientific boundary
Figure != Evidence
Plan != Result
Proposal != Decision
~~~

### Must remain project-specific

~~~text
scientific question
model / Hamiltonian / equations
observables
acceptance thresholds
sampling
numerical method
canonical table schema
literature
visualization
experiment sequence
material or domain assumptions
~~~

The research subject must not be templated into meaninglessness.

Standardize the guardrails, not the science.

## Recommended experiment lifecycle

~~~text
1. Question
2. Prior-art / literature intake
3. Scientific Contract
4. Known-answer reference
5. Implementation
6. Failure injection / Red Team
7. Branch CI
8. Pull-request review
9. Merge
10. Canonical reference generation
11. Reference regression
12. Next-question selection
~~~

Not every project needs every step, but skipping one should be an explicit
decision rather than an accidental omission.

## Decision-support layer

When multiple next calculations are possible, research effort can be treated
as a scarce resource.

A decision-support calculation may compare candidates using quantities such as:

~~~text
expected information gain
correctness risk
numerical-artifact risk
implementation cost
reuse value
verification difficulty
claim safety
~~~

Monte Carlo or sensitivity analysis may be used to ask:

> Does the next-step decision remain stable when these uncertain priorities
> move?

This does not make the output a physical probability.

It is a tool for deciding what to calculate next.

## Visual documentation

Visuals should reduce comprehension cost.

Recommended README budget:

1. project identity / scope;
2. experiment architecture;
3. current roadmap.

Use Mermaid for structural diagrams and plain SVG for composition-heavy static
figures.

A visual must not silently strengthen a scientific claim.

## Anti-patterns

This pattern explicitly tries to avoid:

~~~text
one giant notebook
one giant script
plots as proof
README claims ahead of implementation
hidden parameter provenance
silent default values
unknown spec fields being ignored
mean error hiding worst-case failures
AI-generated code without failure-path tests
massive abstraction before a second concrete use case exists
empty-directory architecture theatre
temporary CI tooling permanently accumulating in main
mixing scientific claims with engineering decision support
~~~

## Minimal new-project start

A new project should begin smaller than the full skeleton.

Recommended minimum:

~~~text
README.md
specs/EXP-001.json
src/project_name/
tests/
docs/EXP-001.md
docs/REFERENCES.md
.github/workflows/ci.yml
~~~

Add `analytic/`, `evidence/`, `research/`, additional lanes, and richer
documentation only when the work earns them.

## Extraction path

This document is intentionally stored inside `topological-spin-lab` first so
the pattern can continue to evolve against a real research repository.

If the pattern proves useful across several independent projects, it may later
be extracted into a dedicated starter repository or project-generation skill.

Until then, this file is the prototype authority for the reusable repository
shape, not a frozen organization-wide standard.

## Principle

> **Do not template the research. Template the discipline around the research.**
