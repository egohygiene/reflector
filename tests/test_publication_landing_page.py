# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pathlib import Path


def test_landing_page_uses_generated_previews_for_social_cards_and_editions() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    html = (repo_root / "docs" / "index.html").read_text(encoding="utf-8")

    assert "previews/paper-cover.webp" in html
    assert "previews/magazine-cover.webp" in html
    assert "previews/print-cover.webp" in html
    assert 'property="og:image"' in html
    assert 'name="twitter:image"' in html


def test_landing_page_exposes_breadcrumbs_history_and_manifest_hydration() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    html = (repo_root / "docs" / "index.html").read_text(encoding="utf-8")

    assert 'aria-label="Breadcrumb"' in html
    assert "Publication history" in html
    assert 'id="status-display"' in html
    assert 'id="version-display"' in html
    assert 'id="build-display"' in html
    assert "fetch('./publication.json')" in html
