# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


SCRIPT_PATH = Path(__file__).resolve().parent.parent / "scripts" / "sync-version.py"
REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def run_sync(
    *extra_args: str,
    repo_root: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(SCRIPT_PATH), *extra_args]
    if repo_root is not None:
        cmd += ["--repo-root", str(repo_root)]
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def make_repo(
    tmp_path: Path,
    version: str,
    pub_yaml_version: str | None = None,
    citation_version: str | None = None,
    zenodo_version: str | None = None,
    codemeta_version: str | None = None,
    pub_json_version: str | None = None,
    pub_json_tag: str | None = None,
    release_manifest_version: str | None = None,
    rp_manifest_version: str | None = None,
) -> Path:
    """Create a minimal fake repository tree for isolated sync tests."""
    (tmp_path / "VERSION").write_text(version + "\n", encoding="utf-8")

    pub_yaml = {
        "title": {"main": "test"},
        "version": pub_yaml_version if pub_yaml_version is not None else version,
    }
    (tmp_path / "metadata").mkdir()
    (tmp_path / "metadata" / "publication.yaml").write_text(
        yaml.dump(pub_yaml), encoding="utf-8"
    )

    citation = {
        "cff-version": "1.2.0",
        "version": citation_version if citation_version is not None else version,
    }
    (tmp_path / "CITATION.cff").write_text(
        yaml.dump(citation), encoding="utf-8"
    )

    zenodo = {
        "title": "test",
        "version": zenodo_version if zenodo_version is not None else version,
    }
    (tmp_path / ".zenodo.json").write_text(
        json.dumps(zenodo, indent=2), encoding="utf-8"
    )

    codemeta = {
        "name": "test",
        "version": codemeta_version if codemeta_version is not None else version,
    }
    (tmp_path / "codemeta.json").write_text(
        json.dumps(codemeta, indent=2), encoding="utf-8"
    )

    pub_json = {
        "project": "test",
        "version": pub_json_version if pub_json_version is not None else version,
        "release_tag": pub_json_tag if pub_json_tag is not None else f"v{version}",
    }
    (tmp_path / "publication.json").write_text(
        json.dumps(pub_json, indent=2), encoding="utf-8"
    )

    release_manifest = {
        "schema_version": "1.0.0",
        "current_version": (
            release_manifest_version
            if release_manifest_version is not None
            else version
        ),
    }
    (tmp_path / "release-manifest.json").write_text(
        json.dumps(release_manifest, indent=2), encoding="utf-8"
    )

    rp_manifest = {
        ".": rp_manifest_version if rp_manifest_version is not None else version
    }
    (tmp_path / ".release-please-manifest.json").write_text(
        json.dumps(rp_manifest, indent=2), encoding="utf-8"
    )

    return tmp_path


# ---------------------------------------------------------------------------
# Live-repo integration tests
# ---------------------------------------------------------------------------


def test_check_mode_passes_on_live_repo() -> None:
    """sync-version.py --check must pass on the live repository."""
    result = run_sync("--check")
    assert result.returncode == 0, result.stdout + result.stderr


def test_apply_mode_is_noop_on_live_repo() -> None:
    """sync-version.py apply must report no changes needed on the live repo."""
    result = run_sync()
    assert result.returncode == 0, result.stdout + result.stderr
    assert "already synchronized" in result.stdout or "no changes" in result.stdout.lower()


# ---------------------------------------------------------------------------
# Isolated unit tests using tmp_path
# ---------------------------------------------------------------------------


def test_check_detects_drift_in_publication_yaml(tmp_path: Path) -> None:
    make_repo(tmp_path, "1.2.3", pub_yaml_version="1.0.0")
    result = run_sync("--check", repo_root=tmp_path)
    assert result.returncode == 1
    assert "publication.yaml" in result.stdout
    assert "DRIFT" in result.stdout


def test_check_detects_drift_in_zenodo_json(tmp_path: Path) -> None:
    make_repo(tmp_path, "1.2.3", zenodo_version="1.0.0")
    result = run_sync("--check", repo_root=tmp_path)
    assert result.returncode == 1
    assert ".zenodo.json" in result.stdout


