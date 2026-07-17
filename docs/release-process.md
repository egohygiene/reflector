<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Release Process

This document describes the end-to-end publication release lifecycle for reflector.

---

## Overview

The publication release lifecycle is orchestrated by a single canonical workflow:

```
.github/workflows/publication.yml
```

This workflow encodes the following deterministic pipeline:

```
VERSION
  ↓
validate
  ↓
audit
  ↓
build
  ↓
package
  ↓
github release
  ↓
archive-ready
```

---

## VERSION — Canonical Source of Truth

[`VERSION`](../VERSION) is the single source of truth for all release metadata.

All release surfaces derive from `VERSION` and are validated automatically:

| Surface | File |
|---|---|
| Publication metadata | `metadata/publication.yaml` |
| Publication manifest | `publication.json` |
| Release manifest | `release-manifest.json` |
| Release-Please manifest | `.release-please-manifest.json` |
| Citation metadata | `CITATION.cff` |
| Zenodo metadata | `.zenodo.json` |
| CodeMeta metadata | `codemeta.json` |

**Drift between `VERSION` and any surface is a validation failure.**

The `scripts/validate-release-lifecycle.py` script enforces synchronization across all surfaces.

---

## Workflow

### Trigger

The publication workflow triggers automatically when:

- `VERSION` changes on `main` (push event)
- Any publication source changes on `main` (paper, magazine, metadata, scripts)
- A `workflow_dispatch` event is issued manually

### Stages

#### Stage 1 — Validate

Runs all synchronization and publication integrity checks:

| Job | Script | Output |
|---|---|---|
| Metadata synchronization | `scripts/validate-metadata.py` | pass/fail |
| Release lifecycle contracts | `scripts/validate-release-lifecycle.py` | pass/fail |
| arXiv packaging readiness | `scripts/validate-arxiv-packaging.py` | `audits/arxiv-validation.md` |
| Build reproducibility | `scripts/validate-build-reproducibility.py` | `audits/build-reproducibility.md` |
| Publication readiness | `scripts/audit-publication-readiness.py` | `audits/publication-readiness.md` |
| REUSE compliance | `fsfe/reuse-action` | pass/fail |

Validation failures block all downstream stages.

#### Stage 2 — Audit (parallel with Stage 1)

Runs static analysis and generates audit reports:

| Job | Tool | Output |
|---|---|---|
| ChkTeX lint | `chktex` + `scripts/audit-chktex.py` | `audits/chktex-audit.md` |

Critical ChkTeX warnings (W11, W17, W19) block downstream stages.

#### Stage 3 — Build (depends on Stage 1)

Builds all publication artifacts in parallel:

| Job | Action | Output |
|---|---|---|
| Build paper | `xu-cheng/latex-action@v4` | `paper/.cache/out/paper.pdf` → `dist/reflector.pdf` |
| Build magazine (digital) | `xu-cheng/latex-action@v4` | `magazine/.cache/out/magazine.pdf` → `reflector-magazine.pdf` |
| Build magazine (print) | `xu-cheng/latex-action@v4` | `magazine/.cache/out/magazine-print.pdf` → `reflector-magazine-print.pdf` |

#### Stage 4 — Package (depends on Stages 2 and 3)

Aggregates all artifacts, generates release bundles, and prepares the full release payload:

```
release/reflector-vX.Y.Z/
├── reflector.pdf                       # canonical paper PDF
├── reflector-magazine.pdf              # digital magazine PDF
├── reflector-magazine-print.pdf        # print magazine PDF
├── reflector-arxiv-vX.Y.Z.zip          # arXiv submission bundle (ZIP)
├── reflector-arxiv-vX.Y.Z.tar.gz       # arXiv submission bundle (TAR.GZ)
├── source.zip                          # full source archive
├── checksums.txt                       # SHA-256 checksums for all assets
├── release-manifest.json               # generated staged release manifest
├── publication.json                    # publication metadata
├── publication-readiness.md            # publication readiness report
├── chktex-audit.md                     # ChkTeX audit report
├── zenodo-readiness.md                 # Zenodo readiness report
├── hero.png                            # hero image
└── release-notes.md                    # changelog-derived release notes
```

**arXiv Bundle Contents:**

