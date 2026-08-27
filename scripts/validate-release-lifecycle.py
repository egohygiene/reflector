#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml


SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
REQUIRED_RELEASE_WORKFLOW_TOKENS = (
    "python scripts/validate-release-lifecycle.py",
    "python scripts/validate-metadata.py",
    "Create GitHub Release",
    "checksums.txt",
    "release-manifest.json",
    "zenodo-readiness.md",
)
REQUIRED_TAG_WORKFLOW_TOKENS = (
    "VERSION",
    "metadata/publication.yaml",
    "git tag -a",
    "git push origin",
)
REQUIRED_PUBLICATION_WORKFLOW_TOKENS = (
    "python scripts/validate-metadata.py",
    "python scripts/validate-release-lifecycle.py",
    "Create GitHub Release",
    "checksums.txt",
    "release-manifest.json",
    "zenodo-readiness.md",
    "reflector-arxiv",
    "GitHub Pages deployment is asynchronous",
    "publication.json",
    "figures/hero.png",
)
COMMON_PAGES_VALIDATION_TOKENS = (
    "ROUTES=(",
    "validate_clean_value() {",
    "printf 'Checking <%s>\\n' \"${url}\"",
    "printf 'Shell-escaped URL: %q\\n' \"${url}\"",
)
COMMON_PAGES_VALIDATION_ERROR_TOKENS = (
    "Malformed validation base URL",
    "Malformed validation URL",
    "must start with https://",
    'validate_clean_value "route" "${route}"',
)
REQUIRED_PAGES_WORKFLOW_TOKENS = (
    "pull_request:",
    'python3 "scripts/stage-pages.py"',
    '"_site/publication.json"',
    'cmp --silent "publication.json" "_site/publication.json"',
    'sha256sum --check --strict "SHA256SUMS"',
    "SOURCE_DATE_EPOCH",
    "metadata/releases",
    "checksums_asset",
    "site.json?revision=",
    "reflector.pdf",
    "reflector-magazine.pdf",
    "reflector-magazine-print.pdf",
    "github.event_name != 'pull_request'",
    "pages: write",
    "id-token: write",
    'rm --force "_site/.reflector-pages-owned"',
    '"_fallback-routes.tsv"',
    "actions/deploy-pages@cd2ce8fcbc39b97be8ca5fce6e763baed58fa128",
)
REQUIRED_TEMPLATE_PAGES_WORKFLOW_TOKENS = (
    'print(manifest[\'slug\'])',
    *COMMON_PAGES_VALIDATION_TOKENS,
    *COMMON_PAGES_VALIDATION_ERROR_TOKENS,
)


def log_error(message: str) -> None:
    print(f"[release-lifecycle] {message}", file=sys.stderr)


def load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        log_error(f"Missing required file: {path}.")
    except json.JSONDecodeError as error:
        log_error(f"Invalid JSON in {path}: {error}.")
    return None


def load_yaml(path: Path) -> dict | None:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        log_error(f"Missing required file: {path}.")
        return None
    except yaml.YAMLError as error:
        log_error(f"Invalid YAML in {path}: {error}.")
        return None
    if not isinstance(data, dict):
        log_error(f"Expected mapping at root of {path}.")
        return None
    return data


