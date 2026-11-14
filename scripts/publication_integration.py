# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Compose production publication interfaces in a disposable synthetic workspace.

This is a contract integration test, never a publisher or proof of manuscript
quality. All commands are local and receive a credential-free environment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
REVISION = "a" * 40
GENERATED_AT = "2026-11-14T00:00:00Z"
EPOCH = "1794614400"
COMMAND_TIMEOUT = 120


class IntegrationError(RuntimeError):
    """Stage-specific failure without credentials or full command output."""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def minimal_pdf(label: str) -> bytes:
    """Build a valid, fixed one-page PDF fixture, not a publication render."""
    stream = f"BT /F1 12 Tf 36 100 Td ({label}) Tj ET\n".encode("ascii")
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>", b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 240 160] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"endstream"]
    result = bytearray(b"%PDF-1.4\n%synthetic-contract-fixture\n")
    offsets = [0]
    for index, value in enumerate(objects, 1):
        offsets.append(len(result)); result.extend(f"{index} 0 obj\n".encode() + value + b"\nendobj\n")
    start = len(result)
    result.extend(f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        result.extend(f"{offset:010d} 00000 n \n".encode())
    result.extend(f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n".encode())
    return bytes(result)


def isolated_environment(root: Path) -> dict[str, str]:
    """Do not inherit provider credentials, Git configuration or TeX inputs."""
    home = root / ".home"
    home.mkdir()
    return {"PATH": os.environ.get("PATH", os.defpath), "HOME": str(home), "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8", "TZ": "UTC", "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull, "GIT_TERMINAL_PROMPT": "0",
        "GIT_AUTHOR_NAME": "Synthetic integration fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
        "GIT_COMMITTER_NAME": "Synthetic integration fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
        "GIT_AUTHOR_DATE": GENERATED_AT, "GIT_COMMITTER_DATE": GENERATED_AT,
        "SOURCE_DATE_EPOCH": EPOCH, "FORCE_SOURCE_DATE": "1", "PYTHONHASHSEED": "0"}


def command(root: Path, environment: dict[str, str], stage: str, *args: str) -> None:
    # File-backed output avoids retaining unbounded compiler logs in memory.
    # Private process groups stop TeX descendants before temporary cleanup.
    with tempfile.TemporaryFile() as output:
        process = None
        finished = False
        try:
            process = subprocess.Popen(args, cwd=root, env=environment, stdin=subprocess.DEVNULL,
                stdout=output, stderr=subprocess.STDOUT, start_new_session=os.name == "posix")
            code = process.wait(timeout=COMMAND_TIMEOUT)
            finished = True
        except (OSError, subprocess.TimeoutExpired) as error:
            raise IntegrationError(f"{stage}: command unavailable or exceeded {COMMAND_TIMEOUT}s deadline") from error
        finally:
            if process is not None and not finished:
                if os.name == "posix":
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                else:
                    process.kill()
                process.wait(timeout=5)
        if code:
            size = output.tell()
            output.seek(max(0, size - 2400))
            detail = output.read().decode("utf-8", errors="replace").replace(str(root), "<FIXTURE_ROOT>")
            raise IntegrationError(f"{stage}: exit {code}; {detail.strip()}")


def prepare_fixture(source: Path, root: Path) -> None:
    for name in ("scripts", "metadata", "docs", "paper", "magazine"):
        def ignore(directory, names):
            excluded = {".cache", "dist", "__pycache__"}
            if Path(directory) == source / "paper":
                excluded |= {"references", "assets", "examples", "diagrams"}
            return [item for item in names if item in excluded
                    and (Path(directory) / item).is_dir()]
        shutil.copytree(source / name, root / name, ignore=ignore)
    for name in ("VERSION", "CITATION.cff", ".zenodo.json", "codemeta.json", "publication.json",
                 "release-manifest.json", ".release-please-manifest.json", ".latexmkrc"):
        shutil.copy2(source / name, root / name)


def synthetic_inputs(root: Path, *, native_builds: bool, environment: dict[str, str]) -> list[dict]:
    paper = root / "paper"
    # Keep metadata/config/title.tex unchanged: canonical metadata is checked
    # independently before the deliberately synthetic producer fixture runs.
    paper.joinpath("paper.tex").write_text(
        "\\documentclass{article}\n\\pdfinfoomitdate=1\n\\pdftrailerid{synthetic-fixture}\n"
        "\\begin{document}Synthetic publication integration fixture.\\nocite{fixture}\n"
        "\\bibliographystyle{plain}\\bibliography{references}\\end{document}\n")
    paper.joinpath("references.bib").write_text(
        "@book{fixture, title={Synthetic fixture}, author={Fixture, Synthetic}, year={2026}, publisher={Fixture}}\n")
    manifest = json.loads((paper / "00README.json").read_text())
    manifest["sources"] = [{"path": "paper.tex", "usage": "toplevel"}, {"path": "references.bib", "usage": "include"}]
    (paper / "00README.json").write_text(json.dumps(manifest, indent=2) + "\n")
    artifacts = [("paper/.cache/out/paper.pdf", "Synthetic paper"),
                 ("magazine/dist/reflector-magazine.pdf", "Synthetic magazine"),
                 ("magazine/dist/reflector-magazine-print.pdf", "Synthetic print")]
    if native_builds:
        for tool in ("latexmk", "pdflatex"):
            if shutil.which(tool, path=environment["PATH"]) is None:
                raise IntegrationError(f"native-builds: required tool {tool} unavailable")
        for name in ("magazine.tex", "magazine-print.tex"):
            (root / "magazine/tex" / name).write_text(
                "\\documentclass{article}\n\\pdfinfoomitdate=1\n\\pdftrailerid{synthetic-fixture}\n"
                f"\\begin{{document}}Synthetic {name} integration fixture.\\end{{document}}\n")
        command(root, environment, "paper-build", "bash", "scripts/build-paper.sh", "paper")
        command(root, environment, "magazine-build", "bash", "scripts/build-magazine.sh", "build-all")
        status = "passed-synthetic-native"
    else:
        for path, label in artifacts:
            destination = root / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(minimal_pdf(label))
        status = "not-selected-synthetic-artifacts-supplied"
    for path, _label in artifacts:
        if not (root / path).read_bytes().startswith(b"%PDF-"):
            raise IntegrationError(f"native-builds: missing PDF artifact {path}")
    preview = root / "integration-previews"
    preview.mkdir()
    for name in ("paper-cover.webp", "magazine-cover.webp", "print-cover.webp"):
        # Pages staging verifies path/hash composition, not image rendering.
        (preview / name).write_bytes(b"synthetic-preview-path-contract\n")
    return [{"stage": "paper-and-magazine-builds", "status": status}]


def pages_arguments(root: Path) -> list[str]:
    return [sys.executable, "scripts/stage-pages.py", "--project-root", ".", "--docs-dir", "docs",
        "--output-dir", "_site", "--publication-manifest", "publication.json",
        "--paper-pdf", "paper/.cache/out/paper.pdf", "--magazine-pdf", "magazine/dist/reflector-magazine.pdf",
        "--magazine-print-pdf", "magazine/dist/reflector-magazine-print.pdf",
        "--preview-dir", "integration-previews", "--hero", "paper/figures/hero.png",
        "--source-revision", REVISION, "--generated-at", GENERATED_AT]


def run_pipeline(source: Path, root: Path, *, native_builds=False, corrupt_stage=None) -> dict:
    """Run only named local interfaces; caller owns the disposable directory."""
    prepare_fixture(source, root)
    environment = isolated_environment(root)
    stages = []
    command(root, environment, "metadata-validation", sys.executable, "scripts/validate-metadata.py")
    command(root, environment, "version-sync", sys.executable, "scripts/sync-version.py", "--check")
    stages.append({"stage": "metadata-and-version", "status": "passed"})
    # The existing consistency audit reads canonical source copies, before the
    # synthetic producer substitutes the tiny paper/magazine build fixtures.
    command(root, environment, "magazine-consistency", sys.executable, "scripts/audit-magazine-consistency.py",
            "--repo-root", ".", "--output", "integration-consistency.md", "--generated-at", GENERATED_AT)
    stages.append({"stage": "canonical-source-magazine-consistency", "status": "passed"})
    command(root, environment, "fixture-git-init", "git", "-c", "init.defaultBranch=fixture", "init", "--template=", "-q")
    stages.extend(synthetic_inputs(root, native_builds=native_builds, environment=environment))
    version = (root / "VERSION").read_text().strip()
    release = root / "release" / f"reflector-v{version}"
    release.mkdir(parents=True)
    command(root, environment, "arxiv-staging", sys.executable, "scripts/stage_arxiv_submission.py",
            "--source-dir", "paper", "--output-dir", "arxiv-bundle",
            "--zip-output", str(release / f"reflector-arxiv-v{version}.zip"),
            "--tar-output", str(release / f"reflector-arxiv-v{version}.tar.gz"))
    command(root, environment, "arxiv-validation", sys.executable, "scripts/validate-arxiv-packaging.py",
            "--bundle-dir", "arxiv-bundle", "--audit-output", "integration-arxiv.md", "--generated-at", GENERATED_AT)
    stages.append({"stage": "arxiv-closure-and-archives", "status": "passed"})
    # A real local Git archive, with a fixed synthetic commit, not a release.
    command(root, environment, "source-archive-index", "git", "add", "VERSION", "metadata", "paper/paper.tex", "paper/00README.json", "publication.json")
    command(root, environment, "source-archive-commit", "git", "-c", "core.hooksPath=/dev/null", "commit", "-qm", "Synthetic integration fixture")
    command(root, environment, "source-archive", "git", "archive", "--format=zip", "--output=" + str(release / "source.zip"), "HEAD")
    for origin, name in (("paper/.cache/out/paper.pdf", "reflector.pdf"),
                         ("magazine/dist/reflector-magazine.pdf", "reflector-magazine.pdf"),
                         ("magazine/dist/reflector-magazine-print.pdf", "reflector-magazine-print.pdf"),
                         ("publication.json", "publication.json"), ("integration-arxiv.md", "arxiv-validation.md"),
                         ("integration-consistency.md", "magazine-consistency.md")):
        shutil.copyfile(root / origin, release / name)
    required = sorted(p.name for p in release.iterdir())
    if corrupt_stage == "release-missing":
        (release / "reflector.pdf").unlink()
    publication = json.loads((root / "publication.json").read_text())
    identifiers = publication["future"]["doi_generation"]
    args = [sys.executable, "scripts/stage-publication-release.py", "--release-dir", str(release),
        "--version", version, "--tag", f"v{version}", "--paper-name", "reflector",
        "--repository", "egohygiene/reflector", "--commit", REVISION, "--generated-at", GENERATED_AT,
        "--doi", identifiers["doi"], "--doi-url", identifiers["doi_url"],
        "--concept-doi", identifiers["concept_doi"], "--concept-doi-url", identifiers["concept_doi_url"],
        "--pages-base-url", publication["pages_url"]]
    for name in required:
        args.extend(["--require", name])
    command(root, environment, "release-staging", *args)
    if corrupt_stage == "checksum":
        (release / "reflector.pdf").write_bytes(b"corrupted synthetic artifact")
    command(release, environment, "checksum-verification", "sha256sum", "--check", "checksums.txt")
    stages.append({"stage": "release-manifest-checksums-and-inventory", "status": "passed"})
    command(root, environment, "pages-staging", *pages_arguments(root))
    if corrupt_stage == "pages":
        (root / "_site/reflector.pdf").write_bytes(b"corrupted staged PDF")
    command(root, environment, "pages-validation", *pages_arguments(root), "--validate-only")
    command(root / "_site", environment, "pages-checksum-verification", "sha256sum", "--check", "SHA256SUMS")
    if (root / "_site/publication.json").read_bytes() != (root / "publication.json").read_bytes():
        raise IntegrationError("cross-surface-consistency: publication manifest changed")
    for name in ("reflector.pdf", "reflector-magazine.pdf", "reflector-magazine-print.pdf"):
        if sha256(release / name) != sha256(root / "_site" / name):
            raise IntegrationError(f"cross-surface-consistency: divergent artifact {name}")
    manifest = json.loads((release / "release-manifest.json").read_text())
    if manifest["version"] != publication["version"] or manifest["tag"] != publication["release_tag"]:
        raise IntegrationError("cross-surface-consistency: release version/tag differs")
    stages.append({"stage": "pages-and-cross-surface-consistency", "status": "passed"})
    artifacts = {str(p.relative_to(root)): sha256(p) for base in (release, root / "_site")
                 for p in sorted(base.rglob("*")) if p.is_file()}
    return {"schema": "reflector.publication-integration/v1", "fixture": "synthetic",
        "status": "passed", "native_fixture_builds": native_builds, "stages": stages,
        "artifacts": dict(sorted(artifacts.items())),
        "interface_sha256": {name: sha256(source / "scripts" / name) for name in (
            "validate-metadata.py", "sync-version.py", "audit-magazine-consistency.py", "build-paper.sh",
            "build-magazine.sh", "stage_arxiv_submission.py", "validate_arxiv_packaging.py",
            "stage-publication-release.py", "stage-pages.py")},
        "excluded": ["Full manuscript/editorial readiness and bibliography/native publication qualification",
            "Preview image rasterization and browser/device rendering",
            "Workflow-inline source archive, release notes, chktex and Zenodo readiness composition",
            "GitHub Actions setup/upload/deployment and real Git tags/releases",
            "Zenodo deposition and arXiv submission"],
        "network": "No network commands selected; no provider credentials inherited"}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-fixture-builds", action="store_true", help="Require actual tiny-fixture TeX builds; never the canonical manuscript")
    parser.add_argument("--report", type=Path, help="Write a new evidence file; existing receipts are refused")
    args = parser.parse_args(argv)
    try:
        with tempfile.TemporaryDirectory(prefix="reflector-publication-integration-") as temporary:
            result = run_pipeline(ROOT, Path(temporary), native_builds=args.native_fixture_builds)
        content = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.report:
            with args.report.open("x", encoding="utf-8") as handle:
                handle.write(content)
        print(content, end="")
        return 0
    except (IntegrationError, OSError, ValueError, KeyError) as error:
        print(f"Publication integration failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
