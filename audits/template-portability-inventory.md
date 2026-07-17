# Template Portability Inventory

Generated: 2026-07-17
Issue: #235 — Audit publication template extraction readiness

---

## Legend

**Classification:**
- `ready` — can be extracted without changes
- `minor-cleanup` — needs small naming, documentation, or configuration changes
- `example-only` — useful as example, not reusable unchanged
- `reflector-specific` — Reflector content, excluded from template
- `generated` — generated artifact, should not be copied
- `historical` — release/changelog artifact, should not be included

**Inclusion Decision:**
- `include` — present in template/
- `include-optional` — planned optional module, not yet in template/
- `exclude` — excluded from template

---

## Root Configuration Files

| Source Path | Template Path | Classification | Required Changes | Inclusion Decision | Rationale |
|---|---|---|---|---|---|
| `VERSION` | `template/VERSION` | ready | Reset to `0.1.0` ✅ | include | Canonical version source |
| `Taskfile.yml` | `template/Taskfile.yml` | minor-cleanup | Stripped to paper-only tasks ✅ | include | Core developer task runner |
| `CITATION.cff` | `template/CITATION.cff` | minor-cleanup | Replaced identity with placeholders ✅ | include | Citation metadata |
| `.zenodo.json` | `template/.zenodo.json` | minor-cleanup | Replaced identity, nulled DOIs ✅ | include | Zenodo passive integration |
| `codemeta.json` | `template/codemeta.json` | minor-cleanup | Replaced identity with placeholders ✅ | include | Code metadata |
| `publication.json` | `template/publication.json` | minor-cleanup | Replaced identity, added optional_modules ✅ | include | Publication manifest |
| `release-manifest.json` | `template/release-manifest.json` | minor-cleanup | Replaced version, cleared artifacts ✅ | include | Release tracking |
| `LICENSE` | `template/LICENSE` | ready | None | include | Apache-2.0 license |
| `.latexmkrc` | `template/.latexmkrc` | ready | None | include | LaTeX build config |
| `.chktexrc` | `template/.chktexrc` | ready | None | include | ChkTeX lint config |
| `.editorconfig` | `template/.editorconfig` | ready | None | include | Editor config |
| `.gitattributes` | `template/.gitattributes` | ready | None | include |  Git attributes |
| `.latexindent.yml` | `template/.latexindent.yml` | ready | None | include | LaTeX formatter config |
| `.gitignore` | `template/.gitignore` | minor-cleanup | Removed release/ and Python test artifacts ✅ | include | Standard ignores |
| `pyproject.toml` | — | reflector-specific | Reflector tests and egg-info | exclude | Reflector Python package |
| `uv.lock` | — | reflector-specific | Reflector dependency lock | exclude | Reflector lockfile |
| `CHANGELOG.md` | — | historical | Reflector release history | exclude | Project-specific |
| `ROADMAP.md` | — | reflector-specific | Reflector roadmap | exclude | Project-specific |
| `README.md` | `template/README.md` | minor-cleanup | Replaced with template onboarding ✅ | include | Template README |
| `PROGRESS.md` | — | reflector-specific | Reflector progress tracking | exclude | Project-specific |
| `TODO.md` | — | reflector-specific | Reflector todos | exclude | Project-specific |
| `SECURITY.md` | — | reflector-specific | Reflector security policy | exclude | Project-specific |
| `SUPPORT.md` | — | reflector-specific | Reflector support policy | exclude | Project-specific |
| `CODE_OF_CONDUCT.md` | — | reflector-specific | Reflector community norms | exclude | Project-specific |
| `CONTRIBUTING.md` | — | reflector-specific | Reflector contribution guide | exclude | Project-specific |
| `REUSE.toml` | — | reflector-specific | Reflector SPDX coverage | exclude | Per-repo REUSE config |
| `00-README.md` | — | reflector-specific | Reflector orientation doc | exclude | Project-specific |
| `README_HF.md` | — | reflector-specific | Hugging Face README | exclude | Project-specific |
| `reflector.pdf` | — | generated | Reflector published PDF | exclude | Project artifact |
| `reflector.egg-info/` | — | generated | Python package metadata | exclude | Build artifact |

