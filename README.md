# reflector

🪞 Reflective synchronization architectures for recursive AI-assisted software engineering.

## Repository overview

This repository contains the **Reflector** paper, publication assets, release metadata,
and automation workflows used to build and publish the draft.

- Canonical synchronization onboarding: [`00-README.md`](./00-README.md)
- Paper source: `paper/`
- Publication site: `docs/`
- Build and publication scripts: `scripts/`
- CI and release workflows: `.github/workflows/`
- Progress dashboard: [`PROGRESS.md`](./PROGRESS.md)

## Orientation and architecture docs

- Canonical repository orientation: [`00-README.md`](./00-README.md)
- Repository architecture: [`docs/architecture-overview.md`](./docs/architecture-overview.md)
- AI onboarding: [`docs/ai-onboarding.md`](./docs/ai-onboarding.md)
- Workflow overview: [`docs/workflows.md`](./docs/workflows.md)
- Local GitHub Actions testing with `act`: [`docs/act.md`](./docs/act.md)
- Publication architecture: [`docs/publication-architecture.md`](./docs/publication-architecture.md)
- Toolchain requirements: [`docs/toolchain.md`](./docs/toolchain.md)

## Local development workflow (Taskfile)

Install [`task`](https://taskfile.dev/installation/) and [`uv`](https://docs.astral.sh/uv/) and then bootstrap locally:

```bash
task setup
```

Core local workflow:

```bash
task doctor
task version
task test
task examples
```

Python dependencies are managed locally with `uv` (`task setup` runs `uv sync --all-extras`).

## Publication links

- GitHub Pages: https://egohygiene.github.io/reflector/
- Repository: https://github.com/egohygiene/reflector
- Citation metadata: [`CITATION.cff`](./CITATION.cff)
- Publication metadata: [`publication.json`](./publication.json)
- Progress dashboard: [`PROGRESS.md`](./PROGRESS.md)

## Build instructions

Requires `latexmk`, `pdflatex`, and `biber`. See [`docs/toolchain.md`](./docs/toolchain.md) for installation steps.

```bash
task build
```

To publish a local PDF into `docs/`:

```bash
./scripts/build-paper.sh paper --publish
```

## Reflector CLI

Set up the local environment:

```bash
task setup
```

Core commands:

- `uv run reflector run`
- `uv run reflector synchronize` (or `uv run reflector sync`)
- `uv run reflector audit`
- `uv run reflector milestone`
- `uv run reflector status`
- `uv run reflector huggingface --check-sdk`

## Release and version metadata

- Current version: [`VERSION`](./VERSION) (`0.0.1`)
- Changelog: [`CHANGELOG.md`](./CHANGELOG.md)
- Release manifest: [`release-manifest.json`](./release-manifest.json)
- Release Please config: [`.release-please-config.json`](./.release-please-config.json)
- Zenodo scaffold: [`.zenodo.json`](./.zenodo.json)
