#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate deterministic checksums and release manifest for a staged publication release."
    )
    parser.add_argument("--release-dir", required=True, help="Path to the staged release directory.")
    parser.add_argument("--version", required=True, help="Release version without the leading v.")
    parser.add_argument("--tag", required=True, help="Release tag (for example v0.1.0).")
    parser.add_argument("--paper-name", required=True, help="Canonical publication/project name.")
    parser.add_argument(
        "--repository",
        default="egohygiene/reflector",
        help="GitHub owner/repository used for generated URLs.",
    )
    parser.add_argument("--commit", default="", help="Git commit SHA for the release.")
    parser.add_argument(
        "--generated-at",
        default="",
        help="Explicit UTC timestamp for deterministic tests (default: current time).",
    )
    parser.add_argument(
        "--require",
        action="append",
        default=[],
        metavar="FILENAME",
        help="Required top-level artifact filename. May be provided multiple times.",
    )
    return parser


def fail(message: str) -> int:
    print(f"[publication-release] {message}", file=sys.stderr)
    return 1


def sha256_for_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def display_path(path: Path, root: Path) -> str:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    try:
        return resolved_path.relative_to(resolved_root).as_posix()
    except ValueError:
        return resolved_path.as_posix()


def validate_required_files(release_dir: Path, required_names: list[str]) -> dict[str, Path] | None:
    if len(required_names) != len(set(required_names)):
        duplicates = sorted({name for name in required_names if required_names.count(name) > 1})
        fail(f"Duplicate required artifact declarations: {', '.join(duplicates)}.")
        return None

    staged_files = {path.name: path for path in sorted(release_dir.iterdir()) if path.is_file()}
    required_paths: dict[str, Path] = {}

    for name in sorted(required_names):
        path = release_dir / name
        if not path.is_file():
            present_files = ", ".join(sorted(staged_files)) or "<none>"
            fail(
                "Missing required release artifact "
                f"'{name}'. Expected path: {path.resolve()}. "
                f"Release directory: {release_dir.resolve()}. "
                f"Present staged files: {present_files}."
            )
            return None
        required_paths[name] = path.resolve()

    return required_paths


def write_checksums(
    release_dir: Path,
    repo_root: Path,
    required_paths: dict[str, Path],
) -> tuple[Path, dict[str, str]]:
    checksums_path = release_dir / "checksums.txt"
    checksum_inventory = {
        name: sha256_for_file(path)
        for name, path in sorted(required_paths.items(), key=lambda item: item[0])
    }
    lines = [f"{checksum_inventory[name]}  {name}" for name in sorted(checksum_inventory)]
    checksums_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("[publication-release] checksums.txt generated:")
    for line in lines:
        print(f"  {line}")
    return checksums_path.resolve(), checksum_inventory


def write_manifest(
    release_dir: Path,
    repo_root: Path,
    version: str,
    tag: str,
    paper_name: str,
    repository: str,
    commit: str,
    generated_at: str,
    required_paths: dict[str, Path],
    checksums_path: Path,
    checksum_inventory: dict[str, str],
) -> Path:
    manifest_path = release_dir / "release-manifest.json"
    owner, repo = repository.split("/", 1)
    release_download_base = f"https://github.com/{repository}/releases/download/{tag}"

    artifacts = []
    for name in sorted(required_paths):
        path = required_paths[name]
        artifacts.append(
            {
                "filename": name,
                "path": display_path(path, repo_root),
                "size_bytes": path.stat().st_size,
                "sha256": checksum_inventory[name],
                "url": f"{release_download_base}/{name}",
            }
        )

    manifest = {
        "schema_version": "1.0.0",
        "project": paper_name,
        "version": version,
        "tag": tag,
        "commit": commit,
        "generated_at": generated_at,
        "release_dir": display_path(release_dir, repo_root),
        "repository": f"https://github.com/{repository}",
        "release_url": f"https://github.com/{repository}/releases/tag/{tag}",
        "pages_url": f"https://{owner}.github.io/{repo}/",
        "checksums": {
            "algorithm": "sha256",
            "path": display_path(checksums_path, repo_root),
            "entries": [
                {"filename": name, "sha256": checksum_inventory[name]}
                for name in sorted(checksum_inventory)
            ],
        },
        "artifacts": artifacts,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"[publication-release] release-manifest.json written to {manifest_path.resolve()}")
    return manifest_path.resolve()


def main() -> int:
    args = build_parser().parse_args()
    repo_root = Path.cwd().resolve()
    release_dir = Path(args.release_dir).resolve()
    if not release_dir.exists():
        return fail(f"Release directory does not exist: {release_dir}.")
    if not release_dir.is_dir():
        return fail(f"Release directory is not a directory: {release_dir}.")

    required_paths = validate_required_files(release_dir, args.require)
    if required_paths is None:
        return 1

    checksums_path, checksum_inventory = write_checksums(release_dir, repo_root, required_paths)
    generated_at = args.generated_at or datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest_path = write_manifest(
        release_dir=release_dir,
        repo_root=repo_root,
        version=args.version,
        tag=args.tag,
        paper_name=args.paper_name,
        repository=args.repository,
        commit=args.commit,
        generated_at=generated_at,
        required_paths=required_paths,
        checksums_path=checksums_path,
        checksum_inventory=checksum_inventory,
    )

    print("[publication-release] staged artifact inventory:")
    print(f"  release_dir={display_path(release_dir, repo_root)}")
    for name in sorted(required_paths):
        print(f"  - {display_path(required_paths[name], repo_root)}")
    print(f"  - {display_path(checksums_path, repo_root)}")
    print(f"  - {display_path(manifest_path, repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