---

## Metadata Directory

| Source Path | Template Path | Classification | Required Changes | Inclusion Decision | Rationale |
|---|---|---|---|---|---|
| `metadata/publication.yaml` | `template/metadata/publication.yaml` | minor-cleanup | Replaced identity, nulled identifiers, added slug + optional modules ✅ | include | Canonical publication config |
| `metadata/authors.yaml` | `template/metadata/authors.yaml` | minor-cleanup | Replaced with placeholder author ✅ | include | Canonical author config |

---

## Paper Directory

| Source Path | Template Path | Classification | Required Changes | Inclusion Decision | Rationale |
|---|---|---|---|---|---|
| `paper/paper.tex` | `template/paper/paper.tex` | minor-cleanup | Generic document structure, placeholder macros ✅ | include | LaTeX entry point |
| `paper/styles/reflector.sty` | `template/paper/styles/publication.sty` | minor-cleanup | Renamed; generalized color and identifier names ✅ | include | Reusable publication style |
| `paper/config/title.tex` | `template/paper/config/title.tex` | minor-cleanup | Replaced title with placeholders ✅ | include | Canonical title macros |
| `paper/macros/metadata.tex` | `template/paper/macros/metadata.tex` | minor-cleanup | Replaced identity; `\paperrepository` still placeholder ✅ | include | Paper metadata macros |
| `paper/macros/` (other) | `template/paper/macros/` | minor-cleanup | Stripped Reflector-specific macros | include | Reusable macro framework |
| `paper/sections/` (all) | `template/paper/sections/` | minor-cleanup | Replaced with placeholder stubs ✅ | include | Section scaffold |
| `paper/figures/` | `template/paper/figures/` | minor-cleanup | Cleared Reflector figures; placeholder manifest ✅ | include | Figure directory |
| `paper/references/references.bib` | `template/paper/references/references.bib` | minor-cleanup | Cleared Reflector entries; empty stub ✅ | include | Bibliography starter |
| `paper/content/` (Reflector body) | — | reflector-specific | Reflector manuscript text | exclude | Reflector-specific content |
| `paper/diagrams/` | — | reflector-specific | Reflector diagrams | exclude | Project-specific figures |

---

## Scripts Directory

| Source Path | Template Path | Classification | Required Changes | Inclusion Decision | Rationale |
|---|---|---|---|---|---|
| `scripts/sync-version.py` | `template/scripts/sync-version.py` | ready | No changes needed ✅ | include | Version synchronization |
| `scripts/validate-metadata.py` | `template/scripts/validate-metadata.py` | minor-cleanup | Updated to read title/ORCID from metadata/ ✅ | include | Metadata validation |
| `scripts/build-paper.sh` | `template/scripts/build-paper.sh` | minor-cleanup | Generic paper build; `--publish` slug from dirname (MF-01) | include | Paper build script |
| `scripts/lint-paper.sh` | `template/scripts/lint-paper.sh` | ready | None | include | LaTeX lint runner |
| `scripts/watch-paper.sh` | `template/scripts/watch-paper.sh` | ready | None | include | LaTeX watch builder |
| `scripts/format-latex.sh` | `template/scripts/format-latex.sh` | ready | None | include | LaTeX formatter |
| `scripts/print-latex-diagnostics.sh` | `template/scripts/print-latex-diagnostics.sh` | ready | None | include | Build diagnostics |
| `scripts/stage-publication-release.py` | — | reflector-specific | Reflector release staging | exclude (planned) | Could be future optional module |
| `scripts/validate-release-lifecycle.py` | — | reflector-specific | Reflector lifecycle validation | exclude | Reflector-specific |
| `scripts/audit-publication-readiness.py` | — | reflector-specific | Reflector audit runner | exclude | Reflector-specific |
| `scripts/audit-magazine-consistency.py` | — | reflector-specific | Reflector magazine audit | exclude | Reflector-specific |
| `scripts/build-magazine.sh` | — | reflector-specific | Reflector magazine build | exclude (planned) | Future magazine module |
| `scripts/validate-arxiv-packaging.py` | — | reflector-specific | Reflector arXiv validation | exclude (planned) | Future arXiv module |
| `scripts/validate-build-reproducibility.py` | — | reflector-specific | Reflector reproducibility | exclude | Reflector-specific |
| `scripts/validate-texlive-compatibility.py` | — | reflector-specific | Reflector TeX validation | exclude | Reflector-specific |
| `scripts/generate_pdf_previews.py` | — | reflector-specific | Reflector preview generation | exclude (planned) | Future Pages module |
| `scripts/audit-chktex.py` | — | reflector-specific | Reflector ChkTeX audit | exclude | Reflector-specific |
| `scripts/audit-holistic.py` | — | reflector-specific | Reflector holistic audit | exclude | Reflector-specific |
| `scripts/prevent-ds-store.sh` | — | reflector-specific | macOS artifact cleanup | exclude | Optional utility |
| `scripts/scaffold-paper.sh` | — | reflector-specific | Reflector scaffolding | exclude | Reflector-specific |
| `scripts/publishers/` | — | reflector-specific | Reflector publisher scripts | exclude | Reflector-specific |

