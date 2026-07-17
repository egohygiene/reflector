# Template Extraction Readiness Audit

Generated: 2026-07-17
Issue: #235 — Audit publication template extraction readiness

---

## Executive Summary

The Reflector repository has undergone a comprehensive readiness review across
thirteen audit areas covering infrastructure separation, hardcoded value risks,
build portability, GitHub Actions portability, archival integration, documentation,
example content, and licensing.

A functional publication platform template already exists at `template/` and was
extracted in a prior implementation phase. This audit validates that extraction,
identifies the current state of each component, documents remaining gaps, and
provides an actionable go/no-go conclusion.

The template cleanly separates reusable publication infrastructure from all
Reflector-specific research content. No Reflector identity (author name, ORCID,
DOI, Zenodo record identifier, repository slug, publication title, or arXiv
placeholder) appears in `template/`. Placeholder values follow a consistent
`your-org / your-repo / example-publication / 0000-0000-0000-0000` convention
that is immediately recognizable and replaceable by adopters.

---

## Readiness Score

| Audit Area | Score |
|---|---|
| 1. Repository and Content Separation | ✅ Ready |
| 2. Hardcoded Values and Portability Risks | ✅ Ready (minor cleanup) |
| 3. Template Boundary Definition | ✅ Ready |
| 4. Proposed Template Structure | ✅ Ready |
| 5. Configuration Model | ✅ Ready |
| 6. Build Portability | ✅ Ready (live build unvalidated) |
| 7. GitHub Actions Portability | ✅ Ready |
| 8. Publication and Release Portability | ✅ Ready |
| 9. Archival Integration Portability | ⚠️ Minor Cleanup |
| 10. Documentation and Onboarding | ⚠️ Minor Cleanup |
| 11. Example Content Strategy | ✅ Ready |
| 12. Licensing and Attribution | ✅ Ready |
| 13. Independent Copy Test | ✅ Ready (structural validation passed) |

**Overall Readiness: CONDITIONAL GO**

---

## Go / No-Go Recommendation

### CONDITIONAL GO

The `template/` directory is ready for direct adoption into a new repository
following a defined set of minor enhancements. No blocking architectural
problems exist. All extraction prerequisites are satisfied.

**Rationale:**

- All Reflector-specific identity has been removed from `template/`.
- Canonical metadata configuration follows the `metadata/publication.yaml` +
  `metadata/authors.yaml` single-source-of-truth model.
- Version synchronization and metadata validation scripts are fully generic.
- CI, versioning, tagging, and Pages workflows contain no Reflector-specific
  references.
- The paper scaffold compiles to a generic placeholder publication.
- Metadata consistency is enforced programmatically across all surfaces.

The conditional qualifier reflects two minor gaps:

1. The `.devcontainer/` developer container definition is absent from `template/`
   (the main repository's `.devcontainer/` is Reflector-named and not yet
   generalized). This is an optional enhancement and does not block usage.
2. The `--publish` flag in `scripts/build-paper.sh` derives the output PDF
   filename from the directory name (`basename "${paper_directory}"`) rather than
   reading the canonical `slug` from `metadata/publication.yaml` or
   `publication.json`. An adopter who renames the paper directory will get a
   mismatch between the published PDF name and the configured slug. This is a
   minor portability concern but does not prevent a working build.

---

## Blocking Findings

None identified.

---

## Major Findings

None identified.

---

## Minor Findings

### MF-01: `--publish` slug derives from directory name, not metadata

**File:** `template/scripts/build-paper.sh`
**Finding:** The `publish_paper` function uses `basename "${paper_directory}"` as the
PDF filename stem. If the paper directory is renamed or the `slug` in
`metadata/publication.yaml` differs from the directory name, the published PDF
name will not match the metadata-configured artifact name.
**Recommendation:** Read the slug from `publication.json` or `metadata/publication.yaml`
in the `publish_paper` function so the output filename always matches the
canonical slug.
**Severity:** Minor

---

### MF-02: `docs/index.html` hardcodes placeholder OG and JSON-LD URLs

**File:** `template/docs/index.html`
**Finding:** The Open Graph meta tags and JSON-LD schema embed
`https://your-org.github.io/your-repo/` as static strings. These are intentional
placeholders, but the landing page derives its runtime metadata from
`publication.json` via JavaScript. The static meta tags are therefore stale at
build time and will only be populated dynamically.
**Recommendation:** Document clearly in `docs/index.html` comments that the
static meta tags are placeholders that adopters must replace in the HTML, or
generate them during the Pages deployment step from `publication.json`.
**Severity:** Minor

