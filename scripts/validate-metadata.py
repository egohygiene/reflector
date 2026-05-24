#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml


SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def fail(message: str) -> int:
    print(f"[metadata] {message}", file=sys.stderr)
    return 1


def main() -> int:
    repository_root = Path(__file__).resolve().parent.parent

    version_path = repository_root / "VERSION"
    version = version_path.read_text(encoding="utf-8").strip()
    if not SEMVER_PATTERN.fullmatch(version):
        return fail(f"VERSION must be semantic version MAJOR.MINOR.PATCH, got '{version}'.")

    publication = load_json(repository_root / "publication.json")
    release_manifest = load_json(repository_root / "release-manifest.json")
    release_please_manifest = load_json(repository_root / ".release-please-manifest.json")

    with (repository_root / "CITATION.cff").open("r", encoding="utf-8") as handle:
        citation = yaml.safe_load(handle)

    checks = [
        ("publication.json.version", publication.get("version")),
        ("publication.json.release_tag", publication.get("release_tag")),
        ("release-manifest.json.current_version", release_manifest.get("current_version")),
        (".release-please-manifest.json['.']", release_please_manifest.get(".")),
        ("CITATION.cff.version", citation.get("version")),
    ]

    expected_values = {
        "publication.json.release_tag": f"v{version}",
    }

    has_error = False
    for name, actual_value in checks:
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
