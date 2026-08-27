#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Stage and validate the deterministic Reflector GitHub Pages artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import posixpath
import re
import shutil
import sys
import tempfile
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from urllib.parse import unquote, urlsplit


CANONICAL_URL = "https://reflector.egohygiene.io/"
FALLBACK_URL = "https://egohygiene.github.io/reflector/"
CUSTOM_DOMAIN = "reflector.egohygiene.io"
PROJECT_NAME = "reflector"
REPOSITORY_URL = "https://github.com/egohygiene/reflector"
OWNER_MARKER = ".reflector-pages-owned"
OWNER_MARKER_CONTENT = {
    "owner": "reflector-pages",
    "schema_version": "1.0.0",
}
CHECKSUM_PATH = "SHA256SUMS"
REQUIRED_PREVIEWS = (
    "paper-cover.webp",
    "magazine-cover.webp",
    "print-cover.webp",
)
ARTIFACTS = (
    (
        "paper",
        "reflector.pdf",
        "/paper/",
        "Paper PDF",
    ),
    (
        "magazine",
        "reflector-magazine.pdf",
        "/magazine/",
        "Digital magazine PDF",
    ),
    (
        "magazine_print",
        "reflector-magazine-print.pdf",
        "/magazine/print/",
        "Print magazine PDF",
    ),
)
ROUTES = (
    ("hub", "/", "index.html", "Publication hub"),
    ("paper", "/paper/", "paper/index.html", "Paper reader"),
    ("magazine", "/magazine/", "magazine/index.html", "Digital magazine reader"),
    (
        "magazine_print",
        "/magazine/print/",
        "magazine/print/index.html",
        "Print edition landing",
    ),
    ("downloads", "/downloads/", "downloads/index.html", "Publication downloads"),
    (
        "publication_manifest",
        "/publication.json",
        "publication.json",
        "Publication manifest",
    ),
    ("site_catalog", "/site.json", "site.json", "Site catalog"),
    ("checksums", "/SHA256SUMS", CHECKSUM_PATH, "Checksum inventory"),
    ("paper_pdf", "/reflector.pdf", "reflector.pdf", "Paper PDF alias"),
    (
        "magazine_pdf",
        "/reflector-magazine.pdf",
        "reflector-magazine.pdf",
        "Digital magazine PDF alias",
    ),
    (
        "magazine_print_pdf",
        "/reflector-magazine-print.pdf",
        "reflector-magazine-print.pdf",
        "Print magazine PDF alias",
    ),
)
HTML_ROUTE_FILES = {
    physical_path: route
    for _route_id, route, physical_path, _label in ROUTES
    if physical_path.endswith(".html")
}
REVISION_PATTERN = re.compile(r"^[0-9a-f]{40}$")
DOI_PATTERN = re.compile(r"^10\.\d{4,9}/\S+$")


class StageError(RuntimeError):
    """Raised when Pages staging or validation cannot safely continue."""


@dataclass(frozen=True)
class StageInputs:
    """Resolved and validated Pages staging inputs."""

    project_root: Path
    docs_dir: Path
    output_dir: Path
    publication_manifest: Path
    paper_pdf: Path
    magazine_pdf: Path
    magazine_print_pdf: Path
    preview_dir: Path
    hero: Path
    source_revision: str
    generated_at: str

    @property
    def artifact_sources(self) -> dict[str, Path]:
        """Return canonical output filenames mapped to native artifact sources."""

        return {
            "reflector.pdf": self.paper_pdf,
            "reflector-magazine.pdf": self.magazine_pdf,
            "reflector-magazine-print.pdf": self.magazine_print_pdf,
        }


