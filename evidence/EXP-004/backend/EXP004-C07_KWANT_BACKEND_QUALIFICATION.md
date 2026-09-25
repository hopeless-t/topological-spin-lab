# EXP004-C07 — Kwant backend qualification and lane disposition

**STATUS:** PRIMITIVE BACKEND QUALIFIED / WILSON PHYSICS NOT YET TESTED

## External Actions result

Run `36117118891` completed both deterministic lanes successfully.

### Stable released lane

```text
Python 3.12.14
Kwant 1.5.0
NumPy 1.26.4
SciPy 1.14.1

modes L/R     1 / 1
T(L->R)       1.0
R(L->L)       0.0
||S†S-I||     0.0
<sigma_z>     1.0
```

### NumPy-2 aligned development lane

Pinned upstream revision:

`ef12fa0d7`

Observed package:

`Kwant 1.5.1.dev68+gef12fa0d7`

```text
Python 3.12.14
NumPy 2.5.3
SciPy 1.18.1

modes L/R     1 / 1
T(L->R)       1.0
R(L->L)       0.0
||S†S-I||     0.0
<sigma_z>     1.0
```

Both lanes therefore satisfy the primitive capability needed for the next
research spike.

## Pseudo-Council

### Round 1

**Release discipline:** prefer stable 1.5.0 because it is an upstream release.

**Stack discipline:** prefer the pinned development snapshot because the
repository's numerical core is already NumPy 2.x; an isolated NumPy-1 transport
environment increases integration and maintenance complexity.

**Reproducibility:** a development dependency can be reproducible when the exact
upstream commit is pinned and the Actions runtime/evidence is preserved.

**Risk:** a pinned unreleased source is not equivalent to a stable release.

Open disagreement: research-spike choice versus canonical project dependency.

### Round 2

Convergence:

```text
next bounded research spike:
    pinned dev ef12fa0d7 + NumPy 2

independent fallback/cross-check:
    stable Kwant 1.5.0 + NumPy 1.26.4

add Kwant to pyproject:
    HOLD
```

This keeps current-stack alignment for the experiment while retaining a stable
independent lane.

## Monte Carlo sensitivity

300,000 draws per scenario compared:
- stable isolated NumPy-1 lane;
- pinned development NumPy-2 lane;
- custom NumPy-2 solver.

Under uniform, ordinary stability-heavy, stack-alignment, maintenance, and
reproducibility scenarios, the pinned dev lane was modal (~94.9–99.98%).

However an intentionally extreme **release-hardline** scenario reversed the
result:

```text
stable isolated NumPy1  ~94.50%
pinned dev NumPy2        ~0.06%
custom solver            ~5.44%
```

That reversal is useful. The correct conclusion is not "dev is universally
better." It is:

> for a bounded research implementation spike, stack alignment plus exact
> source pinning favors the dev lane; for a canonical long-lived dependency,
> upstream release status remains a gating concern.

## Claim ceiling

Backend primitives are qualified.

Not yet qualified:
- Wilson domain-wall Hamiltonian construction in Kwant;
- periodic double-wall lead modes;
- spatial mode classification;
- convergence;
- fermion-doubler rejection in transport;
- EXP-004 scientific acceptance.

## Next bounce

Build the smallest Wilson `r=0.5` **lead-mode / band-structure smoke** on the
pinned NumPy-2 lane.

Do not start the full scattering device yet.

Required first physical bridge:
- encode the frozen VAL-001 Wilson lattice consistently;
- use periodic transverse double-wall geometry;
- verify low-energy mode count, velocity sign, wall localization, and spin
  against EXP-003/VAL-001 before attaching a device region.
