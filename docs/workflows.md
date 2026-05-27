# Workflow Overview

This document summarizes the primary workflows in Reflector.

## 1) Section Writing Workflow

1. Edit semantic section files under `paper/sections/`.
2. Keep manuscript semantics independent from style-specific concerns.
3. Build and review output via existing build pipeline.

## 2) Figure Workflow

1. Manage figure identity/state in `paper/figures/manifest.md`.
2. Preserve recursive prompt history in `paper/figures/prompts/*.prompt.md`.
3. Keep canonical captions in `paper/figures/captions.md`.
4. Keep LaTeX placements and labels synchronized in `paper/sections/*.tex`.
5. Run `python3 scripts/audit-publication-readiness.py` after figure changes.

## 3) Publication Workflow

1. Resolve canonical source and metadata.
2. Build via `scripts/build-paper.sh`.
3. Validate output and synchronization artifacts.
4. Publish/deploy through configured CI workflows.

## 4) Placeholder Replacement Workflow

1. Update the figure prompt file with the latest iteration context and checkpoint notes.
2. Replace placeholder asset while preserving canonical filename/dimensions.
3. Update figure state metadata (`placeholder` → `final`) in the manifest.
4. Reconcile captions/placement metadata if needed.
5. Re-run publication readiness audit.

Canonical lifecycle:

`Placeholder Figure → Prompt Iteration → Candidate Figure → Synchronization Review → Final Publication Figure`

Synchronization review checkpoints:
- Prompt file updated
- Manifest state synchronized
- Caption/label alignment verified
- Publication audit passes

## 5) Synchronization Audit Workflow

1. Run audit tooling from `scripts/` (including publication-readiness checks).
2. Verify references, figures, and metadata alignment.
3. Resolve drift before publication/release steps.

## 6) Pages Deployment Workflow

1. CI builds publication artifacts.
2. Deployment workflow publishes repository-backed output to GitHub Pages.
3. Published surface remains traceable to repository source and metadata.

## 7) Publication Manifest Workflow

1. Use publication metadata/manifests as explicit orchestration contracts.
2. Keep source declaration and output expectations deterministic.
3. Maintain reproducibility by avoiding hidden build assumptions.