class PublicationHTMLParser(HTMLParser):
    """Collect the small HTML contract required by the publication hub."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.html_lang = ""
        self.title_parts: list[str] = []
        self._inside_title = False
        self.h1_count = 0
        self.main_content_count = 0
        self.skip_link_count = 0
        self.canonical_urls: list[str] = []
        self.open_graph: dict[str, list[str]] = {}
        self.ids: list[str] = []
        self.links: list[str] = []
        self.json_ld_blocks: list[str] = []
        self._inside_json_ld = False
        self._json_ld_parts: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        attributes = {name.lower(): value or "" for name, value in attrs}
        lowered_tag = tag.lower()

        if lowered_tag == "html":
            self.html_lang = attributes.get("lang", "").strip()
        if lowered_tag == "title":
            self._inside_title = True
        if lowered_tag == "h1":
            self.h1_count += 1
        if lowered_tag == "main" and attributes.get("id") == "content":
            self.main_content_count += 1
        if lowered_tag == "a" and attributes.get("href") == "#content":
            self.skip_link_count += 1

        element_id = attributes.get("id", "").strip()
        if element_id:
            self.ids.append(element_id)

        if lowered_tag == "link":
            rel_values = set(attributes.get("rel", "").lower().split())
            if "canonical" in rel_values:
                self.canonical_urls.append(attributes.get("href", "").strip())

        if lowered_tag == "meta":
            property_name = attributes.get("property", "").lower().strip()
            if property_name.startswith("og:"):
                self.open_graph.setdefault(property_name, []).append(
                    attributes.get("content", "").strip()
                )

        if lowered_tag == "script" and attributes.get("type", "").lower() == "application/ld+json":
            self._inside_json_ld = True
            self._json_ld_parts = []

        for attribute_name in ("href", "src", "poster", "action"):
            value = attributes.get(attribute_name, "").strip()
            if value:
                self.links.append(value)
        srcset = attributes.get("srcset", "").strip()
        if srcset:
            for candidate in srcset.split(","):
                source = candidate.strip().split(" ", 1)[0]
                if source:
                    self.links.append(source)

    def handle_endtag(self, tag: str) -> None:
        lowered_tag = tag.lower()
        if lowered_tag == "title":
            self._inside_title = False
        if lowered_tag == "script" and self._inside_json_ld:
            self.json_ld_blocks.append("".join(self._json_ld_parts).strip())
            self._inside_json_ld = False
            self._json_ld_parts = []

    def handle_data(self, data: str) -> None:
        if self._inside_title:
            self.title_parts.append(data)
        if self._inside_json_ld:
            self._json_ld_parts.append(data)

    @property
    def title(self) -> str:
        """Return normalized title text."""

        return " ".join("".join(self.title_parts).split())


def log(message: str) -> None:
    """Print one namespaced status line."""

    print(f"[stage-pages] {message}")


def sha256_for_file(path: Path) -> str:
    """Return the SHA-256 digest for one file."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_bytes(value: Any) -> bytes:
    """Serialize deterministic, human-readable JSON."""

    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def load_json(path: Path, label: str) -> dict[str, Any]:
    """Load a JSON object or raise a focused staging error."""

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise StageError(f"Missing {label}: {path}.") from error
    except json.JSONDecodeError as error:
        raise StageError(
            f"Invalid JSON in {label} {path} at line {error.lineno}, "
            f"column {error.colno}: {error.msg}."
        ) from error
    if not isinstance(value, dict):
        raise StageError(f"Expected a JSON object in {label}: {path}.")
    return value


def normalize_generated_at(value: str) -> str:
    """Normalize a supplied timestamp to deterministic UTC RFC 3339 form."""

    candidate = value.strip()
    if not candidate:
        raise StageError("--generated-at must not be empty.")
    try:
        parsed = datetime.fromisoformat(candidate.replace("Z", "+00:00"))
    except ValueError as error:
        raise StageError(
            "--generated-at must be an ISO 8601 timestamp with an explicit timezone."
        ) from error
    if parsed.tzinfo is None:
        raise StageError("--generated-at must include an explicit timezone.")
    normalized = parsed.astimezone(timezone.utc).replace(microsecond=0)
    return normalized.isoformat().replace("+00:00", "Z")


def resolve_input_path(project_root: Path, value: str, label: str, *, directory: bool) -> Path:
    """Resolve one existing input and ensure that it stays inside the project."""

    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = project_root / candidate
    if candidate.is_symlink():
        raise StageError(f"{label} must not be a symlink: {candidate}.")
    try:
        resolved = candidate.resolve(strict=True)
    except FileNotFoundError as error:
        raise StageError(f"Missing {label}: {candidate}.") from error
    try:
        resolved.relative_to(project_root)
    except ValueError as error:
        raise StageError(f"{label} escapes the project root: {resolved}.") from error
    if directory and not resolved.is_dir():
        raise StageError(f"{label} must be a directory: {resolved}.")
    if not directory and not resolved.is_file():
        raise StageError(f"{label} must be a file: {resolved}.")
    return resolved


def resolve_output_path(project_root: Path, value: str) -> Path:
    """Resolve and constrain the generated output directory."""

    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = project_root / candidate
    resolved = candidate.resolve(strict=False)
    try:
        relative = resolved.relative_to(project_root)
    except ValueError as error:
        raise StageError(f"Output directory escapes the project root: {resolved}.") from error
    if len(relative.parts) != 1:
        raise StageError(
            "Output directory must be a dedicated project-root child named "
            "_site, _site-*, or .reflector-pages-*."
        )
    name = relative.name
    if not (
        name == "_site"
        or name.startswith("_site-")
        or name.startswith(".reflector-pages-")
    ):
        raise StageError(
            "Unsafe output directory name. Use _site, _site-*, or .reflector-pages-*."
        )
    return resolved


