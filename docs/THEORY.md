# Theory: EXP-001

EXP-001 uses the effective surface Hamiltonian

$$
H_0(\mathbf{k}) = \alpha(k_x\sigma_y-k_y\sigma_x),
$$

with the surface normal convention fixed to `+z`.

The eigenvalues are

$$
E_\pm = \pm\alpha\sqrt{k_x^2+k_y^2}.
$$

For nonzero momentum, the upper-band spin expectation is

$$
\langle\boldsymbol{\sigma}\rangle_+
=
\frac{1}{|\mathbf{k}|}(-k_y,k_x,0),
$$

and the lower band has the opposite spin.

Consequences used by EXP-001:

- the Hamiltonian is Hermitian;
- the spectrum is gapless at `k = 0`;
- the reference spectrum is symmetric about zero energy;
- spin lies in the surface plane;
- spin is orthogonal to momentum;
- with the `+z` convention, upper-band helicity is `+1` and lower-band helicity
  is `-1`;
- the massless model is time-reversal symmetric.

## Source lineage

The effective-surface-model lineage is documented in
[`REFERENCES.md`](REFERENCES.md), especially:

- `P-TI-2007` for the three-dimensional topological-insulator classification;
- `P-BI2SE3-2009` for the single-surface-Dirac-cone material/model bridge;
- `P-SPIN-2009` for experimental spin-momentum locking;
- `P-MODEL-2010` for the derived effective surface Hamiltonian.

The project-specific Hakken chain from those sources to EXP-001 and later
experiments is recorded in [`LITERATURE_MAP.md`](LITERATURE_MAP.md).

These citations establish the model lineage. They do not make EXP-001 a
simulation of Bi2Se3, NdBi, or any other specific material.

No lattice topology, magnetic gap, edge transport, or material-specific fit is
claimed by EXP-001.
