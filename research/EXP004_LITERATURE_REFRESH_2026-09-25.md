# EXP-004 Literature Refresh — 2026-09-25

**STATUS:** RESEARCH INTAKE / NOT A RESULT

## Question

What is the smallest transport experiment that extends EXP-003 and VAL-001 without overclaiming spin transport or jumping directly to a material/device model?

## Sources checked

### Wilson lattice

Zhou et al., Phys. Rev. B 95, 245137 (2017), DOI 10.1103/PhysRevB.95.245137.

The paper explicitly motivates a two-dimensional Wilson-regularized lattice for
3D-topological-insulator surface states and applies it to low-energy electrical
and transport calculations.

Implication here: VAL-001's Wilson candidate has direct prior-art support for a
transport continuation.

### Kwant

Groth et al., New J. Phys. 16, 063065 (2014), DOI
10.1088/1367-2630/16/6/063065.

Kwant exposes tight-binding leads, propagating modes, scattering matrices,
conductance, wave functions, and related observables.

Implication here: a qualification spike can BORROW a mature scattering engine
rather than making EXP-004 simultaneously a transport-physics experiment and a
new transport-solver project.

### AFM-TI chiral channels

Varnava et al., Nature Communications 12, 3998 (2021), DOI
10.1038/s41467-021-24276-5.

The paper models chiral channels at AFM domain walls and step edges and uses
scattering-matrix language for a more complex quantum-point-junction problem.

Implication here: QPJ physics is real adjacent prior art, but it is downstream
of the cleaner single-channel calibration required here.

### Spin-current caution

Shi et al., Phys. Rev. Lett. 96, 076604 (2006), DOI
10.1103/PhysRevLett.96.076604.

The paper shows that conventional spin-current language is nontrivial in
spin-orbit-coupled systems.

Implication here: EXP-004 should directly measure the spin expectation of
flux-carrying propagating modes. A claim about a conserved spin current requires
a separate observable/continuity definition.

### Landauer lineage

Langreth and Abrahams, Phys. Rev. B 24, 2978 (1981), DOI
10.1103/PhysRevB.24.2978.

Implication here: transmission can support a conductance statement only with
the lead and channel-count conventions attached.

## Atomic decomposition

The proposed EXP-004 problem separates into:

1. **physics target** — continuation of the EXP-003 chiral wall mode;
2. **lattice regularization** — inherited Wilson r=0.5 from VAL-001;
3. **global channel balance** — make the compensating channel explicit rather
   than hide it at a numerical boundary;
4. **transport formalism** — two-terminal scattering / Landauer;
5. **spin observable** — propagating-mode spin expectation;
6. **backend** — independent implementation choice, not scientific authority;
7. **claim ceiling** — generic clean model only.

## Result of intake

The highest-information next experiment is not a QPJ or disorder study.

It is a clean two-terminal domain-wall transport calibration with explicit mode
identity and spin polarization, followed by backend qualification before
implementation.