def assert_no_symlinks(root: Path, label: str) -> None:
    """Reject symlinks so copied inputs cannot change meaning during staging."""

    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise StageError(f"{label} contains a symlink, which is not allowed: {path}.")


def read_owner_marker(output_dir: Path) -> dict[str, Any] | None:
    """Read an existing output ownership marker when it is valid JSON."""

    marker = output_dir / OWNER_MARKER
    if not marker.is_file() or marker.is_symlink():
        return None
    try:
        value = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def validate_existing_output(output_dir: Path) -> None:
    """Refuse replacement of any output not explicitly owned by this script."""

    if not output_dir.exists():
        return
    if output_dir.is_symlink() or not output_dir.is_dir():
        raise StageError(f"Refusing to replace unsafe output path: {output_dir}.")
    if read_owner_marker(output_dir) != OWNER_MARKER_CONTENT:
        raise StageError(
            f"Refusing to replace unowned output directory: {output_dir}. "
            f"Expected marker {OWNER_MARKER}."
        )


def validate_pdf(path: Path, label: str) -> None:
    """Apply a minimal format/nonempty check to a native PDF artifact."""

    if path.stat().st_size == 0:
        raise StageError(f"{label} is empty: {path}.")
    with path.open("rb") as handle:
        if handle.read(5) != b"%PDF-":
            raise StageError(f"{label} does not begin with a PDF header: {path}.")


def validate_publication_manifest(manifest: dict[str, Any]) -> None:
    """Validate the protected publication identity and artifact contract."""

    required_values = {
        "project": PROJECT_NAME,
        "repository_url": REPOSITORY_URL,
        "pages_url": CANONICAL_URL,
        "version_source": "VERSION",
    }
    for field, expected in required_values.items():
        actual = manifest.get(field)
        if actual != expected:
            raise StageError(
                f"publication.json {field} must equal {expected!r}; found {actual!r}."
            )

    version = manifest.get("version")
    release_tag = manifest.get("release_tag")
    status = manifest.get("status")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise StageError("publication.json version must be semantic version MAJOR.MINOR.PATCH.")
    if release_tag != f"v{version}":
        raise StageError(
            f"publication.json release_tag must equal 'v{version}'; found {release_tag!r}."
        )
    if not isinstance(status, str) or not status.strip():
        raise StageError("publication.json status must be a nonempty string.")

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        raise StageError("publication.json artifacts must be an object.")
    paper = artifacts.get("paper")
    magazine = artifacts.get("magazine")
    if not isinstance(paper, dict) or not isinstance(magazine, dict):
        raise StageError("publication.json must declare paper and magazine artifacts.")
    expected_artifact_values = {
        "artifacts.paper.pdf": (paper.get("pdf"), "reflector.pdf"),
        "artifacts.paper.pages_url": (
            paper.get("pages_url"),
            CANONICAL_URL + "reflector.pdf",
        ),
        "artifacts.magazine.pdf": (
            magazine.get("pdf"),
            "reflector-magazine.pdf",
        ),
        "artifacts.magazine.print_pdf": (
            magazine.get("print_pdf"),
            "reflector-magazine-print.pdf",
        ),
        "artifacts.magazine.pages_url": (
            magazine.get("pages_url"),
            CANONICAL_URL + "reflector-magazine.pdf",
        ),
        "artifacts.magazine.print_pages_url": (
            magazine.get("print_pages_url"),
            CANONICAL_URL + "reflector-magazine-print.pdf",
        ),
    }
    for field, (actual, expected) in expected_artifact_values.items():
        if actual != expected:
            raise StageError(
                f"publication.json {field} must equal {expected!r}; found {actual!r}."
            )

    doi_metadata = manifest.get("future", {}).get("doi_generation", {})
    if not isinstance(doi_metadata, dict):
        raise StageError("publication.json future.doi_generation must be an object.")
    doi = doi_metadata.get("doi")
    doi_url = doi_metadata.get("doi_url")
    if not isinstance(doi, str) or not DOI_PATTERN.fullmatch(doi):
        raise StageError("publication.json must contain a valid DOI.")
    if doi_url != f"https://doi.org/{doi}":
        raise StageError("publication.json DOI and DOI URL do not agree.")


def canonical_for_route(route: str) -> str:
    """Build the canonical custom-domain URL for a public route."""

    return CANONICAL_URL.rstrip("/") + route


def recursive_values_for_key(value: Any, key: str) -> Iterable[Any]:
    """Yield values for a JSON key at any nesting level."""

    if isinstance(value, dict):
        for item_key, item_value in value.items():
            if item_key == key:
                yield item_value
            yield from recursive_values_for_key(item_value, key)
    elif isinstance(value, list):
        for item in value:
            yield from recursive_values_for_key(item, key)


