<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# TODO — Publication Completion Roadmap

Canonical execution checklist from publication-ready state through release, archival indexing, discoverability, and ecosystem integration.

## Current objective

1. Finish the paper
2. Finish publication validation
3. Publish Reflector

---

## Pause state — v0.1.3 checkpoint (issue #230)

Active development is paused after the v0.1.3 checkpoint. The following infrastructure
milestones are complete. Template extraction is the next major milestone.

### Completed

- [x] Publication UX stabilization (issue #227)
- [x] Preview generation and artifact routing (issue #227)
- [x] Metadata synchronization across 7 surfaces (issue #227)
- [x] Manual semantic-version bump workflow (issue #227)
- [x] Release workflow ownership clarified — no race conditions (issue #227)
- [x] Audit organization — historical audits archived with index (issues #204, #227)
- [x] Reference-implementation readiness documented (issue #227)
- [x] Repository lifecycle documented (issue #230)
- [x] Durable audit naming applied — `publication-ux-audit.md` (issue #230)
- [x] IMPROVE-06 resolved — `audits/README.md` index created (issue #204)
- [x] IMPROVE-08 resolved — Zenodo deposition checklist in `docs/release-process.md` (issue #204)
- [x] Version-bump dry-run verified: `0.1.2` + patch = `0.1.3` (issue #230)

### Next milestone

```
Template extraction readiness audit
    ↓
Extract reusable publication platform into template/
    ↓
Independent portability validation
    ↓
Optional standalone publication-template repository
```

### Deferred enhancements

The following are intentionally deferred and do not block the v0.1.3 checkpoint:

- arXiv submission
- Zenodo deposition for v0.1.3
- ORCID synchronization
- Hugging Face mirror
- Manuscript editorial revisions (P0/P1 findings from issue #208)
- GitHub repository topics configuration (requires repository settings, not file changes)

---

## Documentation foundation (completed)

Tracks the work from issue #202 — Align repository roadmap and documentation entry points.

- [x] `ROADMAP.md` aligned: completed, active, planned, and aspirational phases distinguished
- [x] `docs/getting-started.md` created with sequential zero-to-working-environment workflow
- [x] `00-README.md` updated as canonical internal orientation document
- [x] `README.md` updated to link to getting-started guide
- [x] `docs/architecture-overview.md` updated with distinct architectural reference content
- [x] `docs/ai-onboarding.md` updated with expanded AI execution guidance
- [x] `CONTRIBUTING.md` updated to reference getting-started guide
- [x] Navigation and cross-references updated throughout

Follow-up tasks (outside issue scope):

- [ ] Audit all internal markdown links across `docs/` for broken references
- [ ] Add link validation to CI to catch broken relative links going forward
- [ ] Consider consolidating `docs/publication-architecture.md` into `docs/architecture-overview.md`

Issue #204 completion items:

- [x] Create `audits/README.md` as the canonical committed audit archive index
- [x] Add explicit Zenodo deposition handoff checklist and recovery guidance to `docs/release-process.md`

Issue #205 completion items:

- [x] Add synchronization checkpoint specification: `specs/synchronization/synchronization-checkpoint.spec.md`
- [x] Add portable repository architecture specification: `specs/repositories/repository-architecture.spec.md`
- [x] Add human governance specification: `specs/governance/human-governance.spec.md`
- [x] Align master and onboarding/navigation docs with implemented specification hierarchy (`specs/reflector.spec.md`, `docs/architecture-overview.md`, `docs/ai-onboarding.md`, `00-README.md`)

Issue #206 completion items:

- [x] Created `tests/conftest.py` with shared fixtures (console capture, audit entries, milestones, boundaries)
- [x] Created `tests/cli/test_main.py` — 30 CLI tests covering all commands (run, synchronize, audit, milestone, status, huggingface, sync), help, exit codes, argument parsing, error behavior, and filesystem effects
- [x] Created `tests/audits/test_pipeline.py` — 31 tests for all four audit pipeline stages, invariant validation, drift detection, aggregation, and report rendering
- [x] Created `tests/synchronization/test_checkpoint.py` — 21 tests for checkpoint initialization, boundary listing, evaluate with known/unknown/null IDs, and render helpers
- [x] Created `tests/orchestration/test_milestone.py` — 30 tests including parameterized transitions, terminal state protection, synchronization boundary enforcement, and inspect/list/advance behavior
- [x] Created `tests/examples/test_examples.py` — 14 tests that mechanically verify each worked example is importable and produces correct return values
- [x] Created `reflector/examples/audit_example.py` — annotated audit pipeline worked example
- [x] Created `reflector/examples/synchronization_example.py` — annotated synchronization checkpoint worked example
- [x] Created `reflector/examples/milestone_example.py` — annotated milestone orchestration worked example with enforced boundary demonstration
- [x] Created `reflector/examples/README.md` — examples index with usage instructions and spec references
- [x] Updated `pyproject.toml` — added `[tool.pytest.ini_options]` with `testpaths`, `markers` (integration), and discovery configuration
- [x] Updated `.github/workflows/synchronization.yml` — added `test-runtime` CI job and path triggers for `reflector/**`, `tests/**`, `pyproject.toml`

New follow-up tasks (outside issue scope):

- [ ] Add coverage measurement (`pytest-cov`) to CI once a coverage threshold is established
- [ ] Extend audit pipeline with pluggable event sources for real agent action capture
- [ ] Add test markers for `slow` and `filesystem` tests to allow selective test runs

---

## Release blockers (must complete before publication is considered complete)

### Phase 1 — Publication Readiness

Key artifacts: [`audits/publication-readiness-summary.md`](./audits/publication-readiness-summary.md), [`audits/publication-readiness.md`](./audits/publication-readiness.md), [`.github/workflows/paper-quality.yml`](./.github/workflows/paper-quality.yml), [`scripts/validate-metadata.py`](./scripts/validate-metadata.py), [`paper/figures/prompts/`](./paper/figures/prompts/)

- [ ] Final paper audit passes
- [x] All GitHub Actions passing
- [x] Figure reproducibility issues resolved
- [x] Prompt preservation complete
- [x] Metadata validation passes
- [ ] Final PDF review completed
- [ ] Final magazine review completed
- [ ] GitHub Release created

### Phase 2 — DOI and Archival Preservation

Key artifacts: [`.zenodo.json`](./.zenodo.json), [`CITATION.cff`](./CITATION.cff), [`metadata/publication.yaml`](./metadata/publication.yaml)

- [ ] Create Zenodo record
- [ ] Connect GitHub Release to Zenodo
- [ ] Generate DOI
- [ ] Verify DOI resolves correctly
- [ ] Add DOI badge to README
- [ ] Add DOI to CITATION.cff
- [ ] Add DOI to publication metadata

### Phase 3 — ORCID Synchronization

Key artifacts: [`CITATION.cff`](./CITATION.cff), [`metadata/authors.yaml`](./metadata/authors.yaml), [`metadata/publication.yaml`](./metadata/publication.yaml)

- [ ] Verify ORCID profile
- [ ] Add publication to ORCID
- [ ] Verify DOI synchronization
- [ ] Verify citation metadata appears correctly

### Phase 4 — arXiv Submission

Key artifacts: [`paper/00README.json`](./paper/00README.json), [`audits/arxiv-validation.md`](./audits/arxiv-validation.md), [`specs/publication/arxiv-publication.spec.md`](./specs/publication/arxiv-publication.spec.md)

- [ ] Confirm arXiv author eligibility
- [ ] Determine endorsement requirements
- [ ] Submit arXiv package
- [ ] Verify metadata
- [ ] Verify PDF rendering
- [ ] Verify references
- [ ] Verify figures
- [ ] Record arXiv identifier
- [ ] Add arXiv badge to README

### Phase 5 — Repository Publication

Key artifacts: [`.github/workflows/release-paper.yml`](./.github/workflows/release-paper.yml), [`.github/workflows/pages.yml`](./.github/workflows/pages.yml), [`docs/release-process.md`](./docs/release-process.md)

- [ ] Create GitHub Release
- [ ] Upload canonical artifacts
- [ ] Upload checksums
- [ ] Verify release notes
- [ ] Verify Pages deployment

---

## Post-publication enhancements (non-blocking)

### Phase 6 — Visibility and Discovery

Key artifacts: [`README.md`](./README.md), [`docs/`](./docs/), [`metadata/publication.yaml`](./metadata/publication.yaml), [`docs/huggingface.md`](./docs/huggingface.md)

- [ ] Portfolio integration
- [ ] GitHub profile integration
- [ ] Website integration
- [ ] OpenAlex indexing investigation
- [ ] Semantic Scholar indexing investigation
- [ ] Google Scholar discoverability investigation
- [ ] Hugging Face mirror evaluation

### Phase 7 — Communication Artifacts

Linked deliverable context: [`README.md`](./README.md), [`docs/index.html`](./docs/index.html), [`audits/publication-readiness-summary.md`](./audits/publication-readiness-summary.md)

#### LinkedIn Post — Research Paper

Create a publication announcement focused on:

- publication journey
- recursive systems
- synchronization
- articulation
- learning through building
- systems thinking

Avoid:

- hype
- exaggerated claims
- AI evangelism

Tone:

- reflective
- thoughtful
- humble
- technically grounded

#### LinkedIn Post — Visual Companion Magazine

Create a separate publication announcement focused on:

- visual communication
- accessibility
- transforming complexity into understanding
- educational design
- knowledge compression

Avoid:

- self-promotion
- marketing language
- clickbait

Tone:

- creative
- reflective
- educational

Deliverables:

- [ ] Paper announcement draft
- [ ] Magazine announcement draft

### Phase 8 — Future Work

Reference artifacts: [`ROADMAP.md`](./ROADMAP.md), [`docs/research/`](./docs/research/)

- [ ] Reflector visual companion expansion
- [ ] Article series
- [ ] Conference submissions
- [ ] Talks
- [ ] Videos
- [ ] Future papers
- [ ] Visual synapse integrations
- [ ] Educational adaptations

---

## Publication Consistency Governance (issue #207)

Tracks the work from issue #207 — Add magazine-to-manuscript consistency auditing.

- [x] Created `specs/publication/magazine-consistency.spec.md` — consistency specification
- [x] Created `magazine/consistency-mapping.yaml` — cross-artifact mapping file
- [x] Created `scripts/audit-magazine-consistency.py` — read-only deterministic audit engine
- [x] Created `tests/audits/fixtures/magazine_consistency/` — minimal independent test fixtures
- [x] Created `tests/audits/test_magazine_consistency.py` — 82 tests covering all required scenarios
- [x] Updated `Taskfile.yml` — added `audit:magazine` task
- [x] Updated `.github/workflows/paper-quality.yml` — integrated magazine consistency audit job
- [x] All 8 consistency rules implemented (RULE-001 through RULE-008)
- [x] Exception governance: narrowly scoped, documented exceptions supported
- [x] Deterministic output ordering verified
- [x] Nonzero exit status for FAIL-severity violations
- [x] Zero exit status for advisory-only findings

Follow-up tasks (outside issue scope):

- [ ] Add `magazine/spec.md` version field synchronized with `metadata/publication.yaml`
- [ ] Add content-drift detection for figure captions referenced in both artifacts
- [ ] Consider automatic exception expiration enforcement in CI

---

## Manuscript Quality Remediation (issue #208)

Tracks the work from issue #208 — Improve manuscript quality and repeat the peer-review audit.

- [x] Pre-remediation baseline established: 103 HIGH, 2 MEDIUM, 26 LOW ChkTeX warnings; peer-review score 62/100
- [x] All 103 W2 (non-breaking space) warnings resolved across 15 section files
- [x] W8 (wrong dash length) resolved: `human--AI` → `human-AI` in `introduction.tex`
- [x] W38 (punctuation before quotes) resolved: `context.''` → `context''.` in `implementation_examples.tex`
- [x] W12 (26 LOW) classified as false positives: sentence-ending periods after citations before LaTeX commands
- [x] Post-remediation ChkTeX result: 0 HIGH, 0 MEDIUM, 26 LOW (all false positives)
- [x] Post-remediation peer-review score: 63/100 (was 62/100; typographic quality improved)
- [x] New audit artifact committed: `audits/manuscript-quality-audit-2026-07-15.md`
- [x] `audits/chktex-audit.md` updated to reflect post-remediation state
- [x] `audits/README.md` updated with new audit entry

Deferred findings (require separate editorial revision work):

- [ ] P0: Add claims-boundary subsection distinguishing demonstrated vs hypothesized evidence (`implementation_examples.tex:136`)
- [ ] P0: Add operational definitions glossary for core terms (drift, alignment, checkpoint sufficiency, trust calibration)
- [ ] P1: Condense overlapping conceptual sections (reflective auditing / synchronization / framework / mixed-initiative)
- [ ] P1: Add one concrete end-to-end walkthrough early in main body
- [ ] P1: Normalize figure label/filename semantics or add explicit mapping table
- [ ] P2: Add lightweight process metrics from manuscript workflow as evidence
- [ ] P2: Add explicit venue-fit and contribution-positioning paragraph

---

- [x] TODO.md exists
- [x] Publication workflow is documented end-to-end
- [x] DOI workflow is documented
- [x] ORCID workflow is documented
- [x] arXiv workflow is documented
- [x] Communication deliverables are defined
- [x] Future work is preserved without competing with publication completion

---

## Notes

- Source of completed checkmarks above: `audits/publication-readiness-summary.md` and current repository state checks.
- Keep this file updated as the single publication completion tracker.
