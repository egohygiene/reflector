<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Audit Index

This directory stores **committed audit artifacts** used as repository governance history.

- Committed audits are part of the long-lived repository trail and are intended for review, release handoff, and historical comparison.
- Temporary CI workspace artifacts (for example, intermediate files produced during a run but not committed) are ephemeral and are not part of this index.
- Historical and superseded artifacts are preserved in [`audits/archive/`](./archive/) — see [`audits/archive/README.md`](./archive/README.md) for the full archive index.

## Naming and timestamp conventions

- Use stable, descriptive filenames (for example, `publication-readiness-audit.md`).
- Include an explicit timestamp in the filename when the artifact represents a point-in-time snapshot (for example, `audit-2026-05-28T00-32-00Z.md`).
- Prefer Markdown (`.md`) for human-readable audits; retain machine-readable companions (for example, `.json`) when they are canonical outputs.
- Preserve historical artifacts unless a documented retention policy explicitly allows removal.
- Move superseded or completed point-in-time audits to `audits/archive/` rather than deleting them.

## Adding or updating committed audits

When adding a committed audit artifact:

1. Add the artifact under `audits/` with a stable filename.
2. Include generation/completion date information inside the artifact when available.
3. Link originating issue/PR/workflow provenance when known; otherwise record `Unknown`.
4. Mark supersession relationships explicitly in the index notes.
5. Update this `audits/README.md` in the same change as the new audit.

Status guidance used below:

- **Current**: canonical artifact currently used in active workflow/review.
- **Recurring**: regenerated repeatedly by workflows or recurring validation cycles.
- **Reference**: stable reference artifact not expected to change frequently.
- **Historical**: retained point-in-time artifact in the archive.
- **Superseded**: retained for provenance but replaced by a newer canonical artifact.

## Active audit index

| Audit | Date | Scope | Status | Origin | Notes |
|---|---|---|---|---|---|
| [`archival-strategy-audit.md`](./archival-strategy-audit.md) | 2026-06-03 | archival strategy and preservation decisions | Reference | Manual review | Point-in-time archival strategy snapshot. |
| [`arxiv-validation.md`](./arxiv-validation.md) | Recurring | arXiv packaging validation | Recurring | `.github/workflows/publication.yml` (`scripts/validate-arxiv-packaging.py`) | Workflow-generated validation report. |
| [`build-reproducibility.md`](./build-reproducibility.md) | Recurring | reproducible build contract checks | Recurring | `.github/workflows/publication.yml` (`scripts/validate-build-reproducibility.py`) | Workflow-generated validation report. |
| [`chktex-audit.md`](./chktex-audit.md) | Recurring | LaTeX linting and warning severity | Recurring | `.github/workflows/publication.yml` (`scripts/audit-chktex.py`) | Updated 2026-07-15 post-remediation: 0 HIGH, 0 MEDIUM, 26 LOW (false positives). |
| [`doi-metadata-audit.md`](./doi-metadata-audit.md) | 2026-06-03 | DOI metadata consistency | Reference | Manual review | DOI-focused synchronization audit. |
| [`final-publication-polish.md`](./final-publication-polish.md) | 2026-07-16 | publication UX polish — preview layout, responsive design | Current | Issue [#227](https://github.com/egohygiene/reflector/issues/227) | Documents the magazine-only preview fix and final landing-page polish. |
| [`orcid-synchronization.md`](./orcid-synchronization.md) | 2026-05-30 | ORCID and citation synchronization | Reference | Manual review | ORCID linkage and metadata alignment. |
| [`pages-asset-lifecycle.md`](./pages-asset-lifecycle.md) | 2026-07-14 | GitHub Pages asset lifecycle behavior | Reference | Manual review | Asset lifecycle behavior on Pages. |
| [`platform-readiness-assessment.md`](./platform-readiness-assessment.md) | 2026-06-03 | platform readiness across publication surfaces | Reference | Manual review | Platform-level readiness assessment. |
| [`publication-artifact-inventory.json`](./publication-artifact-inventory.json) | 2026-06-02 | machine-readable release artifact inventory | Current | Manual or script generation | Canonical inventory companion to Markdown view. |
| [`publication-artifact-inventory.md`](./publication-artifact-inventory.md) | 2026-06-03 | human-readable release artifact inventory | Current | Manual or script generation | Companion to JSON inventory. |
| [`publication-readiness.md`](./publication-readiness.md) | Recurring | publication readiness report | Recurring | `.github/workflows/publication.yml` (`scripts/audit-publication-readiness.py`) | Workflow-generated readiness output. |
| [`reference-implementation-readiness.md`](./reference-implementation-readiness.md) | 2026-07-16 | final reference-implementation readiness review | Current | Issue [#227](https://github.com/egohygiene/reflector/issues/227) | Final readiness assessment before template extraction. |
| [`repository-reflection-audit.md`](./repository-reflection-audit.md) | 2026-06-16 | repository reflection and synchronization | Current | Issue [#196](https://github.com/egohygiene/reflector/issues/196) | Includes findings `IMPROVE-06` and `IMPROVE-08` tracked by issue #204. |
| [`version-bump-workflow-validation.md`](./version-bump-workflow-validation.md) | 2026-07-16 | bump-version workflow design and safeguards | Current | Issue [#227](https://github.com/egohygiene/reflector/issues/227) | Documents the bump-version.yml workflow implementation. |
| [`zenodo-readiness.md`](./zenodo-readiness.md) | Recurring | GitHub Release to Zenodo handoff readiness | Recurring | GitHub Release asset from publication lifecycle | Zenodo handoff snapshot; regenerated each release. |

## Archive

Historical and superseded audit artifacts have been moved to [`audits/archive/`](./archive/).
See [`audits/archive/README.md`](./archive/README.md) for the complete archive index,
a mapping of which issues addressed each audit, and a list of currently active authoritative documents.
