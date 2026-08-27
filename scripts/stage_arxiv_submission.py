#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Stage a deterministic, minimal arXiv submission from declared TeX inputs."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
import shutil
import sys
import tarfile
import tempfile
import zipfile
from collections import deque
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


DEFAULT_MAXIMUM_TOTAL_BYTES = 45_000_000
DEFAULT_MAXIMUM_FILE_BYTES = 10_000_000
ALLOWED_SOURCE_USAGES = {"toplevel", "include", "ignore"}
ALLOWED_SOURCE_EXTENSIONS = {
    ".bib",
    ".eps",
    ".jpeg",
    ".jpg",
    ".pdf",
    ".png",
    ".sty",
    ".tex",
}
GRAPHIC_EXTENSIONS = (".pdf", ".png", ".jpg", ".jpeg", ".eps")
INPUT_PATTERN = re.compile(r"\\(?:input|include)\s*\{([^}]+)\}")
BIBLIOGRAPHY_PATTERN = re.compile(r"\\(?:addbibresource|bibliography)\s*\{([^}]+)\}")
PACKAGE_PATTERN = re.compile(
    r"\\(?:usepackage|RequirePackage)(?:\s*\[[^\]]*\])?\s*\{([^}]+)\}"
)
GRAPHICS_PATTERN = re.compile(
    r"\\includegraphics(?:\s*\[[^\]]*\])?\s*\{([^}]+)\}"
)
GRAPHICSPATH_PATTERN = re.compile(
    r"\\graphicspath\s*\{((?:\s*\{[^{}]+\}\s*)+)\}",
    re.DOTALL,
)


class StageError(RuntimeError):
    """Raised when the canonical source cannot form a safe arXiv submission."""


@dataclass(frozen=True)
class StageResult:
    """Describe one materialized arXiv submission tree."""

    bundle_dir: Path
    files: tuple[PurePosixPath, ...]
    total_bytes: int
    dependency_paths: tuple[PurePosixPath, ...]


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Materialize the exact declared TeX dependency closure required for "
            "an arXiv submission."
        )
    )
    parser.add_argument(
        "--source-dir",
        default="paper",
        help="Canonical paper source directory containing 00README.json.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="New directory that will receive the staged arXiv source tree.",
    )
    parser.add_argument(
        "--zip-output",
        default="",
        help="Optional deterministic ZIP archive path written outside the staged tree.",
    )
    parser.add_argument(
        "--tar-output",
        default="",
        help="Optional deterministic TAR.GZ archive path written outside the staged tree.",
    )
    parser.add_argument(
        "--maximum-total-bytes",
        type=int,
        default=DEFAULT_MAXIMUM_TOTAL_BYTES,
        help="Maximum permitted staged source-tree size in bytes.",
    )
    parser.add_argument(
        "--maximum-file-bytes",
        type=int,
        default=DEFAULT_MAXIMUM_FILE_BYTES,
        help="Maximum permitted individual source-file size in bytes.",
    )
    return parser


def read_manifest(source_dir: Path) -> dict[str, Any]:
    """Load and validate the canonical arXiv source manifest."""

    manifest_path = source_dir / "00README.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise StageError(f"Missing required manifest: {manifest_path}.") from error
    except json.JSONDecodeError as error:
        raise StageError(f"Invalid JSON in {manifest_path}: {error}.") from error

    if not isinstance(manifest, dict):
        raise StageError(f"Manifest must be a JSON object: {manifest_path}.")
    if not isinstance(manifest.get("sources"), list):
        raise StageError("Manifest field 'sources' must be a JSON array.")
    return manifest


def normalize_relative_path(value: str, source_dir: Path) -> PurePosixPath:
    """Return one repository-safe relative source path."""

    if not value or value.strip() != value:
        raise StageError("Manifest source paths must be non-empty trimmed strings.")

    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or path == PurePosixPath("."):
        raise StageError(f"Manifest source path escapes the paper directory: {value!r}.")

    resolved_source = source_dir.resolve()
    candidate = (source_dir / Path(path)).resolve()
    try:
        candidate.relative_to(resolved_source)
    except ValueError as error:
        raise StageError(f"Manifest source path escapes the paper directory: {value!r}.") from error
    return path


