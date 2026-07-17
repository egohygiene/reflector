# Template Extraction Plan

Generated: 2026-07-17
Issue: #235 — Audit publication template extraction readiness

---

## Status

**CONDITIONAL GO.** Template extraction has been completed into `template/`.
This plan documents the extraction phases that were performed, the current
state of the template, and the ordered follow-up tasks required to complete
the remaining minor gaps before the template is fully ready for production use.

---

## Current Template State

The `template/` directory at the repository root contains a functional,
portable publication platform. No Reflector-specific identity appears in
the template. Placeholder conventions are consistent. Core publication
infrastructure is present.

**Completed extraction phases:** Phase 1 through Phase 5 (see below).
**Remaining follow-up tasks:** Phase 6.

---

## Exact Template Directory Structure

```text
template/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   └── workflows/
│       ├── bump-version.yml          — semantic version bump workflow
│       ├── ci.yml                    — validate + build CI
│       ├── pages.yml                 — GitHub Pages deployment
│       ├── paper-quality.yml         — ChkTeX lint
│       └── release-tag.yml           — annotated release tag creation
├── audits/
│   └── README.md                     — audit directory scaffold
├── docs/
│   ├── configuration.md              — configuration reference guide
│   ├── getting-started.md            — first-time setup guide
│   ├── index.html                    — publication landing page
│   ├── publication-workflow.md       — workflow overview
│   ├── release-process.md            — release documentation
│   └── troubleshooting.md            — troubleshooting reference
├── metadata/
│   ├── authors.yaml                  — canonical author identity
│   └── publication.yaml              — canonical publication metadata
├── paper/
│   ├── config/
│   │   └── title.tex                 — canonical title macros
│   ├── figures/                      — figure directory
│   ├── macros/
│   │   └── metadata.tex              — paper metadata macros
│   ├── references/
│   │   └── references.bib            — empty bibliography stub
│   ├── sections/
│   │   ├── abstract.tex              — placeholder abstract
│   │   ├── appendix.tex              — placeholder appendix
│   │   ├── conclusion.tex            — placeholder conclusion
│   │   ├── discussion.tex            — placeholder discussion
│   │   ├── introduction.tex          — placeholder introduction
│   │   ├── limitations.tex           — placeholder limitations
│   │   ├── methodology.tex           — placeholder methodology
│   │   ├── related-work.tex          — placeholder related work
│   │   └── results.tex               — placeholder results
│   ├── styles/
│   │   └── publication.sty           — reusable publication style
│   └── paper.tex                     — LaTeX entry point
├── scripts/
│   ├── build-paper.sh                — paper build script
│   ├── format-latex.sh               — LaTeX formatter
│   ├── lint-paper.sh                 — ChkTeX runner
│   ├── print-latex-diagnostics.sh    — build diagnostics
│   ├── sync-version.py               — version synchronization
│   ├── validate-metadata.py          — metadata consistency validation
│   └── watch-paper.sh                — file watcher
├── specs/
│   ├── README.md                     — specs directory scaffold
│   ├── bug-report.md                 — bug report template
│   └── feature-request.md            — feature request template
├── .chktexrc                         — ChkTeX lint configuration
├── .editorconfig                     — editor configuration
├── .gitattributes                    — Git attributes
├── .gitignore                        — standard ignores
├── .latexindent.yml                  — LaTeX formatter configuration
├── .latexmkrc                        — latexmk build configuration
├── .zenodo.json                      — Zenodo passive integration
├── CITATION.cff                      — citation metadata
├── LICENSE                           — Apache-2.0 license
├── README.md                         — template onboarding documentation
├── Taskfile.yml                      — developer task runner
├── VERSION                           — canonical semantic version
├── codemeta.json                     — code metadata
├── publication.json                  — publication manifest
└── release-manifest.json             — release tracking manifest
```

---

## Files to Copy (When Adopting Template)

Copy the entire `template/` directory as the root of the new repository:

```bash
cp -R template/. /path/to/new-repository/
```

No filtering is needed. All files in `template/` are intended for inclusion.

---

## Files to Transform (Required Configuration)

After copying, the adopter must update these files with publication-specific values:

| File | What to Change |
|---|---|
| `metadata/publication.yaml` | `slug`, `title.*`, `abstract`, `keywords`, `version`, `date_released`, `repository_url`, `pages_url` |
| `metadata/authors.yaml` | Author `family-names`, `given-names`, `orcid`, `orcid_url` |
| `paper/config/title.tex` | `\papertitlemain`, `\papertitlesubtitle` |
| `paper/macros/metadata.tex` | `\paperauthor`, `\paperdate`, `\paperstatus`, `\paperrepository`, `\paperorcid` |
| `VERSION` | Starting version number (can remain `0.1.0`) |

After editing, run:
```bash
python3 scripts/sync-version.py
python3 scripts/validate-metadata.py
```

These two commands propagate changes to all downstream surfaces and confirm
consistency.

---

## Files to Exclude From Adoption

