# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pathlib import Path


def test_landing_page_uses_generated_previews_for_social_cards_and_editions() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    html = (repo_root / "docs" / "index.html").read_text(encoding="utf-8")

    # paper-cover.webp is used in social card og:image meta tags
    assert "previews/paper-cover.webp" in html
    # magazine-cover.webp is the primary left-column preview
    assert "previews/magazine-cover.webp" in html
    # print-cover.webp is intentionally not displayed as a preview image;
    # the print edition remains accessible via PDF links
    assert "previews/print-cover.webp" not in html
    # social card meta tags present
    assert 'property="og:image"' in html
    assert 'name="twitter:image"' in html
    # print edition PDF links are preserved elsewhere on the page
    assert "reflector-magazine-print.pdf" in html


def test_landing_page_exposes_canonical_accessible_progressive_enhancement() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    html = (repo_root / "docs" / "index.html").read_text(encoding="utf-8")

    assert '<link rel="canonical" href="https://reflector.egohygiene.io/">' in html
    assert '<meta property="og:url" content="https://reflector.egohygiene.io/">' in html
    assert '<a class="skip-link" href="#content">' in html
    assert '<main id="content" tabindex="-1">' in html
    assert 'data-publication-manifest="./publication.json"' in html
    assert 'data-publication-status>Draft<' in html
    assert 'data-publication-version>v0.1.2<' in html
    assert '<script src="./assets/site.js" defer></script>' in html


def test_publication_routes_are_first_class_surfaces() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    expected_routes = {
        "paper/index.html": "https://reflector.egohygiene.io/paper/",
        "magazine/index.html": "https://reflector.egohygiene.io/magazine/",
        "magazine/print/index.html": "https://reflector.egohygiene.io/magazine/print/",
        "downloads/index.html": "https://reflector.egohygiene.io/downloads/",
    }

    for relative_path, canonical_url in expected_routes.items():
        html = (repo_root / "docs" / relative_path).read_text(encoding="utf-8")
        assert f'<link rel="canonical" href="{canonical_url}">' in html
        assert f'<meta property="og:url" content="{canonical_url}">' in html
        assert '<a class="skip-link" href="#content">' in html
        assert '<main id="content" tabindex="-1">' in html
        assert "assets/site.js" in html
