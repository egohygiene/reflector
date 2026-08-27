#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Validate the exact staged source tree submitted to arXiv."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from stage_arxiv_submission import (
    ALLOWED_SOURCE_EXTENSIONS,
    ALLOWED_SOURCE_USAGES,
    DEFAULT_MAXIMUM_FILE_BYTES,
    DEFAULT_MAXIMUM_TOTAL_BYTES,
    GRAPHIC_EXTENSIONS,
    StageError,
    declared_source_paths,
    discover_compile_dependencies,
    read_manifest,
    stage_submission,
)


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_AUDIT_OUTPUT = REPOSITORY_ROOT / "audits" / "arxiv-validation.md"
ARXIV_SUPPORTED_COMPILERS = {"pdflatex", "latex", "xelatex", "lualatex"}
ARXIV_SUPPORTED_BIBLIOGRAPHY = {"biber", "bibtex", "bibtex8"}
BANNED_FILENAMES = {".DS_Store", "Thumbs.db", "desktop.ini"}


@dataclass(frozen=True)
class Check:
    """Represent one visible validation result."""

    area: str
    name: str
    status: str
    details: str


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Validate the exact deterministic arXiv submission tree rather than "
            "the broader canonical paper workspace."
        )
    )
    parser.add_argument(
        "--source-dir",
        default="paper",
        help="Canonical source directory used when staging a temporary submission tree.",
    )
    parser.add_argument(
        "--bundle-dir",
        default="",
        help="Existing staged submission tree to validate instead of creating one.",
    )
    parser.add_argument(
        "--audit-output",
        default=str(DEFAULT_AUDIT_OUTPUT),
        help="Markdown report path to write.",
    )
    parser.add_argument(
        "--maximum-total-bytes",
        type=int,
        default=DEFAULT_MAXIMUM_TOTAL_BYTES,
        help="Maximum allowed source-tree size in bytes.",
    )
    parser.add_argument(
        "--maximum-file-bytes",
        type=int,
        default=DEFAULT_MAXIMUM_FILE_BYTES,
        help="Maximum allowed file size in bytes.",
    )
    parser.add_argument(
        "--generated-at",
        default="",
        help="Explicit UTC timestamp for reproducible reports.",
    )
    return parser


def add_check(
    checks: list[Check],
    area: str,
    name: str,
    condition: bool,
    passed: str,
    failed: str,
) -> None:
    """Append one pass/fail check."""

    checks.append(
        Check(
            area=area,
            name=name,
            status="PASS" if condition else "FAIL",
            details=passed if condition else failed,
        )
    )


def format_bytes(value: int) -> str:
    """Return a compact, reader-facing byte count."""

    return f"{value / 1_000_000:.2f} MB ({value} bytes)"


