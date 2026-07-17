<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# ChkTeX Audit Report

Generated at: `2026-07-15T15:00:00Z`

Paper: `paper`
ChkTeX version: `1.7.8`

> **Remediation note:** Updated as part of manuscript quality remediation (issue #208).
> Pre-remediation baseline (2026-05-30): 103 HIGH, 2 MEDIUM, 26 LOW (131 total).
> See [`manuscript-quality-audit-2026-07-15.md`](./manuscript-quality-audit-2026-07-15.md)
> for the full before/after classification and remediation record.

## Summary

| Severity | Count |
|----------|-------|
| 🔴 Critical | 0 |
| 🟠 High | 0 |
| 🟡 Medium | 0 |
| 🔵 Low | 26 |
| **Total** | **26** |

## Publication Readiness

✅ **Ready — no actionable warnings**

> ✅ All HIGH and MEDIUM warnings resolved. Remaining 26 LOW warnings are documented
> false positives (W12: sentence-ending periods after citations before LaTeX commands).

## Warning Details

### 🟠 HIGH

No HIGH warnings.

### 🟡 MEDIUM

No MEDIUM warnings.

### 🔵 LOW

All LOW warnings are W12 (Interword spacing). These fire after `~\cite{...}.` when a
sentence-ending period precedes a new sentence beginning with a LaTeX command (e.g.,
`\reflector{}`). ChkTeX cannot distinguish sentence-ending periods from abbreviation
periods in this context; in every instance the period is genuinely sentence-ending.
Adding `\ ` would suppress sentence-ending spacing, which is typographically incorrect.

**Classification:** False positives. No correction applied.

| File | Line | Col | Warning | Message |
|------|------|-----|---------|---------|
| `abstract.tex` | 5 | 230 | W12 | Interword spacing (`\ ') should perhaps be used. |
| `synchronization.tex` | 6 | 219 | W12 | Interword spacing (`\ ') should perhaps be used. |
| `related_work.tex` | 8 | 385 | W12 | Interword spacing (`\ ') should perhaps be used. |
| `related_work.tex` | 12 | 337 | W12 | Interword spacing (`\ ') should perhaps be used. |
| `cognitive_load_recursive_coordination.tex` | 16 | 195 | W12 | Interword spacing (`\ ') should perhaps be used. |
| `related_work.tex` | 16 | 571 | W12 | Interword spacing (`\ ') should perhaps be used. |
| `limitations.tex` | 20 | 277 | W12 | Interword spacing (`\ ') should perhaps be used. |
| `related_work.tex` | 20 | 180 | W12 | Interword spacing (`\ ') should perhaps be used. |
| `reflector_framework.tex` | 21 | 314 | W12 | Interword spacing (`\ ') should perhaps be used. |
| `related_work.tex` | 24 | 369 | W12 | Interword spacing (`\ ') should perhaps be used. |
| `limitations.tex` | 28 | 213 | W12 | Interword spacing (`\ ') should perhaps be used. |
| `related_work.tex` | 28 | 251 | W12 | Interword spacing (`\ ') should perhaps be used. |
| `introduction.tex` | 29 | 152 | W12 | Interword spacing (`\ ') should perhaps be used. |
| `synchronization.tex` | 31 | 189 | W12 | Interword spacing (`\ ') should perhaps be used. |
| `related_work.tex` | 32 | 43 | W12 | Interword spacing (`\ ') should perhaps be used. |
| `related_work.tex` | 34 | 355 | W12 | Interword spacing (`\ ') should perhaps be used. |
| `mixed_initiative_recursive_systems.tex` | 39 | 52 | W12 | Interword spacing (`\ ') should perhaps be used. |
| `mixed_initiative_recursive_systems.tex` | 39 | 235 | W12 | Interword spacing (`\ ') should perhaps be used. |
| `mixed_initiative_recursive_systems.tex` | 39 | 538 | W12 | Interword spacing (`\ ') should perhaps be used. |
| `mixed_initiative_recursive_systems.tex` | 39 | 672 | W12 | Interword spacing (`\ ') should perhaps be used. |
| `synchronization.tex` | 45 | 143 | W12 | Interword spacing (`\ ') should perhaps be used. |
| `implementation_examples.tex` | 52 | 285 | W12 | Interword spacing (`\ ') should perhaps be used. |
| `reflector_framework.tex` | 58 | 276 | W12 | Interword spacing (`\ ') should perhaps be used. |
| `operational_demonstration.tex` | 59 | 171 | W12 | Interword spacing (`\ ') should perhaps be used. |
| `reflector_framework.tex` | 79 | 98 | W12 | Interword spacing (`\ ') should perhaps be used. |
| `implementation_examples.tex` | 93 | 219 | W12 | Interword spacing (`\ ') should perhaps be used. |

## Resolved Warnings

The following warnings were resolved as part of issue #208 (2026-07-15):

| Warning | Count Resolved | Action |
|---------|---------------|--------|
| W2 — Non-breaking space | 103 | Replaced ` \cite{}`, ` \ref{}`, ` \Cref{}` with `~\cite{}`, `~\ref{}`, `~\Cref{}` across 15 section files |
| W8 — Wrong dash length | 1 | `human--AI` → `human-AI` in `introduction.tex` |
| W38 — Punctuation before quotes | 1 | `context.''` → `context''.` in `implementation_examples.tex` |

## arXiv Submission Readiness

| Check | Status | Notes |
|-------|--------|-------|
| ChkTeX available | ✅ | Required for linting |
| No critical warnings | ✅ | 0 critical |
| No high-severity warnings | ✅ | 0 high (was 103 before remediation) |
| No medium warnings | ✅ | 0 medium (was 2 before remediation) |

## Configuration

ChkTeX is configured via `.chktexrc` at the repository root. Suppressed warnings are
documented with justifications in that file. Inline suppressions (`%chktex N`) are
tracked as Warning 44 and reviewed during audit.

To re-run this audit locally:

```bash
task audit:paper
# or
python scripts/audit-chktex.py
```