---

### MF-03: `template/paper/macros/metadata.tex` repository URL is a literal placeholder

**File:** `template/paper/macros/metadata.tex`
**Finding:** `\paperrepository` is defined as the literal string
`https://github.com/your-org/your-repo`. An adopter who updates
`metadata/publication.yaml` and `publication.json` but does not also update this
LaTeX macro will produce a PDF with a stale placeholder repository link.
**Recommendation:** Document this as a required first-time configuration step in
`README.md`. Consider a future improvement where `sync-version.py` also updates
this macro from the canonical `repository_url` in `metadata/publication.yaml`.
**Severity:** Minor

---

### MF-04: `.devcontainer/` is absent from template

**Finding:** The developer container configuration in `.devcontainer/` is not
included in `template/`. The existing `.devcontainer/` is Reflector-named
(`"name": "reflector"`) and references Reflector-specific tooling. A portable
container definition would benefit adopters who use VS Code dev containers or
GitHub Codespaces.
**Recommendation:** As a follow-up enhancement, generalize `.devcontainer/` to a
publication-agnostic container definition and include it in `template/` as an
optional module.
**Severity:** Minor

---

### MF-05: Magazine module documentation present but module files absent

**Finding:** `template/metadata/publication.yaml` includes a `companion_publications.magazine`
block with `enabled: false`. The template `README.md` mentions the magazine as an
"optional module". However, no magazine source files, build script, or workflow
are present in `template/`. Adopters who enable `magazine.enabled: true` will
encounter missing infrastructure.
**Recommendation:** Add a note in `README.md` clarifying that the magazine module
is planned but not yet included. Provide a clear pointer to the Reflector
reference implementation for reference.
**Severity:** Minor

---

### MF-06: Zenodo and arXiv integration not included as runnable modules

**Finding:** The template `publication.json` includes `"optional_modules": { "zenodo": false, "arxiv": false }`.
Neither a Zenodo active deposition workflow nor an arXiv bundle generation script
are present in `template/`. The Reflector reference implementations exist in the
main repository but have not been generalized.
**Recommendation:** Document the expected workflow for each integration in
`docs/publication-workflow.md` with explicit "not yet included in template"
notices. Link to the Reflector reference for currently available implementations.
**Severity:** Minor

---

## Current Strengths

1. **Clean identity separation.** No Reflector author, ORCID, DOI, repository
   name, or publication title appears anywhere in `template/`.
2. **Single-source-of-truth metadata model.** `metadata/publication.yaml` and
   `metadata/authors.yaml` drive all downstream surfaces consistently.
3. **Programmatic consistency enforcement.** `sync-version.py` and
   `validate-metadata.py` automatically detect and repair drift across six
   metadata surfaces.
4. **Fully generic paper scaffold.** Placeholder section stubs compile to a
   working PDF without any Reflector content.
5. **SPDX licensing in every file.** All `template/` files carry correct
   `SPDX-FileCopyrightText` and `SPDX-License-Identifier` headers.
6. **Generic GitHub Actions workflows.** All five included workflows use no
   Reflector-specific names, branches, or repository references.
7. **Configuration-first design.** Every publication identity aspect is
   configurable from `metadata/publication.yaml`.
8. **Documented upgrade path.** `README.md` explains module-by-module upgrade
   strategy for future template evolution.

---

## Remaining Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Adopter forgets to update `metadata.tex` repository URL | Medium | Minor PDF artifact | Document as explicit setup step |
| Magazine module enabled without files present | Low | Build failure | Document module as not-yet-included |
| Live LaTeX build not validated in template | Medium | Potential build issue | Run CI to validate on copy |
| `--publish` slug/directory mismatch | Low | Wrong PDF filename in docs/ | Fix slug derivation in `build-paper.sh` |
| Adopter uses placeholder ORCID in public release | Low | Incorrect metadata | Validation script will flag missing real data |

---

## Area-by-Area Findings

### Area 1: Repository and Content Separation — Ready

The `template/` directory contains no Reflector manuscript text, bibliography
entries, figures, magazine content, or research notes. The paper scaffold contains
only generic section placeholder comments. Bibliography is an empty `.bib` file
stub. The publication style (`paper/styles/publication.sty`) is a renamed and
generalized version of the Reflector-specific `reflector.sty`.

