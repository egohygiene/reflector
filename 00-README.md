# 00-README — Canonical Repository Orientation

This document is the canonical onboarding and synchronization reference for
contributors, maintainers, and AI assistants working in the reflector
repository. For external discovery, see [`README.md`](./README.md).

## Purpose of this document

`00-README.md` provides an internal map of the repository — its layers,
systems, key files, and workflow philosophy. It does not duplicate setup
instructions (see [`docs/getting-started.md`](./docs/getting-started.md))
or architecture detail (see [`docs/architecture-overview.md`](./docs/architecture-overview.md)).

## Quick navigation

| Need | Go to |
| --- | --- |
| Zero-to-working-environment setup | [`docs/getting-started.md`](./docs/getting-started.md) |
| Architecture and structure reference | [`docs/architecture-overview.md`](./docs/architecture-overview.md) |
| Toolchain requirements and installation | [`docs/toolchain.md`](./docs/toolchain.md) |
| Contribution workflow and conventions | [`CONTRIBUTING.md`](./CONTRIBUTING.md) |
| AI assistant execution guidance | [`docs/ai-onboarding.md`](./docs/ai-onboarding.md) |
| Roadmap and phase status | [`ROADMAP.md`](./ROADMAP.md) |
| Publication system reference | [`docs/publication-system-reference.md`](./docs/publication-system-reference.md) |
| Workflow registry | [`docs/publication-workflow-reference.md`](./docs/publication-workflow-reference.md) |
| Specification contracts | [`specs/`](./specs/) |

## Repository Overview

reflector is both a research manuscript repository and a synchronization system
for deterministic publication workflows.

Core roles:

- semantic paper authoring
- publication orchestration
- specification-driven execution
- recursive synchronization and auditability

## Repository Layers

| Layer | Location | Role |
| --- | --- | --- |
| Manuscript content | `paper/sections/` | Semantic paper text |
| Paper metadata | `paper/macros/`, `paper/config/` | Author, title, version |
| Paper style | `paper/styles/` | Rendering and layout |
| Figure registries | `paper/figures/` | Figure identity, state, captions |
| Specification contracts | `specs/` | Declared workflow and architecture contracts |
| Build scripts | `scripts/` | Deterministic build, audit, and validation utilities |
| CLI package | `reflector/` | Synchronization and orchestration runtime |
| CI workflows | `.github/workflows/` | Automated build, release, and Pages deployment |
| Documentation | `docs/` | Published documentation surface and reference guides |
| Audits | `audits/` | Publication readiness and synchronization audit artifacts |

## Workflow Overview

High-level execution flow:

```text
semantic content
    ↓
specification + manifest alignment
    ↓
synchronization + audits
    ↓
publication orchestration
    ↓
generated artifacts
```

## Publication Overview

Canonical manuscript entrypoint: `paper/paper.tex`
Build orchestration: `scripts/build-paper.sh` + `.latexmkrc`
Publication metadata: `publication.json`, `release-manifest.json`, `CITATION.cff`

Main publication outputs:

- local/CI PDF artifacts
- GitHub Pages-hosted output in `docs/`
- release metadata for versioned publication workflow

## Synchronization Philosophy

reflector prioritizes:

- deterministic inputs and outputs
- explicit contracts over implicit behavior
- inspectable synchronization boundaries
- stable canonical sources with replaceable render layers

Synchronization objective: reduce ambiguity while keeping recursive work
observable and maintainable.

## Specification Philosophy

Specifications in `specs/` define expected architecture and workflow behavior
before or alongside implementation. This keeps:

- execution contracts explicit
- workflow evolution reviewable
- recursive changes bounded by declared intent

## Recursive Workflow Orientation

reflector is designed for repeated authoring and synchronization cycles:

1. update semantic content or metadata
2. reconcile with specs/manifests
3. run synchronization and audits
4. produce publication artifacts
5. observe drift and iterate with explicit checkpoints

## Figure Workflow Orientation

Figure synchronization is deterministic and registry-driven:

- file-level truth and state in `paper/figures/manifest.md`
- caption truth in `paper/figures/captions.md`
- placement truth in `paper/sections/*.tex`
- consistency verification via `scripts/audit-publication-readiness.py`

## Pages and Deployment Overview

GitHub Actions workflows build publication artifacts and deploy Pages content
from repository-managed sources.

Pages deployment role:

- stable public documentation and publication surface
- synchronized with CI outputs and repository metadata

## Publication Pipeline Overview

Publication pipeline is manifest/spec-aware and deterministic by design:

1. resolve canonical source and metadata
2. run orchestrated build workflow
3. validate artifact and synchronization integrity
4. publish/deploy artifacts with traceable metadata

## Detailed Subsystem References

- `docs/publication-system-reference.md` — authoritative end-to-end publication lifecycle
- `docs/publication-workflow-reference.md` — workflow registry, triggers, ownership
- `docs/publication-artifact-reference.md` — artifact lifecycle, producers, consumers
- `docs/publication-lessons-learned.md` — lessons learned and future recommendations
- `docs/architecture-overview.md` — repository structure and synchronization architecture
- `docs/workflows.md` — workflow reference
- `docs/publication-architecture.md` — publication architecture detail
- `docs/ai-onboarding.md` — AI-specific execution guidance