def recursive_strings(value: Any) -> Iterable[str]:
    """Yield every string stored in a JSON-compatible value."""

    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from recursive_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from recursive_strings(item)


def parse_html(path: Path) -> PublicationHTMLParser:
    """Parse HTML and convert parser errors into staging errors."""

    parser = PublicationHTMLParser()
    try:
        parser.feed(path.read_text(encoding="utf-8"))
        parser.close()
    except (OSError, UnicodeDecodeError) as error:
        raise StageError(f"Unable to parse HTML file {path}: {error}.") from error
    return parser


def validate_html_contract(path: Path, route: str) -> PublicationHTMLParser:
    """Validate canonical metadata and baseline accessibility for one route."""

    parser = parse_html(path)
    expected_canonical = canonical_for_route(route)

    if parser.html_lang != "en":
        raise StageError(f"{path} must declare <html lang=\"en\">.")
    if not parser.title:
        raise StageError(f"{path} must contain a nonempty <title>.")
    if parser.h1_count != 1:
        raise StageError(f"{path} must contain exactly one h1; found {parser.h1_count}.")
    if parser.main_content_count != 1:
        raise StageError(f"{path} must contain exactly one <main id=\"content\">.")
    if parser.skip_link_count < 1:
        raise StageError(f"{path} must contain a skip link to #content.")
    duplicate_ids = sorted({item for item in parser.ids if parser.ids.count(item) > 1})
    if duplicate_ids:
        raise StageError(f"{path} contains duplicate ids: {', '.join(duplicate_ids)}.")

    if parser.canonical_urls != [expected_canonical]:
        raise StageError(
            f"{path} must contain exactly one canonical URL {expected_canonical!r}; "
            f"found {parser.canonical_urls!r}."
        )
    if parser.open_graph.get("og:url") != [expected_canonical]:
        raise StageError(
            f"{path} must contain exactly one og:url {expected_canonical!r}."
        )
    og_images = parser.open_graph.get("og:image", [])
    if len(og_images) != 1 or not og_images[0].startswith(CANONICAL_URL):
        raise StageError(
            f"{path} must contain exactly one custom-domain og:image URL."
        )

    if not parser.json_ld_blocks:
        raise StageError(f"{path} must contain JSON-LD structured data.")
    structured_values: list[Any] = []
    for block in parser.json_ld_blocks:
        try:
            structured_values.append(json.loads(block))
        except json.JSONDecodeError as error:
            raise StageError(
                f"Invalid JSON-LD in {path} at line {error.lineno}, "
                f"column {error.colno}: {error.msg}."
            ) from error
    structured_urls = [
        value
        for document in structured_values
        for value in recursive_values_for_key(document, "url")
        if isinstance(value, str)
    ]
    if expected_canonical not in structured_urls:
        raise StageError(
            f"{path} JSON-LD must identify the route URL {expected_canonical!r}."
        )
    if any(
        value.startswith(FALLBACK_URL)
        for document in structured_values
        for value in recursive_strings(document)
    ):
        raise StageError(f"{path} JSON-LD must not use the technical fallback as canonical.")
    return parser


def route_to_file(site_root: Path, source_html: Path, value: str) -> tuple[Path | None, str]:
    """Resolve one local URL to a staged file and fragment."""

    if value.startswith("//"):
        raise StageError(f"Protocol-relative URL is not allowed in {source_html}: {value!r}.")
    parsed = urlsplit(value)
    site_absolute = False
    if parsed.scheme:
        if parsed.scheme not in {"http", "https", "mailto", "tel"}:
            raise StageError(f"Unsupported URL scheme in {source_html}: {value!r}.")
        if parsed.scheme in {"mailto", "tel"}:
            return None, ""
        host = parsed.netloc.lower()
        if host == CUSTOM_DOMAIN:
            raw_path = parsed.path.lstrip("/")
            site_absolute = True
        elif host == "egohygiene.github.io" and (
            parsed.path == "/reflector" or parsed.path.startswith("/reflector/")
        ):
            raw_path = parsed.path.removeprefix("/reflector").lstrip("/")
            site_absolute = True
        else:
            return None, ""
    else:
        raw_path = parsed.path

    if site_absolute:
        relative_path = raw_path
    elif not raw_path:
        relative_path = source_html.relative_to(site_root).as_posix()
    elif raw_path.startswith("/"):
        relative_path = raw_path.lstrip("/")
    else:
        source_parent = source_html.relative_to(site_root).parent.as_posix()
        relative_path = posixpath.join(source_parent, raw_path)

    decoded_path = unquote(relative_path)
    normalized = posixpath.normpath(decoded_path)
    if normalized == ".":
        normalized = ""
    if normalized == ".." or normalized.startswith("../"):
        raise StageError(f"Local URL escapes the staged site in {source_html}: {value!r}.")
    if raw_path.endswith("/") or not normalized:
        normalized = posixpath.join(normalized, "index.html")
    target = site_root / PurePosixPath(normalized)
    if target.is_dir():
        target = target / "index.html"
    return target, unquote(parsed.fragment)