def regular_files(bundle_dir: Path) -> list[Path]:
    """Return regular bundle files in deterministic relative-path order."""

    return sorted(
        (path for path in bundle_dir.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(bundle_dir).as_posix(),
    )


def staged_relative_paths(bundle_dir: Path) -> set[PurePosixPath]:
    """Return all staged regular files as POSIX-relative paths."""

    return {
        PurePosixPath(path.relative_to(bundle_dir).as_posix())
        for path in regular_files(bundle_dir)
    }


def source_entries(manifest: dict[str, Any]) -> Iterable[dict[str, Any]]:
    """Yield structurally valid source entries from a parsed manifest."""

    sources = manifest.get("sources")
    if not isinstance(sources, list):
        return ()
    return (source for source in sources if isinstance(source, dict))


def gather_checks(
    bundle_dir: Path,
    maximum_total_bytes: int,
    maximum_file_bytes: int,
) -> list[Check]:
    """Validate an already-materialized arXiv submission tree."""

    checks: list[Check] = []
    bundle_dir = bundle_dir.resolve()
    add_check(
        checks,
        "Staging",
        "Exact staged submission directory exists",
        bundle_dir.is_dir(),
        "The validator is measuring a materialized arXiv submission directory.",
        f"Staged submission directory is missing: {bundle_dir}.",
    )
    if not bundle_dir.is_dir():
        return checks

    try:
        manifest = read_manifest(bundle_dir)
        manifest_error = ""
    except StageError as error:
        manifest = {}
        manifest_error = str(error)

    add_check(
        checks,
        "Manifest",
        "00README.json is parseable JSON",
        not manifest_error,
        "00README.json is valid JSON in the staged submission.",
        manifest_error or "00README.json is not valid JSON.",
    )
    if manifest_error:
        return checks

    schema_value = str(manifest.get("$schema", ""))
    add_check(
        checks,
        "Manifest",
        "00README schema references arXiv",
        schema_value.startswith("https://arxiv.org/schemas/00readme/"),
        "00README schema references the arXiv 00readme schema.",
        f"00README $schema is not an arXiv 00readme schema: {schema_value!r}.",
    )
    required_keys = {"manifest_version", "publication", "process", "sources", "build"}
    missing_keys = sorted(required_keys - set(manifest))
    add_check(
        checks,
        "Manifest",
        "00README required root keys are present",
        not missing_keys,
        "00README includes all required root keys.",
        "00README is missing required root keys: " + ", ".join(missing_keys),
    )

    process = manifest.get("process") if isinstance(manifest.get("process"), dict) else {}
    compiler = str(process.get("compiler", "")).strip()
    bibliography = str(process.get("bibliography", "")).strip()
    texlive = str(process.get("texlive", "")).strip()
    max_repeat = process.get("max_repeat")
    add_check(
        checks,
        "Manifest",
        "Compiler is arXiv-supported",
        compiler in ARXIV_SUPPORTED_COMPILERS,
        f"Declared compiler {compiler!r} is supported by arXiv.",
        f"Declared compiler {compiler!r} is not arXiv-supported.",
    )
    add_check(
        checks,
        "Manifest",
        "Bibliography tool is arXiv-supported",
        bibliography in ARXIV_SUPPORTED_BIBLIOGRAPHY,
        f"Declared bibliography tool {bibliography!r} is supported by arXiv.",
        f"Declared bibliography tool {bibliography!r} is not arXiv-supported.",
    )
    add_check(
        checks,
        "Manifest",
        "Deterministic staging is declared",
        process.get("deterministic") is True,
        "process.deterministic is true.",
        "process.deterministic must be true.",
    )
    add_check(
        checks,
        "Manifest",
        "TeX Live version is declared",
        bool(texlive),
        f"process.texlive declares {texlive!r}.",
        "process.texlive must declare the tested TeX Live version.",
    )
    add_check(
        checks,
        "Manifest",
        "Maximum compiler repeats are declared",
        isinstance(max_repeat, int) and max_repeat > 0,
        f"process.max_repeat is {max_repeat}.",
        "process.max_repeat must be a positive integer.",
    )

    build = manifest.get("build") if isinstance(manifest.get("build"), dict) else {}
    build_script = str(build.get("script", "")).strip()
    orchestration = str(build.get("orchestration", "")).strip()
    staging = build.get("staging") if isinstance(build.get("staging"), dict) else {}
    normalized_commands = [
        command.strip().split(maxsplit=1)[0].lower()
        for command in build_script.split("&&")
        if command.strip()
    ]
    add_check(
        checks,
        "Manifest",
        "Direct pdflatex/biber path is declared",
        normalized_commands == ["pdflatex", "biber", "pdflatex", "pdflatex"]
        and bool(orchestration),
        "The manifest declares pdflatex, biber, then two pdflatex passes.",
        "build.script must declare pdflatex, biber, pdflatex, pdflatex and "
        "build.orchestration must explain the direct path.",
    )
    add_check(
        checks,
        "Manifest",
        "Submission does not rely on TEXINPUTS overrides",
        build.get("texinputs") == [],
        "build.texinputs is empty; staged compilation resolves declared paths directly.",
        "build.texinputs must be an empty array for the direct staged submission.",
    )
    add_check(
        checks,
        "Manifest",
        "Declared staging budget matches the enforced headroom target",
        staging.get("maximum_submission_bytes") == maximum_total_bytes,
        f"Manifest and validator both enforce {format_bytes(maximum_total_bytes)}.",
        "build.staging.maximum_submission_bytes must equal "
        f"{maximum_total_bytes}.",
    )

    entries = tuple(source_entries(manifest))
    invalid_usages = [
        f"{source.get('path', '')} ({source.get('usage', '')!r})"
        for source in entries
        if str(source.get("usage", "")).strip() not in ALLOWED_SOURCE_USAGES
    ]
    add_check(
        checks,
        "Source declarations",
        "All source usage values are valid",
        not invalid_usages,
        "All source usage values are valid.",
        "Invalid source usage values: " + ", ".join(invalid_usages),
    )

    try:
        declared_paths = declared_source_paths(bundle_dir, manifest)
        declaration_error = ""
    except StageError as error:
        declared_paths = ()
        declaration_error = str(error)
    add_check(
        checks,
        "Source declarations",
        "Declared sources are safe, unique, and present",
        not declaration_error,
        "Every declared source is relative, arXiv-safe, unique, and present.",
        declaration_error or "The source declarations are invalid.",
    )
    if declaration_error:
        return checks

    declared_extensions = {
        path.suffix.lower() for path in declared_paths if path.suffix.lower()
    }
    unsupported_extensions = sorted(
        extension for extension in declared_extensions if extension not in ALLOWED_SOURCE_EXTENSIONS
    )
    add_check(
        checks,
        "Source declarations",
        "All declared source file types are arXiv-safe",
        not unsupported_extensions,
        "All declared source types are arXiv-safe.",
        "Unsupported source types: " + ", ".join(unsupported_extensions),
    )

    staged_paths = staged_relative_paths(bundle_dir)
    expected_paths = {PurePosixPath("00README.json"), *declared_paths}
    missing_paths = sorted(expected_paths - staged_paths, key=lambda path: path.as_posix())
    unexpected_paths = sorted(staged_paths - expected_paths, key=lambda path: path.as_posix())
    add_check(
        checks,
        "Upload structure",
        "Staged tree contains exactly the manifest-declared source set",
        not missing_paths and not unexpected_paths,
        f"The staged tree contains exactly {len(expected_paths)} declared source files.",
        "Missing: "
        + (", ".join(path.as_posix() for path in missing_paths) or "<none>")
        + "; undeclared: "
        + (", ".join(path.as_posix() for path in unexpected_paths) or "<none>"),
    )

    try:
        dependency_paths = discover_compile_dependencies(
            bundle_dir,
            manifest,
            declared_paths,
        )
        dependency_error = ""
    except StageError as error:
        dependency_paths = ()
        dependency_error = str(error)
    add_check(
        checks,
        "Source declarations",
        "Every compiled TeX dependency is declared",
        not dependency_error,
        f"All {len(dependency_paths)} discovered compilation dependencies are declared.",
        dependency_error or "A compiled TeX dependency is not declared.",
    )
    unreferenced_paths = (
        sorted(
            set(declared_paths) - set(dependency_paths),
            key=lambda path: path.as_posix(),
        )
        if not dependency_error
        else []
    )
    add_check(
        checks,
        "Source declarations",
        "Manifest declarations are the exact TeX dependency closure",
        not unreferenced_paths and not dependency_error,
        f"All {len(declared_paths)} declared sources are required by compilation.",
        "Manifest sources outside the compilation closure: "
        + (
            ", ".join(path.as_posix() for path in unreferenced_paths)
            if unreferenced_paths
            else dependency_error
        ),
    )

    symlinks = [
        path.relative_to(bundle_dir).as_posix()
        for path in bundle_dir.rglob("*")
        if path.is_symlink()
    ]
    add_check(
        checks,
        "Upload structure",
        "No symlinks are present",
        not symlinks,
        "No symlinks are present in the staged submission.",
        "Symlinks are not supported by arXiv: " + ", ".join(symlinks),
    )
    banned = sorted(
        path.relative_to(bundle_dir).as_posix()
        for path in regular_files(bundle_dir)
        if path.name in BANNED_FILENAMES
    )
    add_check(
        checks,
        "Upload structure",
        "No banned system files are present",
        not banned,
        "No banned system files are present.",
        "Banned system files: " + ", ".join(banned),
    )
    hidden_paths = sorted(
        path.relative_to(bundle_dir).as_posix()
        for path in regular_files(bundle_dir)
        if any(part.startswith(".") for part in path.relative_to(bundle_dir).parts)
    )
    add_check(
        checks,
        "Upload structure",
        "No hidden runtime files are present",
        not hidden_paths,
        "The staged submission does not rely on hidden files.",
        "Hidden files are not suitable arXiv runtime inputs: " + ", ".join(hidden_paths),
    )

    figure_paths = [
        path for path in declared_paths if path.parts and path.parts[0] == "figures"
    ]
    unsupported_figures = sorted(
        path.as_posix()
        for path in figure_paths
        if path.suffix.lower() not in GRAPHIC_EXTENSIONS
    )
    oversized_files = sorted(
        path.relative_to(bundle_dir).as_posix()
        for path in regular_files(bundle_dir)
        if path.stat().st_size > maximum_file_bytes
    )
    add_check(
        checks,
        "Figure compatibility",
        "All staged figures use arXiv-safe formats",
        not unsupported_figures,
        f"All {len(figure_paths)} staged figures use arXiv-safe formats.",
        "Unsupported figure formats: " + ", ".join(unsupported_figures),
    )
    add_check(
        checks,
        "Figure compatibility",
        "No staged source file exceeds the per-file size limit",
        not oversized_files,
        f"All staged files are at or below {format_bytes(maximum_file_bytes)}.",
        "Oversized staged files: " + ", ".join(oversized_files),
    )

    total_bytes = sum(path.stat().st_size for path in regular_files(bundle_dir))
    add_check(
        checks,
        "Figure compatibility",
        "Exact staged arXiv source tree is within the 45 MB headroom target",
        total_bytes <= maximum_total_bytes,
        f"Exact staged source tree is {format_bytes(total_bytes)}; "
        f"limit is {format_bytes(maximum_total_bytes)}.",
        f"Exact staged source tree is {format_bytes(total_bytes)}; "
        f"limit is {format_bytes(maximum_total_bytes)}.",
    )

    bib_paths = [path for path in declared_paths if path.suffix.lower() == ".bib"]
    bib_entries = 0
    for path in bib_paths:
        content = (bundle_dir / Path(path)).read_text(encoding="utf-8")
        bib_entries += len(re.findall(r"^@\w+\{", content, flags=re.MULTILINE))
    add_check(
        checks,
        "Bibliography",
        "Bibliography source is present and non-empty",
        bool(bib_paths) and bib_entries > 0,
        f"{len(bib_paths)} bibliography file(s) contain {bib_entries} entries.",
        "No non-empty bibliography source is declared.",
    )
    style_paths = [path for path in declared_paths if path.suffix.lower() == ".sty"]
    style_contents = [
        (bundle_dir / Path(path)).read_text(encoding="utf-8") for path in style_paths
    ]
    uses_biblatex = any("biblatex" in content for content in style_contents)
    biber_backend = any("backend=biber" in content for content in style_contents)
    add_check(
        checks,
        "Bibliography",
        "biblatex backend matches the declared biber path",
        not uses_biblatex or (bibliography == "biber" and biber_backend),
        "The bibliography style and manifest agree on biber.",
        "The bibliography style and manifest do not agree on the biber path.",
    )
    return checks


def write_report(
    checks: list[Check],
    output_path: Path,
    generated_at: str,
) -> None:
    """Write a readable audit report from the reviewed checks."""

    pass_count = sum(check.status == "PASS" for check in checks)
    fail_count = sum(check.status == "FAIL" for check in checks)
    by_area: dict[str, list[Check]] = {}
    for check in checks:
        by_area.setdefault(check.area, []).append(check)

    def area_ok(area: str) -> bool:
        return bool(by_area.get(area)) and all(
            check.status == "PASS" for check in by_area[area]
        )

    def mark(value: bool) -> str:
        return "x" if value else " "

    lines = [
        "# arXiv Packaging Validation Report",
        "",
        "Generated at: " + generated_at,
        "",
        "## Executive Summary",
        "",
        "- Validation target: the exact deterministic staged arXiv source tree, not every file retained in the canonical paper workspace.",
        "- The stage contains only the manifest-declared TeX dependency closure plus 00README.json; reference-library PDFs, website assets, and unused artwork remain canonical-only.",
        f"- Total checks: **{len(checks)}**",
        f"- Pass: **{pass_count}**",
        f"- Fail: **{fail_count}**",
        "",
        "Overall result: "
        + ("✅ **arXiv upload-ready**" if fail_count == 0 else "❌ **Not arXiv upload-ready**"),
        "",
        "## Goal Checklist",
        "",
        f"- [{mark(area_ok('Staging'))}] Materialize the exact declared submission tree",
        f"- [{mark(area_ok('Manifest'))}] Validate the arXiv manifest and declared compiler path",
        f"- [{mark(area_ok('Source declarations'))}] Verify the full TeX dependency closure is declared",
        f"- [{mark(area_ok('Upload structure'))}] Exclude hidden, system, and undeclared files",
        f"- [{mark(area_ok('Figure compatibility'))}] Enforce file and bundle-size boundaries",
        f"- [{mark(area_ok('Bibliography'))}] Verify the biber-compatible bibliography path",
        "",
        "## Detailed Checks",
        "",
    ]
    for area in sorted(by_area):
        lines.extend([f"### {area}", "", "| Check | Result | Details |", "| --- | --- | --- |"])
        for check in by_area[area]:
            icon = "✅" if check.status == "PASS" else "❌"
            lines.append(
                f"| {check.name} | {icon} {check.status} | {check.details} |"
            )
        lines.append("")

    if fail_count:
        lines.extend(["## Unresolved Issues", ""])
        for check in checks:
            if check.status == "FAIL":
                lines.append(f"- ❌ **{check.area} / {check.name}**: {check.details}")
        lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def validation_timestamp(value: str) -> str:
    """Return a normalized report timestamp."""

    if value:
        return value
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main(argv: list[str] | None = None) -> int:
    """Run staged arXiv source validation."""

    args = build_parser().parse_args(argv)
    audit_output = Path(args.audit_output).resolve()
    timestamp = validation_timestamp(args.generated_at)
    checks: list[Check]

    if args.maximum_total_bytes <= 0 or args.maximum_file_bytes <= 0:
        checks = [
            Check(
                area="Staging",
                name="Configured size limits are positive",
                status="FAIL",
                details="Configured size limits must be positive integers.",
            )
        ]
    elif args.bundle_dir:
        checks = gather_checks(
            Path(args.bundle_dir),
            args.maximum_total_bytes,
            args.maximum_file_bytes,
        )
    else:
        with tempfile.TemporaryDirectory(prefix="reflector-arxiv-validation-") as directory:
            bundle_dir = Path(directory) / "source"
            try:
                stage_submission(
                    source_dir=Path(args.source_dir),
                    output_dir=bundle_dir,
                    maximum_total_bytes=args.maximum_total_bytes,
                    maximum_file_bytes=args.maximum_file_bytes,
                )
                checks = gather_checks(
                    bundle_dir,
                    args.maximum_total_bytes,
                    args.maximum_file_bytes,
                )
            except StageError as error:
                checks = [
                    Check(
                        area="Staging",
                        name="Deterministic arXiv submission tree can be created",
                        status="FAIL",
                        details=str(error),
                    )
                ]

    write_report(checks, audit_output, timestamp)
    fail_count = sum(check.status == "FAIL" for check in checks)
    print(f"[validate-arxiv-packaging] report written to {audit_output}")
    print(
        "[validate-arxiv-packaging] "
        f"pass={sum(check.status == 'PASS' for check in checks)} fail={fail_count}"
    )
    return 1 if fail_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
