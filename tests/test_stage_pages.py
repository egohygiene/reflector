# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve().parent.parent / "scripts" / "stage-pages.py"
REPOSITORY_ROOT = SCRIPT_PATH.parent.parent
SPEC = importlib.util.spec_from_file_location("stage_pages", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

CANONICAL_URL = "https://reflector.egohygiene.io/"
FALLBACK_URL = "https://egohygiene.github.io/reflector/"
SOURCE_REVISION = "a" * 40
GENERATED_AT = "2026-08-27T00:00:00Z"


def write_json(path: Path, value: Any) -> None:
    """Write stable fixture JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def route_html(route: str, title: str) -> str:
    """Return one complete, accessible publication-route fixture."""

    canonical = CANONICAL_URL.rstrip("/") + route
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <link rel="canonical" href="{canonical}">
  <link rel="manifest" href="/site.webmanifest">
  <meta property="og:title" content="{title}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{CANONICAL_URL}previews/paper-cover.webp">
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "WebPage",
    "name": "{title}",
    "url": "{canonical}"
  }}
  </script>
</head>
<body>
  <a class="skip-link" href="#content">Skip to content</a>
  <main id="content" tabindex="-1">
    <h1>{title}</h1>
    <nav aria-label="Publication routes">
      <a href="/">Hub</a>
      <a href="/paper/">Paper</a>
      <a href="/magazine/">Magazine</a>
      <a href="/magazine/print/">Print edition</a>
      <a href="/downloads/">Downloads</a>
      <a href="/publication.json">Publication manifest</a>
      <a href="/site.json">Site catalog</a>
      <a href="/SHA256SUMS">Checksums</a>
      <a href="/reflector.pdf">Paper PDF</a>
      <a href="/reflector-magazine.pdf">Magazine PDF</a>
      <a href="/reflector-magazine-print.pdf">Print PDF</a>
      <a href="https://doi.org/10.5281/zenodo.20477044">DOI</a>
      <a href="https://github.com/egohygiene/reflector">Source</a>
    </nav>
  </main>
</body>
</html>
"""


def publication_manifest() -> dict[str, Any]:
    """Return the protected publication fixture."""

    return {
        "project": "reflector",
        "status": "draft",
        "version": "0.1.2",
        "release_tag": "v0.1.2",
        "repository_url": "https://github.com/egohygiene/reflector",
        "pages_url": CANONICAL_URL,
        "orcid": "https://orcid.org/0009-0008-5291-9795",
        "release_channel": "github-releases",
        "version_source": "VERSION",
        "citation_source": "CITATION.cff",
        "artifacts": {
            "paper": {
                "pdf": "reflector.pdf",
                "pages_url": CANONICAL_URL + "reflector.pdf",
            },
            "magazine": {
                "pdf": "reflector-magazine.pdf",
                "print_pdf": "reflector-magazine-print.pdf",
                "pages_url": CANONICAL_URL + "reflector-magazine.pdf",
                "print_pages_url": CANONICAL_URL + "reflector-magazine-print.pdf",
            },
        },
        "future": {
            "doi_generation": {
                "enabled": True,
                "provider": "zenodo",
                "doi": "10.5281/zenodo.20477044",
                "doi_url": "https://doi.org/10.5281/zenodo.20477044",
                "concept_doi": "10.5281/zenodo.20477045",
                "concept_doi_url": "https://doi.org/10.5281/zenodo.20477045",
            }
        },
    }


def create_fixture(root: Path) -> None:
    """Create a small but complete Reflector publication workspace."""

    docs = root / "docs"
    route_files = {
        "index.html": ("/", "Reflector publication hub"),
        "paper/index.html": ("/paper/", "Reflector paper"),
        "magazine/index.html": ("/magazine/", "Reflector magazine"),
        "magazine/print/index.html": (
            "/magazine/print/",
            "Reflector print edition",
        ),
        "downloads/index.html": ("/downloads/", "Reflector downloads"),
    }
    for relative_path, (route, title) in route_files.items():
        path = docs / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(route_html(route, title), encoding="utf-8")

    (docs / "CNAME").write_text("reflector.egohygiene.io\n", encoding="utf-8")
    (docs / "icon.png").write_bytes(b"fixture-icon")
    write_json(
        docs / "site.webmanifest",
        {
            "name": "reflector",
            "short_name": "reflector",
            "start_url": "./",
            "scope": "./",
            "display": "standalone",
            "icons": [
                {
                    "src": "icon.png",
                    "sizes": "192x192",
                    "type": "image/png",
                }
            ],
        },
    )
    write_json(root / "publication.json", publication_manifest())

    build_dir = root / "build"
    build_dir.mkdir(parents=True)
    (build_dir / "paper.pdf").write_bytes(b"%PDF-1.7\npaper-fixture\n")
    (build_dir / "magazine.pdf").write_bytes(b"%PDF-1.7\nmagazine-fixture\n")
    (build_dir / "magazine-print.pdf").write_bytes(
        b"%PDF-1.7\nmagazine-print-fixture\n"
    )

    previews = root / "generated-previews"
    previews.mkdir()
    (previews / "paper-cover.webp").write_bytes(b"paper-preview")
    (previews / "magazine-cover.webp").write_bytes(b"magazine-preview")
    (previews / "print-cover.webp").write_bytes(b"print-preview")

    hero = root / "paper" / "figures" / "hero.png"
    hero.parent.mkdir(parents=True)
    hero.write_bytes(b"hero-image")


def stage_arguments(root: Path, output_name: str = "_site") -> list[str]:
    """Return the standard CLI argument set for one fixture."""

    return [
        "--project-root",
        str(root),
        "--docs-dir",
        "docs",
        "--output-dir",
        output_name,
        "--publication-manifest",
        "publication.json",
        "--paper-pdf",
        "build/paper.pdf",
        "--magazine-pdf",
        "build/magazine.pdf",
        "--magazine-print-pdf",
        "build/magazine-print.pdf",
        "--preview-dir",
        "generated-previews",
        "--hero",
        "paper/figures/hero.png",
        "--source-revision",
        SOURCE_REVISION,
        "--generated-at",
        GENERATED_AT,
    ]


def tree_bytes(root: Path) -> dict[str, bytes]:
    """Return all regular files as a stable relative-path byte mapping."""

    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


class StagePagesTests(unittest.TestCase):
    """Exercise the deterministic and safe Pages staging boundary."""

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        create_fixture(self.root)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_stages_complete_catalog_and_preserves_protected_bytes(self) -> None:
        source_manifest = (self.root / "publication.json").read_bytes()

        result = MODULE.main(stage_arguments(self.root))

        self.assertEqual(result, 0)
        site = self.root / "_site"
        self.assertEqual((site / "publication.json").read_bytes(), source_manifest)
        self.assertEqual(
            (site / "reflector.pdf").read_bytes(),
            (self.root / "build" / "paper.pdf").read_bytes(),
        )
        self.assertEqual(
            (site / "reflector-magazine.pdf").read_bytes(),
            (self.root / "build" / "magazine.pdf").read_bytes(),
        )
        self.assertEqual(
            (site / "reflector-magazine-print.pdf").read_bytes(),
            (self.root / "build" / "magazine-print.pdf").read_bytes(),
        )

        catalog = json.loads((site / "site.json").read_text(encoding="utf-8"))
        self.assertEqual(catalog["canonical_url"], CANONICAL_URL)
        self.assertEqual(catalog["fallback_url"], FALLBACK_URL)
        self.assertEqual(catalog["source_revision"], SOURCE_REVISION)
        self.assertEqual(catalog["generated_at"], GENERATED_AT)
        self.assertEqual(catalog["publication"]["version"], "0.1.2")
        self.assertEqual(catalog["publication"]["doi"], "10.5281/zenodo.20477044")
        self.assertEqual(
            [(route["path"], route["status"]) for route in catalog["routes"]],
            [(route, "available") for _route_id, route, _physical, _label in MODULE.ROUTES],
        )

        checksum_lines = (site / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
        checksum_paths = [line.split("  ", 1)[1] for line in checksum_lines]
        expected_paths = sorted(
            path.relative_to(site).as_posix()
            for path in site.rglob("*")
            if path.is_file()
            and path.relative_to(site).as_posix()
            not in {"SHA256SUMS", MODULE.OWNER_MARKER}
        )
        self.assertEqual(checksum_paths, expected_paths)
        self.assertNotIn(MODULE.OWNER_MARKER, checksum_paths)

        validate_result = MODULE.main(stage_arguments(self.root) + ["--validate-only"])
        self.assertEqual(validate_result, 0)

    def test_repository_site_source_satisfies_staging_contract(self) -> None:
        shutil.rmtree(self.root / "docs")
        shutil.copytree(REPOSITORY_ROOT / "docs", self.root / "docs")
        shutil.copyfile(
            REPOSITORY_ROOT / "publication.json",
            self.root / "publication.json",
        )

        result = MODULE.main(stage_arguments(self.root))

        self.assertEqual(result, 0)

    def test_checksum_inventory_covers_nested_same_named_file(self) -> None:
        nested_checksum = self.root / "docs" / "assets" / "SHA256SUMS"
        nested_checksum.parent.mkdir(parents=True)
        nested_checksum.write_text("reference-only\n", encoding="utf-8")

        result = MODULE.main(stage_arguments(self.root))

        self.assertEqual(result, 0)
        checksum_lines = (self.root / "_site" / "SHA256SUMS").read_text(
            encoding="utf-8"
        ).splitlines()
        checksum_paths = [line.split("  ", 1)[1] for line in checksum_lines]
        self.assertIn("assets/SHA256SUMS", checksum_paths)

    def test_repeated_staging_is_byte_for_byte_deterministic(self) -> None:
        first_result = MODULE.main(stage_arguments(self.root, "_site-first"))
        second_result = MODULE.main(stage_arguments(self.root, "_site-second"))

        self.assertEqual(first_result, 0)
        self.assertEqual(second_result, 0)
        self.assertEqual(
            tree_bytes(self.root / "_site-first"),
            tree_bytes(self.root / "_site-second"),
        )

    def test_owned_output_is_replaced_without_retaining_stale_files(self) -> None:
        self.assertEqual(MODULE.main(stage_arguments(self.root)), 0)
        stale_path = self.root / "_site" / "stale.txt"
        stale_path.write_text("stale\n", encoding="utf-8")

        result = MODULE.main(stage_arguments(self.root))

        self.assertEqual(result, 0)
        self.assertFalse(stale_path.exists())

    def test_failed_replacement_preserves_previous_valid_output(self) -> None:
        self.assertEqual(MODULE.main(stage_arguments(self.root)), 0)
        original_tree = tree_bytes(self.root / "_site")
        paper_page = self.root / "docs" / "paper" / "index.html"
        paper_page.write_text(
            paper_page.read_text(encoding="utf-8").replace(
                CANONICAL_URL + "paper/",
                FALLBACK_URL + "paper/",
                1,
            ),
            encoding="utf-8",
        )

        result = MODULE.main(stage_arguments(self.root))

        self.assertEqual(result, 1)
        self.assertEqual(tree_bytes(self.root / "_site"), original_tree)

    def test_missing_native_artifact_fails_without_creating_output(self) -> None:
        (self.root / "build" / "magazine-print.pdf").unlink()

        result = MODULE.main(stage_arguments(self.root))

        self.assertEqual(result, 1)
        self.assertFalse((self.root / "_site").exists())

    def test_publication_url_drift_is_rejected(self) -> None:
        manifest_path = self.root / "publication.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["pages_url"] = FALLBACK_URL
        write_json(manifest_path, manifest)

        result = MODULE.main(stage_arguments(self.root))

        self.assertEqual(result, 1)
        self.assertFalse((self.root / "_site").exists())

    def test_root_absolute_web_manifest_scope_is_rejected(self) -> None:
        manifest_path = self.root / "docs" / "site.webmanifest"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["start_url"] = "/"
        manifest["scope"] = "/"
        write_json(manifest_path, manifest)

        result = MODULE.main(stage_arguments(self.root))

        self.assertEqual(result, 1)
        self.assertFalse((self.root / "_site").exists())

    def test_broken_local_fragment_is_rejected(self) -> None:
        index_path = self.root / "docs" / "index.html"
        index_path.write_text(
            index_path.read_text(encoding="utf-8").replace(
                "</nav>",
                '<a href="/paper/#missing-section">Missing section</a></nav>',
            ),
            encoding="utf-8",
        )

        result = MODULE.main(stage_arguments(self.root))

        self.assertEqual(result, 1)
        self.assertFalse((self.root / "_site").exists())

    def test_unowned_output_is_refused_and_preserved(self) -> None:
        output = self.root / "_site"
        output.mkdir()
        sentinel = output / "keep.txt"
        sentinel.write_text("do not replace\n", encoding="utf-8")

        result = MODULE.main(stage_arguments(self.root))

        self.assertEqual(result, 1)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "do not replace\n")

    def test_source_directory_cannot_be_selected_as_output(self) -> None:
        sentinel = self.root / "docs" / "index.html"
        original = sentinel.read_bytes()
        args = stage_arguments(self.root)
        output_index = args.index("--output-dir") + 1
        args[output_index] = "docs"

        result = MODULE.main(args)

        self.assertEqual(result, 1)
        self.assertEqual(sentinel.read_bytes(), original)

    def test_validate_only_detects_staged_artifact_tampering(self) -> None:
        self.assertEqual(MODULE.main(stage_arguments(self.root)), 0)
        with (self.root / "_site" / "reflector.pdf").open("ab") as handle:
            handle.write(b"tampered")

        result = MODULE.main(stage_arguments(self.root) + ["--validate-only"])

        self.assertEqual(result, 1)

    def test_rejects_noncanonical_source_revision(self) -> None:
        args = stage_arguments(self.root)
        revision_index = args.index("--source-revision") + 1
        args[revision_index] = "abc123"

        result = MODULE.main(args)

        self.assertEqual(result, 1)
        self.assertFalse((self.root / "_site").exists())


if __name__ == "__main__":
    unittest.main()