```
arxiv/
├── paper.tex
├── references.bib
├── .latexmkrc
├── sections/
├── figures/
├── diagrams/
├── assets/
├── references/
├── styles/
├── macros/
├── config/
└── 00README.json
```

The arXiv bundle is reproducible and deterministic:
- `tar` uses `--sort=name` and epoch `--mtime`
- `zip` uses `-X` to strip extended attributes

#### Stage 5 — Release (depends on Stage 4)

Creates the annotated release tag (if absent) and publishes the GitHub Release with all canonical artifacts attached.

**Release assets:**

| Asset | Description |
|---|---|
| `reflector.pdf` | Canonical paper PDF |
| `reflector-magazine.pdf` | Digital magazine PDF |
| `reflector-magazine-print.pdf` | Print magazine PDF |
| `source.zip` | Full source archive |
| `checksums.txt` | SHA-256 checksums |
| `release-manifest.json` | Generated staged release manifest |
| `publication-readiness.md` | Publication readiness audit |
| `chktex-audit.md` | ChkTeX audit report |
| `zenodo-readiness.md` | Zenodo readiness report |

---

## Releasing a New Version

To trigger a complete publication release:

1. **Update `VERSION`:**

   ```
   0.1.0  →  0.1.1
   ```

2. **Propagate the version to all downstream metadata surfaces:**

   ```bash
   python scripts/sync-version.py
   ```

   This command reads `VERSION` and automatically updates all downstream files:

   | File | Field updated |
   |---|---|
   | `metadata/publication.yaml` | `version` |
   | `CITATION.cff` | `version` |
   | `.zenodo.json` | `version` |
   | `codemeta.json` | `version` |
   | `publication.json` | `version`, `release_tag` |
   | `release-manifest.json` | `current_version` |
   | `.release-please-manifest.json` | root package version |

   Run `python scripts/sync-version.py --check` to verify synchronization
   without making any changes. Drift will be reported as non-zero exit.

   Alternatively, use the Taskfile:

   ```bash
   task sync:version        # apply sync
   task sync:version:check  # verify sync (dry run)
   ```

3. **Add changelog entry:**

   Add a section to `CHANGELOG.md`:

   ```markdown
   ## [0.1.1] — YYYY-MM-DD

   ### Changed
   - Description of changes.
   ```

4. **Push to `main`.**

The publication workflow will:
- validate all surfaces are synchronized
- build all artifacts
- generate audit reports and checksums
- create the release tag `v0.1.1`
- publish the GitHub Release with all assets

---

## Manual Dispatch

The publication workflow can be triggered manually via `workflow_dispatch`:

| Input | Description | Default |
|---|---|---|
| `paper` | Paper source directory | `paper` |
| `dry_run` | Skip GitHub Release creation | `false` |
| `fail_on_warnings` | Fail on any ChkTeX warning | `false` |

Use `dry_run: true` to test the full pipeline without publishing a release.

For the canonical staging layout, checksum contract, and manifest generation rules, see [`docs/publication-infrastructure.md`](publication-infrastructure.md).

---

## Manual Semantic-Version Bump

The `.github/workflows/bump-version.yml` workflow provides a safe, maintainer-controlled path for advancing the canonical version.

### How to use

1. Open **GitHub Actions → Bump Version** in the repository.
2. Click **Run workflow**.
3. Select the bump type: `patch`, `minor`, or `major`.
4. Optionally enable **Dry run** to preview the next version without committing.
5. Click **Run workflow**.

### What the workflow does

```
Select bump type (major / minor / patch)
    ↓
Validate current branch is default branch
    ↓
Validate bump type and current VERSION
    ↓
Compute next version (dry run exits here)
    ↓
Confirm target tag does not already exist
    ↓
Write new version to VERSION
    ↓
python scripts/sync-version.py
    ↓
python scripts/sync-version.py --check
python scripts/validate-metadata.py
python scripts/validate-release-lifecycle.py
    ↓
Commit all synchronized surfaces
    ↓
Push commit to default branch
    ↓
release-tag.yml creates the annotated tag
    ↓
publication.yml builds and publishes release artifacts
```

### Design decision — single tag ownership

The bump workflow **only** advances the VERSION and synchronized surfaces. It does not create the release tag directly. Tag creation remains owned by `release-tag.yml`, which triggers automatically when VERSION changes on `main`. This preserves one unambiguous owner for tag creation and prevents duplicate or racing tag events.

