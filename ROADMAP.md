---
schema: aether.architecture-document/v1
id: reflector-roadmap
title: Reflector Roadmap
kind: architecture-document
version: 0.1.0
status: draft
owners:
  - egohygiene
created: 2026-08-19
updated: 2026-08-27
governed_by:
  - architecture-roadmap
depends_on:
  - reflector-vision
  - reflector-pillars
  - reflector-architecture
  - reflector-decisions
related:
  - reflector-purpose
  - reflector-principles
  - reflector-manifesto
  - reflector-epistemology
supersedes: []
---

# Roadmap

<!-- BEGIN ROADMAP EXECUTION SNAPSHOT -->
<!-- roadmap-manifest
schema: hygiene.roadmap/v1alpha1
repository: egohygiene/reflector
visibility: public
publication: composed
route: /roadmap/
updated: 2026-08-26
-->
## 2026-08-27 execution snapshot

> This evidence-reconciled snapshot is the issue-generation and visual-roadmap handoff. The longer-horizon strategy below remains canonical context; generated HTML, JSON, progress, issue plans, and commit lists are projections.

**Lifecycle:** public research preview
**Current gate:** Make the custom-domain paper and magazine hub canonical while preserving every native publication and archival contract.
**North-star outcome:** A reproducible research and publication platform whose manuscripts, evidence, templates, and public outputs remain traceable.

### Visual roadmap publication

**Mode:** `composed`
**Route:** `/roadmap/`
**Current publication evidence:** Live GitHub Pages research site plus GitHub Releases; v0.1.2 observed.

Compose dist/roadmap/ into the repository's existing final site artifact at /roadmap/. The current Pages workflow remains the only deployer.

### Quest line

<!-- roadmap-step
id: REF-Q01
status: complete
depends_on: []
issues: []
-->
#### REF-Q01 — Publish the research preview

**State:** `complete`
**Depends on:** None

**Outcome:** A versioned public research preview and live Pages surface are available.

**Exit criteria:**

- [x] The release and site are publicly accessible.
- [x] REUSE and Pages checks pass.

**Current evidence:**

- Release v0.1.2 was published on 2026-07-15.
- Pages and REUSE workflows were observed green.

<!-- roadmap-step
id: REF-Q02
status: active
depends_on: [REF-Q01]
issues: []
-->
#### REF-Q02 — Reconcile roadmap and commit policy

**State:** `active`
**Depends on:** `REF-Q01`

**Outcome:** Roadmap status matches shipped work and contribution checks accept the documented convention.

**Exit criteria:**

- [ ] Template extraction is marked complete with evidence.
- [ ] The architecture-corpus commit pattern either conforms or the policy is deliberately updated.

**Current evidence:**

- Template extraction completed in PR #232 on 2026-07-16 but remains listed as next work.
- Commitlint rejected the non-conventional architecture-corpus message.

<!-- roadmap-step
id: REF-Q03
status: ready
depends_on: [REF-Q02]
issues: []
-->
#### REF-Q03 — Complete the manuscript revision

**State:** `ready`
**Depends on:** `REF-Q02`

**Outcome:** The next manuscript checkpoint incorporates review evidence and reproducible figures.

**Exit criteria:**

- [ ] Claims link to source data and generation steps.
- [ ] The published preview identifies its manuscript and evidence versions.

**Current evidence:**

- The repository is a v0.1.2 research preview rather than a final publication.

<!-- roadmap-step
id: REF-Q04
status: planned
depends_on: [REF-Q03]
issues: [244]
-->
#### REF-Q04 — Execute the research loop

**State:** `planned`
**Depends on:** `REF-Q03`

**Outcome:** Issue #244 turns research questions, evidence, synthesis, and publication into a repeatable loop.

**Exit criteria:**

- [ ] Issue #244 closes with an end-to-end documented run.
- [ ] Every stage emits reviewable evidence and supports reruns.

**Current evidence:**

- Issue #244 opened on 2026-08-19.

<!-- roadmap-step
id: REF-Q05
status: active
depends_on: [REF-Q01]
issues: [247, 249]
-->
#### REF-Q05 — Harden publication and transfer Beacon assets

**State:** `active`
**Depends on:** `REF-Q01`

**Outcome:** Publication is durable and reusable publication tooling moves to Beacon with clear ownership.

**Exit criteria:**

- [ ] Release, archival, citation, and accessibility checks pass.
- [ ] Transferred templates or tooling have one authoritative home and a versioned consumer path.
- [ ] The pinned Beacon compatibility canary packages the native paper, magazine, and metadata artifacts without deploying or changing public contracts.

**Current evidence:**

- Architecture PR #245 merged at d1bc53ee59c9186717b0e626072d45c8fd1cc224 on 2026-08-20.
- Issue #247 scopes a compatibility-first transfer boundary that can proceed independently of manuscript revision and the research loop.
- Issue #249 tracks the pre-existing 86 MB arXiv bundle against the 50 MB upload limit surfaced by the compatibility validation pass.
- Reflector remains authoritative for paper, magazine, Pages, DOI, Zenodo, arXiv, and release behavior while the Beacon adapter is proven.

<!-- roadmap-step
id: REF-Q06
status: active
depends_on: [REF-Q01]
issues: [250]
-->
#### REF-Q06 — Reconcile the canonical publication hub

**State:** `active`
**Depends on:** `REF-Q01`

**Outcome:** `reflector.egohygiene.io` provides stable paper, magazine, print,
download, manifest, DOI, release, and source routes from one deterministic
Actions deployment.

**Exit criteria:**

- [x] The complete review artifact is deterministic and retains all root PDF aliases.
- [x] Native publication commands remain authoritative and Beacon remains optional.
- [x] The repository-defined Actions workflow is isolated as the intended deployer.
- [ ] Pages settings use Actions and disable the legacy `main:/docs` deployment path.
- [ ] The live custom domain, technical fallback, DNS, TLS, and post-deploy checks pass.

**Current evidence:**

- Issue #250 owns the compatibility-preserving site and deployment migration.
- DOI `10.5281/zenodo.20477044`, release `v0.1.2`, and historical artifacts are protected.

### Roadmap-to-issue handoff

- A step is complete only when its exit criteria and required evidence are satisfied; commit count never determines progress.
- Ready steps without an issue are candidates for the private, duplicate-aware roadmap.issue-plan.json dry run. Planned steps remain preview-only unless a reviewer explicitly opts them in with issue_policy: propose.
- Issue creation or reconciliation requires human approval or an explicitly authorized Pace operation and returns issue references through a reviewable roadmap pull request.
- Pull requests and commits should include Roadmap-Step: <ID>; historical evidence may be linked through existing issue and pull-request relationships.
- Public rendering uses only allowlisted build-time evidence and never places a GitHub token or private issue plan in the browser artifact.

<!-- END ROADMAP EXECUTION SNAPSHOT -->

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