def declared_source_paths(source_dir: Path, manifest: dict[str, Any]) -> tuple[PurePosixPath, ...]:
    """Return the unique included source paths declared by 00README.json."""

    paths: list[PurePosixPath] = []
    seen: set[PurePosixPath] = set()
    toplevel_paths: list[PurePosixPath] = []

    for source in manifest["sources"]:
        if not isinstance(source, dict):
            raise StageError("Each manifest source entry must be a JSON object.")

        usage = str(source.get("usage", "")).strip()
        if usage not in ALLOWED_SOURCE_USAGES:
            raise StageError(f"Unsupported manifest source usage: {usage!r}.")

        path = normalize_relative_path(str(source.get("path", "")), source_dir)
        if usage == "toplevel":
            toplevel_paths.append(path)
        if usage == "ignore":
            continue
        if path in seen:
            raise StageError(f"Manifest declares duplicate source path: {path.as_posix()}.")
        if path.suffix.lower() not in ALLOWED_SOURCE_EXTENSIONS:
            raise StageError(
                f"Manifest source type is not arXiv-safe: {path.as_posix()}."
            )
        source_path = source_dir / Path(path)
        if not source_path.is_file():
            raise StageError(f"Manifest source is missing or not a file: {path.as_posix()}.")
        seen.add(path)
        paths.append(path)

    if toplevel_paths != [PurePosixPath("paper.tex")]:
        raise StageError(
            "Manifest must declare paper.tex as its only toplevel source; found "
            + ", ".join(path.as_posix() for path in toplevel_paths)
            + "."
        )
    if PurePosixPath("paper.tex") not in seen:
        raise StageError("Manifest must include paper.tex as an included source.")
    return tuple(sorted(paths, key=lambda path: path.as_posix()))


def strip_tex_comments(content: str) -> str:
    """Remove unescaped LaTeX comments before dependency scanning."""

    lines: list[str] = []
    for line in content.splitlines():
        index = 0
        while index < len(line):
            if line[index] == "%" and (index == 0 or line[index - 1] != "\\"):
                line = line[:index]
                break
            index += 1
        lines.append(line)
    return "\n".join(lines)


def resolve_file_reference(
    source_dir: Path,
    value: str,
    suffixes: tuple[str, ...],
    current_path: PurePosixPath | None = None,
    search_paths: Iterable[PurePosixPath] = (),
) -> PurePosixPath:
    """Resolve a TeX path reference to a real, contained source file."""

    raw_path = PurePosixPath(value.strip())
    if raw_path.is_absolute() or ".." in raw_path.parts or raw_path == PurePosixPath("."):
        raise StageError(f"TeX dependency escapes the staged source directory: {value!r}.")

    candidates: list[PurePosixPath] = [raw_path]
    if current_path is not None:
        candidates.append(current_path.parent / raw_path)
    candidates.extend(search_path / raw_path for search_path in search_paths)

    expanded: list[PurePosixPath] = []
    for candidate in candidates:
        if candidate.suffix:
            expanded.append(candidate)
        else:
            expanded.extend(candidate.with_suffix(suffix) for suffix in suffixes)

    source_root = source_dir.resolve()
    for candidate in expanded:
        normalized = PurePosixPath(candidate)
        candidate_path = (source_dir / Path(normalized)).resolve()
        try:
            candidate_path.relative_to(source_root)
        except ValueError as error:
            raise StageError(
                f"TeX dependency escapes the staged source directory: {value!r}."
            ) from error
        if candidate_path.is_file():
            return normalized

    attempted = ", ".join(path.as_posix() for path in expanded)
    raise StageError(f"Unable to resolve TeX dependency {value!r}; attempted: {attempted}.")


def collect_graphics_paths(source_dir: Path, declared_paths: Iterable[PurePosixPath]) -> tuple[PurePosixPath, ...]:
    """Collect \\graphicspath directories declared by local TeX and style inputs."""

    directories: set[PurePosixPath] = set()
    for relative_path in declared_paths:
        if relative_path.suffix.lower() not in {".sty", ".tex"}:
            continue
        content = strip_tex_comments(
            (source_dir / Path(relative_path)).read_text(encoding="utf-8")
        )
        for match in GRAPHICSPATH_PATTERN.finditer(content):
            for value in re.findall(r"\{([^{}]+)\}", match.group(1)):
                path = PurePosixPath(value.strip())
                if path.is_absolute() or ".." in path.parts:
                    raise StageError(f"Invalid \\graphicspath entry: {value!r}.")
                directories.add(path)
    return tuple(sorted(directories, key=lambda path: path.as_posix()))


