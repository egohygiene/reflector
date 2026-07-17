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


def test_landing_page_exposes_breadcrumbs_history_and_manifest_hydration() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    html = (repo_root / "docs" / "index.html").read_text(encoding="utf-8")

    assert 'aria-label="Breadcrumb"' in html
    assert "Publication history" in html
    assert 'id="status-display"' in html
    assert 'id="version-display"' in html
    assert 'id="build-display"' in html
    assert "fetch('./publication.json')" in html