def validate_local_links(site_root: Path) -> None:
    """Validate local HTML links, embedded resources, and target fragments."""

    html_parsers = {
        path.resolve(): parse_html(path)
        for path in sorted(site_root.rglob("*.html"))
    }
    for html_path, parser in html_parsers.items():
        for value in parser.links:
            target, fragment = route_to_file(site_root, html_path, value)
            if target is None:
                continue
            try:
                target.resolve(strict=False).relative_to(site_root.resolve())
            except ValueError as error:
                raise StageError(
                    f"Local URL escapes the staged site in {html_path}: {value!r}."
                ) from error
            if not target.is_file():
                raise StageError(
                    f"Broken local URL in {html_path.relative_to(site_root)}: "
                    f"{value!r} resolves to missing {target.relative_to(site_root)}."
                )
            if fragment:
                if target.suffix.lower() not in {".html", ".htm"}:
                    raise StageError(
                        f"Fragment URL in {html_path.relative_to(site_root)} targets a "
                        f"non-HTML file: {value!r}."
                    )
                target_parser = html_parsers.get(target.resolve())
                if target_parser is None:
                    target_parser = parse_html(target)
                if fragment not in set(target_parser.ids):
                    raise StageError(
                        f"Broken fragment in {html_path.relative_to(site_root)}: "
                        f"{value!r} does not match an id in {target.relative_to(site_root)}."
                    )


def validate_web_manifest(site_root: Path) -> None:
    """Validate root-scoped web-app metadata and icon paths."""

    manifest_path = site_root / "site.webmanifest"
    manifest = load_json(manifest_path, "web manifest")
    if manifest.get("start_url") != "./":
        raise StageError("site.webmanifest start_url must equal './'.")
    if manifest.get("scope") != "./":
        raise StageError("site.webmanifest scope must equal './'.")
    icons = manifest.get("icons", [])
    if not isinstance(icons, list) or not icons:
        raise StageError("site.webmanifest must declare at least one icon.")
    for icon in icons:
        if not isinstance(icon, dict) or not isinstance(icon.get("src"), str):
            raise StageError("site.webmanifest contains an invalid icon declaration.")
        target, _fragment = route_to_file(site_root, site_root / "index.html", icon["src"])
        if target is None:
            raise StageError(
                f"site.webmanifest icon must be a local site asset: {icon['src']!r}."
            )
        if not target.is_file():
            raise StageError(f"site.webmanifest icon is missing: {icon['src']!r}.")


def artifact_record(path: Path, filename: str, reader_route: str, label: str) -> dict[str, Any]:
    """Build one deterministic site-catalog artifact record."""

    return {
        "filename": filename,
        "label": label,
        "media_type": "application/pdf",
        "reader_route": reader_route,
        "sha256": sha256_for_file(path),
        "size_bytes": path.stat().st_size,
        "url": CANONICAL_URL + filename,
    }


def build_site_catalog(
    site_root: Path,
    publication_manifest: dict[str, Any],
    publication_sha256: str,
    source_revision: str,
    generated_at: str,
) -> dict[str, Any]:
    """Derive the deterministic public catalog from protected metadata and files."""

    doi_metadata = publication_manifest["future"]["doi_generation"]
    release_tag = publication_manifest["release_tag"]
    previews = {}
    for preview_name in REQUIRED_PREVIEWS:
        preview_path = site_root / "previews" / preview_name
        preview_id = preview_name.removesuffix(".webp").replace("-", "_")
        previews[preview_id] = {
            "media_type": "image/webp",
            "path": f"previews/{preview_name}",
            "sha256": sha256_for_file(preview_path),
            "size_bytes": preview_path.stat().st_size,
            "url": CANONICAL_URL + f"previews/{preview_name}",
        }

    artifact_records = {
        artifact_id: artifact_record(site_root / filename, filename, reader_route, label)
        for artifact_id, filename, reader_route, label in ARTIFACTS
    }
    hero_path = site_root / "figures" / "hero.png"
    return {
        "artifacts": artifact_records,
        "canonical_url": CANONICAL_URL,
        "checksums": {
            "algorithm": "sha256",
            "path": CHECKSUM_PATH,
        },
        "custom_domain": CUSTOM_DOMAIN,
        "fallback_url": FALLBACK_URL,
        "generated_at": generated_at,
        "hero": {
            "media_type": "image/png",
            "path": "figures/hero.png",
            "sha256": sha256_for_file(hero_path),
            "size_bytes": hero_path.stat().st_size,
            "url": CANONICAL_URL + "figures/hero.png",
        },
        "previews": previews,
        "project": PROJECT_NAME,
        "publication": {
            "doi": doi_metadata["doi"],
            "doi_url": doi_metadata["doi_url"],
            "manifest_path": "publication.json",
            "manifest_sha256": publication_sha256,
            "release_tag": release_tag,
            "release_url": f"{REPOSITORY_URL}/releases/tag/{release_tag}",
            "status": publication_manifest["status"],
            "version": publication_manifest["version"],
        },
        "repository_url": REPOSITORY_URL,
        "routes": [
            {
                "id": route_id,
                "label": label,
                "path": route,
                "physical_path": physical_path,
                "status": "available",
            }
            for route_id, route, physical_path, label in ROUTES
        ],
        "schema_version": "1.0.0",
        "source_revision": source_revision,
    }