def discover_compile_dependencies(
    source_dir: Path,
    manifest: dict[str, Any],
    declared_paths: Iterable[PurePosixPath],
) -> tuple[PurePosixPath, ...]:
    """Discover the file closure directly referenced by the submitted manuscript."""

    declared = set(declared_paths)
    toplevel_paths = [
        normalize_relative_path(str(source["path"]), source_dir)
        for source in manifest["sources"]
        if isinstance(source, dict) and source.get("usage") == "toplevel"
    ]
    graphics_paths = collect_graphics_paths(source_dir, declared)
    discovered: set[PurePosixPath] = set()
    pending: deque[PurePosixPath] = deque(toplevel_paths)

    while pending:
        current_path = pending.popleft()
        if current_path in discovered:
            continue
        discovered.add(current_path)
        if current_path.suffix.lower() not in {".sty", ".tex"}:
            continue

        content = strip_tex_comments(
            (source_dir / Path(current_path)).read_text(encoding="utf-8")
        )
        dependencies: list[PurePosixPath] = []

        for match in INPUT_PATTERN.finditer(content):
            dependencies.append(
                resolve_file_reference(
                    source_dir,
                    match.group(1),
                    (".tex",),
                    current_path=current_path,
                )
            )

        for match in BIBLIOGRAPHY_PATTERN.finditer(content):
            for value in match.group(1).split(","):
                dependencies.append(
                    resolve_file_reference(
                        source_dir,
                        value,
                        (".bib",),
                        current_path=current_path,
                    )
                )

        for match in PACKAGE_PATTERN.finditer(content):
            for value in match.group(1).split(","):
                package = value.strip()
                try:
                    dependencies.append(
                        resolve_file_reference(
                            source_dir,
                            package,
                            (".sty",),
                            current_path=current_path,
                        )
                    )
                except StageError:
                    if "/" in package or package.startswith("."):
                        raise
                    continue

        for match in GRAPHICS_PATTERN.finditer(content):
            dependencies.append(
                resolve_file_reference(
                    source_dir,
                    match.group(1),
                    GRAPHIC_EXTENSIONS,
                    current_path=current_path,
                    search_paths=graphics_paths,
                )
            )

        for dependency in dependencies:
            if dependency not in discovered:
                pending.append(dependency)

    undeclared = sorted(discovered - declared, key=lambda path: path.as_posix())
    if undeclared:
        names = ", ".join(path.as_posix() for path in undeclared)
        raise StageError(
            "Manifest does not declare every compiled TeX dependency: " + names + "."
        )
    return tuple(sorted(discovered, key=lambda path: path.as_posix()))


