#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml


SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
MISSING = object()

# Canonical paper title — single source of truth for title consistency checks.
# Must match the value defined in paper/config/title.tex (\papertitlefull).
CANONICAL_TITLE = (
    "reflector: reflective synchronization systems for recursive AI-assisted software engineering"
)


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
    """Extract the \\papertitlefull expansion from a LaTeX title config file.

    Reads \\papertitlemain and \\papertitlesubtitle definitions and assembles
    the full title as ``<main>: <subtitle>`` so that the Python representation
    matches the LaTeX \\papertitlefull macro without requiring a live TeX run.
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
    """Collapse multi-line YAML title strings to a single normalised line.

    YAML ``>-`` block scalars fold newlines into spaces, but the resulting
    string may still contain extra internal whitespace.  This helper collapses
    any run of whitespace to a single space so that the comparison against the
    canonical title is whitespace-agnostic.
    """
    if value is MISSING or not isinstance(value, str):
        return value
    return " ".join(value.split())


def main() -> int:
    repository_root = Path(__file__).resolve().parent.parent

    version_path = repository_root / "VERSION"
    try:
        version = version_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        log_error(f"Missing required metadata file: {version_path}.")
        return 1
    if not SEMVER_PATTERN.fullmatch(version):
        log_error(f"VERSION must be semantic version MAJOR.MINOR.PATCH, got '{version}'.")
        return 1

    publication = load_json(repository_root / "publication.json")
    release_manifest = load_json(repository_root / "release-manifest.json")
    release_please_manifest = load_json(repository_root / ".release-please-manifest.json")
    citation = load_yaml(repository_root / "CITATION.cff")
    zenodo = load_json(repository_root / ".zenodo.json")
    readme_json = load_json(repository_root / "paper" / "00README.json")
    if any(
        item is None
        for item in (publication, release_manifest, release_please_manifest, citation, zenodo, readme_json)
    ):
        return 1

    checks = [
        ("publication.json.version", publication.get("version", MISSING)),
        ("publication.json.release_tag", publication.get("release_tag", MISSING)),
        ("release-manifest.json.current_version", release_manifest.get("current_version", MISSING)),
        (".release-please-manifest.json['.']", release_please_manifest.get(".", MISSING)),
        ("CITATION.cff.version", citation.get("version", MISSING)),
    ]

    expected_values = {
        "publication.json.release_tag": f"v{version}",
    }

    has_error = False
    for name, actual_value in checks:
        if actual_value is MISSING:
            has_error = True
            log_error(f"Missing required metadata field: {name}.")
            continue

        expected = expected_values.get(name, version)
        if actual_value != expected:
            has_error = True
            print(
                f"[metadata] {name} must equal '{expected}' (found '{actual_value}').",
                file=sys.stderr,
            )

    # ---------------------------------------------------------------------------
    # Title consistency — every metadata surface must carry the canonical title.
    # ---------------------------------------------------------------------------

    latex_title = load_latex_title(repository_root / "paper" / "config" / "title.tex")
    if latex_title is None:
        has_error = True
    elif latex_title != CANONICAL_TITLE:
        has_error = True
        log_error(
            f"paper/config/title.tex title does not match canonical title.\n"
            f"  expected: '{CANONICAL_TITLE}'\n"
            f"  found:    '{latex_title}'"
        )

    title_checks = [
        ("CITATION.cff.title", _normalise_title(citation.get("title", MISSING))),
        (".zenodo.json.title", zenodo.get("title", MISSING)),
        ("paper/00README.json.publication.title", readme_json.get("publication", {}).get("title", MISSING)),
    ]

    for name, actual_title in title_checks:
        if actual_title is MISSING:
            has_error = True
            log_error(f"Missing required title field: {name}.")
            continue
        if actual_title != CANONICAL_TITLE:
            has_error = True
            log_error(
                f"{name} does not match canonical title.\n"
                f"  expected: '{CANONICAL_TITLE}'\n"
                f"  found:    '{actual_title}'"
            )

    if has_error:
        return 1

    print("[metadata] metadata validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
