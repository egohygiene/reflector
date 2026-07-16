# Template Extraction Result

## What was copied/adapted

- Root publication configuration files were copied into `template/`
- Paper build, lint, watch, and diagnostics scripts were adapted
- The publication style was renamed and generalized as `publication.sty`
- Metadata surfaces and workflows were rewritten with placeholder identity

## What was excluded

- Reflector manuscript content
- Reflector-specific names, identifiers, repository URLs, and publication metadata
- Magazine-specific publication artifacts
- Repository code outside the reusable publication platform

## Component transformation log

- `reflector.sty` renamed to `publication.sty`
- color, listing, and callout identifiers were generalized
- metadata validation now reads canonical title and ORCID from template config
- version sync surfaces were reduced to template-owned manifests
- Pages deployment was simplified to a paper-only path

## Known limitations

- A full live LaTeX build was not executed during extraction
- `publication.json` and `release-manifest.json` remain starter manifests and may be extended by adopters
- local `--publish` naming in `build-paper.sh` remains source-compatible rather than slug-derived

## Content-leak validation results

- no Alan Szmyt identity in `template/`
- no Reflector DOI or canonical ORCID in `template/`
- no Reflector publication title in `template/`
- provenance references to Reflector are limited to origin notes
