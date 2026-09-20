# EXP-001 canonical reference evidence

This directory contains the canonical numerical reference for **EXP-001 —
Massless Surface Dirac Reference**.

The reference was generated only after the EXP-001 implementation, intentional
failure-path tests, branch CI, pull-request CI, and main CI had passed.

## Canonical source

- source commit: `042e406528065a1d9a8b1fe4ac16ac7418f6814c`
- experiment: `specs/EXP-001.json`
- canonical spec SHA-256: `5e468e65433413f7d4fdce1d0e6452f3862932b45ef621e1567b6f76f17bacb5`
- execution status: `PASS`

The source commit is intentionally earlier than the commit that stores these
files. This avoids a circular provenance claim in which evidence would need to
contain the hash of a commit that does not exist until the evidence is added.

## Canonical generator

The reviewed candidate was generated on GitHub Actions:

- workflow run: `35504696459`
- runner family: GitHub-hosted Ubuntu
- Python: `3.12.14`
- NumPy: `2.5.3`
- recorded platform: `Linux-6.17.0-1022-azure-x86_64-with-glibc2.39`
- reviewed artifact digest:
  `sha256:27ac026205ebc2bb7f2903d69ff64023b03bc862279b73947b2a756db120d5ec`

The generation workflow checked out the source commit above, ran the test
suite, executed EXP-001, verified every scientific check, verified row counts
and finite numeric values, and then copied the reviewed files to this branch
without manual transcription.

## Canonical files

The scientific reference set is exactly:

| File | Role | SHA-256 |
| --- | --- | --- |
| `manifest.json` | provenance and spec identity | `a6ddb6ebb5387f4b2c43c244d9554972482d2cf272741ca21caf0988cebe62b1` |
| `metrics.json` | acceptance metrics and check results | `0194630315cc381a26f6aae15233e5b09041b688466ca05111045caeb75256f1` |
| `spectrum.csv` | 201-point spectrum observation | `9488e535b285302f619b78c2266d7fbf5f854c4e0e9e6e5cf155c72c1caca427` |
| `spin_ring.csv` | 72 angles × 2 bands spin observation | `429c19f300ddf0f73b51d16746ebdaa3cd86d4db303620fcaa9a1ee8a2279b66` |

`README.md` documents the reference but is not itself scientific evidence.

## What is not canonical

Rendered PNG figures are intentionally excluded. They are human-inspection
artifacts and can vary with plotting-library, font, metadata, or rendering
environment without changing the physics.

Raw eigenvectors are also excluded because their global complex phase is not a
physical observable.

## Reproduction rule

A future run is not required to reproduce every CSV byte exactly. Floating
point last bits may differ across runners or numerical-library builds.

Reproduction means:

1. the experiment specification has the same semantic SHA-256;
2. the run is valid and completes;
3. every scientific acceptance check passes;
4. the expected observation grids are complete;
5. current numerical observations remain within the experiment's declared
   tolerances of this reference.

The CI suite uses this directory as a regression anchor so the reference cannot
silently drift away from the current EXP-001 contract.

## Authority boundary

This reference demonstrates only the claims in the EXP-001 contract. It does
not establish an NdBi material model, magnetic gap, topological invariant,
edge state, transport result, QAH state, or material prediction.
