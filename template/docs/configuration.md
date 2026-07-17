# Configuration

## `metadata/publication.yaml`

Configure:

- `slug`
- `title.main`, `title.subtitle`, `title.full`
- `abstract`
- `keywords`
- `version`, `status`, `date_released`, `license`
- `identifiers.*`
- `repository_url` and `pages_url`

## `metadata/authors.yaml`

Configure the canonical author list with:

- `family-names`
- `given-names`
- `alias`
- `orcid`
- `orcid_url`
- optional `github`, `affiliation`, `email`

## Artifact naming

Artifact naming is derived from `slug`:

- `<slug>.pdf`
- release asset basenames
- GitHub Pages PDF routes

## VERSION management

`VERSION` is the canonical semantic version source. Update it directly or via
`bump-version.yml`, then run `scripts/sync-version.py`.

## Optional modules

- GitHub Pages
- GitHub Releases
- Zenodo
- arXiv
- companion formats such as a magazine or supplement
