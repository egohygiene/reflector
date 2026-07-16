# Getting Started

## Prerequisites

- TeX Live with `latexmk`
- `biber`
- Python 3
- [`task`](https://taskfile.dev/)

## Quick start

1. Copy `template/` into a new repository root.
2. Configure `metadata/publication.yaml`.
3. Edit `paper/macros/metadata.tex` and `paper/config/title.tex`.
4. Run `task setup` and `task validate`.
5. Build the paper with `task paper:build`.
