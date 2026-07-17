# Template Configuration Model

Generated: 2026-07-17
Issue: #235 — Audit publication template extraction readiness

---

## Overview

The template uses a two-file canonical configuration model. All publication
identity, metadata, and version information is defined in two authoritative YAML
sources. Downstream metadata surfaces are derived programmatically from these
sources through a synchronization script and a validation script.

Adopters configure their publication by editing exactly two files, then running
one command to propagate changes.

---

## Canonical Configuration Sources

### Primary Source 1: `metadata/publication.yaml`

**Role:** Single source of truth for all publication-level metadata.

Defines:
- `slug` — short identifier used for artifact file naming
- `title.main`, `title.subtitle`, `title.full` — full publication title
- `abstract` — publication abstract for metadata surfaces
- `keywords` — search and index keywords
- `version` — current semantic version (synchronized from `VERSION`)
- `status` — publication lifecycle status (`draft`, `submitted`, `published`)
- `date_released` — publication date
- `license` — SPDX license identifier
- `identifiers.doi` — DOI (null until formally assigned)
- `identifiers.arxiv_id` — arXiv identifier (null until accepted)
- `identifiers.zenodo_doi` — Zenodo deposition DOI
- `identifiers.zenodo_concept_doi` — Zenodo concept DOI
- `repository_url` — canonical repository URL
- `pages_url` — canonical GitHub Pages URL
- `preferred_citation.type` — citation type for CITATION.cff
- `companion_publications.magazine.enabled` — magazine module toggle

### Primary Source 2: `metadata/authors.yaml`

**Role:** Single source of truth for all author identity information.

Defines (per author):
- `family-names` — author last name
- `given-names` — author first name
- `alias` — internal reference alias
- `orcid` — bare ORCID identifier (without URL prefix)
- `orcid_url` — full ORCID URL
- Optional: `github`, `affiliation`, `email`

### Version File: `VERSION`

**Role:** Canonical semantic version number (`MAJOR.MINOR.PATCH`).

All other version surfaces are derived from this file. Only `VERSION` should be
edited directly to advance the version. Downstream surfaces are updated by
`scripts/sync-version.py`.

---

## Required User Inputs

The minimum information a user must provide to configure a new publication:

| Field | Source File | Example |
|---|---|---|
| Project slug | `metadata/publication.yaml` | `my-paper` |
| Publication title (main) | `metadata/publication.yaml` | `Adaptive Memory Systems` |
| Publication title (subtitle) | `metadata/publication.yaml` | `A Framework for AI Memory Management` |
| Full title | `metadata/publication.yaml` | `Adaptive Memory Systems: A Framework...` |
| Abstract | `metadata/publication.yaml` | (paragraph text) |
| Version | `VERSION` | `0.1.0` |
| Release date | `metadata/publication.yaml` | `2026-06-01` |
| Author family name | `metadata/authors.yaml` | `Smith` |
| Author given name | `metadata/authors.yaml` | `Jane` |
| Author ORCID | `metadata/authors.yaml` | `0009-0001-2345-6789` |
| Repository URL | `metadata/publication.yaml` | `https://github.com/org/repo` |
| GitHub Pages URL | `metadata/publication.yaml` | `https://org.github.io/repo/` |
| LaTeX title macros | `paper/config/title.tex` | `\newcommand{\papertitlemain}{...}` |
| LaTeX metadata macros | `paper/macros/metadata.tex` | `\paperauthor`, `\paperrepository`, etc. |

---

## Optional Integrations

| Module | Configuration | Status |
|---|---|---|
| Zenodo deposition | `metadata/publication.yaml` → `identifiers.zenodo_doi`, `.zenodo.json` | Available (passive via GitHub release) |
| arXiv submission | `metadata/publication.yaml` → `identifiers.arxiv_id` | Manual (bundle generation not yet in template) |
| Magazine publication | `metadata/publication.yaml` → `companion_publications.magazine.enabled` | Not yet included in template |
| GitHub Pages | `docs/` + `pages.yml` workflow | Included |
| GitHub Releases | `bump-version.yml` + `release-tag.yml` | Included |
| Dev container | `.devcontainer/` | Not yet in template |

---

## Generated Metadata Surfaces

After editing the canonical sources and running `python3 scripts/sync-version.py`,
the following surfaces are automatically synchronized:

| Surface | Type | Key Synchronized Fields |
|---|---|---|
| `CITATION.cff` | YAML | `version`, `title`, `authors[0].orcid`, `repository-code` |
| `.zenodo.json` | JSON | `version`, `title`, `creators[0].orcid`, `doi`, `conceptdoi` |
| `codemeta.json` | JSON | `version`, `name`, `author[0].@id`, `codeRepository`, `url` |
| `publication.json` | JSON | `version`, `release_tag`, `title`, `slug`, `artifacts.paper.pdf` |
| `release-manifest.json` | JSON | `current_version`, `release_tag` |
| `metadata/publication.yaml` | YAML | `version` |

