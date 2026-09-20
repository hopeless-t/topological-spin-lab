# Reproducibility

The project separates intended experiments from observed evidence.

```text
Experiment Spec
      ↓
Execution
      ↓
Observations
      ↓
Acceptance Checks
      ↓
Evidence
```

## Status meanings

- `PASS`: the experiment executed and every scientific acceptance check passed.
- `FAIL`: the experiment executed but at least one scientific check failed.
- `INVALID`: the specification was rejected before experiment execution.
- `ERROR`: software, runtime, or I/O prevented valid evaluation.

`PASS` is derived from check results. Physics code cannot inject a successful
status directly.

## Evidence authority

Structured numerical outputs are authoritative for acceptance. Figures are
human-inspection artifacts.

Raw eigenvectors are not canonical evidence because their global complex phase
is arbitrary.

## Provenance

Reference evidence records the canonical specification hash, Git commit when
available, Python version, NumPy version, platform, and derived experiment
status.

## Determinism

EXP-001 contains no randomness. CI executes the same typed specification twice
and requires exactly equal structured numerical results in the same runtime.
Cross-runtime acceptance is based on numerical tolerances rather than
byte-identical figure files.
