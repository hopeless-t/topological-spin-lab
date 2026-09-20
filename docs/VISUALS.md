# Visual documentation policy

Visuals in this repository are navigation and explanation aids. They are not
scientific evidence unless an experiment contract explicitly says otherwise.

## Tool choice

### Mermaid — default for structural diagrams

Use Mermaid inside Markdown for:

- experiment architecture;
- roadmaps;
- source-to-experiment lineage;
- state and workflow diagrams.

Why:

- rendered directly by GitHub;
- text-diffable;
- easy to review in pull requests;
- no external design tool is required;
- diagrams stay close to the prose they explain.

### Plain SVG — default for composition-heavy static figures

Use hand-authored, standards-based SVG when a visual form is awkward in
Mermaid, such as the project-identity Venn diagram.

The SVG file is both source and deliverable. Avoid embedded scripts,
foreignObject, external fonts, and remote assets.

### External design tools — optional presentation layer

Figma/FigJam and Canva are available as editing tools and can be useful for
presentation-grade variants. They are not the authoritative source for core
repository diagrams unless an editable source is also stored or reproducibly
exported.

Unity was considered for the Venn diagram, but is not selected:

- no direct Unity integration was available in the current ChatGPT tool set;
- a game-engine project would be disproportionate for a static vector figure;
- binary/editor-state workflows are harder to review than Mermaid or SVG;
- Git-based reproducibility is worse for this use case.

Whimsical and Miro integrations also exist in the plugin ecosystem, but they
are unnecessary for the current repository because Mermaid and SVG cover the
required diagrams without adding an external dependency.

## README budget

Keep the README to at most three primary visuals:

1. project identity Venn diagram;
2. experiment-harness architecture;
3. experiment roadmap.

Detailed literature diagrams belong in docs/LITERATURE_MAP.md.

## Scientific boundary

Visuals must not silently strengthen a claim.

Examples:

- a generic effective-model diagram must not be labeled as an NdBi simulation;
- an arrow between papers is navigation, not proof of direct derivation;
- a roadmap node is planned work, not an implemented result;
- a rendered plot is not acceptance evidence unless the experiment contract
  explicitly makes it so.

## Accessibility

Every standalone SVG should contain a title and description. Important
information must also be available in surrounding Markdown; no critical
meaning may exist only in color or geometry.

## Maintenance

When a frozen experiment contract changes, update the corresponding diagram in
the same pull request. A stale diagram is treated as a documentation defect.
