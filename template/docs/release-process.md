# Release Process

## Semantic versioning with `VERSION`

Use semantic versioning for the canonical publication version.

## Manual bump workflow

Run the `bump-version.yml` workflow to compute and commit the next version.

## Tag creation

Run `release-tag.yml` to create the annotated `vX.Y.Z` tag after validation.

## Release asset naming

Use the publication slug for release assets, for example `<slug>.pdf`.
