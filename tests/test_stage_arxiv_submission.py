# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import subprocess
import sys
import tarfile
import unittest
import zipfile
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIRECTORY = REPOSITORY_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIRECTORY))

from stage_arxiv_submission import StageError, stage_submission, write_deterministic_tar_gz, write_deterministic_zip


def write_text(path: Path, content: str) -> None:
    """Write one UTF-8 fixture file."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_bytes(path: Path, content: bytes) -> None:
    """Write one binary fixture file."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def manifest(source_paths: list[str]) -> dict[str, object]:
    """Return one minimal but valid arXiv source manifest."""

    return {
        "$schema": "https://arxiv.org/schemas/00readme/v1",
        "manifest_version": 1,
        "publication": {"title": "fixture"},
        "process": {
            "compiler": "pdflatex",
            "bibliography": "biber",
            "deterministic": True,
            "texlive": "2025",
            "max_repeat": 10,
        },
        "sources": [
            {
                "path": source_path,
                "usage": "toplevel" if source_path == "paper.tex" else "include",
            }
            for source_path in source_paths
        ],
        "build": {
            "texinputs": [],
            "script": "pdflatex paper.tex && biber paper && pdflatex paper.tex && pdflatex paper.tex",
            "orchestration": "direct pdflatex/biber",
            "staging": {"maximum_submission_bytes": 45_000_000},
        },
    }


def create_fixture(root: Path, source_paths: list[str] | None = None) -> Path:
    """Create a canonical source fixture with unrelated retained materials."""

    source_dir = root / "paper"
    source_paths = source_paths or [
        "paper.tex",
        "sections/introduction.tex",
        "styles/fixture.sty",
        "references.bib",
        "figures/architecture.png",
    ]
    write_text(
        source_dir / "paper.tex",
        r"""\documentclass{article}
\usepackage{styles/fixture}
\addbibresource{references.bib}
\begin{document}
\input{sections/introduction}
\printbibliography
\end{document}
""",
    )
    write_text(
        source_dir / "styles" / "fixture.sty",
        r"""\RequirePackage{graphicx}
\RequirePackage[backend=biber]{biblatex}
\graphicspath{{figures/}}
""",
    )
    write_text(
        source_dir / "sections" / "introduction.tex",
        r"""\section{Introduction}
\includegraphics{architecture.png}
""",
    )
    write_text(source_dir / "references.bib", "@article{fixture, title={Fixture}}\n")
    write_bytes(source_dir / "figures" / "architecture.png", b"fixture-image")
    write_bytes(source_dir / "references" / "library.pdf", b"retained-reference-pdf")
    write_bytes(source_dir / "assets" / "website-preview.png", b"website-preview")
    write_text(
        source_dir / "00README.json",
        json.dumps(manifest(source_paths), indent=2) + "\n",
    )
    return source_dir


