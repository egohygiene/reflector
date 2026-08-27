# Reflector Pages deployment

Reflector publishes one deterministic site artifact through GitHub Actions.
The repository's Pages setting is the custom-domain authority; `docs/CNAME`
is retained only as a cutover assertion while branch deployment is retired.

## Ownership

| Concern | Authority |
| --- | --- |
| Paper source and PDF | `paper/` and `scripts/build-paper.sh` |
| Magazine source and PDFs | `magazine/` and `scripts/build-magazine.sh` |
| Static site source | `docs/` |
| Site catalog and integrity projection | `scripts/stage-pages.py` |
| Pages deployment | `.github/workflows/pages.yml` |
| DOI, Zenodo, and release history | Existing publication and release contracts |
| Beacon compatibility | `.beacon/` canary; optional and non-deploying |

The workflow never writes generated PDFs, previews, manifests, or catalogs
back into `docs/`. It stages them under disposable `_site/` output and verifies
the native PDF hashes before upload. Its local ownership marker is removed from
the final artifact so `SHA256SUMS` covers every deployed file. Manual partial
builds may reuse v0.1.2 release PDFs only after checking both the release
checksum asset and each PDF against `metadata/releases/v0.1.2.json`.

## Stable routes

| Route | Contract |
| --- | --- |
| `/` | Publication hub |
| `/paper/` | Paper landing and reader |
| `/magazine/` | Digital magazine landing and reader |
| `/magazine/print/` | Print edition landing and download |
| `/downloads/` | Artifacts, release, DOI, source, and integrity evidence |
| `/publication.json` | Byte-identical canonical publication manifest |
| `/site.json` | Deterministic site catalog |
| `/SHA256SUMS` | Complete site integrity inventory |
| `/reflector.pdf` | Permanent paper alias |
| `/reflector-magazine.pdf` | Permanent digital magazine alias |
| `/reflector-magazine-print.pdf` | Permanent print magazine alias |

## Actions cutover

1. Verify `egohygiene.io` in the GitHub organization account.
2. In the repository Pages settings, set the custom domain to
   `reflector.egohygiene.io`.
3. Select **GitHub Actions** as the Pages source.
4. Confirm the Squarespace DNS CNAME points `reflector` to
   `egohygiene.github.io` without a wildcard record.
5. Merge only after the pull-request Pages artifact passes.
6. Confirm the main deployment and all post-deploy HTTPS checks pass.
7. Enable **Enforce HTTPS** after GitHub issues the certificate.

## Technical fallback

`https://egohygiene.github.io/reflector/` is not a second canonical site. It
is the GitHub project URL and should redirect to, or serve compatibly with, the
custom domain. Nested links are relative so a downloaded artifact remains
navigable under either base path. Post-deploy validation follows every stable
fallback route and compares the resulting bytes with the deployed artifact.

## Rollback

If the Actions deployment or certificate fails:

1. Disable further Pages deployments by pausing the workflow in GitHub.
2. Keep the last successful Pages artifact and all release assets unchanged.
3. Temporarily restore `main:/docs` only if an immediate static fallback is
   required; root PDFs are release assets and are never renamed.
4. Remove the custom domain from the repository Pages settings before removing
   its DNS CNAME, preventing a dangling domain claim.
5. Repair and validate the complete review artifact, select GitHub Actions
   again, restore the custom domain, then rerun the workflow on `main`.

Rollback never changes the DOI, Zenodo records, release tags, publication
manifest history, or native source paths.
