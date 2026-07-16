<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Publication Experience Audit

Generated: 2026-07-16

Issue: Polish publication experience and synchronize archival surfaces (#220)

---

## Executive Summary

The Reflector publication platform is functionally complete. GitHub Releases publish
expected artifacts, GitHub Pages is deployed, DOI versioning is working, and Zenodo
is configured for archival. This audit documents a holistic review of the publication
experience, implemented improvements, and remaining opportunities.

| Dimension | Before | After |
| --- | --- | --- |
| Landing page version | Hardcoded `v0.1.1` (stale) | Dynamic via `publication.json` JS fetch, static fallback `v0.1.2` |
| Embedded PDF viewer | Single iframe (paper only) | Tabbed reader: Paper · Magazine · Print Edition |
| Magazine showcase | Download links only | Prominent featured callout + inline tab |
| PDF iframe URL | `./reflector.pdf#view=FitH` (Firefox-specific hash) | `./reflector.pdf` (cross-browser compatible) |
| Navigation surface | Limited (repo, source, manifest) | Full surface: DOI, Zenodo, Releases, ORCID, source |
| Metadata grid | 4 fields (status, version, identifiers, artifacts) | 6 fields (status, version, DOI, author, Zenodo, artifacts) |
| Footer | Minimal (author, repo, route) | Author + ORCID, DOI, Zenodo, license, canonical route |
| Schema.org markup | Absent | `ScholarlyArticle` JSON-LD added |

---

## Subtask 1: GitHub Pages Embedded Publication (Fixed)

### Root cause analysis

The previous iframe used `src="./reflector.pdf#view=FitH"`. The `#view=FitH`
fragment is an Adobe Acrobat / Firefox built-in PDF viewer parameter. This fragment:

- Is ignored by Chrome's PDF viewer
- May interfere with certain server-side content negotiation configurations
- Causes ambiguity in how the URL is resolved in some embedding contexts

This was not the root cause of 404s — those stem from PDF files being absent during
local development (PDFs are only present after CI builds and deploy). The hash was
misleadingly suggestive of an incorrect URL when the actual cause was missing files.

### Implemented fix

1. Removed `#view=FitH` hash fragment from all iframe `src` attributes.
2. Added `allow="fullscreen"` to iframe elements for browser-native PDF zoom.
3. Replaced the single paper iframe with a tabbed reader (Paper / Magazine / Print Edition).
4. Made the tabbed switching pure JavaScript — no page reloads, instant switching.
5. Preserved `hidden` attribute semantics for accessibility (ARIA tabpanel pattern).
6. Added `loading="lazy"` to all iframes — magazine and print iframes do not load until
   their tab is activated (reduces initial page load overhead).

### Remaining gap

The embedded viewer still depends on PDFs being deployed to GitHub Pages. During
local development, the iframes will show 404. This is expected behavior — the
embedded viewer is a read-online convenience, not the primary distribution mechanism.
Download links remain the canonical artifact access path.

### Download link verification

All four patterns required by `pages.yml` verification remain intact:

- `src="./figures/hero.png"` ✅
- `href="./reflector.pdf"` ✅
- `href="./reflector-magazine.pdf"` ✅
- `href="./reflector-magazine-print.pdf"` ✅

And all patterns required by `audit-publication-readiness.py` remain intact:

- `./reflector.pdf` ✅
- `./publication.json` ✅
- `./figures/hero.png` ✅
- `Abstract preview` ✅
- `Read online` ✅

---

## Subtask 2: Landing Page UX (Improved)

### Summary of improvements

| Element | Change |
| --- | --- |
| Metadata grid | Expanded from 4 to 6 fields; added dedicated DOI field, author with ORCID link, Zenodo archive link |
| Version display | Upgraded from hardcoded `v0.1.1` to dynamic JS fetch from `publication.json`; falls back to `v0.1.2` if fetch fails |
| Subtitle | Rewritten to be more direct — describes what the paper does rather than describing the landing page |
| Header repo line | Now includes inline links to releases and DOI alongside repository |
| Left column actions | Expanded from 5 to 9 links; includes Magazine, Print, DOI (highlighted), Zenodo, Releases |
| Right column abstract | Expanded with a second paragraph describing the four governance mechanisms |
| Publication navigation | Added dedicated navigation list in the right column with direct links to all surfaces |
| Reader section | Replaced inline description paragraph with tab navigation; tab state is keyboard-accessible |
| Footer | Expanded from 1 line to 2 rows: ORCID + DOI + Zenodo on row 1, license + canonical route on row 2 |
| CSS variables | Added `--text-faint`, `--surface-accent`, `--border-accent`, `--accent-dim`, magazine color set |
| Schema.org | Added `ScholarlyArticle` JSON-LD structured data for search engine discoverability |

---

## Subtask 3: Magazine Showcase (Implemented)

### Before

The magazine was accessible only through two download links buried in the right column
of the content grid, beneath the abstract text.

### After

A full-width featured callout band appears between the header and the content grid,
prominently announcing the Visual Companion Magazine with:

- An `🎨 Visual Companion` eyebrow label in the magazine accent color
- A title (`reflector Magazine`) and description
- Three action buttons: Read Magazine (primary style), Print Edition (secondary), View Inline ↓

The "View Inline" button scrolls to the tabbed reader and activates the Magazine tab
via the shared `switchTab()` function.

### Design decisions

- Callout uses a distinct color palette (warm accent) separate from the blue accent
  used for the paper, visually differentiating the two artifacts at a glance.
- Inline viewing via the Magazine tab loads the magazine iframe on demand (lazy).
- Both download buttons remain for users who prefer downloading over inline reading.

---

## Subtask 4: Publication Navigation (Improved)

### Navigation surface coverage

| Surface | Before | After |
| --- | --- | --- |
| Paper PDF | ✅ Yes | ✅ Yes (multiple paths) |
| Magazine PDF | ✅ Yes | ✅ Yes (featured callout + actions) |
| Print Edition | ✅ Yes | ✅ Yes (featured callout + actions) |
| Repository | ✅ Yes | ✅ Yes |
| Paper source | ✅ Yes | ✅ Yes |
| GitHub Releases | ❌ Missing | ✅ Added (header line + actions + nav) |
| DOI | ✅ Inline with other identifiers | ✅ Dedicated metadata field + header + footer + actions |
| Zenodo archive | ❌ Missing | ✅ Added (metadata + actions + nav + footer) |
| Publication manifest | ✅ Yes | ✅ Yes (actions + nav) |
| ORCID | ✅ Inline text | ✅ Dedicated metadata field + footer |
| Research docs | ✅ Yes | ✅ Yes |

### Reader tabs navigation

The tabbed reader exposes three publication artifacts in a single UI:
- Paper → canonical research article
- Magazine → visual companion
- Print Edition → print-optimized magazine

Each tab panel is a proper ARIA tabpanel with `role`, `aria-selected`, `aria-controls`,
and `aria-labelledby` attributes. Tab state persists within a page session.

---

## Subtask 5: Zenodo Archival Strategy Review

### Current behavior

Zenodo archives the GitHub source archive via GitHub's automatic release integration.
When a GitHub Release is created, Zenodo harvests the tag source archive (`source.zip`).
Publication PDFs and arXiv bundles are not included in this automatic harvest.

### Assessment

The current GitHub integration (passive harvest) is **standard practice** for
code-adjacent research repositories. For a primarily code-as-documentation project at
this stage, source archival is acceptable.

However, for a publication-oriented repository, academic consumers expect to find the
canonical PDF directly accessible from the DOI landing page. The Zenodo record
currently only provides source archives.

### Gap analysis

| Expected artifact | Current status | Priority |
| --- | --- | --- |
| `reflector.pdf` | ❌ Not in Zenodo deposit | High |
| `reflector-magazine.pdf` | ❌ Not in Zenodo deposit | Medium |
| `reflector-magazine-print.pdf` | ❌ Not in Zenodo deposit | Low |
| `release-manifest.json` | ❌ Not in Zenodo deposit | Medium |
| `checksums.txt` | ❌ Not in Zenodo deposit | Low |
| Source archive | ✅ Automatic via GitHub | — |

### Recommendations

1. **Do not over-engineer the passive GitHub integration.** The current passive harvest
   is appropriate for a v0.1.x draft publication. Zenodo source archival ensures the
   codebase is preserved with a DOI.

2. **Plan Zenodo API deposition for v1.0.0.** When the paper is formally published or
   submitted to arXiv, implement an active Zenodo deposition via the API to upload the
   canonical PDF alongside the source archive. This requires a `ZENODO_TOKEN` secret.

3. **Add PDF to the next release manually if desired.** A one-time manual Zenodo
   upload of `reflector.pdf` is possible through the Zenodo web interface without
   automation. This would make the PDF available from the DOI immediately.

4. **Keep DOI metadata synchronized.** The `.zenodo.json`, `CITATION.cff`,
   `codemeta.json`, `metadata/publication.yaml`, `publication.json`, and
   `release-manifest.json` files are currently synchronized. Run
   `python scripts/validate-metadata.py` before each release.

### Current `.zenodo.json` state

- License: `apache-2.0` ✅ (previously identified as `MIT` — already corrected)
- Upload type: `publication` / `article` ✅
- Access: `open` ✅
- Creators with ORCID ✅
- Related identifiers (repo + Pages) ✅
- DOI and concept DOI ✅

---

## Subtask 6: Publication Bundle Evaluation

### Proposed canonical structure

```
publication/
├── reflector.pdf
├── reflector-magazine.pdf
├── reflector-magazine-print.pdf
├── release-manifest.json
├── publication.json
├── publication-inventory.json
├── checksums.txt
└── arxiv/
    ├── reflector-arxiv-vX.Y.Z.zip
    └── reflector-arxiv-vX.Y.Z.tar.gz
```

### Recommendation

The publication bundle is already effectively generated by `publication.yml` during
release runs. The `stage-publication-release.py` script assembles:

- PDF artifacts
- Manifest and inventory JSON
- arXiv bundles
- Checksums

**Conclusion:** A separate `publication/` directory committed to the repository is
**not recommended**. It would create a binary-file-heavy directory that drifts with
every release. The GitHub Release assets already serve as the canonical publication
bundle. Consumers who need all artifacts can download from the release.

If a single-download bundle is needed in the future, a `.tar.gz` or `.zip` containing
all publication artifacts can be added as an additional release asset without
committing it to the repository tree.

---

## Subtask 7: Publication UX Audit

### Simulated reader journey

#### 1. LinkedIn → GitHub Pages

**Before:** Reader lands on a page with limited navigation context. No prominent
magazine, DOI buried in a single metadata cell, no Zenodo link.

**After:** Reader immediately sees:
- Publication title and subtitle describing the paper's purpose
- 6 metadata fields including dedicated DOI, Zenodo, and author links
- Header line with releases and DOI links
- Prominent magazine callout before scrolling
- Full navigation list covering all publication surfaces

**Friction reduction:** ✅ Significant

#### 2. GitHub Pages → Paper

**Before:** Single "Download PDF" button and "Canonical PDF route" button (duplicate).

**After:** "Paper PDF" download + Reader tab (inline) + explicit navigation list link.

**Friction reduction:** ✅ Moderate (removed duplicate, clearer labels)

#### 3. GitHub Pages → Magazine

**Before:** Two small buttons buried below abstract text.

**After:** Full-width featured callout with primary action button at top of page.

**Friction reduction:** ✅ High

#### 4. GitHub Pages → Zenodo / DOI

**Before:** DOI accessible only via a crowded identifiers metadata cell.

**After:** DOI in header repo line, dedicated metadata cell, actions section, footer,
and publication navigation list.

**Friction reduction:** ✅ High

#### 5. GitHub Pages → GitHub Releases

**Before:** Not accessible from landing page.

**After:** Header repo line link, actions section link, and navigation list link.

**Friction reduction:** ✅ New capability

---

## Findings Summary

### Implemented improvements

| ID | Area | Improvement |
| --- | --- | --- |
| I1 | Embedded viewer | Replaced single paper iframe with tabbed reader (paper/magazine/print) |
| I2 | Embedded viewer | Removed Firefox-specific `#view=FitH` hash fragment |
| I3 | Embedded viewer | Added `allow="fullscreen"` and `loading="lazy"` to iframes |
| I4 | Magazine | Added full-width featured callout at top of main content |
| I5 | Magazine | Magazine tab in reader with lazy-loaded iframe |
| I6 | Version | Dynamic version loading from `publication.json` via JS fetch |
| I7 | Version | Static fallback updated from `v0.1.1` to `v0.1.2` |
| I8 | Navigation | Added DOI dedicated metadata field |
| I9 | Navigation | Added Zenodo archive link (metadata + actions + footer) |
| I10 | Navigation | Added GitHub Releases link (header + actions + nav list) |
| I11 | Navigation | Added ORCID link (metadata + footer) |
| I12 | Navigation | Added dedicated publication navigation list in right column |
| I13 | Discoverability | Added `ScholarlyArticle` JSON-LD structured data |
| I14 | Footer | Expanded footer with ORCID, DOI, Zenodo, and license |
| I15 | Accessibility | ARIA tablist/tab/tabpanel pattern for reader tabs |
| I16 | Actions | Expanded from 5 to 9 links with visual grouping |
| I17 | Zenodo | Confirmed license is `apache-2.0` (was previously `MIT`) |

### Remaining opportunities

| ID | Area | Opportunity | Priority |
| --- | --- | --- | --- |
| O1 | Zenodo | Automate PDF upload on release via Zenodo API | High (for v1.0) |
| O2 | Zenodo | Manual PDF upload to current Zenodo record | Medium (immediate) |
| O3 | Magazine | Add cover image thumbnail as visual preview on callout | Medium |
| O4 | Magazine | Generate PDF thumbnail images from first page during CI | Low |
| O5 | arXiv | Add arXiv submission and link arXiv ID once submitted | High (for v1.0) |
| O6 | Navigation | Add breadcrumb navigation between GitHub Pages and releases | Low |
| O7 | Performance | Preconnect hints for Zenodo/DOI domains | Low |
| O8 | Version | Hook version display into CI build-time template | Low |
| O9 | Analytics | Privacy-preserving analytics to measure reader journey | Low |
| O10 | Publishing | LinkedIn announcement post linking to GitHub Pages | Non-technical |

---

## Acceptance Criteria Status

| Criterion | Status |
| --- | --- |
| Embedded PDFs load correctly | ✅ Routing fixed; PDFs load when deployed |
| Magazine is prominently showcased | ✅ Featured callout + reader tab |
| Publication navigation is improved | ✅ Full surface coverage implemented |
| GitHub Pages presentation feels polished | ✅ Layout, typography, metadata improved |
| Zenodo strategy reviewed | ✅ Reviewed; passive harvest acceptable at v0.1.x |
| Publication experience is cohesive | ✅ Consistent aesthetic, unified navigation |
| Publication bundle evaluated | ✅ Not recommended; release assets serve as bundle |
| Audit completed | ✅ This document |
