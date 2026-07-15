---
title: Magazine-to-Manuscript Consistency Specification
version: 1.0.0
status: active
category:
  - publication
  - consistency
  - auditing
tags:
  - magazine
  - manuscript
  - synchronization
  - consistency
  - audit
---

<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Magazine-to-Manuscript Consistency Specification

## Purpose and Applicability

This specification defines the deterministic consistency contract between the canonical
research manuscript (`paper/`) and the visual companion magazine (`magazine/`).

The manuscript is the canonical semantic source for all publication content. The magazine
is a visually adapted companion artifact that communicates manuscript concepts through
editorial layout, infographics, and visual storytelling. Visual adaptation is intentional
and expected; it is not a consistency failure.

This specification applies to:
- The manuscript at `paper/`
- The magazine at `magazine/`
- Canonical publication metadata at `metadata/`
- The cross-artifact consistency mapping at `magazine/consistency-mapping.yaml`

This specification does not apply to:
- Subjective editorial decisions (typography, layout, color)
- Visual equivalence between figures and page images
- Natural-language equivalence of prose

---

## Canonical Content Ownership

| Data Category | Canonical Source | Notes |
|---|---|---|
| Publication title | `metadata/publication.yaml:title.full` | Propagated to all artifacts |
| Publication version | `metadata/publication.yaml:version` | Required sync to `publication.json` |
| Author metadata | `metadata/authors.yaml` | ORCID and name are canonical |
| DOI and release metadata | `publication.json` + `metadata/publication.yaml` | Both are required to agree |
| Figure identifiers | `paper/figures/manifest.md` | Manuscript is canonical source |
| Figure captions | `paper/figures/captions.md` | Manuscript is canonical source |
| Magazine page assets | `magazine/pages/` | Magazine owns page rendering |
| Magazine page declarations | `magazine/tex/magazine.tex` | Magazine owns page ordering |
| Cross-artifact mappings | `magazine/consistency-mapping.yaml` | Explicit mapping file |

The manuscript owns all semantic content. The magazine owns all visual rendering decisions.
Metadata files own all publication identity and citation metadata.

---

## Supported Cross-Artifact Identifiers

| Identifier Type | Format | Example |
|---|---|---|
| Magazine mapping entry ID | `<category>-<slug>` | `page01-cover`, `meta-title` |
| Manuscript figure ID | `reflector-figure-N` | `reflector-figure-1` |
| Magazine page ID | `pageNN-<slug>` | `page03-recursive-drift` |
| Consistency rule ID | `<category>-<name>` | `metadata-title-match` |
| Exception ID | `exc-<slug>` | `exc-visual-adaptation` |

All identifiers must be stable once assigned. Renaming an identifier without updating all
references is a consistency violation.

---

## Required and Optional Relationships

### Required Relationships (violations produce FAIL status)

1. **Required files exist**: All declared required files must be present on disk.
2. **Mapping is valid**: `magazine/consistency-mapping.yaml` must exist and parse as valid YAML.
3. **No duplicate mapping IDs**: Each entry in the mapping must have a unique `id`.
4. **Required mapping targets exist**: Magazine page files declared in `magazine.tex` must exist.
5. **Declared page assets exist**: Pages listed in `magazine/tex/magazine.tex` via `\includegraphics` must exist.

### Advisory Relationships (violations produce WARN status)

6. **Metadata version advisory**: `version` in `metadata/publication.yaml` should match `version` in `magazine/spec.md`.
7. **Figure source advisory**: Manuscript figure IDs referenced in figure mappings should exist in `paper/figures/manifest.md`.
8. **Orphaned mappings**: Mapping entries that reference non-existent files produce warnings.

### Informational

9. **Approved exceptions**: Exceptions declared in the mapping are reported separately and do not count as failures.

---

## Validation Rules

### RULE-001: required-files-exist

**Category:** structural  
**Severity:** FAIL  
**Description:** All files required by this specification must exist at their declared paths.

Required files:
- `paper/paper.tex`
- `paper/figures/manifest.md`
- `metadata/publication.yaml`
- `metadata/authors.yaml`
- `publication.json`
- `magazine/tex/magazine.tex`
- `magazine/spec.md`
- `magazine/consistency-mapping.yaml`

**Remediation:** Create or restore the missing required file.

---

### RULE-002: mapping-valid-yaml

**Category:** mapping  
**Severity:** FAIL  
**Description:** `magazine/consistency-mapping.yaml` must be parseable as valid YAML.

**Remediation:** Fix the YAML syntax error in the mapping file.

---

### RULE-003: mapping-no-duplicate-ids

**Category:** mapping  
**Severity:** FAIL  
**Description:** Every entry across all mapping sections must have a unique `id` value.

**Remediation:** Rename or remove the duplicate mapping entry.

---

