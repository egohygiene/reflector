# Publication Platform Template

A portable research publication template extracted from the Reflector reference
implementation. Copy this directory into a new repository to bootstrap a paper,
metadata surfaces, validation scripts, CI workflows, and a GitHub Pages landing
page.

> **Origin note:** this template was extracted from Reflector, which remains the
> reference implementation for the broader publication platform.

## What this template provides

- A standalone LaTeX paper scaffold in `paper/`
- Canonical metadata files in `metadata/`, `CITATION.cff`, `.zenodo.json`, and `codemeta.json`
- Version synchronization and metadata validation scripts in `scripts/`
- CI, lint, version bump, release tag, and Pages workflows in `.github/workflows/`
- A reusable documentation and publication surface in `docs/`

## Core modules

### Paper Authoring

- `paper/paper.tex` entry point
- `paper/styles/publication.sty` reusable publication style
- section stubs for abstract, introduction, methods, results, and appendix
- figure and bibliography registries

### Metadata & Versioning

- `VERSION` as the canonical semantic version source
- `metadata/publication.yaml` for publication-level metadata
- `metadata/authors.yaml` for author identity data
- `scripts/sync-version.py` for downstream version propagation
- `scripts/validate-metadata.py` for consistency checks

### CI

- `ci.yml` for metadata validation and paper builds
- `paper-quality.yml` for ChkTeX linting
- `bump-version.yml` for manual semantic version bumps
- `release-tag.yml` for annotated tag creation
- `pages.yml` for GitHub Pages deployment

## Optional modules

- **GitHub Pages** via `docs/` and `.github/workflows/pages.yml`
- **GitHub Releases** via version/tag automation
- **arXiv** by adapting the release bundle for arXiv submission
- **Zenodo** via `.zenodo.json` and DOI metadata fields

## Prerequisites

- TeX Live with `latexmk` and `biber`
- Python 3.11+
- [`task`](https://taskfile.dev/)
- `chktex`

## Quick start

1. Copy the contents of `template/` into a new repository root.
2. Update `metadata/publication.yaml`.
3. Update `metadata/authors.yaml`.
4. Update `paper/config/title.tex` and `paper/macros/metadata.tex`.
5. Run `task setup`.
6. Run `task validate`.
7. Run `task paper:build`.

## Directory structure

```text
template/
├── .github/
├── audits/
├── docs/
├── metadata/
├── paper/
├── scripts/
├── specs/
├── .chktexrc
├── .editorconfig
├── .gitattributes
├── .gitignore
├── .latexindent.yml
├── .latexmkrc
├── .zenodo.json
├── CITATION.cff
├── LICENSE
├── README.md
├── Taskfile.yml
├── VERSION
├── codemeta.json
├── publication.json
└── release-manifest.json
```

## Configuration guide

- Use `metadata/publication.yaml` as the canonical publication metadata source
- Use `metadata/authors.yaml` for canonical author identity
- Keep title, repository URL, Pages URL, and release date aligned across all surfaces
- Treat `publication.json` and `release-manifest.json` as generated or synchronized metadata surfaces
- Run `python3 scripts/sync-version.py` after changing `VERSION`

## Task reference

- `task setup`
- `task validate`
- `task paper:build`
- `task paper:watch`
- `task paper:lint`
- `task paper:format`
- `task metadata:sync`
- `task metadata:check`

## Publishing options

- Publish a PDF artifact through CI
- Deploy a landing page and PDF through GitHub Pages
- Create annotated Git tags from semantic versions
- Attach release assets to GitHub Releases
- Fill DOI metadata and archive through Zenodo when ready

## Upgrading the template

When the reference implementation evolves, compare your repository against a
fresh copy of this template and merge changes module by module:

1. root configuration
2. scripts and workflows
3. metadata surfaces
4. paper style and scaffolding
5. documentation and publishing surfaces

Keep your repository identity separate from template internals so future
upgrades remain mechanical and low risk.
