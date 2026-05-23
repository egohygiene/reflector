# Contributing

Thank you for your interest in contributing to this repository.

## Repository Structure

```
papers/
└── <paper-slug>/
    ├── paper.tex           # Main LaTeX document
    ├── references.bib      # BibTeX bibliography
    ├── README.md           # Paper overview
    ├── abstract.md         # Abstract draft (plain text)
    ├── outline.md          # Section outline
    ├── notes.md            # Research notes and brainstorming
    ├── roadmap.md          # Development roadmap
    ├── sections/           # LaTeX section files
    ├── figures/            # Generated figures and exports
    ├── diagrams/           # Source diagram files (Excalidraw, etc.)
    ├── assets/             # Static assets (images, logos, etc.)
    ├── references/         # Reference documents and PDFs
    └── examples/           # Example artifacts and code snippets
```

## Adding a New Paper

1. Create a new directory under `papers/<paper-slug>/`
2. Copy the template from `templates/paper/`
3. Update `papers/<paper-slug>/README.md` with paper metadata
4. Add sections under `papers/<paper-slug>/sections/`
5. Update the root `README.md` to list the new paper

## Building Papers

```bash
# Build a specific paper
./scripts/build-paper.sh papers/reflector

# Build all papers
./scripts/build-paper.sh --all

# Watch and auto-rebuild during development
./scripts/watch-paper.sh papers/reflector
```

## Style Guidelines

- Use spaces (not tabs) for indentation
- LaTeX files use 2-space indentation
- Markdown files follow standard CommonMark
- Section filenames use `snake_case.tex`
- Diagram source files use `kebab-case.excalidraw`
- Figure exports use `kebab-case.pdf` or `kebab-case.png`; reserve `hero.png` as the canonical publication preview asset

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
feat: add milestone synchronization section
fix: correct bibliography citation keys
docs: update reflector abstract
chore: update build workflow dependencies
research: document recursive drift case study findings
spec: align release metadata schema
sync: reconcile publication routes and release artifacts
audit: verify release manifest checksums
```

Commit messages are validated in CI using `commitlint`.

## Pull Requests

1. Fork the repository
2. Create a feature branch from `main`
3. Make your changes
4. Ensure the paper builds successfully: `./scripts/build-paper.sh papers/<slug>`
5. Open a pull request with a clear description

## License

By contributing, you agree that your contributions will be licensed under the repository's [LICENSE](./LICENSE).