### RULE-004: magazine-pages-declared-exist

**Category:** structural  
**Severity:** FAIL  
**Description:** Every page image referenced via `\includegraphics` in `magazine/tex/magazine.tex`
must exist as a file on disk relative to the magazine directory.

**Remediation:** Add the missing page image file or remove the declaration from `magazine.tex`.

---

### RULE-005: mapping-source-files-exist

**Category:** mapping  
**Severity:** WARN  
**Description:** Each `manuscript_source` path declared in the mapping must resolve to an
existing file in the repository.

**Remediation:** Correct the `manuscript_source` path or remove the orphaned mapping entry.

---

### RULE-006: mapping-target-files-exist

**Category:** mapping  
**Severity:** WARN  
**Description:** Each `magazine_target` path declared in the mapping must resolve to an
existing file in the repository.

**Remediation:** Add the missing target file or remove the orphaned mapping entry.

---

### RULE-007: metadata-version-advisory

**Category:** metadata  
**Severity:** WARN  
**Description:** The `version` field in `metadata/publication.yaml` should match the
`version` field in `magazine/spec.md` when both are present. Advisory — intentional
version skew may be documented as an exception.

**Remediation:** Update `magazine/spec.md` to reflect the current publication version,
or document the intentional version difference as an exception in the mapping.

---

### RULE-008: figure-ids-in-manifest

**Category:** figures  
**Severity:** WARN  
**Description:** Manuscript figure IDs referenced as `manuscript_figure_id` in figure
mappings should exist in `paper/figures/manifest.md`.

**Remediation:** Correct the `manuscript_figure_id` or update the manifest to include
the missing figure.

---

## Intentional Divergence Behavior

Intentional differences between the manuscript and magazine must be documented as
explicit exceptions in `magazine/consistency-mapping.yaml` under the `exceptions` key.

Each exception must include:
- `id`: A stable unique identifier (format: `exc-<slug>`)
- `rule`: The specific rule being excepted (must reference a RULE-NNN identifier)
- `rationale`: A concise human-readable explanation
- `scope`: The narrowest scope that describes the affected content
- `approved_by`: The approving authority or provenance

Exceptions may optionally include:
- `review_date`: When the exception should be re-evaluated

**Constraints:**
- Exceptions must be narrowly scoped.
- Directory-wide or rule-wide suppressions are prohibited.
- Exceptions do not suppress structural errors (missing files, invalid YAML, duplicate IDs).

---

## Diagnostic Requirements

Each finding must identify:
- The violated rule identifier (RULE-NNN)
- The manuscript source path
- The magazine target path
- The observed mismatch or condition
- The expected relationship
- A remediation direction

---

## Exit-Status Behavior

| Condition | Exit Code |
|---|---|
| All required checks pass (FAIL count = 0) | 0 |
| Any required-rule violation (FAIL count > 0) | 1 |
| Only warnings or advisory findings | 0 |
| Approved exceptions only | 0 |

Warnings and approved exceptions do not cause a nonzero exit status.

---

## Local and CI Execution

**Canonical local command:**
```
task audit:magazine
```

or directly:
```
python scripts/audit-magazine-consistency.py
```

**CI integration:** The audit is integrated into the `paper-quality.yml` workflow.
It runs on changes to `paper/**`, `magazine/**`, `metadata/**`, and
`magazine/consistency-mapping.yaml`.

Local and CI execution use the same audit entry point. The audit requires no network
access, external services, or credentials.

---

## Conformance Criteria

An implementation conforms to this specification when it:

1. Evaluates all rules defined above.
2. Returns a nonzero exit status for all FAIL-severity violations.
3. Returns a zero exit status for WARN-only or exception-only findings.
4. Reports FAIL, WARN, INFO, and SKIP (exception) findings distinctly.
5. Produces deterministic output ordering across repeated executions.
6. Does not modify any source artifact.
7. Requires no network access or credentials.
8. Identifies the violated rule, source, target, and remediation for each finding.

---

## Scope Clarification

This specification defines **structural consistency** — verifiable from file contents
and declared identifiers without subjective interpretation.

The following are explicitly **out of scope** and must not be treated as consistency failures:
- Visual rendering differences between manuscript figures and magazine pages
- Editorial tone, prose style, or content emphasis differences
- Layout, typography, or color decisions
- The absence of a magazine equivalent for a manuscript section
- Natural-language equivalence checks

---

## References

- `paper/figures/manifest.md` — Figure identity registry
- `paper/figures/captions.md` — Caption registry
- `magazine/consistency-mapping.yaml` — Cross-artifact mapping
- `metadata/publication.yaml` — Canonical publication metadata
- `specs/publication/publication-manifest.spec.md` — Publication manifest architecture
- `scripts/audit-magazine-consistency.py` — Audit implementation