def iter_checksum_files(site_root: Path) -> list[Path]:
    """Return the exact publishable-file inventory covered by SHA256SUMS."""

    files: list[Path] = []
    for path in site_root.rglob("*"):
        if path.is_symlink():
            raise StageError(f"Staged site contains a forbidden symlink: {path}.")
        relative_path = path.relative_to(site_root).as_posix()
        if path.is_file() and relative_path not in {CHECKSUM_PATH, OWNER_MARKER}:
            files.append(path)
    return sorted(files, key=lambda path: path.relative_to(site_root).as_posix())


def write_checksums(site_root: Path) -> None:
    """Write the complete, stable staged-site checksum inventory."""

    lines = [
        f"{sha256_for_file(path)}  {path.relative_to(site_root).as_posix()}"
        for path in iter_checksum_files(site_root)
    ]
    (site_root / CHECKSUM_PATH).write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate_checksums(site_root: Path) -> None:
    """Verify checksum ordering, coverage, and every recorded digest."""

    checksum_file = site_root / CHECKSUM_PATH
    try:
        lines = checksum_file.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as error:
        raise StageError(f"Missing staged checksum inventory: {checksum_file}.") from error
    expected_files = [
        path.relative_to(site_root).as_posix() for path in iter_checksum_files(site_root)
    ]
    parsed: dict[str, str] = {}
    for line in lines:
        parts = line.split("  ", 1)
        if len(parts) != 2 or not re.fullmatch(r"[0-9a-f]{64}", parts[0]):
            raise StageError(f"Invalid SHA256SUMS entry: {line!r}.")
        digest, relative_path = parts
        if relative_path in parsed:
            raise StageError(f"Duplicate SHA256SUMS path: {relative_path}.")
        parsed[relative_path] = digest
    if list(parsed) != expected_files:
        raise StageError(
            "SHA256SUMS must cover every staged file exactly once in sorted order."
        )
    for relative_path, expected_digest in parsed.items():
        actual_digest = sha256_for_file(site_root / PurePosixPath(relative_path))
        if actual_digest != expected_digest:
            raise StageError(
                f"SHA256SUMS mismatch for {relative_path}: expected "
                f"{expected_digest}, found {actual_digest}."
            )


def validate_catalog(site_root: Path, inputs: StageInputs, manifest: dict[str, Any]) -> None:
    """Validate the generated catalog against protected metadata and staged bytes."""

    catalog = load_json(site_root / "site.json", "site catalog")
    expected_catalog = build_site_catalog(
        site_root,
        manifest,
        sha256_for_file(inputs.publication_manifest),
        inputs.source_revision,
        inputs.generated_at,
    )
    if catalog != expected_catalog:
        raise StageError("site.json does not match the deterministic derived catalog.")
    actual_routes = [
        (item.get("id"), item.get("path"), item.get("physical_path"), item.get("status"))
        for item in catalog.get("routes", [])
        if isinstance(item, dict)
    ]
    expected_routes = [
        (route_id, route, physical_path, "available")
        for route_id, route, physical_path, _label in ROUTES
    ]
    if actual_routes != expected_routes:
        raise StageError("site.json route/status catalog does not match the public contract.")


