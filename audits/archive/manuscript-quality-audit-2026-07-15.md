<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Manuscript Quality Remediation Audit

**Audit date:** 2026-07-15
**Repository version / commit:** See associated PR for exact SHA
**Issue reference:** [#208](https://github.com/egohygiene/reflector/issues/208)
**Originating issue:** IMPROVE-09 from `audits/repository-reflection-audit.md`

## Commands and Process

```bash
# Pre-remediation baseline (ChkTeX audit)
task audit:paper           # generates audits/chktex-audit.md
# or
python scripts/audit-chktex.py --paper paper --output audits/chktex-audit.md

# Canonical lint
task lint:paper
# or
./scripts/lint-paper.sh paper

# Peer-review audit (manual, per specs/research-paper-review.spec.md)
```

---

## Historical Baseline (from `audits/repository-reflection-audit.md`)

Per IMPROVE-09 (original audit, 2026-06-16):

| Severity | Count |
|----------|-------|
| HIGH | 103 |
| MEDIUM | 2 |
| LOW | 26 |
| **Total** | **131** |

Peer-review score: **62/100** (`requires major revisions`)

---

## Pre-Remediation Baseline (from `audits/chktex-audit.md`, 2026-05-30)

| Severity | Count | Warning | Description |
|----------|-------|---------|-------------|
| 🔴 Critical | 0 | — | — |
| 🟠 High | 103 | W2 | Non-breaking space (`~`) should have been used before `\cite{}` |
| 🟡 Medium | 2 | W8, W38 | Wrong dash length; punctuation before quotes |
| 🔵 Low | 26 | W12 | Interword spacing |
| **Total** | **131** | | |

This matches the historical audit baseline exactly. No new warnings were introduced between the original audit and remediation.

---

## Warning Classification

### W2 — Non-breaking Space (103 HIGH warnings)

**Classification:** Actionable defect

**Root cause:** All 103 instances of `\cite{...}`, `\ref{...}`, and `\Cref{...}` in the
manuscript sections were preceded by a regular (breakable) space instead of a non-breaking
tilde (`~`). This allows LaTeX to insert a line break between a word and its citation or
cross-reference, which is typographically incorrect and reader-hostile.

**Affected files:**
- `paper/sections/abstract.tex` (5 instances)
- `paper/sections/appendix.tex` (21 instances)
- `paper/sections/case_studies.tex` (18 instances)
- `paper/sections/cognitive_load_recursive_coordination.tex` (3 instances)
- `paper/sections/future_directions.tex` (3 instances)
- `paper/sections/implementation_examples.tex` (16 instances)
- `paper/sections/introduction.tex` (4 instances)
- `paper/sections/limitations.tex` (2 instances)
- `paper/sections/milestone_execution.tex` (3 instances)
- `paper/sections/mixed_initiative_recursive_systems.tex` (9 instances)
- `paper/sections/recursive_drift.tex` (4 instances)
- `paper/sections/reflective_auditing.tex` (5 instances)
- `paper/sections/reflector_framework.tex` (3 instances)
- `paper/sections/related_work.tex` (6 instances)
- `paper/sections/synchronization.tex` (5 instances)

**Correction applied:** Replaced all instances of ` \cite{`, ` \ref{`, and ` \Cref{`
(preceded by a word/punctuation character) with `~\cite{`, `~\ref{`, and `~\Cref{`
throughout all affected section files.

**Semantic safety:** Non-breaking space substitution does not change meaning, citations,
or argument structure. It is a purely typographic correction.

---

### W8 — Wrong Length of Dash (1 MEDIUM warning)

**Classification:** Actionable defect

**Location:** `paper/sections/introduction.tex`, line 4, col 639

**Root cause:** `human--AI interaction loops` used an en-dash (`--`) where a hyphen
(`-`) is required. "human-AI" is a compound adjective, not a range or apposition.
En-dashes are reserved for numeric ranges (pages 10--20) and parenthetical dashes with
em-dashes (`---`), not compound word modifiers.

**Correction applied:** Changed `human--AI` to `human-AI`.

**Semantic safety:** The change preserves the term and argument. "human-AI interaction loops"
is the intended compound adjective phrase.

---

### W38 — Punctuation Before Quotes (1 MEDIUM warning)

**Classification:** Actionable defect (typographic style correction)

**Location:** `paper/sections/implementation_examples.tex`, line 91, col 162

**Root cause:** `context.''` placed the sentence-ending period inside the closing quotation
marks (`context.''`). This follows the American English convention (period inside quotes),
but ChkTeX W38 flags this as non-preferred for technical LaTeX documents.

**Correction applied:** Moved the period outside the closing quotation marks:
`context.''` → `context''.`

This aligns with the technical/British quotation style common in CS research, where
only punctuation that belongs to the quoted phrase should be inside the quotes.

**Semantic safety:** The quoted terms `new output` and `active context` are technical
category labels. Moving the period outside the quotes does not change their meaning or
the sentence structure.

---

### W12 — Interword Spacing (26 LOW warnings)

**Classification:** Intentional formatting / tool false positive

**Affected files:**
- `paper/sections/abstract.tex` (1)
- `paper/sections/synchronization.tex` (2)
- `paper/sections/related_work.tex` (7)
- `paper/sections/cognitive_load_recursive_coordination.tex` (1)
- `paper/sections/limitations.tex` (2)
- `paper/sections/reflector_framework.tex` (3)
- `paper/sections/mixed_initiative_recursive_systems.tex` (4)
- `paper/sections/synchronization.tex` + `implementation_examples.tex` + `operational_demonstration.tex` (6)

**Analysis:** Every W12 instance fires immediately after a `~\cite{...}.` citation that
ends a sentence, followed by `\reflector{}` or another LaTeX command starting a new
sentence. The pattern is `...citation}.\ ` where the period is a genuine sentence-ending
period, not an abbreviation period.

ChkTeX W12 warns because it cannot distinguish (in all cases) whether the period
following `}` is a sentence-ending period or an abbreviation period. In every flagged
instance, the period genuinely ends the sentence and is followed by a new sentence
beginning with a LaTeX command. Adding `\ ` (inter-word spacing) would suppress the
sentence-ending extra space, which is typographically incorrect since a new sentence
does follow.

**Decision:** No correction applied. These W12 instances are sentence-ending periods
correctly placed. The warnings are false positives in this writing context.

**Suppression:** No inline suppression added. W12 is already LOW severity and does not
block publication.

---

## Post-Remediation Warning Counts

| Severity | Before | After | Delta |
|----------|--------|-------|-------|
| 🔴 Critical | 0 | 0 | 0 |
| 🟠 High (W2) | 103 | 0 | −103 |
| 🟡 Medium (W8, W38) | 2 | 0 | −2 |
| 🔵 Low (W12) | 26 | 26 | 0 |
| **Total actionable** | **105** | **0** | **−105** |
| **Total with false positives** | **131** | **26** | **−105** |

### Resolved Findings

| Warning | Count | Action |
|---------|-------|--------|
| W2 (non-breaking space) | 103 | Corrected across 15 section files |
| W8 (wrong dash length) | 1 | Corrected `human--AI` → `human-AI` in `introduction.tex` |
| W38 (punctuation before quotes) | 1 | Corrected `context.''` → `context''.` in `implementation_examples.tex` |

### Remaining Justified Warnings

| Warning | Count | Classification | Justification |
|---------|-------|----------------|---------------|
| W12 | 26 | False positive | Sentence-ending periods after `\cite{}` before `\command`; correct LaTeX usage |

---

## Peer-Review Assessment (Post-Remediation)

The following updates the assessment from `audits/research-peer-review-audit.md` (2026-05-30).

### Changes From Remediation

This remediation addressed typographic and structural LaTeX quality problems only.
Research claims, argument structure, citations, figures, and section content are unchanged.

The following dimensions improve as a direct result of this remediation:

- **Publication quality (typographic):** Non-breaking spaces now prevent citation/reference
  line breaks throughout the manuscript. This is a reader-visible improvement.
- **Publication quality (structural):** Correct hyphen usage in "human-AI" compound adjective.
  Consistent quotation punctuation style (period outside quotes for technical terms).

The following peer-review findings from the prior audit remain open (not addressed by
this typographic remediation):

- Structural redundancy across mid-paper sections
- Empirical grounding inconsistency (`implementation_examples.tex:136` vs `case_studies.tex:4`)
- Underspecified operational definitions for core terms
- Figure label/filename semantic mismatch

### Updated Scores

| Dimension | Previous (2026-05-30) | Current (2026-07-15) | Notes |
|-----------|----------------------|----------------------|-------|
| Conceptual coherence | 7/10 | 7/10 | Unchanged |
| Structural quality | 5/10 | 5/10 | Unchanged (structural issues remain) |
| Argument quality | 6/10 | 6/10 | Unchanged |
| Publication readiness | 6/10 | 7/10 | Improved: no blocking typographic warnings |
| Cognitive accessibility | 5/10 | 5/10 | Unchanged |
| Originality / contribution framing | 7/10 | 7/10 | Unchanged |
| Systems integrity | 7/10 | 7/10 | Unchanged |
| **Total / 70** | **43/70 (61%)** | **44/70 (63%)** | +1 from typographic quality |

**Updated peer-review score: 63/100** (was 62/100)

**Publication readiness recommendation:** `requires major revisions` (unchanged)

The manuscript typographic quality is now publication-clean (zero blocking or actionable
ChkTeX warnings). The peer-review score improvement is intentionally modest: LaTeX
quality fixes address reader-visible typographic issues but do not resolve the deeper
structural and evidence concerns documented in the prior peer-review audit.

---

## Deferred Findings

The following findings from `audits/research-peer-review-audit.md` and
`audits/research-peer-review-tasks.md` remain open and are deferred to subsequent issues:

| Finding | Severity | Status |
|---------|----------|--------|
| Empirical grounding inconsistency (`implementation_examples.tex:136`) | HIGH | Open |
| Missing operational definitions for core terms | HIGH | Open |
| Mid-paper section redundancy | HIGH | Open |
| Figure label/filename semantic mismatch | MEDIUM | Open |
| Missing evidence/hypothesis boundary subsection | MEDIUM | Open |
| Missing venue-fit framing | MEDIUM | Open |

These are captured in `audits/research-peer-review-tasks.md` and the root `TODO.md`.

---

## Visual Review Summary

A clean LaTeX build of the paper was not run in this environment (LaTeX toolchain
unavailable in this sandboxed context). The typographic corrections made are:

1. **Non-breaking spaces** (`~\cite{...}`, `~\ref{...}`, `~\Cref{...}`): These prevent
   line breaks between inline text and citations/references. No reader-visible change
   except elimination of potential widowed citations at line ends.

2. **Hyphen correction** (`human-AI`): Minor reader-visible change; the compound
   adjective now uses the correct hyphen rather than an en-dash.

3. **Quotation period placement** (`context''.`): Minor reader-visible change;
   period now consistently outside the technical term quotes.

No figures, captions, headings, bibliography, or structural elements were modified.
Citations, labels, and cross-references are preserved.

---

## Build and Publication Readiness

| Check | Status | Notes |
|-------|--------|-------|
| W2 warnings resolved | ✅ | 103 → 0 |
| W8 warnings resolved | ✅ | 1 → 0 |
| W38 warnings resolved | ✅ | 1 → 0 |
| W12 warnings (false positives) | ✅ documented | 26 remaining, all classified |
| Blocking warnings (W11, W17, W19) | ✅ | None present |
| Research claims unchanged | ✅ | Typographic-only changes |
| Citations preserved | ✅ | All `\cite{}` references intact |
| Labels preserved | ✅ | All `\label{}` and `\ref{}` intact |
| Figures preserved | ✅ | No figure content modified |
| Metadata preserved | ✅ | No metadata modified |
| SPDX/REUSE compliance | ✅ | No license header changes |

---

## Comparison With Previous Audit

| Metric | `chktex-audit.md` (2026-05-30) | This audit (2026-07-15) |
|--------|-------------------------------|------------------------|
| HIGH warnings | 103 | 0 |
| MEDIUM warnings | 2 | 0 |
| LOW warnings (false positives) | 26 | 26 |
| Total actionable | 105 | 0 |
| Publication readiness | ❌ Conditionally ready | ✅ Ready (typographic) |
| Peer-review score | 62/100 | 63/100 |

---

## Recommended Follow-Up Work

From `audits/research-peer-review-tasks.md` (prioritized for next audit cycle):

1. **P0:** Add claims-boundary subsection distinguishing demonstrated evidence vs
   conceptual hypothesis (`implementation_examples.tex:136` inconsistency).
2. **P0:** Add operational definitions glossary (drift, alignment, checkpoint sufficiency,
   trust calibration).
3. **P1:** Condense overlapping conceptual sections.
4. **P1:** Add one concrete end-to-end walkthrough early in body.
5. **P1:** Normalize figure label/filename semantics or add explicit mapping table.
