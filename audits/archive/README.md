<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Audit Archive

This directory contains historical audit artifacts that have been completed,
superseded, or fully addressed. They are preserved here as a traceable record
of the work performed during Reflector's development.

**Do not delete files from this archive.** They serve as evidence of completed
audit and remediation cycles, point-in-time publication snapshots, and
governance milestones.

---

## Active documents

The following documents remain actively maintained in the parent `audits/`
directory and are **not** archived here:

| Document | Status | Description |
|---|---|---|
| `audits/README.md` | Active | Canonical index for committed audit artifacts |
| `audits/arxiv-validation.md` | Recurring | CI-generated arXiv packaging validation |
| `audits/build-reproducibility.md` | Recurring | CI-generated build reproducibility checks |
| `audits/chktex-audit.md` | Recurring | CI-generated LaTeX linting audit |
| `audits/publication-readiness.md` | Recurring | CI-generated publication readiness report |
| `audits/zenodo-readiness.md` | Recurring | CI-generated Zenodo handoff readiness |
| `audits/publication-artifact-inventory.json` | Current | Machine-readable artifact inventory |
| `audits/publication-artifact-inventory.md` | Current | Human-readable artifact inventory |
| `audits/repository-reflection-audit.md` | Current | IMPROVE-06 and IMPROVE-08 resolved in #204; resolutions documented in #230 |
| `audits/archival-strategy-audit.md` | Reference | Archival strategy decisions |
| `audits/doi-metadata-audit.md` | Reference | DOI metadata consistency findings |
| `audits/orcid-synchronization.md` | Reference | ORCID linkage and citation alignment |
| `audits/pages-asset-lifecycle.md` | Reference | GitHub Pages asset lifecycle behavior |
| `audits/platform-readiness-assessment.md` | Reference | Platform readiness assessment |
| `audits/publication-ux-audit.md` | Current | Issue #227 publication UX audit (renamed from `final-publication-polish.md` in issue #230) |
| `audits/version-bump-workflow-validation.md` | Current | Issue #227 bump-version workflow validation; dry-run v0.1.3 added in #230 |
| `audits/reference-implementation-readiness.md` | Current | Issue #227 reference implementation readiness; lifecycle section added in #230 |
| `audits/v0.1.3-checkpoint-readiness.md` | Current | Issue #230 v0.1.3 patch release readiness checkpoint |

---

## Archived audit index

| Audit | Date | Issue / Origin | Notes |
|---|---|---|---|
| [`audit-2026-05-23T17-06-52.log`](./audit-2026-05-23T17-06-52.log) | 2026-05-23 | Manual run | Raw execution log; timestamped point-in-time artifact. |
| [`audit-2026-05-28T00-32-00Z.md`](./audit-2026-05-28T00-32-00Z.md) | 2026-05-28 | Manual review | Holistic publication and synchronization snapshot. |
| [`audit-2026-05-28T00-33-56Z.md`](./audit-2026-05-28T00-33-56Z.md) | 2026-05-28 | Manual review | Second holistic snapshot from the same session. |
| [`audit-run-fresh-repository-drift-cleanup-and-final-pre-figure-audit.md`](./audit-run-fresh-repository-drift-cleanup-and-final-pre-figure-audit.md) | 2026-05-30 | Manual review | Repository drift cleanup and pre-figure readiness. |
| [`final-publication-audit.md`](./final-publication-audit.md) | 2026-06-03 | Manual review | Final publication checkpoint before release v0.1.0. |
| [`manuscript-quality-audit-2026-07-15.md`](./manuscript-quality-audit-2026-07-15.md) | 2026-07-15 | Issue #208 | ChkTeX remediation and peer-review re-audit. Before/after: 105 actionable warnings → 0; peer-review 62/100 → 63/100. |
| [`pages-publication-validation.md`](./pages-publication-validation.md) | 2026-07-14 | Manual review | GitHub Pages URL validation snapshot. Superseded by ongoing CI. |
| [`pages-synchronization-findings.md`](./pages-synchronization-findings.md) | 2026-07-14 | Manual review | Pages synchronization findings; addressed and closed. |
| [`publication-experience-audit.md`](./publication-experience-audit.md) | 2026-07-14 | Pre-issue #227 | Publication UX improvements implemented before issue #227. Superseded by `audits/publication-ux-audit.md`. |
| [`publication-infrastructure-audit-followup.md`](./publication-infrastructure-audit-followup.md) | 2026-06-02 | Manual review | Follow-up to earlier infrastructure audit; all items closed. |
| [`publication-lifecycle-validation.md`](./publication-lifecycle-validation.md) | 2026-06-03 | Manual review | Lifecycle contract validation snapshot; superseded by CI validation. |
| [`publication-performance-review.md`](./publication-performance-review.md) | 2026-06-03 | Manual review | Performance review; findings incorporated and closed. |
| [`publication-polish-audit.md`](./publication-polish-audit.md) | 2026-06-03 | Manual review | Earlier polish audit; superseded by issue #227 work. |
| [`publication-readiness-audit.md`](./publication-readiness-audit.md) | 2026-05-30 | Manual review | Narrative readiness snapshot; superseded by CI-generated `publication-readiness.md`. |
| [`publication-readiness-summary.md`](./publication-readiness-summary.md) | 2026-05-30 | Manual review | Summary companion to readiness audits; findings addressed. |
| [`publication-system-action-items.md`](./publication-system-action-items.md) | 2026-06-02 | Manual review | Action register; all tracked items closed or incorporated into docs. |
| [`publication-system-audit.md`](./publication-system-audit.md) | 2026-06-02 | Manual review | Primary system architecture and risk audit. Findings addressed across multiple issues. |
| [`research-peer-review-audit.md`](./research-peer-review-audit.md) | 2026-05-30 | Manual review | Pre-remediation peer-review baseline (62/100). See `manuscript-quality-audit-2026-07-15.md` for post-remediation results. |
| [`research-peer-review-tasks.md`](./research-peer-review-tasks.md) | 2026-07-14 | Manual review | Task companion to the peer-review audit; addressed by issue #208. |
| [`template-extraction-notes.md`](./template-extraction-notes.md) | 2026-06-03 | Manual review | Template extraction observations for a future extraction pass. |
| [`template-extraction-opportunities.md`](./template-extraction-opportunities.md) | 2026-06-03 | Manual review | Reusable template extraction opportunities; actionable items deferred. |
| [`zenodo-integration-audit.md`](./zenodo-integration-audit.md) | 2026-06-03 | Manual review | Zenodo integration setup and metadata; formalized in `docs/release-process.md`. |

---

## What addressed each audit

| Issue / Milestone | Audits addressed |
|---|---|
| Pre-v0.1.0 stabilization | `audit-2026-05-23`, `audit-2026-05-28`, `publication-readiness-audit.md`, `publication-readiness-summary.md` |
| Publication system build-out | `publication-system-audit.md`, `publication-system-action-items.md`, `publication-infrastructure-audit-followup.md`, `publication-lifecycle-validation.md` |
| v0.1.0 release | `final-publication-audit.md`, `zenodo-integration-audit.md`, `publication-performance-review.md` |
| Template extraction survey | `template-extraction-notes.md`, `template-extraction-opportunities.md` |
| Issue #208 — ChkTeX remediation | `manuscript-quality-audit-2026-07-15.md`, `research-peer-review-tasks.md` |
| Pages stabilization | `pages-publication-validation.md`, `pages-synchronization-findings.md` |
| Issue #227 — final polish | `publication-experience-audit.md`, `publication-polish-audit.md` (both superseded by `audits/publication-ux-audit.md`) |
