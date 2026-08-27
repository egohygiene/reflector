# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_validate_release_lifecycle_passes() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        [sys.executable, "scripts/validate-release-lifecycle.py"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_publication_workflow_treats_pages_checks_as_advisory() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    workflow = (repo_root / ".github" / "workflows" / "publication.yml").read_text(encoding="utf-8")

    assert "GitHub Pages deployment is asynchronous" in workflow
    assert "Continuing with release asset validation." in workflow
    assert "GitHub Pages publishes from a separate workflow." in workflow
    assert "ROUTES=(" in workflow
    assert 'printf \'Checking <%s>\\n\' "${url}"' in workflow
    assert "Shell-escaped URL" in workflow
    assert "Malformed validation base URL" in workflow
    assert "Malformed validation URL" in workflow
    assert "curl_status=$?" in workflow


def test_pages_workflow_publishes_canonical_manifest_and_required_routes() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    workflow = (repo_root / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")

    assert "pull_request:" in workflow
    assert 'python3 "scripts/stage-pages.py"' in workflow
    assert '"paper-cover=.pages-inputs/reflector.pdf"' in workflow
    assert '"magazine-cover=.pages-inputs/reflector-magazine.pdf"' in workflow
    assert '"print-cover=.pages-inputs/reflector-magazine-print.pdf"' in workflow
    assert '"_site/publication.json"' in workflow
    assert "site.json?revision=" in workflow
    assert '"_site/SHA256SUMS"' in workflow
    assert 'cmp --silent "publication.json" "_site/publication.json"' in workflow
    assert 'sha256sum --check --strict "SHA256SUMS"' in workflow


def test_pages_workflow_keeps_build_metadata_out_of_publication_manifest() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    workflow = (repo_root / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")

    assert "Inject build metadata into published manifest" not in workflow
    assert 'cp "${ROOT_MANIFEST}" "${DOCS_MANIFEST}"' not in workflow
    assert "SOURCE_DATE_EPOCH" in workflow
    assert "metadata/releases" in workflow
    assert "checksums_asset" in workflow
    assert "site.json" in workflow
    assert 'rm --force "_site/.reflector-pages-owned"' in workflow
    assert '"_fallback-routes.tsv"' in workflow


def test_pages_workflow_deploys_only_from_main_with_job_scoped_permissions() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    workflow = (repo_root / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")

    assert "permissions:\n  contents: read" in workflow
    assert "if: github.event_name != 'pull_request' && github.ref == 'refs/heads/main'" in workflow
    assert "      id-token: write" in workflow
    assert "      pages: write" in workflow
    assert "actions/deploy-pages@cd2ce8fcbc39b97be8ca5fce6e763baed58fa128" in workflow


def test_template_pages_workflow_validates_clean_urls_from_slug_routes() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    workflow = (repo_root / "template" / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")

    assert "print(manifest['slug'])" in workflow
    assert "ROUTES=(" in workflow
    assert '"${SLUG}.pdf"' in workflow
    assert 'printf \'Checking <%s>\\n\' "${url}"' in workflow
    assert "Shell-escaped URL" in workflow
    assert "Malformed validation base URL" in workflow
    assert "Malformed validation URL" in workflow