These `template/` files do not need modification but may need to be verified:

- `publication.json` — values are synchronized from metadata after running `sync-version.py`
- `release-manifest.json` — reset to generic stub, synchronized by sync-version.py
- `CITATION.cff` — synchronized by sync-version.py
- `.zenodo.json` — synchronized by sync-version.py
- `codemeta.json` — synchronized by sync-version.py

---

## Files to Create (New Publication)

The adopter will need to create:

| File | Purpose |
|---|---|
| `paper/references/references.bib` entries | Add bibliography entries as the paper is written |
| `paper/sections/*.tex` content | Replace placeholder stubs with actual content |
| `paper/figures/` content | Add actual figures and update manifest |
| `docs/{slug}.pdf` | Generated by CI or `task paper:build --publish` |

---

## References to Update

| Location | Reference | Update Required |
|---|---|---|
| `docs/index.html` meta OG tags | `your-org.github.io/your-repo` | Replace with actual Pages URL |
| `docs/index.html` JSON-LD schema | `your-org.github.io/your-repo` | Replace with actual Pages URL |
| `docs/index.html` preview image | `your-org.github.io/your-repo/preview.png` | Replace or remove until image exists |
| All `docs/*.md` placeholder references | `your-org`, `your-repo` | Replace with actual values |

---

## Validations to Run

Run these validations immediately after copying and configuring the template:

```bash
# Verify all version surfaces are synchronized
python3 scripts/sync-version.py --check

# Validate all metadata surfaces are consistent
python3 scripts/validate-metadata.py

# Lint the paper LaTeX source
bash scripts/lint-paper.sh paper

# Build the paper locally
bash scripts/build-paper.sh paper

# Verify the Taskfile works
task validate
task paper:build
```

Expected outcome: all commands exit 0 with no errors.

---

## Portability Test Procedure

To verify the template is self-contained and free of Reflector-specific content:

```bash
# 1. Create a fresh temporary directory
TMPDIR=$(mktemp -d)

# 2. Copy the template
cp -R template/. "${TMPDIR}/"

# 3. Verify no Reflector-specific strings
grep -r "Alan\|Szmyt\|egohygiene\|reflector[^/]" "${TMPDIR}/" --include="*.yaml" --include="*.yml" --include="*.json" --include="*.md" --include="*.tex" --include="*.sh" --include="*.py" 2>/dev/null | grep -v ".git"

# 4. Check placeholder conventions are consistent
grep -r "your-org\|your-repo\|example-publication\|0000-0000-0000-0000" "${TMPDIR}/" 2>/dev/null | grep -v ".git"

# 5. Run metadata validation (requires Python + pyyaml)
cd "${TMPDIR}"
pip install pyyaml
python3 scripts/sync-version.py --check
python3 scripts/validate-metadata.py

# 6. Check script syntax
bash -n scripts/build-paper.sh
bash -n scripts/lint-paper.sh
bash -n scripts/watch-paper.sh
bash -n scripts/format-latex.sh
bash -n scripts/print-latex-diagnostics.sh

# 7. Cleanup
cd /
rm -rf "${TMPDIR}"
```

Expected outcome:
- Step 3 produces no output (no Reflector-specific strings)
- Step 4 shows only intentional `your-org/your-repo` placeholders
- Step 5 exits 0 with "All version surfaces are synchronized" and "All metadata surfaces are consistent"
- Step 6 exits 0 for all scripts

---

## Cleanup Procedure

After creating the new publication repository from the template:

1. Replace all placeholder values with real publication identity.
2. Remove template-specific comments from `README.md` (the `> Origin note` callout).
3. Update `docs/index.html` static meta tags with actual URLs.
4. Run `python3 scripts/sync-version.py` to propagate all changes.
5. Run `python3 scripts/validate-metadata.py` to confirm consistency.
6. Enable GitHub Pages in repository settings (source: GitHub Actions).
7. Push to `main` to trigger initial CI, Pages deployment, and release tag.

---

## Ordered Follow-Up Phases

### Phase 6: Remaining Minor Fixes (follow-up from this audit)

These tasks address the minor findings documented in `template-extraction-readiness.md`:

#### Task 6.1 — Fix `--publish` slug derivation in `build-paper.sh`

**File:** `template/scripts/build-paper.sh`
**Change:** Update the `publish_paper` function to read the slug from
`publication.json` or `metadata/publication.yaml` instead of using
`basename "${paper_directory}"`.

```bash
# Current (fragile):
slug="$(basename "${paper_directory}")"

# Recommended (canonical):
slug="$(python3 -c "
import json
from pathlib import Path
manifest = json.loads(Path('${REPOSITORY_ROOT}/publication.json').read_text())
print(manifest['slug'])
")"
```

**Acceptance:** `--publish` produces a PDF named `{slug}.pdf` regardless of
the paper directory name.

---

#### Task 6.2 — Document `metadata.tex` as required first-time configuration step

