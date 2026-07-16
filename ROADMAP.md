# Roadmap

This document tracks the high-level development roadmap for reflector.

Each phase is labeled with its current status:

- ✅ **Completed** — work is done and merged
- 🔄 **Active** — work is ongoing in the current development cycle
- 📋 **Planned** — prioritized and scheduled for an upcoming cycle
- 🔭 **Aspirational** — intended future direction, not yet scheduled

---

## Phase 1 — Repository Foundation and Publication Infrastructure ✅

All repository scaffolding, CI, and publication infrastructure is complete.

- [x] Repository structure and conventions
- [x] Developer experience configuration (`.editorconfig`, `.gitignore`, pre-commit hooks)
- [x] LaTeX build pipeline and reproducible build configuration
- [x] GitHub Actions automation (build, REUSE, Pages, release)
- [x] GitHub Pages publishing and deployment surface
- [x] reflector paper scaffold and section structure
- [x] Diagram and figure infrastructure with synchronization registries
- [x] Shared paper template system (publisher-agnostic style layer)
- [x] Specification contracts in `specs/`
- [x] REUSE/SPDX compliance and licensing infrastructure
- [x] Publication metadata and release manifest
- [x] CLI package (`reflector`) with synchronization and audit commands
- [x] Zenodo DOI provisioning and archival infrastructure
- [x] Documentation architecture and entry point system

---

## Phase 2 — reflector Paper: Draft ✅

The manuscript draft is substantially complete. All planned sections have initial content.

- [x] Abstract and introduction sections
- [x] Recursive Development Systems / Recursive Drift section
- [x] Human-in-the-Loop Governance and Synchronization section
- [x] Reflective Auditing Systems section
- [x] Milestone Synchronization and Checkpoint Contracts section
- [x] Mixed-Initiative Recursive Systems section
- [x] Operational Demonstration section
- [x] Implementation Examples section
- [x] Case Studies section
- [x] Limitations section
- [x] Related Work section
- [x] Future Directions section
- [x] Conclusion section
- [x] Initial bibliography compilation

---

## Phase 3 — Manuscript Revision and Quality Improvement 🔄

Active work to strengthen the draft through revision, figure integration, and quality auditing.

- [ ] Revise and tighten all section drafts for consistency and clarity
- [ ] Create and finalize architecture diagrams (Excalidraw → PDF/PNG exports)
- [ ] Integrate figures into LaTeX document with caption registry alignment
- [ ] Finalize abstract
- [ ] Run runtime test coverage for CLI and synchronization workflows
- [ ] Run and resolve ChkTeX linting and publication quality checks
- [ ] Complete consistency audit across specs, sections, and metadata
- [ ] Final bibliography review and citation key normalization

---

## Phase 4 — Publication Hardening 📋

Preparation for stable public release and external submission.

- [ ] Final PDF generation and end-to-end review
- [ ] Final magazine artifact review
- [ ] arXiv submission preparation and packaging validation
- [ ] GitHub Release publication with canonical artifacts and checksums
- [ ] GitHub Pages update and deployment verification
- [ ] DOI finalization and badge update
- [ ] ORCID synchronization
- [ ] CITATION.cff and codemeta.json update for release version

---

## Phase 5 — Future Work 🔭

Longer-horizon aspirations beyond the initial manuscript release.

- [ ] Scaffold next paper using shared template
- [ ] Article series exploring subsystem topics
- [ ] Conference submission preparation
- [ ] Hugging Face mirror and model card
- [ ] Reflector visual companion expansion
- [ ] Educational adaptations and talks
- [ ] Extend automation pipelines for multi-paper repositories

---

## Repository Lifecycle

Reflector is both the published research project and the reference implementation
of a reproducible publication platform. The intended evolution is:

```
Reflector (reference implementation)
    ↓
Template Extraction  ← next major milestone
    ↓
Reusable Publication Platform
    ↓
Future Publications
```

Template extraction is the next explicit milestone after the initial manuscript
publication. It is tracked separately from the manuscript release.
