# Getting Started

This guide walks you through acquiring reflector, setting up a local development
environment, building the manuscript, and verifying the CLI. Follow the steps
in order for the smoothest experience.

## What is reflector?

reflector is a research manuscript repository and synchronization platform for
studying recursive AI-assisted software engineering. The repository includes:

- a research manuscript in `paper/` built with LaTeX
- a synchronization-oriented CLI in `reflector/`
- deterministic publication workflows in `scripts/` and `.github/workflows/`
- specification contracts in `specs/`
- a GitHub Pages publication surface

By the end of this guide you will have a working local environment capable of
running the test suite, building the paper PDF, and invoking the reflector CLI.

## Prerequisites

| Tool | Purpose | Minimum version |
| --- | --- | --- |
| `git` | Repository acquisition | Any recent version |
| `uv` | Python environment and dependency management | 0.11+ |
| `task` | Task runner for the canonical developer workflow | Any recent version |
| `latexmk` | Multi-pass LaTeX compilation | 4.75+ |
| `pdflatex` | PDF rendering | TeXLive 2025 |
| `biber` | Bibliography processing | 2.19+ |

`uv` and `task` are the only hard requirements for Python-only tasks.
LaTeX tools (`latexmk`, `pdflatex`, `biber`) are required to build the paper.

### Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install task

```bash
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b ~/.local/bin
```

### Install LaTeX tools

See [`docs/toolchain.md`](./toolchain.md) for platform-specific instructions
covering Ubuntu/Debian, macOS (Homebrew), and Windows.

## Acquire the repository

```bash
git clone https://github.com/egohygiene/reflector.git
cd reflector
```

## Set up the local environment

Run the canonical setup task. This installs the reflector package and all
development dependencies into a managed virtual environment, then runs a
diagnostic check.

```bash
task setup
```

`task setup` runs `uv sync --all-extras` followed by `task doctor`. Expected
output ends with:

```
✅ reflector setup complete.
```

## Run the environment diagnostic

If you need to re-verify the environment later:

```bash
task doctor
```

Expected output confirms `uv`, Python, the reflector package, and (if
installed) LaTeX tools are all available:

```
reflector doctor
---------------
uv 0.x.x (...)
Python 3.x.x
reflector x.x.x
✅ reflector package import OK
✅ latexmk available
✅ biber available
```

Missing LaTeX tools produce a warning (`⚠️`) instead of blocking the setup.
They are only required for paper builds.

## Run the test suite

```bash
task test
```

`task test` runs the fast, unit, and integration test suites in sequence. If
no tests have been collected yet, the runner exits cleanly with an informational
message.

## Build and verify the paper

Build the manuscript PDF:

```bash
task build
```

This invokes `./scripts/build-paper.sh paper`. The output PDF is written to
`paper/.cache/out/paper.pdf`.

To open the PDF automatically after building:

```bash
./scripts/build-paper.sh paper --open
```

To copy the PDF into `docs/` for publication:

```bash
./scripts/build-paper.sh paper --publish
```

> **Note:** Building the paper requires `latexmk`, `pdflatex`, and `biber`.
> If they are not installed, `task doctor` will show a warning. See
> [`docs/toolchain.md`](./toolchain.md) for installation instructions.

## Install or invoke the reflector CLI

The setup step above already installs the CLI. You can invoke it directly:

```bash
uv run reflector --help
```

Or use the task aliases:

```bash
task version    # print the CLI version
task run        # run reflector workflow in dry-run mode
task examples   # run CLI examples (help, milestone list, status, dry-run)
```

## Verify the CLI

```bash
task version
```

Expected output:

```
reflector x.x.x
```

To explore available commands:

```bash
uv run reflector --help
uv run reflector milestone --list
uv run reflector status
```

## Common setup problems

| Symptom | Resolution |
| --- | --- |
| `task: command not found` | Install `task` — see [Install task](#install-task) above |
| `uv: command not found` | Install `uv` — see [Install uv](#install-uv) above |
| `latexmk: command not found` | See [`docs/toolchain.md`](./toolchain.md) for LaTeX installation |
| `biber: command not found` | See [`docs/toolchain.md`](./toolchain.md) for biber installation |
| Paper build fails with missing `.sty` | Run `sudo tlmgr install <package>` or install `texlive-full` |
| `reflector: command not found` | Run `task setup` or `uv sync --all-extras` |

For build failure diagnostics:

```bash
LATEX_LOG_TAIL_LINES=200 ./scripts/build-paper.sh paper
./scripts/print-latex-diagnostics.sh paper
```

## Recommended next documents

| Need | Document |
| --- | --- |
| Internal repository orientation | [`00-README.md`](../00-README.md) |
| Detailed toolchain reference | [`docs/toolchain.md`](./toolchain.md) |
| Architecture reference | [`docs/architecture-overview.md`](./architecture-overview.md) |
| Contribution workflow | [`CONTRIBUTING.md`](../CONTRIBUTING.md) |
| AI assistant orientation | [`docs/ai-onboarding.md`](./ai-onboarding.md) |
| Repository roadmap | [`ROADMAP.md`](../ROADMAP.md) |
