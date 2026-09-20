# EXP-002 canonical reference evidence

This directory contains the canonical numerical reference for **EXP-002 —
Magnetic Mass / Dirac Gap**.

The reference was generated only after the EXP-002 implementation, intentional
failure-path tests, branch CI, pull-request CI, and main CI had passed.

## Canonical source

- source commit: `7a9a3ade0fa4bffa74cee61f1e59419ea60eff89`
- experiment: `specs/EXP-002.json`
- canonical spec SHA-256: `94024656cf4b6e1b343b49977d586ffa84de7eede98b84db64c299233899bb96`
- execution status: `PASS`

The source commit is intentionally earlier than the commit that stores these
files. This avoids circular provenance.

## Canonical generator

The reviewed candidate was generated on GitHub Actions:

- workflow run: `35507417640`
- runner family: GitHub-hosted Ubuntu
- Python: `3.12.14`
- NumPy: `2.5.3`
- recorded platform: `Linux-6.17.0-1022-azure-x86_64-with-glibc2.39`
- reviewed artifact digest:
  `sha256:e249fd9ad6d76ab0bb0492cb8beb79fe256769d83031385c31024668fbf4419c`

The generation workflow checked out the immutable source commit, ran the full
test suite, executed EXP-002, required all eleven scientific checks to pass,
verified the observation-grid sizes and finite values, verified the canonical
0.040 eV direct gap, verified the expected sign of out-of-plane spin, and then
copied the reviewed files to the evidence branch without manual transcription.

## Canonical files

The scientific reference set is exactly:

| File | Role | SHA-256 |
| --- | --- | --- |
| `manifest.json` | provenance and spec identity | `10042140a8d3ec1ca8826b7df05c390e8fc85d854bbe718076e6205225b9e590` |
| `metrics.json` | acceptance metrics and check results | `5eb30e6c4ba7af6261d74844c3d77db31a727367bc890f4b7a23b02323e2625a` |
| `spectrum.csv` | 201-point gapped spectrum observation | `4c3da58540f5bfac57110a20da8acdbc9469a4fcddfc55dac523c9377e483a98` |
| `spin_ring.csv` | 72 angles × 2 bands spin observation | `2257457e3a7fc8126eb616285d5254b3583dc2912d8ec36b23f348399b139522` |

`README.md` documents the reference but is not itself scientific evidence.

## Canonical physical sanity

For the frozen generic parameters

~~~text
alpha = 1.0 eV·Å
m     = +0.020 eV
~~~

the reference verifies:

- direct gap at `k=0`: `0.040 eV`;
- upper-band ring spin has positive `sigma_z`;
- lower-band ring spin has negative `sigma_z`;
- all eleven EXP-002 acceptance checks pass.

These statements belong to the generic effective model only.

## What is not canonical

Rendered PNG figures are excluded because rendering details may vary without
changing the numerical physics.

Raw eigenvectors are excluded because their global complex phase is arbitrary.

No derived EXP-001-to-EXP-002 `delta.json` is stored. Cross-experiment
differences are derived from the two independent canonical references rather
than duplicated as a fifth authority file.

## Reproduction rule

A future run is not required to reproduce every CSV byte exactly. Floating
point last bits may differ across runners or numerical-library builds.

Reproduction means:

1. the experiment specification has the same semantic SHA-256;
2. the run is valid and completes;
3. every EXP-002 scientific acceptance check passes;
4. spectrum and spin grids are complete;
5. the canonical gap and mass-sign spin sanity checks remain true;
6. current numerical observations stay within the declared EXP-002 tolerances
   of this reference.

The CI suite uses this directory as a regression anchor.

## Authority boundary

This reference demonstrates only the frozen EXP-002 generic uniform-mass
Dirac-model contract. It does not establish an NdBi material model, an AFM-TI
classification, a Chern number, a QAH state, an axion-insulator state, an edge
state, or quantized transport.
