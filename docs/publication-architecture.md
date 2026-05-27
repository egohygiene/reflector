# Publication Architecture Overview

This document describes Reflector's publication architecture and reproducibility model.

## arXiv Workflow

Reflector maintains arXiv-oriented publication behavior through deterministic LaTeX build and packaging conventions defined in scripts, workflows, and publication specs.

Key concerns:
- stable manuscript entrypoint (`paper/paper.tex`)
- explicit build orchestration (`scripts/build-paper.sh`, `.latexmkrc`)
- metadata consistency across publication files

## Publication Manifests

Publication metadata files (for example `publication.json`, `release-manifest.json`, and related specs) act as orchestration surfaces for repeatable publication behavior.

Manifest philosophy:
- explicit source/target expectations
- reproducible output contracts
- inspectable publication metadata

## Semantic/Render Separation

Reflector separates semantic manuscript content from render infrastructure:
- semantic text and structure in content files
- metadata in dedicated macro/config layers
- style/render concerns in publisher-facing style assets

This supports long-term portability across renderer targets.

## Renderer Abstraction Concepts

Renderer abstraction is treated as architecture, not ad hoc formatting:
- canonical semantic source remains stable
- target renderers adapt output conventions
- renderer changes should not require semantic manuscript rewrites

## Publication Reproducibility Philosophy

Reproducibility is achieved through:
- deterministic build scripts and CI workflows
- explicit metadata and manifest surfaces
- validation/audit checkpoints for synchronization integrity

Target outcome: low-ambiguity, inspectable, repeatable publication generation.
