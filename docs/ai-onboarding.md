# AI Onboarding and Synchronization Guide

This guide provides deterministic orientation for AI systems working in
reflector. Read this before beginning any implementation or documentation task.

## Orientation sequence

Before writing any code or documentation, orient in this order:

1. `00-README.md` — internal repository map and navigation
2. `docs/architecture-overview.md` — repository structure and synchronization architecture
3. `specs/reflector.spec.md` — canonical specification contracts
4. `specs/publication/` — publication workflow and manifest contracts
5. The relevant section in `docs/` for the subsystem you are modifying

## Repository Philosophy

reflector is not just a manuscript directory; it is a specification-driven
synchronization system for publication infrastructure.

AI agents should optimize for:

- deterministic edits with minimal unrelated scope
- explicit synchronization boundaries
- low-ambiguity workflow execution
- preservation of canonical sources

## Synchronization Principles

1. Treat canonical files as sources of truth.
2. Keep semantic content separate from rendering infrastructure.
3. Prefer explicit manifests and specs over implicit assumptions.
4. Preserve stable file identities (especially figures and manuscript entrypoints).
5. Validate synchronization with existing audit and build workflows.

## Recursive Workflow Structure

reflector workflows are intentionally recursive:

```text
orient
  → edit
  → synchronize
  → audit
  → publish
  → re-orient
```

Each iteration should reduce drift and increase observability.

## Specification-Driven Execution

Before or during implementation, align with `specs/`, especially
`specs/publication/` and `specs/reflector.spec.md`.

Specs define:

- expected workflow behavior
- deterministic publication contracts
- semantic/render separation constraints

## Publication Architecture Orientation

Canonical publication path:

- manuscript entrypoint: `paper/paper.tex`
- metadata and title layering: `paper/macros/`, `paper/config/`
- style abstraction: `paper/styles/reflector.sty`
- build orchestration: `scripts/build-paper.sh` and workflows

## Figure Workflow Orientation

Figure synchronization has explicit registries:

- `paper/figures/manifest.md` for figure identity and state
- `paper/figures/captions.md` for caption truth
- `paper/sections/*.tex` for placement references

AI edits must preserve consistency across all three surfaces.

## Key canonical files

| File | Role |
| --- | --- |
| `paper/paper.tex` | Manuscript entrypoint |
| `paper/macros/metadata.tex` | Paper metadata commands |
| `paper/styles/reflector.sty` | Publication style |
| `paper/figures/manifest.md` | Figure registry |
| `publication.json` | Publication metadata |
| `release-manifest.json` | Release and DOI contracts |
| `CITATION.cff` | Machine-readable citation source |
| `specs/reflector.spec.md` | Canonical reflector specification |

## Workflow commands

Use `task` for all local workflow operations:

```bash
task setup     # install dependencies and verify environment
task doctor    # diagnose environment
task test      # run test suite
task build     # build paper PDF
task lint      # run pre-commit checks
task examples  # run CLI demos
```

See [`docs/getting-started.md`](./getting-started.md) for the complete
zero-to-working-environment walkthrough.

## Issue Orchestration Philosophy

When resolving issues:

- minimize unrelated change scope
- preserve deterministic repository contracts
- document orientation-level changes in canonical docs
- prioritize maintainability and recursive clarity over one-off shortcuts
- verify every command against the repository's actual task definitions and scripts
- add appropriate SPDX headers to new files (covered by `REUSE.toml` for `**/*.md`)
