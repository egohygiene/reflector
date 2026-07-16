#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Publication Template Contributors
# SPDX-License-Identifier: Apache-2.0
"""Propagate the canonical version from VERSION to all downstream metadata files.

Usage
-----
    python scripts/sync-version.py              # apply sync
    python scripts/sync-version.py --check      # verify without writing (dry run)
    python scripts/sync-version.py --version X.Y.Z  # override version

Every file listed in VERSION_SURFACES is validated to carry exactly the
version string (or derived tag) read from the VERSION file.  Running the
script with --check only reports drift without modifying any files;
running it without --check applies all updates atomically.

Surfaces updated
----------------
    metadata/publication.yaml   version
    CITATION.cff                version
    .zenodo.json                version
    codemeta.json               version
    publication.json            version + release_tag
    release-manifest.json       current_version
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml


SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


def log(message: str) -> None:
    print(f"[sync-version] {message}")


def log_error(message: str) -> None:
    print(f"[sync-version] ERROR: {message}", file=sys.stderr)


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------


def read_version(repo_root: Path, version_override: str | None) -> str | None:
    """Return the canonical version string."""
    if version_override is not None:
        version = version_override.strip()
    else:
        try:
            version = (repo_root / "VERSION").read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            log_error(f"Missing required file: {repo_root / 'VERSION'}.")
            return None
    if not SEMVER_PATTERN.fullmatch(version):
        log_error(f"Version must be MAJOR.MINOR.PATCH, got '{version}'.")
        return None
    return version


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        log_error(f"Missing required file: {path}.")
    except json.JSONDecodeError as exc:
        log_error(f"Invalid JSON in {path}: {exc}.")
    return None


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def load_yaml(path: Path) -> dict[str, Any] | None:
    try:
        text = path.read_text(encoding="utf-8")
        data = yaml.safe_load(text)
    except FileNotFoundError:
        log_error(f"Missing required file: {path}.")
        return None
    except yaml.YAMLError as exc:
        log_error(f"Invalid YAML in {path}: {exc}.")
        return None
    if not isinstance(data, dict):
        log_error(f"Expected mapping at root of {path}.")
        return None
    return data


# ---------------------------------------------------------------------------
# Per-file sync helpers
# ---------------------------------------------------------------------------


def _sync_publication_yaml(path: Path, version: str, check: bool) -> bool:
    """Sync metadata/publication.yaml version field."""
    data = load_yaml(path)
    if data is None:
        return False
    if str(data.get("version")) == version:
        return True
    if check:
        log(f"  DRIFT  {path.name}: version '{data.get('version')}' != '{version}'")
        return False

    text = path.read_text(encoding="utf-8")
    updated = re.sub(
        r'^(version:\s+)["\']?\d+\.\d+\.\d+["\']?',
        f'\\g<1>"{version}"',
        text,
        flags=re.MULTILINE,
        count=1,
    )
    if updated == text:
        log_error(f"Could not locate version field in {path}; skipping update.")
        return False
    path.write_text(updated, encoding="utf-8")
    log(f"  UPDATED {path.name}: version → '{version}'")
    return True


def _sync_citation_cff(path: Path, version: str, check: bool) -> bool:
    """Sync CITATION.cff version field."""
    data = load_yaml(path)
    if data is None:
        return False
    if str(data.get("version")) == version:
        return True
    if check:
        log(f"  DRIFT  {path.name}: version '{data.get('version')}' != '{version}'")
        return False

    text = path.read_text(encoding="utf-8")
    updated = re.sub(
        r'^(version:\s+)\S+',
        f'\\g<1>{version}',
        text,
        flags=re.MULTILINE,
        count=1,
    )
    if updated == text:
        log_error(f"Could not locate version field in {path}; skipping update.")
        return False
    path.write_text(updated, encoding="utf-8")
    log(f"  UPDATED {path.name}: version → '{version}'")
    return True


def _sync_zenodo_json(path: Path, version: str, check: bool) -> bool:
    """Sync .zenodo.json version field."""
    data = load_json(path)
    if data is None:
        return False
    if str(data.get("version")) == version:
        return True
    if check:
        log(f"  DRIFT  {path.name}: version '{data.get('version')}' != '{version}'")
        return False
    data["version"] = version
    write_json(path, data)
    log(f"  UPDATED {path.name}: version → '{version}'")
    return True


def _sync_codemeta_json(path: Path, version: str, check: bool) -> bool:
    """Sync codemeta.json version field."""
    data = load_json(path)
    if data is None:
        return False
    if str(data.get("version")) == version:
        return True
    if check:
        log(f"  DRIFT  {path.name}: version '{data.get('version')}' != '{version}'")
        return False
    data["version"] = version
    write_json(path, data)
    log(f"  UPDATED {path.name}: version → '{version}'")
    return True


def _sync_publication_json(path: Path, version: str, check: bool) -> bool:
    """Sync publication.json version and release_tag fields."""
    data = load_json(path)
    if data is None:
        return False
    tag = f"v{version}"
    current_version_ok = str(data.get("version")) == version
    current_tag_ok = str(data.get("release_tag")) == tag
    if current_version_ok and current_tag_ok:
        return True
    if check:
        if not current_version_ok:
            log(f"  DRIFT  {path.name}: version '{data.get('version')}' != '{version}'")
        if not current_tag_ok:
            log(f"  DRIFT  {path.name}: release_tag '{data.get('release_tag')}' != '{tag}'")
        return False
    data["version"] = version
    data["release_tag"] = tag
    write_json(path, data)
    log(f"  UPDATED {path.name}: version → '{version}', release_tag → '{tag}'")
    return True


def _sync_release_manifest_json(path: Path, version: str, check: bool) -> bool:
    """Sync release-manifest.json current_version field."""
    data = load_json(path)
    if data is None:
        return False
    if str(data.get("current_version")) == version:
        return True
    if check:
        log(f"  DRIFT  {path.name}: current_version '{data.get('current_version')}' != '{version}'")
        return False
    data["current_version"] = version
    write_json(path, data)
    log(f"  UPDATED {path.name}: current_version → '{version}'")
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Propagate the canonical version from VERSION to all downstream "
            "metadata files."
        )
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "Verify synchronization without writing any files. "
            "Exits 1 if any surface is out of date."
        ),
    )
    parser.add_argument(
        "--version",
        default=None,
        help=(
            "Override the version to sync instead of reading from the VERSION file. "
            "Must be MAJOR.MINOR.PATCH."
        ),
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help=(
            "Path to the repository root. "
            "Defaults to the parent of this script's directory."
        ),
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.repo_root is not None:
        repo_root = Path(args.repo_root).resolve()
    else:
        repo_root = Path(__file__).resolve().parent.parent
    check = args.check

    version = read_version(repo_root, args.version)
    if version is None:
        return 1

    mode = "CHECK" if check else "APPLY"
    log(f"{mode}: version = {version}")
    log("")

    surfaces = [
        (
            repo_root / "metadata" / "publication.yaml",
            _sync_publication_yaml,
        ),
        (
            repo_root / "CITATION.cff",
            _sync_citation_cff,
        ),
        (
            repo_root / ".zenodo.json",
            _sync_zenodo_json,
        ),
        (
            repo_root / "codemeta.json",
            _sync_codemeta_json,
        ),
        (
            repo_root / "publication.json",
            _sync_publication_json,
        ),
        (
            repo_root / "release-manifest.json",
            _sync_release_manifest_json,
        ),
    ]

    all_ok = True
    updated_count = 0
    for path, sync_fn in surfaces:
        result = sync_fn(path, version, check)
        if result is False and check:
            all_ok = False
        elif result is True:
            pass  # already in sync
        elif not check:
            updated_count += 1

    log("")
    if check:
        if all_ok:
            log("All version surfaces are synchronized.")
            return 0
        else:
            log_error(
                "Version drift detected. Run 'python scripts/sync-version.py' to fix."
            )
            return 1
    else:
        if updated_count == 0:
            log("All version surfaces already synchronized — no changes needed.")
        else:
            log(f"Synchronized {updated_count} surface(s).")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