def validate_staged_site(site_root: Path, inputs: StageInputs) -> None:
    """Run the full publication-site integrity contract."""

    if site_root.is_symlink() or not site_root.is_dir():
        raise StageError(f"Staged site must be a real directory: {site_root}.")
    assert_no_symlinks(site_root, "Staged site")

    marker = read_owner_marker(site_root)
    if marker != OWNER_MARKER_CONTENT:
        raise StageError(f"Staged site is missing valid ownership marker {OWNER_MARKER}.")
    cname = site_root / "CNAME"
    if cname.read_text(encoding="utf-8").strip() != CUSTOM_DOMAIN:
        raise StageError(f"CNAME must contain exactly {CUSTOM_DOMAIN!r}.")

    for _route_id, _route, physical_path, _label in ROUTES:
        required_path = site_root / PurePosixPath(physical_path)
        if not required_path.is_file() or required_path.stat().st_size == 0:
            raise StageError(f"Required public route file is missing or empty: {physical_path}.")

    source_manifest_bytes = inputs.publication_manifest.read_bytes()
    staged_manifest_path = site_root / "publication.json"
    if staged_manifest_path.read_bytes() != source_manifest_bytes:
        raise StageError("Staged publication.json must be byte-for-byte identical to its source.")
    manifest = load_json(staged_manifest_path, "staged publication manifest")
    validate_publication_manifest(manifest)

    for filename, source in inputs.artifact_sources.items():
        staged = site_root / filename
        validate_pdf(staged, filename)
        if sha256_for_file(source) != sha256_for_file(staged):
            raise StageError(f"Staged {filename} does not match its native source artifact.")
    for preview_name in REQUIRED_PREVIEWS:
        source = inputs.preview_dir / preview_name
        staged = site_root / "previews" / preview_name
        if sha256_for_file(source) != sha256_for_file(staged):
            raise StageError(f"Staged preview {preview_name} does not match its source.")
    if sha256_for_file(inputs.hero) != sha256_for_file(site_root / "figures" / "hero.png"):
        raise StageError("Staged hero image does not match its source.")

    validate_catalog(site_root, inputs, manifest)
    for physical_path, route in HTML_ROUTE_FILES.items():
        validate_html_contract(site_root / physical_path, route)
    validate_local_links(site_root)
    validate_web_manifest(site_root)
    validate_checksums(site_root)


def copy_docs_source(docs_dir: Path, site_root: Path) -> None:
    """Copy the repository-owned site source without following symlinks."""

    assert_no_symlinks(docs_dir, "Docs source")
    shutil.copytree(docs_dir, site_root, dirs_exist_ok=True, symlinks=False)


def assemble_site(site_root: Path, inputs: StageInputs) -> None:
    """Assemble, catalog, checksum, and validate one temporary site tree."""

    copy_docs_source(inputs.docs_dir, site_root)

    for generated_name in (
        "site.json",
        CHECKSUM_PATH,
        *inputs.artifact_sources.keys(),
        "publication.json",
    ):
        generated_path = site_root / generated_name
        if generated_path.exists():
            if generated_path.is_dir():
                shutil.rmtree(generated_path)
            else:
                generated_path.unlink()

    (site_root / OWNER_MARKER).write_bytes(json_bytes(OWNER_MARKER_CONTENT))
    for filename, source in inputs.artifact_sources.items():
        validate_pdf(source, f"Native {filename}")
        shutil.copyfile(source, site_root / filename)

    shutil.copyfile(inputs.publication_manifest, site_root / "publication.json")

    staged_previews = site_root / "previews"
    if staged_previews.exists():
        shutil.rmtree(staged_previews)
    shutil.copytree(inputs.preview_dir, staged_previews, symlinks=False)
    for preview_name in REQUIRED_PREVIEWS:
        preview_path = staged_previews / preview_name
        if not preview_path.is_file() or preview_path.stat().st_size == 0:
            raise StageError(f"Required preview is missing or empty: {preview_name}.")

    hero_dir = site_root / "figures"
    hero_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(inputs.hero, hero_dir / "hero.png")

    publication_manifest = load_json(inputs.publication_manifest, "publication manifest")
    validate_publication_manifest(publication_manifest)
    publication_sha256 = sha256_for_file(inputs.publication_manifest)
    catalog = build_site_catalog(
        site_root,
        publication_manifest,
        publication_sha256,
        inputs.source_revision,
        inputs.generated_at,
    )
    (site_root / "site.json").write_bytes(json_bytes(catalog))
    write_checksums(site_root)
    validate_staged_site(site_root, inputs)


def replace_transactionally(staged_dir: Path, output_dir: Path) -> None:
    """Atomically finalize a validated tree while preserving rollback."""

    if not output_dir.exists():
        os.replace(staged_dir, output_dir)
        return

    backup_dir = output_dir.parent / f".reflector-pages-backup-{uuid.uuid4().hex}"
    os.replace(output_dir, backup_dir)
    try:
        os.replace(staged_dir, output_dir)
    except BaseException:
        os.replace(backup_dir, output_dir)
        raise
    shutil.rmtree(backup_dir)