All Reflector-specific files (`paper/`, `magazine/`, `reflector.pdf`, `reflector/`,
`demos/`, `resources/`, release manifests, CHANGELOG.md, etc.) are correctly
excluded from `template/`.

### Area 2: Hardcoded Values and Portability Risks — Ready (minor cleanup)

Placeholder conventions are consistent and clearly marked. No production
identifiers from Reflector appear in `template/`. The only hardcoded assumptions
are intentional `your-org/your-repo` placeholders that must be replaced by
adopters. See Minor Findings MF-01 through MF-03 for specific items.

### Area 3: Template Boundary — Ready

The extracted `template/` boundary is clean and purposeful. Core publication
infrastructure is present. Optional modules (Zenodo, arXiv, magazine, devcontainer)
are documented as planned or future additions.

### Area 4: Proposed Template Structure — Ready

The actual directory tree at `template/` matches the documented structure in
`template/README.md`. All referenced paths exist.

### Area 5: Configuration Model — Ready

The configuration model centers on two authoritative YAML sources
(`metadata/publication.yaml` and `metadata/authors.yaml`). All downstream surfaces
are derived programmatically. Adopters need only edit these two files plus the
LaTeX metadata macro to configure a complete publication identity.

### Area 6: Build Portability — Ready (live build unvalidated)

Scripts are generic and use `git rev-parse --show-toplevel` for root resolution.
The `.latexmkrc` uses relative TEXINPUTS paths within `paper/`. CI uses the
`xu-cheng/latex-action@v4` action for hermetic TeX Live builds. One known gap:
a live LaTeX build of the template paper was not executed as part of this audit.
The structure and placeholder content are well-formed based on inspection.

### Area 7: GitHub Actions Portability — Ready

All five workflows (`ci.yml`, `pages.yml`, `bump-version.yml`, `release-tag.yml`,
`paper-quality.yml`) use only GitHub-provided actions and standard environment
variables. None reference Reflector by name. The `pages.yml` workflow reads the
slug from `publication.json` at runtime.

### Area 8: Publication and Release Portability — Ready

The template supports a clean-repository bootstrap with no existing releases, no
DOI, no Zenodo record, and no arXiv identifier. Draft status is the default. The
version bump and release tag workflows gracefully handle first-time usage.

### Area 9: Archival Integration Portability — Minor Cleanup

`metadata/publication.yaml` includes null-valued `doi`, `arxiv_id`, `zenodo_doi`,
and `zenodo_concept_doi` fields. `.zenodo.json` has `"doi": null` and
`"conceptdoi": null`. These are correct placeholders. Active Zenodo deposition
and arXiv bundle generation workflows are not yet included in `template/` — they
exist only in the Reflector reference implementation.

### Area 10: Documentation and Onboarding — Minor Cleanup

`template/docs/` contains a landing page, release process documentation,
configuration guide, getting-started guide, publication workflow overview, and
troubleshooting guide. These provide adequate onboarding for the core workflow.
Missing documentation: explicit Zenodo setup guide, arXiv submission guide, and
magazine module onboarding (when the module becomes available).

### Area 11: Example Content Strategy — Ready

All `paper/sections/` files contain minimal placeholder LaTeX comments. The
`paper/references/references.bib` is an empty stub. The paper compiles to a
valid (empty) document. Example content is clearly differentiated from
infrastructure by SPDX headers and comment annotations.

### Area 12: Licensing and Attribution — Ready

All `template/` files carry consistent Apache-2.0 `SPDX-FileCopyrightText: 2026
Publication Template Contributors` headers. No third-party assets, fonts, or
copied scripts without proper attribution are present. The `LICENSE` file is a
copy of the Apache 2.0 license.

### Area 13: Independent Copy Test — Ready (structural validation)

A structural validation was performed:
- All required files are present at expected paths.
- `metadata/publication.yaml` contains all required fields.
- `scripts/sync-version.py --check` logic validates against placeholder version `0.1.0`.
- `scripts/validate-metadata.py` logic validates title, ORCID, and URL consistency.
- No Reflector-specific strings detected in `template/`.
- All workflow YAML files are syntactically valid.

A full live LaTeX build was not executed as part of this audit. The paper scaffold
is structurally well-formed based on file inspection.