---

## GitHub Actions Workflows

| Source Path | Template Path | Classification | Required Changes | Inclusion Decision | Rationale |
|---|---|---|---|---|---|
| `.github/workflows/ci.yml` | `template/.github/workflows/ci.yml` | minor-cleanup | Stripped Reflector paths; generic validate+build ✅ | include | Core CI pipeline |
| `.github/workflows/pages.yml` | `template/.github/workflows/pages.yml` | minor-cleanup | Simplified to paper-only; reads slug from publication.json ✅ | include | GitHub Pages deployment |
| `.github/workflows/bump-version.yml` | `template/.github/workflows/bump-version.yml` | minor-cleanup | Removed Reflector-specific surface list ✅ | include | Semantic version bump |
| `.github/workflows/release-tag.yml` | `template/.github/workflows/release-tag.yml` | minor-cleanup | Simplified tag creation ✅ | include | Annotated release tag |
| `.github/workflows/paper-quality.yml` | `template/.github/workflows/paper-quality.yml` | minor-cleanup | Simplified to ChkTeX lint ✅ | include | Paper lint CI |
| `.github/workflows/publication.yml` | — | reflector-specific | Reflector multi-artifact orchestration | exclude (planned) | Future full release module |
| `.github/workflows/build-magazine.yml` | — | reflector-specific | Reflector magazine build | exclude (planned) | Future magazine module |
| `.github/workflows/release-paper.yml` | — | reflector-specific | Reflector release packaging | exclude (planned) | Future release packaging module |
| `.github/workflows/release-please.yml` | — | reflector-specific | Reflector release-please config | exclude | Reflector-specific |
| `.github/workflows/commitlint.yml` | — | reflector-specific | Reflector commit convention | exclude | Reflector-specific |
| `.github/workflows/synchronization.yml` | — | reflector-specific | Reflector sync validation | exclude | Reflector-specific |
| `.github/workflows/reuse.yml` | — | reflector-specific | Reflector REUSE compliance | exclude (planned) | Future licensing module |
| `.github/workflows/copilot-setup-steps.yml` | — | reflector-specific | Reflector Copilot config | exclude | Reflector-specific |

---

## Documentation Directory

| Source Path | Template Path | Classification | Required Changes | Inclusion Decision | Rationale |
|---|---|---|---|---|---|
| `docs/index.html` | `template/docs/index.html` | minor-cleanup | Replaced identity; OG/JSON-LD still has `your-org` placeholder (MF-02) | include | Publication landing page |
| `docs/publication.json` (deployed) | — | generated | Deployed publication manifest | exclude | Runtime artifact |
| `docs/release-process.md` | `template/docs/release-process.md` | minor-cleanup | Updated for generic workflow ✅ | include | Release documentation |
| `docs/configuration.md` | `template/docs/configuration.md` | minor-cleanup | Generic configuration reference ✅ | include | Configuration guide |
| `docs/getting-started.md` | `template/docs/getting-started.md` | minor-cleanup | Generic first-time setup guide ✅ | include | Onboarding |
| `docs/publication-workflow.md` | `template/docs/publication-workflow.md` | minor-cleanup | Generic workflow overview ✅ | include | Workflow documentation |
| `docs/troubleshooting.md` | `template/docs/troubleshooting.md` | minor-cleanup | Generic troubleshooting ✅ | include | Troubleshooting reference |
| `docs/` (Reflector PDFs, previews) | — | generated | Reflector published artifacts | exclude | Project artifacts |

