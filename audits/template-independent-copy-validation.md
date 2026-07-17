# Template Independent Copy Validation

## Validation process

1. Copy `template/` into a fresh repository
2. Confirm root config, metadata, scripts, and workflows exist
3. Run metadata synchronization checks
4. Run shell and Python syntax validation
5. Inspect docs and publication artifact routing

## Prerequisites check

Expected target-repository prerequisites:

- Python 3 with `pyyaml`
- TeX Live with `latexmk`
- `biber`
- `chktex`
- optional `task`

## Expected outcomes

- `python3 scripts/sync-version.py --check` succeeds
- `python3 scripts/validate-metadata.py` succeeds
- `bash -n scripts/*.sh` succeeds
- workflow YAML remains parseable
- `docs/index.html` shows placeholder content until `publication.json` is deployed

## Manual adjustment log

- added standalone `publication.json` and `release-manifest.json` because the template scripts depend on them
- simplified Pages deployment to the generic paper publication path
- removed dependencies on release lifecycle scripts that were outside template scope

## Live-build note

A full live LaTeX build was not run as part of this extraction. Validation focused
on structure, metadata consistency, and script syntax.
