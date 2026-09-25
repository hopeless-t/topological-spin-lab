# EXP004-C08 — Wilson periodic-double-wall lead smoke design

**STATUS:** PHYSICS BRIDGE SPIKE / NO DEVICE SCATTERING

## Fresh exploration

VAL-001 froze a one-dimensional Wilson reduction with

```text
(r alpha / a) (1 - cos(k_x a)) sigma_z
```

and selected `r=0.5` as the conventional-lattice transport candidate.

For a lead that is also discretized along transport direction y, a Wilson term
must regulate the y Brillouin-zone edge as well. The D4 transport literature
lineage supports the 2D Wilson strategy; this bounce tests the isotropic
nearest-neighbor extension rather than silently assuming the 1D reduction is
already a transport Hamiltonian.

Candidate 2D lattice form:

```text
H = alpha/a [sin(kx a) sigma_y - sin(ky a) sigma_x]
  + {m(x) + r alpha/a[(1-cos(kx a))+(1-cos(ky a))]} sigma_z
```

## Periodic double wall

Use:

```text
a  = 10 A = 0.2 xi
Nx = 80
L  = 800 A
wall separation = 400 A = 8 xi
```

Periodic mass:

```text
m(x) = m0 tanh(
  sin(2 pi x/L) / (2 pi w/L)
)
```

It has exact periodicity and two zeros.

Near x=0:

```text
m(x) -> m0 tanh(x/w)
```

so x=0 is the EXP-003 negative-to-positive canonical wall.

The wall at L/2 has the opposite orientation.

## Atomic checks

At small positive lead phase `k=0.05`:

- exactly two states in the provisional low-energy window;
- canonical wall mode localizes near x=0;
- opposite mode localizes near L/2;
- canonical wall has `sigma_x ~ -1`;
- opposite wall has `sigma_x ~ +1`;
- signs of E and dE/dk match the EXP-003 chiral orientations;
- energy/slope remain close to the low-k continuum known answer.

At `k=pi`:

- Wilson `r=0.5` should remove the y-direction low-energy doubler;
- red-team `r=0` should recover the unwanted low-energy copy.

Kwant `Bands` is also checked against its documented Bloch Hamiltonian
construction to catch lead-cell convention mistakes.

## Pseudo-Council

**Continuum:** require direct recovery of EXP-003 spin and propagation sign.

**VAL-001:** preserve `r=0.5`; do not reopen regulator optimization.

**Lattice:** the y Wilson term is necessary because transport turns ky from a
continuum parameter into a lattice momentum.

**Topology:** keep both compensating wall modes explicit on a periodic ring.

**Numerics:** use the pinned NumPy-2 Kwant lane already qualified in C07.

**Falsification:** include the `r=0` Brillouin-edge control. A smoke that
cannot reveal the doubler is not sufficient.

Council converged.

## Why Monte Carlo is not used here

This bounce asks deterministic spectral questions with analytic and red-team
known answers. Random preference sampling would be weaker evidence.

Monte Carlo returns only when choosing among uncertain engineering designs or
sampling a real sensitivity space.

## Gate

A PASS authorizes only the next bounded step: freeze a convergence pilot for
this lead geometry.

It does not authorize a finite scattering region or EXP-004 PASS.