class StageArxivSubmissionTests(unittest.TestCase):
    """Exercise the exact submission boundary rather than the full paper workspace."""

    def test_stages_only_manifest_declared_compilation_inputs(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source_dir = create_fixture(root)
            result = stage_submission(source_dir, root / "arxiv")

            self.assertEqual(
                {path.as_posix() for path in result.files},
                {
                    "00README.json",
                    "figures/architecture.png",
                    "paper.tex",
                    "references.bib",
                    "sections/introduction.tex",
                    "styles/fixture.sty",
                },
            )
            self.assertFalse((root / "arxiv" / "assets").exists())
            self.assertFalse((root / "arxiv" / "references").exists())
            self.assertEqual(
                result.total_bytes,
                sum(path.stat().st_size for path in (root / "arxiv").rglob("*") if path.is_file()),
            )

    def test_rejects_manifest_missing_a_compiled_dependency(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source_dir = create_fixture(
                root,
                [
                    "paper.tex",
                    "sections/introduction.tex",
                    "styles/fixture.sty",
                    "references.bib",
                ],
            )

            with self.assertRaisesRegex(
                StageError,
                "does not declare every compiled TeX dependency",
            ):
                stage_submission(source_dir, root / "arxiv")

    def test_requires_paper_tex_as_the_only_toplevel_source(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source_dir = create_fixture(root)
            invalid_manifest = manifest(
                [
                    "paper.tex",
                    "sections/introduction.tex",
                    "styles/fixture.sty",
                    "references.bib",
                    "figures/architecture.png",
                ]
            )
            invalid_manifest["sources"][0]["usage"] = "include"
            invalid_manifest["sources"][1]["usage"] = "toplevel"
            write_text(
                source_dir / "00README.json",
                json.dumps(invalid_manifest, indent=2) + "\n",
            )

            with self.assertRaisesRegex(
                StageError,
                "paper.tex as its only toplevel source",
            ):
                stage_submission(source_dir, root / "arxiv")

    def test_finds_local_packages_without_a_directory_prefix(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source_dir = create_fixture(root)
            write_text(
                source_dir / "styles" / "fixture.sty",
                r"""\RequirePackage{nested}
\RequirePackage{graphicx}
\RequirePackage[backend=biber]{biblatex}
\graphicspath{{figures/}}
""",
            )
            write_text(source_dir / "styles" / "nested.sty", r"\ProvidesPackage{nested}")
            source_paths = [
                "paper.tex",
                "sections/introduction.tex",
                "styles/fixture.sty",
                "styles/nested.sty",
                "references.bib",
                "figures/architecture.png",
            ]
            write_text(
                source_dir / "00README.json",
                json.dumps(manifest(source_paths), indent=2) + "\n",
            )

            result = stage_submission(source_dir, root / "arxiv")

            self.assertIn(
                PurePosixPath("styles/nested.sty"),
                result.dependency_paths,
            )

    def test_rejects_manifest_overdeclaring_unused_canonical_material(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source_dir = create_fixture(
                root,
                [
                    "paper.tex",
                    "sections/introduction.tex",
                    "styles/fixture.sty",
                    "references.bib",
                    "figures/architecture.png",
                    "assets/website-preview.png",
                ],
            )

            with self.assertRaisesRegex(
                StageError,
                "outside the TeX dependency closure",
            ):
                stage_submission(source_dir, root / "arxiv")

    def test_archives_are_deterministic(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source_dir = create_fixture(root)
            result = stage_submission(source_dir, root / "arxiv")

            first_zip = root / "first.zip"
            second_zip = root / "second.zip"
            first_tar = root / "first.tar.gz"
            second_tar = root / "second.tar.gz"
            write_deterministic_zip(result.bundle_dir, first_zip)
            write_deterministic_zip(result.bundle_dir, second_zip)
            write_deterministic_tar_gz(result.bundle_dir, first_tar)
            write_deterministic_tar_gz(result.bundle_dir, second_tar)

            self.assertEqual(first_zip.read_bytes(), second_zip.read_bytes())
            self.assertEqual(first_tar.read_bytes(), second_tar.read_bytes())
            with zipfile.ZipFile(first_zip) as archive:
                self.assertEqual(
                    archive.namelist(),
                    sorted(path.as_posix() for path in result.files),
                )
            with tarfile.open(first_tar) as archive:
                self.assertEqual(
                    archive.getnames(),
                    sorted(path.as_posix() for path in result.files),
                )

    def test_repository_source_stages_below_the_headroom_target(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            result = stage_submission(
                REPOSITORY_ROOT / "paper",
                Path(temporary_directory) / "arxiv",
            )

            self.assertLessEqual(result.total_bytes, 45_000_000)
            self.assertFalse((result.bundle_dir / "references").exists())
            self.assertFalse((result.bundle_dir / "assets").exists())
            self.assertFalse((result.bundle_dir / "figures" / "hero.png").exists())

    def test_validator_measures_a_staged_bundle_and_rejects_tampering(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source_dir = create_fixture(root)
            bundle_dir = root / "arxiv"
            stage_submission(source_dir, bundle_dir)
            report_path = root / "report.md"

            valid = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIRECTORY / "validate-arxiv-packaging.py"),
                    "--bundle-dir",
                    str(bundle_dir),
                    "--audit-output",
                    str(report_path),
                    "--generated-at",
                    "2026-08-27T00:00:00Z",
                ],
                capture_output=True,
                check=False,
                text=True,
            )
            self.assertEqual(valid.returncode, 0, valid.stderr)
            self.assertIn("exact deterministic staged arXiv source tree", report_path.read_text(encoding="utf-8"))

            write_text(bundle_dir / "unrelated.txt", "not a submission source\n")
            invalid = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIRECTORY / "validate-arxiv-packaging.py"),
                    "--bundle-dir",
                    str(bundle_dir),
                    "--audit-output",
                    str(report_path),
                    "--generated-at",
                    "2026-08-27T00:00:00Z",
                ],
                capture_output=True,
                check=False,
                text=True,
            )
            self.assertEqual(invalid.returncode, 1)
            self.assertIn("undeclared: unrelated.txt", report_path.read_text(encoding="utf-8"))

    def test_validator_rejects_overdeclared_staged_source(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source_dir = create_fixture(root)
            bundle_dir = root / "arxiv"
            stage_submission(source_dir, bundle_dir)
            report_path = root / "report.md"

            staged_manifest = json.loads(
                (bundle_dir / "00README.json").read_text(encoding="utf-8")
            )
            staged_manifest["sources"].append(
                {"path": "unused.tex", "usage": "include"}
            )
            write_text(bundle_dir / "unused.tex", r"\section{Unused}")
            write_text(
                bundle_dir / "00README.json",
                json.dumps(staged_manifest, indent=2) + "\n",
            )

            invalid = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIRECTORY / "validate-arxiv-packaging.py"),
                    "--bundle-dir",
                    str(bundle_dir),
                    "--audit-output",
                    str(report_path),
                    "--generated-at",
                    "2026-08-27T00:00:00Z",
                ],
                capture_output=True,
                check=False,
                text=True,
            )

            self.assertEqual(invalid.returncode, 1)
            self.assertIn(
                "Manifest declarations are the exact TeX dependency closure",
                report_path.read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
