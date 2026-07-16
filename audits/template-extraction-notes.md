# Template Extraction Notes

## Reusable components reinforced by this change

- `scripts/generate_pdf_previews.py` as a reusable CI thumbnail generator for publication PDFs
- `pages.yml` preview-generation and published-manifest enrichment steps
- landing-page breadcrumb, edition-card, and publication-history UI patterns
- manifest-driven publication metadata hydration for version, status, and build details

## Suggested extraction boundaries

1. **Publication asset preparation**
   - PDF copy/synchronization
   - preview generation
   - published-manifest enrichment

2. **Landing-page shell**
   - social preview metadata
   - breadcrumb navigation
   - publication edition cards
   - embedded-reader tabs

3. **Optional analytics policy**
   - documented only by default
   - explicit opt-in for privacy-preserving deployments

## Why this helps future extraction

The new logic keeps publication metadata generation and preview generation in CI-owned steps instead of hard-coding more values into the static landing page. That makes the future template easier to parameterize across projects with different PDFs, release tags, and archive destinations.
