#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0

"""Build and stage Reflector's native artifacts for Beacon packaging."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

PROFILE_ID = "reflector-compatibility"
PROFILE_VERSION = "0.1.0"
LOCK_PATH = Path("dependencies/beacon.lock.json")

ARTIFACT_SOURCES = {
    "reflector.pdf": Path("paper/.cache/out/paper.pdf"),
    "reflector-magazine.pdf": Path("magazine/dist/reflector-magazine.pdf"),
    "reflector-magazine-print.pdf": Path("magazine/dist/reflector-magazine-print.pdf"),
    "publication.json": Path("publication.json"),
    "release-manifest.json": Path("release-manifest.json"),
}

NATIVE_COMMANDS = (
    ("python3", "scripts/validate-metadata.py"),
    ("bash", "scripts/build-paper.sh", "paper"),
    ("bash", "scripts/build-magazine.sh", "build-all"),
)


def parse_args() -> argparse.Namespace:
    """Parse Beacon execution-adapter arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def load_lock(project: Path) -> dict[str, Any]:
    """Load and validate the immutable Beacon dependency pin."""
    lock_path = project / LOCK_PATH
    data = json.loads(lock_path.read_text(encoding="utf-8"))
    expected = {
        "schema_version": 1,
        "cli_version": "0.1.0-alpha.1",
        "rust_toolchain": "1.97.1",
        "compatibility_profile": PROFILE_ID,
        "compatibility_profile_version": PROFILE_VERSION,
    }
    for key, value in expected.items():
        if data.get(key) != value:
            raise ValueError(f"{lock_path}: expected {key}={value!r}")

    revision = str(data.get("revision", ""))
    if len(revision) != 40 or any(character not in "0123456789abcdef" for character in revision):
        raise ValueError(f"{lock_path}: revision must be a lowercase 40-character Git SHA")
    if not str(data.get("repository", "")).startswith("https://github.com/"):
        raise ValueError(f"{lock_path}: repository must be an HTTPS GitHub URL")
    return data


def run(command: tuple[str, ...], project: Path) -> None:
    """Run one authoritative native validation or build command."""
    print(f"[reflector-compatibility] running: {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=project, check=True)


def git_output(project: Path, *arguments: str) -> str:
    """Return normalized Git output for provenance evidence."""
    result = subprocess.run(
        ("git", *arguments),
        cwd=project,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def sha256(path: Path) -> str:
    """Return a streaming SHA-256 digest for one artifact."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_pdf(path: Path) -> None:
    """Require a parseable, non-empty PDF with an inspectable font table."""
    if not path.is_file() or path.stat().st_size == 0:
        raise FileNotFoundError(f"missing or empty PDF: {path}")
    subprocess.run(("pdfinfo", str(path)), check=True, capture_output=True)
    subprocess.run(("pdffonts", str(path)), check=True, capture_output=True)


def copy_artifacts(project: Path, output: Path) -> list[dict[str, Any]]:
    """Copy native artifacts into Beacon's temporary, verified output directory."""
    output.mkdir(parents=True, exist_ok=False)
    records: list[dict[str, Any]] = []
    for artifact, source_relative in ARTIFACT_SOURCES.items():
        source = project / source_relative
        if artifact.endswith(".pdf"):
            verify_pdf(source)
        elif not source.is_file() or source.stat().st_size == 0:
            raise FileNotFoundError(f"missing or empty artifact: {source}")

        destination = output / artifact
        shutil.copyfile(source, destination)
        records.append(
            {
                "bytes": destination.stat().st_size,
                "path": artifact,
                "sha256": sha256(destination),
                "source": source_relative.as_posix(),
            }
        )
    return records


def compatibility_report(
    project: Path,
    lock: dict[str, Any],
    artifacts: list[dict[str, Any]],
) -> dict[str, Any]:
    """Create deterministic, reviewable compatibility and exception evidence."""
    return {
        "schema_version": 1,
        "profile": {"id": PROFILE_ID, "version": PROFILE_VERSION},
        "beacon_dependency": {
            "cli_version": lock["cli_version"],
            "repository": lock["repository"],
            "revision": lock["revision"],
            "rust_toolchain": lock["rust_toolchain"],
        },
        "reflector_source": {
            "dirty": bool(git_output(project, "status", "--porcelain", "--untracked-files=no")),
            "repository": "https://github.com/egohygiene/reflector",
            "revision": git_output(project, "rev-parse", "HEAD"),
        },
        "native_contracts": {
            "magazine": "scripts/build-magazine.sh build-all",
            "metadata": "scripts/validate-metadata.py",
            "paper": "scripts/build-paper.sh paper",
            "release": ".github/workflows/publication.yml",
            "web": ".github/workflows/pages.yml",
        },
        "compatibility": {
            "magazine": {
                "beacon_profile": "magazine",
                "status": "compatible-with-native-adapter",
                "variants": ["digital", "print"],
            },
            "publication_package": {
                "beacon_contract": "beacon-package.json plus SHA256SUMS",
                "status": "compatible",
            },
            "research_paper": {
                "beacon_profile": "research-paper",
                "status": "compatible-with-native-adapter",
            },
        },
        "exceptions": [
            {
                "id": "REF-B01",
                "owner": "reflector",
                "boundary": "Reflector retains its bespoke style, macros, biblatex, and biber build.",
                "follow_up": "Adopt shared components individually after visual and citation parity is proven.",
            },
            {
                "id": "REF-B02",
                "owner": "beacon",
                "boundary": "Reflector's magazine is image-first and preserves prompt-to-page provenance.",
                "follow_up": "Add a Beacon page-manifest import seam before replacing any native magazine source.",
            },
            {
                "id": "REF-B03",
                "owner": "reflector",
                "boundary": "Pages, DOI, Zenodo, arXiv, release names, and public URLs remain native.",
                "follow_up": "Evaluate transfer only in a separately scoped, migration-safe issue.",
            },
        ],
        "artifacts": artifacts,
        "side_effects": {
            "deploys": False,
            "publishes": False,
            "releases": False,
        },
    }


def main() -> int:
    """Run native contracts, stage artifacts, and emit compatibility evidence."""
    args = parse_args()
    project = args.project.resolve(strict=True)
    output = args.output.resolve(strict=False)
    if output.exists():
        raise FileExistsError(f"Beacon output must not exist before adapter execution: {output}")

    lock = load_lock(project)
    for command in NATIVE_COMMANDS:
        run(command, project)

    artifacts = copy_artifacts(project, output)
    report = compatibility_report(project, lock, artifacts)
    report_path = output / "compatibility-report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[reflector-compatibility] staged {len(artifacts) + 1} artifacts", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
