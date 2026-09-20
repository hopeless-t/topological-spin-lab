# EXP-003 canonical reference evidence

This directory contains the canonical numerical reference for **EXP-003 —
Continuum Magnetic Mass Domain-Wall Reference**.

The reference was generated only after the EXP-003 scientific contract,
intentional failure-path tests, branch CI, pull-request CI, and main CI had
passed.

## Canonical source

- source commit: `c4daf00e5c0b04d32580f1a659b6d6bb6fab2f79`
- experiment: `specs/EXP-003.json`
- canonical spec SHA-256:
  `a05a60de01cd07c4e8de092a5cbf91bde6e595baa6d5ad43e38c635bc1301f54`
- execution status: `PASS`

The source commit predates the commit that stores these files, avoiding
circular provenance.

## Canonical generator

The reviewed candidate was generated on GitHub Actions:

- workflow run: `35508575765`
- runner family: GitHub-hosted Ubuntu
- Python: `3.12.14`
- NumPy: `2.5.3`
- recorded platform:
  `Linux-6.17.0-1022-azure-x86_64-with-glibc2.39`
- reviewed artifact digest:
  `sha256:214644a6226a5f75835489dc4212ad0e99928896332cce08e903b5833b0c47d0`

The one-shot generator checked out the immutable source commit, ran the full
test suite, executed EXP-003, independently reviewed the generated physics
sanity conditions, and copied the reviewed outputs to the evidence branch
without manual transcription.

## Canonical files

The scientific reference set is exactly:

| File | Role | Git blob ID |
| --- | --- | --- |
| `manifest.json` | provenance and spec identity | `8b6f45da190c3512579f132045f40f63ee0c4718` |
| `metrics.json` | ten acceptance checks and metrics | `8927d5cd8955dc7a74cd4f972d99f9710128e774` |
| `profile.csv` | 241-point mass/localization profile | `07cb52310dd070051afd27da4e543ac104333f17` |
| `dispersion.csv` | 101-point chiral-mode dispersion | `81293574cecf2c9129f523a9fe046bc93ebc6da4` |

The artifact SHA-256 above protects the reviewed candidate bundle; the Git
blob IDs identify the exact files stored in this reference tree.

`README.md` documents the reference but is not scientific evidence.

## Canonical physical sanity

The reviewed reference verifies:

- all ten EXP-003 acceptance checks pass;
- the profile contains 241 points over the frozen ±12 xi window;
- the dispersion contains 101 ky points;
- x=0 is sampled;
- m(0)=0;
- the probability density peaks at x=0;
- negative ky has negative bound-mode energy;
- ky=0 has zero bound-mode energy within tolerance;
- positive ky has positive bound-mode energy;
- every sampled bound-mode energy remains inside the asymptotic massive
  continuum;
- wall reversal flips dispersion and spin within the frozen tolerances.

For the canonical run:

~~~text
max operator residual       ≈ 6.13e-18 eV
finite-window norm error    ≈ 7.58e-11
max dispersion error        ≈ 6.94e-18 eV
max in-gap excess           = 0
wall-reversal dispersion    = 0
wall-reversal spin error    = 0
~~~

## What is not canonical

Rendered PNG figures are excluded. They are human-inspection artifacts.

Raw spinors/eigenvectors are excluded because representation-dependent phase
and basis details are not the scientific observable being frozen.

No separate reversal table or EXP-002-to-EXP-003 delta file is stored.
Reversal is already covered by acceptance metrics, and cross-experiment
differences are derived from independent canonical references.

## Reproduction rule

A future run need not reproduce every CSV byte exactly.

Reproduction means:

1. the experiment specification has the same semantic SHA-256;
2. execution is valid;
3. every EXP-003 scientific acceptance check passes;
4. the 241-point profile and 101-point dispersion grids remain complete;
5. center localization, chirality, in-gap binding, and wall reversal remain
   valid;
6. current structured observations stay within the experiment's frozen
   numerical tolerances of this reference.

The CI suite uses this directory as a regression anchor.

## Authority boundary

This reference establishes only the generic **continuum sign-changing
Dirac-mass** known-answer contract.

It does not establish an NdBi domain wall, a material-specific AFM-TI channel,
a lattice bulk-boundary invariant, a Chern number, quantized transport,
disorder immunity, or freedom from lattice-regulator artifacts.
