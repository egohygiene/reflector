#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Publication Template Contributors
# SPDX-License-Identifier: Apache-2.0
"""Validate publication metadata consistency across all surfaces.

Usage
-----
    python scripts/validate-metadata.py

Checks that:
  - VERSION is valid semver
  - All version surfaces match VERSION
  - All title surfaces match metadata/publication.yaml title.full
  - All ORCID surfaces match metadata/authors.yaml authors[0].orcid
  - Required metadata fields are present

Exits 0 when all checks pass, 1 when any check fails.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml


SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
DOI_PATTERN = re.compile(r"^10\.\d{4,9}/[-._;()/:A-Z0-9]+$", re.IGNORECASE)
MISSING = object()


def load_json(path: Path) -> dict | None:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        log_error(f"Missing required metadata file: {path}.")
    except json.JSONDecodeError as error:
        log_error(f"Invalid JSON in {path}: {error}.")
    return None


def load_yaml(path: Path) -> dict | None:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except FileNotFoundError:
        log_error(f"Missing required metadata file: {path}.")
        return None
    except yaml.YAMLError as error:
        log_error(f"Invalid YAML in {path}: {error}.")
        return None
    if not isinstance(data, dict):
        log_error(f"Expected mapping at root of {path}.")
        return None
    return data


def load_latex_title(path: Path) -> str | None:
    """Extract the assembled full title from a LaTeX title config file.

    Reads \\papertitlemain and \\papertitlesubtitle definitions and assembles
    the full title as ``<main>: <subtitle>`` without requiring a live TeX run.
    """
    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        log_error(f"Missing required title config: {path}.")
        return None

    def extract_command(name: str) -> str | None:
        pattern = re.compile(
            rf"\\newcommand{{\\{name}}}{{%\n\s*(.*?)%\n}}",
            re.DOTALL,
        )
        match = pattern.search(content)
        if not match:
            return None
        return " ".join(match.group(1).split())

    main = extract_command("papertitlemain")
    subtitle = extract_command("papertitlesubtitle")
    if main is None or subtitle is None:
        log_error(
            f"Could not parse \\papertitlemain or \\papertitlesubtitle in {path}."
        )
        return None
    return f"{main}: {subtitle}"


def log_error(message: str) -> None:
    print(f"[metadata] {message}", file=sys.stderr)


def _normalise_title(value: object) -> object:
    """Collapse multi-line YAML title strings to a single normalised line."""
    if value is MISSING or not isinstance(value, str):
        return value
    return " ".join(value.split())


def _extract_citation_orcid(citation: dict) -> object:
    """Extract the bare ORCID identifier from CITATION.cff authors[0]."""
    authors = citation.get("authors", [])
    if not isinstance(authors, list) or not authors:
        return MISSING
    orcid_url = authors[0].get("orcid", MISSING)
    if orcid_url is MISSING or not isinstance(orcid_url, str):
        return MISSING
    prefix = "https://orcid.org/"
    if orcid_url.startswith(prefix):
        return orcid_url[len(prefix):]
    return orcid_url


def _extract_zenodo_orcid(zenodo: dict) -> object:
    """Extract the bare ORCID identifier from .zenodo.json creators[0]."""
    creators = zenodo.get("creators", [])
    if not isinstance(creators, list) or not creators:
        return MISSING
    return creators[0].get("orcid", MISSING)


def _extract_codemeta_orcid(codemeta: dict) -> object:
    """Extract the bare ORCID identifier from codemeta.json author[0].@id."""
    authors = codemeta.get("author", [])
    if not isinstance(authors, list) or not authors:
        return MISSING
    author_id = authors[0].get("@id", MISSING)
    if author_id is MISSING or not isinstance(author_id, str):
        return MISSING
    prefix = "https://orcid.org/"
    if author_id.startswith(prefix):
        return author_id[len(prefix):]
    return author_id


def _normalise_doi(value: object) -> object:
    if value is MISSING or value is None:
        return MISSING
    if not isinstance(value, str):
        return value
    doi = value.strip()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if doi.lower().startswith(prefix):
            doi = doi[len(prefix):]
            break
    return doi


def main() -> int:
    repository_root = Path(__file__).resolve().parent.parent

    # ---------------------------------------------------------------------------
    # Read canonical VERSION
    # ---------------------------------------------------------------------------

    version_path = repository_root / "VERSION"
    try:
        version = version_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        log_error(f"Missing required file: {version_path}.")
        return 1
    if not SEMVER_PATTERN.fullmatch(version):
        log_error(f"VERSION must be MAJOR.MINOR.PATCH, got '{version}'.")
        return 1

    # ---------------------------------------------------------------------------
    # Load canonical metadata sources
    # ---------------------------------------------------------------------------

    meta_publication = load_yaml(repository_root / "metadata" / "publication.yaml")
    meta_authors = load_yaml(repository_root / "metadata" / "authors.yaml")
    if meta_publication is None or meta_authors is None:
        return 1

    # ---------------------------------------------------------------------------
    # Derive canonical title and ORCID from metadata sources
    # ---------------------------------------------------------------------------

    title_block = meta_publication.get("title")
    canonical_title_full = (
        title_block.get("full", MISSING) if isinstance(title_block, dict) else MISSING
    )
    if canonical_title_full is MISSING:
        log_error("Missing required field: metadata/publication.yaml title.full.")
        return 1
    canonical_title_full = _normalise_title(canonical_title_full)

    _raw_authors = meta_authors.get("authors")
    canonical_authors = _raw_authors if isinstance(_raw_authors, list) else []
    if not canonical_authors:
        log_error("metadata/authors.yaml authors list is missing or empty.")
        return 1
    canonical_orcid = canonical_authors[0].get("orcid", MISSING)
    if canonical_orcid is MISSING:
        log_error("metadata/authors.yaml authors[0].orcid is missing.")
        return 1
    canonical_orcid = str(canonical_orcid)

    has_error = False

    # ---------------------------------------------------------------------------
    # Version consistency: metadata/publication.yaml
    # ---------------------------------------------------------------------------

    canonical_version = meta_publication.get("version", MISSING)
    if canonical_version is MISSING:
        log_error("Missing required field: metadata/publication.yaml version.")
        return 1
    if str(canonical_version) != version:
        log_error(
            f"metadata/publication.yaml version must equal VERSION ('{version}'), "
            f"found '{canonical_version}'."
        )
        return 1

    # ---------------------------------------------------------------------------
    # Load downstream metadata surfaces
    # ---------------------------------------------------------------------------

    publication = load_json(repository_root / "publication.json")
    release_manifest = load_json(repository_root / "release-manifest.json")
    citation = load_yaml(repository_root / "CITATION.cff")
    zenodo = load_json(repository_root / ".zenodo.json")
    codemeta = load_json(repository_root / "codemeta.json")
    if any(
        item is None
        for item in (publication, release_manifest, citation, zenodo, codemeta)
    ):
        return 1

    # ---------------------------------------------------------------------------
    # Version consistency checks
    # ---------------------------------------------------------------------------

    version_checks = [
        ("publication.json.version", publication.get("version", MISSING), version),
        ("publication.json.release_tag", publication.get("release_tag", MISSING), f"v{version}"),
        ("release-manifest.json.current_version", release_manifest.get("current_version", MISSING), version),
        ("CITATION.cff.version", citation.get("version", MISSING), version),
        (".zenodo.json.version", zenodo.get("version", MISSING), version),
        ("codemeta.json.version", codemeta.get("version", MISSING), version),
    ]

    for name, actual_value, expected in version_checks:
        if actual_value is MISSING:
            has_error = True
            log_error(f"Missing required metadata field: {name}.")
            continue
        if str(actual_value) != str(expected):
            has_error = True
            log_error(
                f"{name} must equal '{expected}' (found '{actual_value}')."
            )

    # ---------------------------------------------------------------------------
    # Title consistency checks
    # ---------------------------------------------------------------------------

    latex_title = load_latex_title(repository_root / "paper" / "config" / "title.tex")
    if latex_title is None:
        has_error = True
    elif _normalise_title(latex_title) != canonical_title_full:
        has_error = True
        log_error(
            f"paper/config/title.tex title does not match canonical title.\n"
            f"  expected: '{canonical_title_full}'\n"
            f"  found:    '{_normalise_title(latex_title)}'"
        )

    title_checks = [
        ("CITATION.cff.title", _normalise_title(citation.get("title", MISSING))),
        (".zenodo.json.title", zenodo.get("title", MISSING)),
        ("codemeta.json.name", _normalise_title(codemeta.get("name", MISSING))),
        (
            "publication.json.title.full",
            _normalise_title(publication.get("title", {}).get("full", MISSING)),
        ),
    ]

    for name, actual_title in title_checks:
        if actual_title is MISSING:
            has_error = True
            log_error(f"Missing required title field: {name}.")
            continue
        if _normalise_title(actual_title) != canonical_title_full:
            has_error = True
            log_error(
                f"{name} does not match canonical title.\n"
                f"  expected: '{canonical_title_full}'\n"
                f"  found:    '{_normalise_title(actual_title)}'"
            )

    # ---------------------------------------------------------------------------
    # ORCID consistency checks
    # ---------------------------------------------------------------------------

    orcid_checks = [
        ("CITATION.cff.authors[0].orcid", _extract_citation_orcid(citation)),
        (".zenodo.json.creators[0].orcid", _extract_zenodo_orcid(zenodo)),
        ("codemeta.json.author[0].@id", _extract_codemeta_orcid(codemeta)),
    ]

    for name, actual_orcid in orcid_checks:
        if actual_orcid is MISSING:
            has_error = True
            log_error(f"Missing required ORCID field: {name}.")
            continue
        if str(actual_orcid) != canonical_orcid:
            has_error = True
            log_error(
                f"{name} does not match canonical ORCID.\n"
                f"  expected: '{canonical_orcid}'\n"
                f"  found:    '{actual_orcid}'"
            )

    # ---------------------------------------------------------------------------
    # DOI consistency (warn only when DOIs are present)
    # ---------------------------------------------------------------------------

    publication_identifiers = meta_publication.get("identifiers", {})
    canonical_doi = (
        _normalise_doi(publication_identifiers.get("doi", MISSING))
        if isinstance(publication_identifiers, dict)
        else MISSING
    )

    if canonical_doi is not MISSING:
        zenodo_doi = _normalise_doi(zenodo.get("doi", MISSING))
        citation_doi = citation.get("doi", MISSING)
        doi_checks = [
            (".zenodo.json.doi", zenodo_doi),
            ("CITATION.cff.doi", _normalise_doi(citation_doi)),
        ]
        for name, actual_doi in doi_checks:
            if actual_doi is MISSING:
                continue  # Optional — not required before formal publication
            if actual_doi != canonical_doi:
                has_error = True
                log_error(
                    f"{name} does not match canonical DOI.\n"
                    f"  expected: '{canonical_doi}'\n"
                    f"  found:    '{actual_doi}'"
                )

    # ---------------------------------------------------------------------------
    # Repository URL and artifact consistency
    # ---------------------------------------------------------------------------

    canonical_repository_url = meta_publication.get("repository_url", MISSING)
    canonical_pages_url = meta_publication.get("pages_url", MISSING)
    repository_checks = [
        (
            "publication.json.repository_url",
            publication.get("repository_url", MISSING),
            canonical_repository_url,
        ),
        (
            "publication.json.pages_url",
            publication.get("pages_url", MISSING),
            canonical_pages_url,
        ),
        (
            "CITATION.cff.repository-code",
            citation.get("repository-code", MISSING),
            canonical_repository_url,
        ),
        (
            "codemeta.json.codeRepository",
            codemeta.get("codeRepository", MISSING),
            canonical_repository_url,
        ),
        (
            "codemeta.json.url",
            codemeta.get("url", MISSING),
            canonical_pages_url,
        ),
    ]
    for name, actual_url, expected_url in repository_checks:
        if expected_url is MISSING:
            has_error = True
            log_error(f"Missing canonical URL field for {name}.")
            continue
        if actual_url is MISSING:
            has_error = True
            log_error(f"Missing required URL field: {name}.")
            continue
        if actual_url != expected_url:
            has_error = True
            log_error(
                f"{name} does not match canonical URL.\n"
                f"  expected: '{expected_url}'\n"
                f"  found:    '{actual_url}'"
            )

    canonical_slug = meta_publication.get("slug", MISSING)
    expected_pdf_name = f"{canonical_slug}.pdf" if canonical_slug is not MISSING else MISSING
    actual_pdf_name = publication.get("artifacts", {}).get("paper", {}).get("pdf", MISSING)
    if canonical_slug is MISSING:
        has_error = True
        log_error("metadata/publication.yaml slug is missing.")
    elif actual_pdf_name is MISSING:
        has_error = True
        log_error("publication.json.artifacts.paper.pdf is missing.")
    elif actual_pdf_name != expected_pdf_name:
        has_error = True
        log_error(
            "publication.json.artifacts.paper.pdf does not match the canonical slug.\n"
            f"  expected: '{expected_pdf_name}'\n"
            f"  found:    '{actual_pdf_name}'"
        )

    # ---------------------------------------------------------------------------
    # Result
    # ---------------------------------------------------------------------------

    if has_error:
        log_error("Metadata validation failed. See errors above.")
        return 1

    print("[metadata] All metadata surfaces are consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
