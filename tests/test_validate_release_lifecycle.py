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