def sha256_for_file(path: Path) -> str:
    """Return a SHA-256 checksum for one regular file."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def regular_files(root: Path) -> list[Path]:
    """Return staged regular files in deterministic path order."""

    return sorted(
        (path for path in root.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(root).as_posix(),
    )


def copy_source_file(source_dir: Path, staging_dir: Path, relative_path: PurePosixPath) -> None:
    """Copy one declared source file into the staged bundle with normalized metadata."""

    source_path = source_dir / Path(relative_path)
    destination = staging_dir / Path(relative_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_path, destination)
    os.chmod(destination, 0o644)
    os.utime(destination, (0, 0))


def ensure_archive_is_outside_bundle(archive_path: Path, bundle_dir: Path) -> None:
    """Reject archive outputs that would recursively include themselves."""

    try:
        archive_path.resolve().relative_to(bundle_dir.resolve())
    except ValueError:
        return
    raise StageError(f"Archive output must be outside the staged source tree: {archive_path}.")


def write_deterministic_zip(bundle_dir: Path, archive_path: Path) -> None:
    """Write a deterministic ZIP archive of one staged submission."""

    ensure_archive_is_outside_bundle(archive_path, bundle_dir)
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        archive_path,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for source_path in regular_files(bundle_dir):
            relative_path = source_path.relative_to(bundle_dir).as_posix()
            info = zipfile.ZipInfo(relative_path, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, source_path.read_bytes())


def write_deterministic_tar_gz(bundle_dir: Path, archive_path: Path) -> None:
    """Write a deterministic TAR.GZ archive of one staged submission."""

    ensure_archive_is_outside_bundle(archive_path, bundle_dir)
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with archive_path.open("wb") as raw_output:
        with gzip.GzipFile(
            filename="",
            mode="wb",
            fileobj=raw_output,
            mtime=0,
        ) as gzip_output:
            with tarfile.open(
                mode="w",
                fileobj=gzip_output,
                format=tarfile.PAX_FORMAT,
            ) as archive:
                for source_path in regular_files(bundle_dir):
                    relative_path = source_path.relative_to(bundle_dir).as_posix()
                    info = archive.gettarinfo(str(source_path), arcname=relative_path)
                    info.uid = 0
                    info.gid = 0
                    info.uname = ""
                    info.gname = ""
                    info.mtime = 0
                    info.mode = 0o644
                    with source_path.open("rb") as handle:
                        archive.addfile(info, handle)


def stage_submission(
    source_dir: Path,
    output_dir: Path,
    maximum_total_bytes: int = DEFAULT_MAXIMUM_TOTAL_BYTES,
    maximum_file_bytes: int = DEFAULT_MAXIMUM_FILE_BYTES,
) -> StageResult:
    """Materialize an exact, bounded arXiv source tree."""

    source_dir = source_dir.resolve()
    output_dir = output_dir.resolve()
    if not source_dir.is_dir():
        raise StageError(f"Source directory does not exist: {source_dir}.")
    if output_dir.exists():
        raise StageError(
            f"Refusing to replace an existing staging directory: {output_dir}."
        )
    if maximum_total_bytes <= 0 or maximum_file_bytes <= 0:
        raise StageError("Size limits must be positive integers.")

    manifest = read_manifest(source_dir)
    declared_paths = declared_source_paths(source_dir, manifest)
    dependency_paths = discover_compile_dependencies(source_dir, manifest, declared_paths)
    unreferenced_paths = sorted(
        set(declared_paths) - set(dependency_paths),
        key=lambda path: path.as_posix(),
    )
    if unreferenced_paths:
        names = ", ".join(path.as_posix() for path in unreferenced_paths)
        raise StageError(
            "Manifest declares files outside the TeX dependency closure: " + names + "."
        )
    staged_paths = (PurePosixPath("00README.json"), *declared_paths)

    for relative_path in staged_paths:
        source_path = source_dir / Path(relative_path)
        if source_path.stat().st_size > maximum_file_bytes:
            raise StageError(
                f"Source file exceeds the per-file limit: {relative_path.as_posix()}."
            )

    total_bytes = sum((source_dir / Path(path)).stat().st_size for path in staged_paths)
    if total_bytes > maximum_total_bytes:
        raise StageError(
            "Staged arXiv source tree exceeds the configured size limit: "
            f"{total_bytes} > {maximum_total_bytes} bytes."
        )

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary_directory = Path(
        tempfile.mkdtemp(prefix=f".{output_dir.name}.", dir=output_dir.parent)
    )
    try:
        for relative_path in staged_paths:
            copy_source_file(source_dir, temporary_directory, relative_path)
        temporary_directory.replace(output_dir)
    except Exception:
        shutil.rmtree(temporary_directory, ignore_errors=True)
        raise

    files = tuple(
        PurePosixPath(path.relative_to(output_dir).as_posix())
        for path in regular_files(output_dir)
    )
    return StageResult(
        bundle_dir=output_dir,
        files=files,
        total_bytes=total_bytes,
        dependency_paths=dependency_paths,
    )


def main(argv: list[str] | None = None) -> int:
    """Run the staging command."""

    args = build_parser().parse_args(argv)
    source_dir = Path(args.source_dir)
    output_dir = Path(args.output_dir)
    try:
        result = stage_submission(
            source_dir=source_dir,
            output_dir=output_dir,
            maximum_total_bytes=args.maximum_total_bytes,
            maximum_file_bytes=args.maximum_file_bytes,
        )
        if args.zip_output:
            write_deterministic_zip(result.bundle_dir, Path(args.zip_output))
        if args.tar_output:
            write_deterministic_tar_gz(result.bundle_dir, Path(args.tar_output))
    except StageError as error:
        print(f"[stage-arxiv-submission] {error}", file=sys.stderr)
        return 1

    print(
        "[stage-arxiv-submission] "
        f"staged_files={len(result.files)} total_bytes={result.total_bytes} "
        f"bundle_dir={result.bundle_dir}"
    )
    if args.zip_output:
        print(
            "[stage-arxiv-submission] "
            f"zip={Path(args.zip_output).resolve()} "
            f"sha256={sha256_for_file(Path(args.zip_output))}"
        )
    if args.tar_output:
        print(
            "[stage-arxiv-submission] "
            f"tar_gz={Path(args.tar_output).resolve()} "
            f"sha256={sha256_for_file(Path(args.tar_output))}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