`scripts/validate-metadata.py` cross-validates all surfaces for consistency.
Running `python3 scripts/validate-metadata.py` will report any drift.

---

## Secrets and Repository Settings

### Required for GitHub Actions

| Secret / Setting | Required For | Notes |
|---|---|---|
| `GITHUB_TOKEN` | `bump-version.yml` — commit push | Automatically available |
| GitHub Pages — enabled in repo settings | `pages.yml` | Manual one-time setup |
| GitHub Pages — source set to GitHub Actions | `pages.yml` | Manual one-time setup |

### Required for Zenodo Integration (optional)

| Secret / Setting | Required For | Notes |
|---|---|---|
| `ZENODO_TOKEN` | Active Zenodo deposition workflow | Not yet included in template |
| Zenodo concept record ID | `metadata/publication.yaml identifiers.zenodo_concept_doi` | Set after first manual deposit |

### Required for arXiv Integration (optional)

| Secret / Setting | Required For | Notes |
|---|---|---|
| None (manual submission) | arXiv bundle upload | Manual boundary by design |

---

## Feature Flags and Module Configuration

### Enabled by Default

- Paper PDF build via CI (`ci.yml` `build-paper` job)
- Metadata validation via CI (`ci.yml` `validate` job)
- ChkTeX paper linting (`paper-quality.yml`)
- Version bump automation (`bump-version.yml`)
- Release tag automation (`release-tag.yml`)
- GitHub Pages deployment (`pages.yml`)

### Disabled by Default

Set `companion_publications.magazine.enabled: true` in `metadata/publication.yaml`
to signal intent to use the magazine module. Note: magazine infrastructure is not
yet included in the template.

Set `optional_modules.zenodo: true` in `publication.json` to indicate Zenodo
integration is active.

Set `optional_modules.arxiv: true` in `publication.json` to indicate arXiv
integration is active.

---

## Artifact Naming Convention

Publication artifacts derive their filenames from the `slug` field in
`metadata/publication.yaml`. The slug is used as:

- PDF artifact name: `{slug}.pdf`
- `publication.json` → `artifacts.paper.pdf`: `{slug}.pdf`
- `docs/{slug}.pdf` — deployed PDF path on GitHub Pages

The slug must be a lowercase hyphen-separated identifier with no spaces or special
characters. Changing the slug after publication requires updating the PDF filename
in all deployment surfaces.

---

## Validation Commands

| Command | Purpose |
|---|---|
| `python3 scripts/sync-version.py --check` | Verify all version surfaces match VERSION |
| `python3 scripts/sync-version.py` | Apply VERSION to all surfaces |
| `python3 scripts/validate-metadata.py` | Cross-validate all metadata surfaces |
| `task metadata:check` | Run both validation commands |
| `task metadata:sync` | Apply version synchronization |
| `task validate` | Run metadata check + paper lint |

---

## Configuration Workflow for a New Publication

```
1. Copy template/ into new repository root
2. Edit metadata/publication.yaml
   → set slug, title, abstract, keywords, repository_url, pages_url
3. Edit metadata/authors.yaml
   → set author name and ORCID
4. Edit paper/config/title.tex
   → update \papertitlemain and \papertitlesubtitle
5. Edit paper/macros/metadata.tex
   → update \paperauthor, \paperrepository, \paperdate, \paperstatus
6. Edit VERSION
   → set starting version (e.g. 0.1.0)
7. Run: python3 scripts/sync-version.py
   → propagates version to all downstream surfaces
8. Run: python3 scripts/validate-metadata.py
   → confirms all surfaces are consistent
9. Run: task paper:build
   → validates the LaTeX build compiles cleanly
10. Enable GitHub Pages in repository settings
    → source: GitHub Actions
11. Push to main
    → triggers CI, Pages deployment, and release tag creation
```

---

## Drift Detection

`scripts/validate-metadata.py` exits non-zero when:

- Any version surface diverges from `VERSION`
- Title in CITATION.cff, `.zenodo.json`, codemeta.json, or publication.json diverges from `metadata/publication.yaml title.full`
- ORCID in CITATION.cff, `.zenodo.json`, or codemeta.json diverges from `metadata/authors.yaml authors[0].orcid`
- DOI surfaces diverge when a DOI is assigned
- Repository URL or Pages URL diverge across surfaces
- PDF artifact name in `publication.json` does not match `{slug}.pdf`

CI (`ci.yml`) runs `validate-metadata.py` on every push to `main` and on all
pull requests. Drift blocks merges when branch protection is enabled.