### Safeguards

| Safeguard | Behavior |
|---|---|
| Default-branch check | Fails if the workflow is triggered on any branch other than `main` |
| Bump type validation | Fails on any input other than `major`, `minor`, `patch` |
| Semver format check | Fails if the current VERSION is not `MAJOR.MINOR.PATCH` |
| Duplicate tag check | Fails if the target tag already exists |
| Required files check | Fails if any canonical metadata surface is missing |
| Validation gate | Fails before committing if `validate-metadata.py` or `validate-release-lifecycle.py` report drift |
| Concurrency group | Prevents two simultaneous bump workflows from running |
| Dry run mode | Preview the version bump without modifying any files |

### Version surfaces updated by the workflow

The workflow calls `python scripts/sync-version.py` which updates all downstream surfaces:

| File | Field |
|---|---|
| `VERSION` | canonical version (written first) |
| `metadata/publication.yaml` | `version` |
| `CITATION.cff` | `version` |
| `.zenodo.json` | `version` |
| `codemeta.json` | `version` |
| `publication.json` | `version`, `release_tag` |
| `release-manifest.json` | `current_version` |
| `.release-please-manifest.json` | `"."` (root package) |

---

## arXiv Workflow

When a GitHub Release is published:

1. Download `reflector-arxiv-vX.Y.Z.tar.gz` or `reflector-arxiv-vX.Y.Z.zip` from the release.
2. Validate the arXiv bundle locally using `python scripts/validate-arxiv-packaging.py`.
3. Upload to [arxiv.org](https://arxiv.org) via the submission portal.
4. Record the arXiv identifier (`arxiv_id`) in `metadata/publication.yaml`.
5. Update `CITATION.cff` and `.zenodo.json` with the arXiv ID.
6. Tag a metadata-update release.

---

## Zenodo Deposition Handoff

The publication workflow automates validation, build, packaging, and GitHub Release publication. Zenodo deposition and DOI publication remain human-gated.

### Automation boundary

| Step category | Ownership | Notes |
|---|---|---|
| Automated | GitHub Actions (`.github/workflows/publication.yml`) | Produces release artifacts and `zenodo-readiness.md`. |
| Manual | Maintainer/releaser | Performs deposition drafting, upload checks, metadata review, and DOI publication actions. |
| Human approval gate | Maintainer/releaser | Final Zenodo publish action must not occur until prior checks pass. |

### Sequential Zenodo deposition checklist

1. **Preconditions (automated outputs required):** Confirm publication workflow validation completed successfully (`scripts/validate-metadata.py`, `scripts/validate-release-lifecycle.py`) and that no release-blocking checks are failing.
2. **Verify target GitHub Release exists and is complete (manual):** Open the intended tag release and confirm required assets are present (`reflector.pdf`, `reflector-magazine.pdf`, `reflector-magazine-print.pdf`, `checksums.txt`, `release-manifest.json`, `publication-readiness.md`, `chktex-audit.md`, `zenodo-readiness.md`).
3. **Select Zenodo environment (manual):** Use [Zenodo Sandbox](https://sandbox.zenodo.org) for process testing and [Zenodo production](https://zenodo.org) for real publication.
4. **Sandbox test first (manual, recommended):** Rehearse deposition steps in sandbox whenever process logic or metadata workflows change.
5. **Create or update the deposition draft (manual):** Open an existing draft for the target release if present; otherwise create one deposition draft only.
6. **Upload and verify artifacts (manual):** Upload canonical release artifacts and verify filenames/checksums against `checksums.txt`.
7. **Review deposition metadata (manual):** Confirm authorship, version, license, description, repository relation, and related identifiers align with `metadata/publication.yaml`, `CITATION.cff`, `.zenodo.json`, `codemeta.json`, and `publication.json`.
8. **Final publication gate (human approval):** Publish the Zenodo deposition only after all prior checks succeed and metadata is verified.
9. **DOI confirmation (manual):** Confirm Zenodo has minted/published the DOI and that the DOI resolves.
10. **Synchronize DOI surfaces (manual + automated validation):** Update DOI-bearing metadata (`metadata/publication.yaml`, `CITATION.cff`, `.zenodo.json`, `codemeta.json`, and any DOI fields in release metadata), then run metadata synchronization validation.
11. **Run post-deposition validation (manual command execution):** Run `python scripts/validate-metadata.py` and `python scripts/validate-release-lifecycle.py` before any follow-up release metadata publication step.
12. **Record the completed handoff (manual governance):** Record deposition completion and DOI confirmation in the appropriate release notes and/or committed audit trail under `audits/`.

**Do not treat DOI registration as complete until Zenodo confirms publication.**

### Failure and recovery guidance (pause-and-verify)

- **GitHub Release does not exist:** Stop. Do not start a deposition. Re-run/fix release workflow and verify release publication first.
- **Expected release artifacts are missing:** Pause deposition updates. Regenerate release artifacts via the publication workflow; avoid partial uploads that create drift.
- **Zenodo draft metadata is incorrect:** Edit the draft metadata and re-verify against canonical metadata surfaces before publishing. Do not publish with known drift.
- **DOI reserved but deposition unpublished:** Treat as incomplete handoff. Keep draft unpublished until metadata and artifact checks are complete; then publish once.
- **Metadata synchronization fails after DOI assignment:** Pause any follow-up release actions, fix metadata drift, re-run validators, and only proceed after passing checks.
- **Deposition appears to duplicate an existing release:** Stop and reconcile against existing Zenodo records; update the existing draft/record when applicable instead of publishing duplicates.
- **Release workflow is re-run after Zenodo publication:** Re-verify release assets and metadata; if artifacts changed, update the existing Zenodo record/version per Zenodo policy rather than creating a conflicting duplicate deposition.

---

## DOI Canonicalization

reflector now tracks two Zenodo DOI forms:

- **Version DOI (canonical for citation):** `10.5281/zenodo.20477044`
- **Concept DOI (latest-family discovery):** `10.5281/zenodo.20477045`

Canonical usage policy:

1. Use the **version DOI** in citation metadata (`CITATION.cff`, `codemeta.json`, release manifest DOI fields) to preserve reproducibility.
2. Track the **concept DOI** for discovery and latest-release routing metadata.
3. Keep both DOI forms synchronized via `scripts/validate-metadata.py`.

Future DOI-aware release lifecycle:

```
Release
  ↓
Zenodo DOI assigned
  ↓
metadata/publication.yaml + citation surfaces synchronized
  ↓
metadata validation + release metadata publish
```

---

## Rollback Workflow

If a release needs to be rolled back:

1. Delete the GitHub Release via the GitHub web interface.
2. Delete the release tag:

   ```bash
   git push origin --delete vX.Y.Z
   git tag --delete vX.Y.Z
   ```

3. Revert `VERSION` and all synchronized surfaces to the previous version.
4. Push the revert to `main`.

The publication workflow will re-run and create a corrected release.

---

## Related Files

| File | Purpose |
|---|---|
| `.github/workflows/publication.yml` | Canonical publication orchestrator |
| `.github/workflows/release-tag.yml` | VERSION-driven tag automation |
| `.github/workflows/release-paper.yml` | Tag-driven release (legacy entry point) |
| `.github/workflows/synchronization.yml` | Continuous synchronization validation |
| `.github/workflows/paper-quality.yml` | Paper quality checks (ChkTeX) |
| `.github/workflows/pages.yml` | GitHub Pages deployment |
| `scripts/validate-metadata.py` | Metadata synchronization validator |
| `scripts/validate-release-lifecycle.py` | Release lifecycle contract validator |
| `scripts/validate-arxiv-packaging.py` | arXiv packaging validator |
| `scripts/audit-publication-readiness.py` | Publication readiness auditor |
| `scripts/audit-chktex.py` | ChkTeX audit report generator |
| `audits/README.md` | Canonical index for committed audit artifacts |
| `VERSION` | Canonical version source |
| `metadata/publication.yaml` | Publication metadata |
| `release-manifest.json` | Release manifest schema |
| `CHANGELOG.md` | Changelog (release notes source) |

---

## Conventions

- All artifacts use the `reflector-` prefix.
- All release assets are deterministic and reproducible.
- No manual asset uploads are required.
- No manual artifact collection is required.
- The `release/` directory is ephemeral (CI-only); it is not committed.