def stage_pages(inputs: StageInputs) -> None:
    """Build and transactionally finalize the Pages artifact."""

    validate_existing_output(inputs.output_dir)
    temporary_path = Path(
        tempfile.mkdtemp(prefix=".reflector-pages-staging-", dir=inputs.project_root)
    )
    try:
        assemble_site(temporary_path, inputs)
        replace_transactionally(temporary_path, inputs.output_dir)
    except BaseException:
        if temporary_path.exists():
            shutil.rmtree(temporary_path)
        raise


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""

    parser = argparse.ArgumentParser(
        description="Stage and validate the deterministic Reflector Pages artifact."
    )
    parser.add_argument("--project-root", default=".", help="Reflector repository root.")
    parser.add_argument(
        "--docs-dir",
        default="docs",
        help="Repository-owned site source directory.",
    )
    parser.add_argument("--output-dir", default="_site", help="Owned Pages output directory.")
    parser.add_argument(
        "--publication-manifest",
        default="publication.json",
        help="Protected publication manifest copied byte-for-byte.",
    )
    parser.add_argument("--paper-pdf", required=True, help="Native reflector paper PDF.")
    parser.add_argument("--magazine-pdf", required=True, help="Native digital magazine PDF.")
    parser.add_argument(
        "--magazine-print-pdf",
        required=True,
        help="Native print magazine PDF.",
    )
    parser.add_argument(
        "--preview-dir",
        required=True,
        help="Directory containing all three WebP previews.",
    )
    parser.add_argument("--hero", required=True, help="Canonical publication hero PNG.")
    parser.add_argument(
        "--source-revision",
        required=True,
        help="Exact 40-character Git source revision represented by the artifact.",
    )
    parser.add_argument(
        "--generated-at",
        required=True,
        help="Explicit timezone-aware generation timestamp.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate an existing owned output without replacing it.",
    )
    return parser


def resolve_inputs(args: argparse.Namespace) -> StageInputs:
    """Resolve CLI values into the safe staging contract."""

    project_root = Path(args.project_root).resolve(strict=True)
    if not project_root.is_dir():
        raise StageError(f"Project root must be a directory: {project_root}.")
    output_dir = resolve_output_path(project_root, args.output_dir)
    docs_dir = resolve_input_path(project_root, args.docs_dir, "docs directory", directory=True)
    publication_manifest = resolve_input_path(
        project_root,
        args.publication_manifest,
        "publication manifest",
        directory=False,
    )
    paper_pdf = resolve_input_path(project_root, args.paper_pdf, "paper PDF", directory=False)
    magazine_pdf = resolve_input_path(
        project_root,
        args.magazine_pdf,
        "magazine PDF",
        directory=False,
    )
    magazine_print_pdf = resolve_input_path(
        project_root,
        args.magazine_print_pdf,
        "print magazine PDF",
        directory=False,
    )
    preview_dir = resolve_input_path(
        project_root,
        args.preview_dir,
        "preview directory",
        directory=True,
    )
    hero = resolve_input_path(project_root, args.hero, "hero image", directory=False)

    if output_dir == docs_dir or output_dir in docs_dir.parents:
        raise StageError("Output directory must not replace or contain the docs source.")
    protected_inputs = {
        docs_dir,
        publication_manifest,
        paper_pdf,
        magazine_pdf,
        magazine_print_pdf,
        preview_dir,
        hero,
    }
    if any(output_dir == path or output_dir in path.parents for path in protected_inputs):
        raise StageError("Output directory overlaps a protected staging input.")

    revision = args.source_revision.strip().lower()
    if not REVISION_PATTERN.fullmatch(revision):
        raise StageError("--source-revision must be exactly 40 lowercase hexadecimal characters.")

    return StageInputs(
        project_root=project_root,
        docs_dir=docs_dir,
        output_dir=output_dir,
        publication_manifest=publication_manifest,
        paper_pdf=paper_pdf,
        magazine_pdf=magazine_pdf,
        magazine_print_pdf=magazine_print_pdf,
        preview_dir=preview_dir,
        hero=hero,
        source_revision=revision,
        generated_at=normalize_generated_at(args.generated_at),
    )


def main(argv: list[str] | None = None) -> int:
    """Stage or validate the complete publication site."""

    try:
        args = build_parser().parse_args(argv)
        inputs = resolve_inputs(args)
        if args.validate_only:
            validate_existing_output(inputs.output_dir)
            validate_staged_site(inputs.output_dir, inputs)
            log(f"validated {inputs.output_dir}")
        else:
            stage_pages(inputs)
            log(f"staged {inputs.output_dir}")
        return 0
    except StageError as error:
        print(f"[stage-pages] ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
