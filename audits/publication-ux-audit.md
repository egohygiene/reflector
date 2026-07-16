<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Publication UX Audit

**Date:** 2026-07-16
**Issue:** [#227](https://github.com/egohygiene/reflector/issues/227)
**Scope:** Publication landing-page UX, preview layout, responsive design, final visual polish

---

## Summary

This audit documents the final holistic stabilization and polish pass applied to the
Reflector publication landing page as part of issue #227. The work closes the remaining
presentation and layout defects identified before template extraction.

---

## Subtask 1 — Publication Preview Layout Fix

### Problem identified

The left column of the publication landing page (`docs/index.html`) displayed all three
generated PDF previews simultaneously inside a `edition-grid` CSS grid with
`grid-template-columns: repeat(3, minmax(0, 1fr))`.

The containing left column has a `max-width: 300px` (defined by the `content-grid`
template: `minmax(0, 300px) minmax(0, 1fr)`). This caused each of the three preview
images to render as a compressed vertical strip approximately 87px wide, producing
a broken visual presentation.

### Fix applied

- Removed the `edition-grid` CSS class and all three edition card components from the
  left column.
- Removed the `.hero-figure` section (hero infographic) from the left column. The hero
  image remains available as the `og:image` meta tag and as the fallback `onerror`
  target for all preview images.
- Added a new `.magazine-cover-preview` component in the left column:
  - Displays only `./previews/magazine-cover.webp`.
  - Uses `width: 100%; height: auto; aspect-ratio: 3/4; object-fit: contain` to
    preserve aspect ratio without cropping or stretching.
  - Adds a `max-height: 48rem` guard to prevent excessive vertical growth on tall viewports.
  - The entire image is clickable and routes to `./reflector-magazine.pdf`.
  - Includes a title, description, and three action buttons below the cover:
    **🎨 Read magazine**, **View inline ↓**, **🖨️ Print edition**.

### Edition preservation

The paper and print-edition previews and links are preserved elsewhere on the page:
- In the `.actions` quick-link bar (same left column, below the cover).
- In the "Publication navigation" list in the right column.
- In the "Read online" tabbed reader (Paper / Magazine / Print Edition tabs).
- In the magazine-callout banner at the top of `<main>`.

---

## Subtask 2 — Responsive Preview

The new `.magazine-cover-preview img` styles apply across all breakpoints:

| Breakpoint | Behavior |
|---|---|
| Large desktop (≥ 900px) | Left column capped at 300px. Cover fills column width with `aspect-ratio: 3/4`. |
| Standard laptop (900px) | Same as desktop. Column breakpoint defined by `content-grid`. |
| Tablet / narrow (< 900px) | `content-grid` collapses to `1fr`. Cover fills the full available width. |
| Mobile portrait (< 760px) | Same single-column flow. Cover fills container with preserved ratio. |

The `object-fit: contain` value ensures the full magazine cover is always visible
with no cropping, even when the container dimensions do not match the native 3:4 ratio
exactly.

The `.magazine-cover-actions` uses `flex-wrap: wrap` to allow buttons to reflow
cleanly on narrow containers.

---

## Subtask 3 — Preview Generation and Manifest Mapping

### Expected mapping

| Preview asset | Maps to |
|---|---|
| `./previews/paper-cover.webp` | `reflector.pdf` |
| `./previews/magazine-cover.webp` | `reflector-magazine.pdf` |
| `./previews/print-cover.webp` | `reflector-magazine-print.pdf` |

### Verification

- The `magazine-cover.webp` is the only preview rendered in the primary left-column
  preview area.
- The `paper-cover.webp` and `print-cover.webp` are no longer displayed in the same
  visual stack as the magazine cover.
- All preview images include `onerror` fallback to `./figures/hero.png` to handle
  gracefully when previews have not yet been generated.
- No CSS loop or JS loop substitutes multiple previews into the left-column container.

---

## Subtask 4 — Final Landing-Page Polish

### Changes applied

| Area | Change |
|---|---|
| Content hierarchy | Magazine cover is now the primary left-column visual artifact. |
| Image sizing | `object-fit: contain` prevents cropping; `max-height: 48rem` prevents overflow. |
| Action grouping | Magazine cover card has its own three action buttons; `.actions` quick-links remain. |
| Dark mode | `background: #0f1318` behind cover image ensures legibility against dark backgrounds. |
| Fallback behavior | `onerror` handler routes to hero.png for all cover images. |
| CSS cleanup | Removed unused `.hero-figure`, `.edition-grid`, `.edition-card*` styles. |
| Responsive CSS | Removed superseded `.edition-grid { grid-template-columns: 1fr }` breakpoint. |
| JavaScript | Added `view-magazine-inline-left` button listener in the left column. |

### Preserved

- Paper remains the canonical research artifact (right column, publication navigation).
- Print edition remains accessible via quick-links and reader tabs.
- Magazine-callout banner at top of `<main>` is unchanged.
- Tabbed reader (Paper / Magazine / Print) is unchanged.
- All PDF links and DOI references are unchanged.
- JavaScript `publication.json` dynamic loading is unchanged.
- Footer is unchanged.

---

## Acceptance criteria status

| Criterion | Status |
|---|---|
| Only the magazine cover is displayed as the primary left-column preview | ✅ |
| The full magazine cover fits naturally within the column | ✅ |
| The preview remains correct across desktop, tablet, and mobile layouts | ✅ |
| Paper and print-edition access remain available elsewhere | ✅ |
| Generated previews map to the correct publication artifacts | ✅ |
| No preview is stretched, cropped incorrectly, or compressed into a vertical strip | ✅ |
| The landing page receives a final restrained polish pass | ✅ |

---

## Files modified

| File | Change |
|---|---|
| `docs/index.html` | Replace edition-grid + hero-figure with magazine-cover-preview component |
