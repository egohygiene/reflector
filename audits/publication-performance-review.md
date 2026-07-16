# Publication Performance Review

## Changes applied

- Added `preconnect` and `dns-prefetch` hints for GitHub, DOI, Zenodo, and ORCID routes used on the landing page.
- Preloaded the primary hero image and kept below-the-fold edition preview images lazy-loaded where appropriate.
- Reused generated cover previews for publication cards and social previews instead of relying only on the large hero asset.
- Kept the embedded PDF readers lazy-loaded and avoided eager loading additional iframes.
- Generated preview assets once during CI so the landing page can present lighter-weight images before full PDF access.

## Notes

- Full local PDF build benchmarking was limited in the sandbox because the base environment is missing LaTeX package `lmodern.sty`.
- Existing metadata validation and version synchronization checks already pass and were preserved.

## Recommended future follow-up

- Measure GitHub Pages response and asset sizes after deployment using published artifacts.
- If publication collections grow, consider paginated galleries before adding more embedded content above the fold.
