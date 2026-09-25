# EXP004-C04 — Kwant build-isolation correction

**STATUS:** CORRECTIVE BACKEND QUALIFICATION / NO SCIENTIFIC CHANGE

Public Actions run `36116441805` reached the hosted Ubuntu 24.04 runner and
failed while building Kwant 1.5.0.

Observed failure:

```text
NumPy header directory cannot be determined ("import numpy" failed)
fatal error: numpy/arrayobject.h: No such file or directory
```

The canonical environment already had NumPy 2.5.3 installed, but pip's isolated
build environment did not expose those headers to the Kwant 1.5.0 source
build.

The current Kwant development installation guidance explicitly recommends
building with the intended NumPy environment available via
`--no-build-isolation`.

Correction:

1. install NumPy/SciPy and tinyarray into the selected Python 3.12 environment;
2. build Kwant 1.5.0 with `--no-build-isolation`;
3. rerun the exact same deterministic known-answer smoke.

No physics model, tolerance, or expected result changed.

This is a backend-build qualification defect, not an EXP-004 physics failure.