def validate_version_surfaces(repo_root: Path) -> bool:
    version_value = (repo_root / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER_PATTERN.fullmatch(version_value):
        log_error(f"VERSION must be semantic version MAJOR.MINOR.PATCH, got '{version_value}'.")
        return False

    publication_yaml = load_yaml(repo_root / "metadata" / "publication.yaml")
    publication_json = load_json(repo_root / "publication.json")
    release_baseline = load_json(
        repo_root / "metadata" / "releases" / f"v{version_value}.json"
    )
    release_manifest = load_json(repo_root / "release-manifest.json")
    release_please_manifest = load_json(repo_root / ".release-please-manifest.json")
    if any(
        item is None
        for item in (
            publication_yaml,
            publication_json,
            release_baseline,
            release_manifest,
            release_please_manifest,
        )
    ):
        return False

    checks: list[tuple[str, str | None, str]] = [
        ("metadata/publication.yaml.version", str(publication_yaml.get("version")), version_value),
        ("publication.json.version", str(publication_json.get("version")), version_value),
        ("publication.json.version_source", str(publication_json.get("version_source")), "VERSION"),
        ("publication.json.release_tag", str(publication_json.get("release_tag")), f"v{version_value}"),
        ("metadata/releases baseline.schema_version", str(release_baseline.get("schema_version")), "1.0.0"),
        ("metadata/releases baseline.release_tag", str(release_baseline.get("release_tag")), f"v{version_value}"),
        ("release-manifest.json.current_version", str(release_manifest.get("current_version")), version_value),
        (".release-please-manifest.json['.']", str(release_please_manifest.get(".")), version_value),
    ]

    valid = True
    for field_name, actual, expected in checks:
        if actual != expected:
            valid = False
            log_error(f"{field_name} must equal '{expected}' (found '{actual}').")

    release_commit = str(release_baseline.get("release_commit", ""))
    if not re.fullmatch(r"[0-9a-f]{40}", release_commit):
        valid = False
        log_error("metadata/releases baseline.release_commit must be a 40-character SHA.")

    checksums_asset = release_baseline.get("checksums_asset", {})
    if not isinstance(checksums_asset, dict) or checksums_asset.get("filename") != "checksums.txt":
        valid = False
        log_error("metadata/releases baseline must declare checksums.txt.")
    elif not re.fullmatch(r"[0-9a-f]{64}", str(checksums_asset.get("sha256", ""))):
        valid = False
        log_error("metadata/releases checksums.txt digest must be a SHA-256 value.")

    expected_artifacts = {
        "reflector.pdf",
        "reflector-magazine.pdf",
        "reflector-magazine-print.pdf",
    }
    artifacts = release_baseline.get("artifacts", {})
    if not isinstance(artifacts, dict) or set(artifacts) != expected_artifacts:
        valid = False
        log_error("metadata/releases baseline must pin all three publication artifacts exactly.")
    else:
        for filename, record in artifacts.items():
            digest = record.get("sha256", "") if isinstance(record, dict) else ""
            size_bytes = record.get("size_bytes", 0) if isinstance(record, dict) else 0
            if not re.fullmatch(r"[0-9a-f]{64}", str(digest)):
                valid = False
                log_error(f"metadata/releases baseline digest is invalid for {filename}.")
            if not isinstance(size_bytes, int) or size_bytes <= 0:
                valid = False
                log_error(f"metadata/releases baseline size is invalid for {filename}.")
    return valid


def validate_workflow_contracts(repo_root: Path) -> bool:
    release_workflow_path = repo_root / ".github" / "workflows" / "release-paper.yml"
    tag_workflow_path = repo_root / ".github" / "workflows" / "release-tag.yml"
    publication_workflow_path = repo_root / ".github" / "workflows" / "publication.yml"
    pages_workflow_path = repo_root / ".github" / "workflows" / "pages.yml"
    template_pages_workflow_path = repo_root / "template" / ".github" / "workflows" / "pages.yml"

    try:
        release_workflow_text = release_workflow_path.read_text(encoding="utf-8")
        tag_workflow_text = tag_workflow_path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        log_error(f"Missing required workflow file: {error.filename}.")
        return False

    valid = True
    for token in REQUIRED_RELEASE_WORKFLOW_TOKENS:
        if token not in release_workflow_text:
            valid = False
            log_error(f"release-paper.yml is missing required token: '{token}'.")

    for token in REQUIRED_TAG_WORKFLOW_TOKENS:
        if token not in tag_workflow_text:
            valid = False
            log_error(f"release-tag.yml is missing required token: '{token}'.")

    if publication_workflow_path.exists():
        publication_workflow_text = publication_workflow_path.read_text(encoding="utf-8")
        for token in REQUIRED_PUBLICATION_WORKFLOW_TOKENS:
            if token not in publication_workflow_text:
                valid = False
                log_error(f"publication.yml is missing required token: '{token}'.")

    if pages_workflow_path.exists():
        pages_workflow_text = pages_workflow_path.read_text(encoding="utf-8")
        for token in REQUIRED_PAGES_WORKFLOW_TOKENS:
            if token not in pages_workflow_text:
                valid = False
                log_error(f"pages.yml is missing required token: '{token}'.")

    if template_pages_workflow_path.exists():
        template_pages_workflow_text = template_pages_workflow_path.read_text(encoding="utf-8")
        for token in REQUIRED_TEMPLATE_PAGES_WORKFLOW_TOKENS:
            if token not in template_pages_workflow_text:
                valid = False
                log_error(f"template/.github/workflows/pages.yml is missing required token: '{token}'.")

    return valid


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    checks = [
        validate_version_surfaces(repo_root),
        validate_workflow_contracts(repo_root),
    ]
    if not all(checks):
        return 1
    print("[release-lifecycle] release lifecycle validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
