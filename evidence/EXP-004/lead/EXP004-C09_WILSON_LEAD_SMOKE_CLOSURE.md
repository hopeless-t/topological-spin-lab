# EXP004-C09 — Wilson lead-mode smoke closure

**STATUS:** LEAD-MODE BRIDGE PASS / CONVERGENCE NOT YET ESTABLISHED

Public GitHub Actions run `36118618663` completed successfully on the pinned
NumPy-2 Kwant lane.

## Low-k recovery

At lead phase `k=+0.05` the two states inside the provisional
`|E| < 0.015 eV` window were spatially separated between the two periodic
domain walls.

Canonical negative-to-positive wall, x=0:

```text
E                         +0.0049979231 eV
expected |E|               0.0049979169 eV
dE/dk_phase               +0.0998748569 eV
expected |dE/dk_phase|     0.0998750260 eV
<sigma_x>                 -0.999998773
wall weight (within 2 xi)  0.969257746
density peak               0 A
```

Opposite wall, x=400 A:

```text
E                         -0.0049979231 eV
dE/dk_phase               -0.0998748569 eV
<sigma_x>                 +0.999998773
wall weight (within 2 xi)  0.969257746
density peak               400 A
```

Changing the sign of k reverses the energy assignment consistently.

This is the expected EXP-003 chirality/spin pattern on the periodic
double-wall lead.

## Doubler red team

At the y Brillouin-zone edge `k=pi`:

```text
Wilson r=0.5:
  minimum |E| = 0.0811868939 eV

naive r=0:
  minimum |E| = 2.74e-19 eV
```

So the smoke detects the unwanted naive-lattice low-energy copy and observes
its removal by the 2D Wilson extension.

This is considerably stronger than checking the Wilson lane alone because the
red-team control demonstrates that the chosen observable can actually see the
target failure mode.

## Numerical cross-check

Kwant `Bands` was compared against its documented Bloch construction:

```text
max spectrum residual at k=0.05  2.95e-16 eV
max spectrum residual at k=pi    6.38e-16 eV
```

## Evidence

Actions artifact:

```text
id      10855718954
sha256  e5b6d80d544c60d1a66b0c3d3054955c5cf8625f2c6273ad413a8786ba4166d3
```

## Pseudo-Council closure

**Continuum:** EXP-003 low-k energy, velocity sign, and sigma-x are recovered.

**Lattice:** the isotropic y Wilson extension passes the intended doubler
red-team at this grid point.

**Topology:** the compensating wall is explicit and spatially separated rather
than hidden at a hard boundary.

**Numerics:** the lead Bloch implementation agrees with the direct documented
Kwant construction to floating-point precision.

**Falsification:** one point cannot establish convergence. The PASS authorizes
a convergence pilot, not a scattering device.

Council converged.

## Decision

```text
Wilson lead-mode bridge      PASS
single-grid scientific claim LIMITED
convergence                  NOT ESTABLISHED
finite scattering device     NOT AUTHORIZED
next                         convergence pilot
```

## Next bounce

Freeze a compact convergence matrix before changing the model.

Candidate axes:
- a/xi: 0.30, 0.20, 0.15, 0.10;
- wall separation/xi: 4, 6, 8, 10;
- small k-phase samples around zero;
- Wilson r fixed at 0.5 for the primary lane;
- r=0 retained only as a doubler red-team.

Measure energy/slope error, spin error, localization leakage, wall-wall
hybridization, and Brillouin-edge gap.

Monte Carlo/Sobol may be useful **after** the deterministic grid establishes
which axes materially control error; it should not replace the convergence
grid.
