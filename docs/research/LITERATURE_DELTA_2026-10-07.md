# Literature delta — 2026-10-07

**Status:** research intake / source delta  
**Authority:** primary literature informs questions and model boundaries; it does not become repository evidence by citation alone.

This note records literature that materially changes how the next `topological-spin-lab`
experiments should be framed. It is deliberately separate from canonical experiment
evidence.

## 1. Direct NdBi lineage has strengthened

### Yamamoto et al. — spin splitting in NdBi surface states (2025)

Rikako Yamamoto et al.,  
“Spin splitting in the surface electronic structure of antiferromagnet NdBi,”  
*Physical Review Research* **7**, L022005 (2025).  
DOI: https://doi.org/10.1103/PhysRevResearch.7.L022005

Reported relevance:

- laser-SARPES resolves oppositely spin-polarized surface bands in the AFM state;
- the spin polarization is antisymmetric around a time-reversal-invariant momentum;
- the interpretation combines surface inversion-symmetry breaking with AFM order;
- single-q DFT reproduces the observed spin-split surface-state structure.

### Fukushima et al. — spin-polarized surface Dirac gap in NdBi (2026)

Yuto Fukushima et al.,  
“Direct observation of a spin-polarized surface Dirac gap in the antiferromagnetic topological insulator NdBi,”  
*Nature Communications* (2026).  
DOI: https://doi.org/10.1038/s41467-026-77571-4

This source is already part of the repository’s direct lineage. Its newly important
implication for the restart is methodological:

- a `17 ± 2 meV` surface Dirac gap is directly resolved;
- the gap is linked experimentally to surface magnetic order;
- controlled surface contamination suppresses the relevant magnetic surface state/gap.

### Consequence for this repository

The current two-component generic Dirac model remains valid as a **known-answer model**,
but it is not an adequate model of all observed NdBi surface phenomenology.

In particular, do not infer that EXP-002/003/004 reproduce:

- the observed pair of spin-split NdBi surface bands;
- the NdBi magnetic-domain structure;
- the material-specific gap magnitude;
- the detailed symmetry mechanism producing the observed surface states.

A later material-informed lane must therefore begin with a **model-adequacy contract**,
not by substituting `m = 8.5 meV` into the current generic model and calling it NdBi.

## 2. Domain-wall transport literature has become more geometry-sensitive

### Pournaghavi and Canali — magnetic-TI nanoribbon domain-wall transport (2024)

Nezhat Pournaghavi and Carlo M. Canali,  
“Chiral edge transport along domain walls in magnetic topological insulator nanoribbons,”  
*Journal of Physics: Condensed Matter* **36**, 405803 (2024).  
DOI: https://doi.org/10.1088/1361-648X/ad5d34

Reported relevance:

- atomistic tight-binding + NEGF transport;
- conductance depends on domain-wall orientation relative to transport;
- a transport-aligned wall can produce quantized conductance in the studied model;
- a perpendicular wall does not generically preserve the same quantization;
- propagating domain-wall modes carry a spin-polarized character.

### Cheng — snake states at magnetic-TI domain walls (2025)

Shuguang Cheng,  
“Snake states at domain walls of magnetic topological insulators,”  
*Physical Review B* **112**, 115302 (2025).  
DOI: https://doi.org/10.1103/yjxb-hl6h

Reported relevance:

- transmission can oscillate with snake-state wave cycles;
- wavelength depends on wall profile and orientation;
- slanted/curved-wall transport can show endpoint-controlled behavior within the studied model;
- strong-disorder and finite-domain cases expose additional transport regimes.

### Consequence for EXP-004 and its successors

The existing EXP-004 straight, clean, identical-lead/device geometry remains the correct
first calibration because it removes geometry as a confounder.

But a PASS there must not be promoted to a general statement that “domain-wall shape does
not matter” or “domain-wall transport is quantized.”

A new post-baseline geometry lane should explicitly test:

1. straight transport-aligned wall;
2. slanted wall;
3. smoothly curved wall with fixed endpoints;
4. transverse/perpendicular wall;
5. endpoint displacement at fixed curve class.

The primary observables should remain channel-resolved: transmission, reflection,
mode localization, spin expectation, and channel count.

## 3. Experimental chiral transport now emphasizes leakage/coexistence

### Zhu et al. — direct imaging of zero-field chiral edge current (2025)

Jinjiang Zhu et al.,  
“Direct observation of chiral edge current at zero magnetic field in a magnetic topological insulator,”  
*Nature Communications* (2025).  
DOI: https://doi.org/10.1038/s41467-025-56326-7

Reported relevance:

- zero-field chiral edge current is directly imaged in MnBi2Te4;
- edge current can coexist with finite bulk conduction;
- a chiral boundary channel therefore does not imply an experimentally isolated
  single-channel transport problem.

### Zhang et al. — zero-field chiral edge transport in MnBi2Te4 (2025)

Chusheng Zhang et al.,  
“Zero-field chiral edge transport in an intrinsic magnetic topological insulator MnBi2Te4,”  
*Nature Communications* **16**, 5587 (2025).  
DOI: https://doi.org/10.1038/s41467-025-59160-z

Reported relevance:

- multi-terminal transport resolves zero-field chiral edge transport;
- near the band edge, chiral edge transport interacts with bulk conduction channels;
- nonideal longitudinal/transverse resistances remain physically informative rather
  than simply constituting numerical failure.

### Consequence for later robustness work

After the clean single-channel calibration, a useful successor is not merely “add random
onsite disorder.” A more diagnostic lane is:

```text
protected/chiral channel
+ controlled trivial or bulk-like leakage channel
-> channel-resolved scattering
-> identify when total conductance ceases to diagnose channel identity
```

This can directly test a failure mode relevant to experimental interpretation:
**correct topological channel identity with non-ideal total transport.**

## 4. New candidate research axes

These are proposals, not authorized experiments.

### AXIS-A — Geometry / path topology

Question:

> Which transport properties depend on local wall curvature, global endpoint placement,
> and orientation relative to the leads?

Reason:

Recent numerical work makes geometry a first-class variable rather than a drawing detail.

### AXIS-B — Magnetic-mass amplitude versus sign

Question:

> What survives when the surface magnetic mass is suppressed locally without changing
> sign, compared with a true sign-changing mass domain wall?

Reason:

The 2026 NdBi result ties the observed gap to surface magnetic order. A “mass suppression
trench” is therefore a useful null/control geometry against the sign-changing topological
wall.

Expected distinction:

- sign change: topological mass-domain-wall known answer may support a chiral bound mode;
- same-sign suppression: no topological sign change, so no such protected mode should be
  assumed.

### AXIS-C — Channel leakage / mixed transport

Question:

> Can the harness preserve the identity of the chiral wall mode when trivial or bulk-like
> propagating channels coexist?

Reason:

Recent MnBi2Te4 experiments show that chiral edge physics and bulk conduction can coexist.

### AXIS-D — NdBi model adequacy

Question:

> What is the smallest effective model that can reproduce the *qualitative class* of
> spin-split, AFM- and surface-symmetry-dependent states seen in NdBi without claiming a
> first-principles material model?

This axis must remain downstream of the generic transport calibration.

## Claim ceiling

This literature delta authorizes **questions**, not scientific results.

It does not authorize:

- an NdBi-specific transport prediction;
- a material fit;
- a claim of QAH quantization in NdBi;
- a claim that a curved-wall result from another model transfers unchanged to this one;
- a claim that bulk/edge coexistence is reproduced before a corresponding experiment is
  implemented and validated.