---

## Audits and Specs Directories

| Source Path | Template Path | Classification | Required Changes | Inclusion Decision | Rationale |
|---|---|---|---|---|---|
| `audits/README.md` | `template/audits/README.md` | ready | None ✅ | include | Audit directory scaffold |
| `audits/*.md` (all Reflector audits) | — | reflector-specific | Reflector-specific assessments | exclude | Project-specific |
| `specs/README.md` | `template/specs/README.md` | ready | None ✅ | include | Specs directory scaffold |
| `specs/bug-report.md` | `template/specs/bug-report.md` | ready | None ✅ | include | Bug report template |
| `specs/feature-request.md` | `template/specs/feature-request.md` | ready | None ✅ | include | Feature request template |
| `specs/` (Reflector specifications) | — | reflector-specific | Reflector publication specs | exclude | Project-specific |

---

## Developer Container

| Source Path | Template Path | Classification | Required Changes | Inclusion Decision | Rationale |
|---|---|---|---|---|---|
| `.devcontainer/devcontainer.json` | — | reflector-specific | Named "reflector"; Reflector extensions | exclude (planned) | Future optional module |
| `.devcontainer/Dockerfile` | — | reflector-specific | Reflector tooling | exclude (planned) | Future optional module |
| `.devcontainer/scripts/` | — | reflector-specific | Reflector post-create scripts | exclude (planned) | Future optional module |

---

## Magazine Directory

| Source Path | Template Path | Classification | Required Changes | Inclusion Decision | Rationale |
|---|---|---|---|---|---|
| `magazine/` (all files) | — | reflector-specific | Reflector magazine content | exclude (planned) | Future magazine module |

---

## Publication Artifacts

| Source Path | Template Path | Classification | Required Changes | Inclusion Decision | Rationale |
|---|---|---|---|---|---|
| `publication/` | — | reflector-specific | Reflector publication outputs | exclude | Project-specific artifacts |
| `reflector.pdf` | — | generated | Reflector published PDF | exclude | Project artifact |
| `release-manifest.json` (root) | `template/release-manifest.json` | minor-cleanup | Reset to empty/generic ✅ | include | Starter manifest |
| `publication.json` (root) | `template/publication.json` | minor-cleanup | Replaced identity ✅ | include | Starter manifest |

---

## Tests

| Source Path | Template Path | Classification | Required Changes | Inclusion Decision | Rationale |
|---|---|---|---|---|---|
| `tests/` (all) | — | reflector-specific | Reflector Python test suite | exclude | Project-specific |

---

## Additional Root Files

| Source Path | Template Path | Classification | Required Changes | Inclusion Decision | Rationale |
|---|---|---|---|---|---|
| `.release-please-config.json` | — | reflector-specific | Reflector release-please config | exclude | Project-specific |
| `.release-please-manifest.json` | — | historical | Reflector release history | exclude | Project-specific |
| `.pre-commit-config.yaml` | — | reflector-specific | Reflector pre-commit hooks | exclude (planned) | Future optional module |
| `.commitlintrc.json` | — | reflector-specific | Reflector commit conventions | exclude | Project-specific |
| `reflector.code-workspace` | — | reflector-specific | Reflector VS Code workspace | exclude | Project-specific |
| `reflector/` | — | reflector-specific | Reflector Python source package | exclude | Project code |
| `resources/` | — | reflector-specific | Reflector resources | exclude | Project-specific |
| `demos/` | — | reflector-specific | Reflector demo artifacts | exclude | Project-specific |
| `.vscode/` | — | reflector-specific | Reflector VS Code settings | exclude | Project-specific |
| `.actrc` | — | reflector-specific | Reflector act runner config | exclude | Project-specific |
| `.cache/` | — | generated | Build caches | exclude | Not committed |