**File:** `template/README.md` and `template/docs/getting-started.md`
**Change:** Add an explicit bullet in the Quick Start section noting that
`paper/macros/metadata.tex` must be updated with the actual `\paperrepository`
URL and author details.

**Acceptance:** A developer following Quick Start knows to update
`paper/macros/metadata.tex` before building.

---

#### Task 6.3 — Add comment to `docs/index.html` for static meta tags

**File:** `template/docs/index.html`
**Change:** Add HTML comments above the Open Graph and JSON-LD blocks noting
they are static placeholders that must be updated when adopting the template.

**Acceptance:** Comments are present and actionable.

---

#### Task 6.4 — Update `README.md` to clarify magazine module status

**File:** `template/README.md`
**Change:** Under "Optional modules", add a note that the magazine module is
planned but not yet included in the template. Point to the Reflector reference
implementation for an available example.

**Acceptance:** Adopters are not surprised when enabling `magazine.enabled: true`
without further infrastructure.

---

#### Task 6.5 — Update `README.md` to clarify Zenodo and arXiv module status

**File:** `template/README.md`
**Change:** Under "Optional modules", add notes that active Zenodo deposition
and arXiv bundle generation workflows are not yet included in the template.

**Acceptance:** Adopters understand which optional modules are fully supported
versus planned.

---

### Phase 7: Optional Enhancements (future iterations)

These are improvements that would increase template value but are not required
for current adoption:

#### Task 7.1 — Add generic `.devcontainer/` to template

Create a publication-agnostic dev container configuration:
- Name the container generically (e.g., `publication`)
- Include TeX Live, Python, Task, and ChkTeX in the container image
- Generalize post-create scripts
- Include the container definition in `template/.devcontainer/`

#### Task 7.2 — Add Zenodo active deposition workflow

Generalize the Zenodo deposition workflow from the Reflector reference
implementation and add it to `template/.github/workflows/zenodo.yml` as an
optional module activated by `optional_modules.zenodo: true`.

#### Task 7.3 — Add arXiv bundle generation script

Generalize the arXiv packaging validation script and add it to
`template/scripts/` as an optional tool.

#### Task 7.4 — Add release packaging script

Generalize `scripts/stage-publication-release.py` from the Reflector reference
implementation and add it to `template/scripts/` as part of a GitHub Release
packaging workflow.

#### Task 7.5 — Add pre-commit configuration

Provide a generic `template/.pre-commit-config.yaml` with LaTeX lint and Python
format hooks as an optional quality gate.

#### Task 7.6 — Add REUSE compliance infrastructure

Add `LICENSES/` directory and `REUSE.toml` as an optional compliance module.

---

## Definition of Done

The template extraction is complete when:

- [x] `template/` exists and contains all required infrastructure files
- [x] No Reflector-specific identity appears in `template/`
- [x] `python3 scripts/sync-version.py --check` passes on a fresh copy
- [x] `python3 scripts/validate-metadata.py` passes on a fresh copy
- [x] All workflow YAML files parse without errors
- [x] All shell scripts pass `bash -n` syntax check
- [x] Paper scaffold is structurally valid
- [x] Placeholder conventions are consistent throughout
- [ ] `--publish` flag derives slug from canonical metadata (Task 6.1)
- [ ] `getting-started.md` documents `metadata.tex` update (Task 6.2)
- [ ] `docs/index.html` static meta tag comments added (Task 6.3)
- [ ] Magazine module status clarified in README (Task 6.4)
- [ ] Zenodo/arXiv module status clarified in README (Task 6.5)

---

## Expected Validation Commands After Follow-Up

After completing Phase 6, run:

```bash
# From template/ (or a fresh copy)
python3 scripts/sync-version.py --check
python3 scripts/validate-metadata.py
bash -n scripts/build-paper.sh
bash -n scripts/lint-paper.sh
bash -n scripts/watch-paper.sh
bash -n scripts/format-latex.sh
bash -n scripts/print-latex-diagnostics.sh
task validate
```

All commands should exit 0 with no errors or warnings.

---

## Extraction Handoff Summary

| Item | Status |
|---|---|
| Template extraction | Complete |
| Reflector identity removed | ✅ Verified |
| Placeholder conventions consistent | ✅ Verified |
| Metadata pipeline functional | ✅ Verified |
| CI workflows generic | ✅ Verified |
| Paper scaffold builds | ✅ Structurally valid (live build not yet validated) |
| Minor finding MF-01 (`--publish` slug) | ⚠️ Task 6.1 required |
| Minor finding MF-02 (`index.html` meta tags) | ⚠️ Task 6.3 recommended |
| Minor finding MF-03 (`metadata.tex` repository URL) | ⚠️ Task 6.2 documentation |
| Minor finding MF-04 (devcontainer absent) | ℹ️ Task 7.1 future enhancement |
| Minor finding MF-05 (magazine module absent) | ⚠️ Task 6.4 documentation |
| Minor finding MF-06 (Zenodo/arXiv absent) | ⚠️ Task 6.5 documentation |
