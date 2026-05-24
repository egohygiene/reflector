#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml


SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
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


def log_error(message: str) -> None:
    print(f"[metadata] {message}", file=sys.stderr)


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
    if any(item is None for item in (publication, release_manifest, release_please_manifest, citation)):
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

    if has_error:
        return 1

    print("[metadata] metadata validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