def test_check_detects_drift_in_codemeta_json(tmp_path: Path) -> None:
    make_repo(tmp_path, "1.2.3", codemeta_version="1.0.0")
    result = run_sync("--check", repo_root=tmp_path)
    assert result.returncode == 1
    assert "codemeta.json" in result.stdout


def test_check_detects_drift_in_publication_json_version(tmp_path: Path) -> None:
    make_repo(tmp_path, "1.2.3", pub_json_version="1.0.0")
    result = run_sync("--check", repo_root=tmp_path)
    assert result.returncode == 1
    assert "publication.json" in result.stdout


def test_check_detects_drift_in_publication_json_release_tag(tmp_path: Path) -> None:
    make_repo(tmp_path, "1.2.3", pub_json_tag="v1.0.0")
    result = run_sync("--check", repo_root=tmp_path)
    assert result.returncode == 1
    assert "publication.json" in result.stdout


def test_check_detects_drift_in_release_manifest(tmp_path: Path) -> None:
    make_repo(tmp_path, "1.2.3", release_manifest_version="1.0.0")
    result = run_sync("--check", repo_root=tmp_path)
    assert result.returncode == 1
    assert "release-manifest.json" in result.stdout


def test_check_detects_drift_in_rp_manifest(tmp_path: Path) -> None:
    make_repo(tmp_path, "1.2.3", rp_manifest_version="1.0.0")
    result = run_sync("--check", repo_root=tmp_path)
    assert result.returncode == 1
    assert ".release-please-manifest.json" in result.stdout


def test_apply_updates_drifted_surfaces(tmp_path: Path) -> None:
    make_repo(
        tmp_path,
        "2.0.0",
        pub_yaml_version="1.0.0",
        zenodo_version="1.0.0",
        codemeta_version="1.0.0",
        pub_json_version="1.0.0",
        pub_json_tag="v1.0.0",
        release_manifest_version="1.0.0",
        rp_manifest_version="1.0.0",
    )

    result = run_sync(repo_root=tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr

    # Verify all surfaces were updated.
    pub_yaml = yaml.safe_load(
        (tmp_path / "metadata" / "publication.yaml").read_text(encoding="utf-8")
    )
    assert pub_yaml["version"] == "2.0.0"

    zenodo = json.loads((tmp_path / ".zenodo.json").read_text(encoding="utf-8"))
    assert zenodo["version"] == "2.0.0"

    codemeta = json.loads((tmp_path / "codemeta.json").read_text(encoding="utf-8"))
    assert codemeta["version"] == "2.0.0"

    pub_json = json.loads((tmp_path / "publication.json").read_text(encoding="utf-8"))
    assert pub_json["version"] == "2.0.0"
    assert pub_json["release_tag"] == "v2.0.0"

    release_manifest = json.loads(
        (tmp_path / "release-manifest.json").read_text(encoding="utf-8")
    )
    assert release_manifest["current_version"] == "2.0.0"

    rp_manifest = json.loads(
        (tmp_path / ".release-please-manifest.json").read_text(encoding="utf-8")
    )
    assert rp_manifest["."] == "2.0.0"


def test_apply_is_idempotent(tmp_path: Path) -> None:
    make_repo(tmp_path, "3.0.0")
    run_sync(repo_root=tmp_path)
    result = run_sync(repo_root=tmp_path)
    assert result.returncode == 0
    assert "already synchronized" in result.stdout


def test_version_override_flag(tmp_path: Path) -> None:
    make_repo(tmp_path, "1.0.0")
    result = run_sync("--version", "5.0.0", repo_root=tmp_path)
    assert result.returncode == 0

    pub_json = json.loads((tmp_path / "publication.json").read_text(encoding="utf-8"))
    assert pub_json["version"] == "5.0.0"
    assert pub_json["release_tag"] == "v5.0.0"


def test_invalid_version_rejected(tmp_path: Path) -> None:
    make_repo(tmp_path, "1.0.0")
    result = run_sync("--version", "notaversion", repo_root=tmp_path)
    assert result.returncode == 1


def test_check_passes_when_all_synchronized(tmp_path: Path) -> None:
    make_repo(tmp_path, "4.5.6")
    result = run_sync("--check", repo_root=tmp_path)
    assert result.returncode == 0
    assert "synchronized" in result.stdout
