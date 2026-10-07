# VAL-002 source refresh — 2026-10-07

**Status:** SOURCE REVIEW COMPLETE / MODEL FITTING NOT AUTHORIZED  
**Purpose:** freeze the empirical/material-reference targets that VAL-002 must explain before any larger NdBi Hamiltonian is proposed.

## Research rule

This source refresh does not license a Hamiltonian.

The required order is:

```text
source observation
-> declared experimental/material context
-> observable contract
-> representability audit
-> smallest candidate model
-> falsification / fit
```

Terms may not be added to a reduced model merely because they look physically plausible.

## Primary source set

### S1 — domain-selective NdBi surface Dirac response

A. Honma et al.,
“Antiferromagnetic topological insulator with selectively gapped Dirac cones,”
*Nature Communications* **14**, 7396 (2023).
DOI: `10.1038/s41467-023-42782-6`

Materially relevant observations:

- NdBi (001) contains distinct antiferromagnetic surface domains;
- the surface with an out-of-plane component of the AF-ordering vector exhibits a strongly gapped Dirac-cone state;
- a surface parallel to the AF-ordering vector can retain a gapless Dirac state despite broken time reversal;
- the distinction is tied to whether the combined antiferromagnetic symmetry is broken or preserved;
- the surface Brillouin zone contains Dirac-state structure around both surface Gamma and M points.

**VAL-002 consequence:** surface index, AF-domain/symmetry class, and selected TRIM are explicit context variables. A single unconditional target called “the NdBi gap” is invalid.

### S2 — multi-q / band-folding material reference

L.-L. Wang et al.,
“Unconventional surface state pairs in a high-symmetry lattice with anti-ferromagnetic band-folding,”
*Communications Physics* **6**, 78 (2023).
DOI: `10.1038/s42005-023-01180-6`

Materially relevant observations/calculations:

- type-I AFM 1q, 2q, and 3q structures generate different band-folding patterns;
- unconventional surface-state pairs appear inside AFM band-folding hybridization gaps;
- surface multiplicity depends on magnetic order and surface orientation;
- the reported calculations give 1q/2q Dirac-semimetal and 3q Weyl-semimetal bulk structures;
- a Fermi-arc-like surface signature does not uniquely diagnose a Weyl bulk phase.

**VAL-002 consequence:** magnetic q-order is an explicit model/context input and branch multiplicity is an adequacy observable. The contract must not silently hard-code one q-order as universal NdBi.

### S3 — spin-split AFM surface bands

R. Yamamoto et al.,
“Spin splitting in the surface electronic structure of antiferromagnet NdBi,”
*Physical Review Research* **7**, L022005 (2025).
DOI: `10.1103/PhysRevResearch.7.L022005`

Materially relevant observations:

- two surface bands appearing in the AFM state carry opposite spin polarization;
- the measured polarization is antisymmetric about a time-reversal-invariant momentum;
- the result is interpreted as surface inversion-symmetry breaking acting together with AF order;
- single-q DFT reproduces the observed spin-split surface-state structure.

**VAL-002 consequence:** energy dispersion alone is insufficient. A candidate must expose vector spin information and reproduce at least the qualitative branch/spin antisymmetry class in the declared context.

### S4 — directly measured spin-polarized surface Dirac gap

Y. Fukushima et al.,
“Direct observation of a spin-polarized surface Dirac gap in the antiferromagnetic topological insulator NdBi,”
*Nature Communications* (2026), published 15 September 2026.
DOI: `10.1038/s41467-026-77571-4`

Materially relevant observations:

- a spin-polarized topological surface Dirac cone is resolved from bulk-derived states;
- the measured Dirac-point gap is `17 ± 2 meV`;
- the reported DFT reference is approximately `12 meV`;
- temperature dependence and controlled surface contamination link the gap to surface magnetic order;
- the gap opens only in the presence of the relevant surface magnetic order.

**VAL-002 consequence:** the magnetic gap is a quantitative target only inside the source’s declared surface/magnetic context. Surface/bulk discrimination and magnetic-order sensitivity are mandatory observables, not optional interpretation.

### S5 — local termination and one-dimensional edge-state discriminator

A. Almoalem et al.,
“Spectroscopic Evidence of Edge-Localized States in an Antiferromagnet Topological Insulator NdBi,”
*Advanced Science* **13** (30), e22116 (2026), first published 14 January 2026.
DOI: `10.1002/advs.202522116`

Materially relevant observations:

- spin-polarized STM/QPI distinguishes ferromagnetic and antiferromagnetic terminations;
- odd step edges on the ferromagnetic termination act as magnetic domain walls and host localized one-dimensional edge modes;
- the edge-state signal disappears above the Néel temperature;
- analogous step edges on the antiferromagnetic surface do not show the enhanced edge-state density of states;
- the reported edge signal is localized on nanometer scale and is discussed in a material with nearby trivial/nontrivial bands.

**VAL-002 consequence:** termination and boundary class are experimentally discriminating variables. However, this is **not part of the minimum C01 surface-band adequacy gate**. It is frozen as a downstream boundary/edge discriminator for a later VAL-002 stage so that the first material model is not over-scoped.

## Reconciliation rather than source averaging

The primary sources do not define one context-free NdBi band structure. They probe or calculate different:

- surface terminations;
- AF domains;
- symmetry classes;
- q-orders;
- momenta / TRIMs;
- spectroscopy modalities;
- boundary geometries.

VAL-002 must therefore treat these as explicit coordinates rather than averaging apparently different observations into one parameter set.

In particular:

```text
2025 single-q spin-SARPES reproduction
!= evidence that single-q is the only admissible NdBi order

2026 17±2 meV gapped surface cone
!= an unconditional gap required on every NdBi surface/domain

2026 FM-step edge state
!= a mandatory observable for the first uniform-surface reduced model
```

## Frozen source-role classification

### Mandatory C01 sources

`S1–S4` define the first model-adequacy target contract.

### Downstream discriminator

`S5` is mandatory for a later termination/boundary validation stage, but deliberately does not block the first uniform-surface representability test.

## Source-to-observable map

```text
surface/domain symmetry response        S1
branch count / q-order dependence       S2
spin-split branch structure             S3
vector spin antisymmetry                S3
quantitative Dirac gap                  S4
surface vs bulk discrimination          S4
surface-magnetism sensitivity           S4
termination-dependent 1D edge state     S5 (downstream)
```

## Claim ceiling

This refresh freezes observations and source roles only. It does not establish:

- which reduced Hamiltonian is correct;
- whether L1 or L2 is sufficient;
- numerical coupling constants;
- an NdBi transport prediction;
- a material-specific domain-wall conductance;
- that the edge-localized state is reproduced by the current L0 EXP-004 model.
