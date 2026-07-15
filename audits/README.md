<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Audit Archive Index

This directory stores **committed audit artifacts** used as repository governance history.

- Committed audits are part of the long-lived repository trail and are intended for review, release handoff, and historical comparison.
- Temporary CI workspace artifacts (for example, intermediate files produced during a run but not committed) are ephemeral and are not part of this index.

## Naming and timestamp conventions

- Use stable, descriptive filenames (for example, `publication-readiness-audit.md`).
- Include an explicit timestamp in the filename when the artifact represents a point-in-time snapshot (for example, `audit-2026-05-28T00-32-00Z.md`).
- Prefer Markdown (`.md`) for human-readable audits; retain machine-readable companions (for example, `.json`) when they are canonical outputs.
- Preserve historical artifacts unless a documented retention policy explicitly allows removal.

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
- **Historical**: retained point-in-time artifact.
- **Superseded**: retained for provenance but replaced by a newer canonical artifact.

## Committed audit index

| Audit | Date | Scope | Status | Origin | Notes |
|---|---|---|---|---|---|
| [`archival-strategy-audit.md`](./archival-strategy-audit.md) | 2026-06-03 | archival strategy and preservation decisions | Historical | Manual review (provenance detail: Unknown) | Point-in-time archival audit snapshot. |
| [`arxiv-validation.md`](./arxiv-validation.md) | 2026-05-28 | arXiv packaging validation | Recurring | `.github/workflows/publication.yml` (`scripts/validate-arxiv-packaging.py`) | Workflow-generated validation report. |
| [`audit-2026-05-23T17-06-52.log`](./audit-2026-05-23T17-06-52.log) | 2026-05-23 | point-in-time audit execution log | Historical | Manual or local run (Unknown) | Timestamped raw log artifact. |
| [`audit-2026-05-28T00-32-00Z.md`](./audit-2026-05-28T00-32-00Z.md) | 2026-05-28 | holistic publication + synchronization review | Historical | Manual review (Unknown) | Timestamped holistic audit report. |
| [`audit-2026-05-28T00-33-56Z.md`](./audit-2026-05-28T00-33-56Z.md) | 2026-05-28 | holistic publication + synchronization review | Historical | Manual review (Unknown) | Timestamped holistic audit report. |
| [`audit-run-fresh-repository-drift-cleanup-and-final-pre-figure-audit.md`](./audit-run-fresh-repository-drift-cleanup-and-final-pre-figure-audit.md) | 2026-05-30 | repository drift cleanup + pre-figure readiness | Historical | Manual review (Unknown) | Scenario-specific point-in-time audit. |
| [`build-reproducibility.md`](./build-reproducibility.md) | 2026-05-28 | reproducible build contract checks | Recurring | `.github/workflows/publication.yml` (`scripts/validate-build-reproducibility.py`) | Workflow-generated validation report. |
| [`chktex-audit.md`](./chktex-audit.md) | 2026-05-30 | LaTeX linting and warning severity | Recurring | `.github/workflows/publication.yml` (`scripts/audit-chktex.py`) | Updated 2026-07-15 post-remediation: 0 HIGH, 0 MEDIUM, 26 LOW (false positives). See `manuscript-quality-audit-2026-07-15.md`. |
| [`doi-metadata-audit.md`](./doi-metadata-audit.md) | 2026-06-03 | DOI metadata consistency | Historical | Manual review (Unknown) | DOI-focused synchronization audit. |
| [`final-publication-audit.md`](./final-publication-audit.md) | 2026-06-03 | final publication readiness and release quality | Historical | Manual review (Unknown) | Final publication checkpoint artifact. |
| [`orcid-synchronization.md`](./orcid-synchronization.md) | 2026-05-30 | ORCID and citation synchronization | Historical | Manual review (Unknown) | ORCID linkage and metadata alignment. |
| [`pages-asset-lifecycle.md`](./pages-asset-lifecycle.md) | 2026-07-14 | GitHub Pages asset lifecycle behavior | Historical | Manual review (Unknown) | Generation date not explicit in file; first committed on 2026-07-14. |
| [`pages-publication-validation.md`](./pages-publication-validation.md) | 2026-07-14 | publication URL validation on Pages | Historical | Manual review (Unknown) | Generation date not explicit in file; first committed on 2026-07-14. |
| [`pages-synchronization-findings.md`](./pages-synchronization-findings.md) | 2026-07-14 | Pages synchronization findings | Historical | Manual review (Unknown) | Generation date not explicit in file; first committed on 2026-07-14. |
| [`platform-readiness-assessment.md`](./platform-readiness-assessment.md) | 2026-06-03 | platform readiness across publication surfaces | Historical | Manual review (Unknown) | Platform-level readiness assessment. |
| [`publication-artifact-inventory.json`](./publication-artifact-inventory.json) | 2026-06-02 | machine-readable release artifact inventory | Historical | Manual or script generation (Unknown) | Canonical inventory companion to Markdown view. |
| [`publication-artifact-inventory.md`](./publication-artifact-inventory.md) | 2026-06-03 | human-readable release artifact inventory | Historical | Manual or script generation (Unknown) | Companion to JSON inventory. |
| [`publication-infrastructure-audit-followup.md`](./publication-infrastructure-audit-followup.md) | 2026-06-02 | publication infrastructure follow-up actions | Historical | Manual review (Unknown) | Follow-up to earlier infrastructure audit. |
| [`publication-lifecycle-validation.md`](./publication-lifecycle-validation.md) | 2026-06-03 | lifecycle contract validation | Historical | Manual review (Unknown) | Lifecycle validation snapshot. |
| [`publication-readiness-audit.md`](./publication-readiness-audit.md) | 2026-05-30 | publication readiness findings | Historical | Manual review (Unknown) | Narrative readiness audit snapshot. |
| [`publication-readiness-summary.md`](./publication-readiness-summary.md) | 2026-05-30 | readiness status summary | Historical | Manual review (Unknown) | Summary companion to readiness audits. |
| [`publication-readiness.md`](./publication-readiness.md) | 2026-05-30 | publication readiness report | Recurring | `.github/workflows/publication.yml` (`scripts/audit-publication-readiness.py`) | Workflow-generated readiness output. |
| [`publication-system-action-items.md`](./publication-system-action-items.md) | 2026-06-02 | publication system remediations | Historical | Manual review (Unknown) | Action register derived from system audit. |
| [`publication-system-audit.md`](./publication-system-audit.md) | 2026-06-02 | publication system architecture and risk review | Historical | Manual review (Unknown) | Primary system audit artifact. |
| [`repository-reflection-audit.md`](./repository-reflection-audit.md) | 2026-06-16 | repository reflection and synchronization | Current | Issue [#196](https://github.com/egohygiene/reflector/issues/196) | Includes findings `IMPROVE-06` and `IMPROVE-08` tracked by issue #204. |
| [`manuscript-quality-audit-2026-07-15.md`](./manuscript-quality-audit-2026-07-15.md) | 2026-07-15 | manuscript ChkTeX remediation and peer-review re-audit | Historical | Issue [#208](https://github.com/egohygiene/reflector/issues/208) | Before/after: 105 actionable warnings → 0; peer-review 62/100 → 63/100. Supplements `chktex-audit.md` and `research-peer-review-audit.md`. |
| [`research-peer-review-audit.md`](./research-peer-review-audit.md) | 2026-05-30 | research manuscript peer-review readiness | Historical | Manual review (Unknown) | Peer-review quality snapshot. Pre-remediation baseline (62/100). Superseded for typographic quality by `manuscript-quality-audit-2026-07-15.md`; structural findings remain open. |
| [`research-peer-review-tasks.md`](./research-peer-review-tasks.md) | 2026-07-14 | research peer-review action tracking | Historical | Manual review (Unknown) | Task companion to peer-review audit; generation date not explicit, first committed on 2026-07-14. |
| [`template-extraction-opportunities.md`](./template-extraction-opportunities.md) | 2026-06-03 | reusable template extraction opportunities | Historical | Manual review (Unknown) | Template-system follow-up findings. |
| [`zenodo-integration-audit.md`](./zenodo-integration-audit.md) | 2026-06-03 | Zenodo integration setup and metadata | Historical | Manual review (Unknown) | Integration-focused audit before handoff formalization. |
| [`zenodo-readiness.md`](./zenodo-readiness.md) | 2026-07-14 | GitHub Release to Zenodo handoff readiness | Recurring | GitHub Release asset from publication lifecycle (specific workflow run: Unknown) | v0.1.0 handoff snapshot; generation date not explicit in file, first committed on 2026-07-14. |
