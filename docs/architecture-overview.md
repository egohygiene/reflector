# Repository Architecture Overview

This document is the architectural reference for the reflector repository. It
describes the repository's layer model, synchronization boundaries, and
specification organization. For setup instructions, see
[`docs/getting-started.md`](./getting-started.md). For an internal navigation
map, see [`00-README.md`](../00-README.md).

## Structure Map

| Directory | Role |
| --- | --- |
| `paper/` | Canonical manuscript source and publication assembly |
| `paper/sections/` | Semantic manuscript content (LaTeX section files) |
| `paper/figures/` | Figure files and synchronization registries |
| `paper/macros/` | Paper metadata commands (`\papertitle`, `\paperauthor`, etc.) |
| `paper/config/` | Canonical title source (single source of truth for title) |
| `paper/styles/` | Publication style layer — swap per publisher target |
| `specs/` | Specification contracts for workflows and publication architecture |
| `reflector/` | Synchronization and orchestration CLI package |
| `scripts/` | Deterministic build, validation, and audit scripts |
| `.github/workflows/` | CI execution for build, release, and Pages deployment |
| `docs/` | Published documentation surface and reference guides |
| `audits/` | Generated or maintained audit summaries and checkpoints |
| `metadata/` | Canonical repository and publication metadata (YAML) |

## Publication Architecture

reflector uses a layered publication architecture that separates concerns at
each rendering boundary:

```text
Title Layer     → paper/config/           (single source of truth for title)
Content Layer   → paper/sections/         (what the paper says)
Metadata Layer  → paper/macros/           (who/what/when; inputs config/title.tex)
Style Layer     → paper/styles/           (how it looks; swap per publisher)
Build Layer     → .latexmkrc, scripts/    (how it compiles)
```

Swapping the publication style requires only changing one line in `paper.tex`:

```latex
\usepackage{reflector}   % current draft / arXiv style
% \usepackage{ieee}      % future: IEEE format
% \usepackage{acm}       % future: ACM format
```

## Semantic/Render Separation

The repository keeps semantic writing and rendering concerns separated:

- semantic text stays in section-oriented manuscript files (`paper/sections/`)
- publication style and package decisions are isolated in the style layer
- workflow scripts compile and publish without redefining manuscript semantics
- metadata flows from canonical sources (`CITATION.cff`, `publication.json`,
  `paper/macros/metadata.tex`) without duplication

## Specification Organization

Publication specifications are organized under `specs/`:

| Path | Purpose |
| --- | --- |
| `specs/reflector.spec.md` | Canonical reflector specification |
| `specs/publication/` | Manifest architecture, semantic content boundaries, workflow model, renderer abstraction, arXiv publication orientation |
| `specs/workflows/` | Recursive workflow and figure pipeline blueprints |
| `specs/synchronization/` | Checkpoint and boundary contracts |
| `specs/repositories/` | Portable publication repository architecture standards |

## Workflow Organization

Workflow logic is distributed across three execution layers:

| Layer | Location | Scope |
| --- | --- | --- |
| CLI orchestration | `reflector/` | Local and CI synchronization commands |
| Shell/Python scripts | `scripts/` | Build, audit, and validation utilities |
| CI workflows | `.github/workflows/` | Automated build, release, and Pages deployment |

This creates explicit execution boundaries between local automation and CI
deployment, making workflow state inspectable at each layer.

## Figure Synchronization Architecture

Figure state is managed through three synchronized registries:

| Registry | Location | Truth surface |
| --- | --- | --- |
| Figure manifest | `paper/figures/manifest.md` | File identity and state |
| Caption registry | `paper/figures/captions.md` | Caption canonical text |
| Placement references | `paper/sections/*.tex` | Figure placement in manuscript |

Consistency across all three surfaces is validated by
`scripts/audit-publication-readiness.py`.

## Synchronization Philosophy

Architecture decisions favor:

- explicit canonical sources
- deterministic transformations
- inspectable workflow boundaries
- low-ambiguity handoffs between humans, AI systems, and CI

## CI/CD Architecture

GitHub Actions workflows provide:

| Workflow | Trigger | Purpose |
| --- | --- | --- |
| `build-paper.yml` | push, PR | Compile manuscript PDF |
| `pages.yml` | push to main | Deploy GitHub Pages |
| `reuse.yml` | push, PR | REUSE/SPDX compliance |
| `synchronization.yml` | push, PR (metadata paths) | Metadata consistency validation |
| `release-paper.yml` | release tag | Publish release artifacts |
| `paper-quality.yml` | push, PR | ChkTeX and quality checks |

## Publication Metadata Sources

| File | Role |
| --- | --- |
| `CITATION.cff` | Machine-readable citation (GitHub and downstream tooling) |
| `publication.json` | Publication metadata and DOI |
| `release-manifest.json` | Release contracts and checksum declarations |
| `codemeta.json` | CodeMeta software metadata |
| `.zenodo.json` | Zenodo deposit configuration |
| `metadata/repository.yaml` | Canonical repository metadata |
| `metadata/authors.yaml` | Author metadata |
| `metadata/publication.yaml` | Publication lifecycle metadata |
