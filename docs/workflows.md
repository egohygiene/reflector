# Workflow Overview

This document summarizes the primary workflows in Reflector.

## 1) Section Writing Workflow

1. Edit semantic section files under `paper/sections/`.
2. Keep manuscript semantics independent from style-specific concerns.
3. Build and review output via existing build pipeline.

## 2) Figure Workflow

1. Manage figure identity/state in `paper/figures/manifest.md`.
2. Keep canonical captions in `paper/figures/captions.md`.
3. Keep LaTeX placements and labels synchronized in `paper/sections/*.tex`.
4. Run `python3 scripts/audit-publication-readiness.py` after figure changes.

## 3) Publication Workflow

1. Resolve canonical source and metadata.
2. Build via `scripts/build-paper.sh`.
3. Validate output and synchronization artifacts.
4. Publish/deploy through configured CI workflows.

## 4) Placeholder Replacement Workflow

1. Replace placeholder asset while preserving canonical filename/dimensions.
2. Update figure state metadata (`placeholder` → `final`) in the manifest.
3. Reconcile captions/placement metadata if needed.
4. Re-run publication readiness audit.

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
