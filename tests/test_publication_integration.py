# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Exercise actual publication interfaces, never publication providers."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import time

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("publication_integration", ROOT / "scripts/publication_integration.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


@pytest.mark.integration
def test_composed_production_interfaces_are_deterministic_and_cleaned(tmp_path):
    before = {name: (ROOT / name).read_bytes() for name in ("VERSION", "publication.json", "paper/paper.tex")}
    roots = []
    with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
        roots = [Path(first), Path(second)]
        a = MODULE.run_pipeline(ROOT, roots[0])
        b = MODULE.run_pipeline(ROOT, roots[1])
        assert a == b
        assert a["status"] == "passed"
        assert a["fixture"] == "synthetic"
        assert a["native_fixture_builds"] is False
        assert a["stages"][2]["status"] == "not-selected-synthetic-artifacts-supplied"
        assert len(a["artifacts"]) > 20
        text = json.dumps(a)
        assert first not in text and second not in text
        assert not any(name.endswith((".tmp", ".log")) for name in a["artifacts"])
    assert all(not root.exists() for root in roots)
    assert before == {name: (ROOT / name).read_bytes() for name in before}


@pytest.mark.integration
@pytest.mark.parametrize("corruption,stage", [
    ("release-missing", "release-staging"),
    ("checksum", "checksum-verification"),
    ("pages", "pages-validation"),
])
def test_real_missing_and_corrupted_artifacts_fail_at_named_stage(tmp_path, corruption, stage):
    with pytest.raises(MODULE.IntegrationError, match=stage) as error:
        MODULE.run_pipeline(ROOT, tmp_path, corrupt_stage=corruption)
    assert "reflector.pdf" in str(error.value)
    assert str(tmp_path) not in str(error.value)


def test_environment_excludes_provider_credentials_and_private_configuration(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_TOKEN", "synthetic-provider-canary")
    monkeypatch.setenv("GITHUB_TOKEN", "synthetic-provider-canary")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "synthetic-provider-canary")
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("TEXINPUTS", "/synthetic-private-source")
    environment = MODULE.isolated_environment(tmp_path)
    assert "synthetic-provider-canary" not in json.dumps(environment)
    assert "GIT_CONFIG_COUNT" not in environment and "TEXINPUTS" not in environment
    assert environment["GIT_TERMINAL_PROMPT"] == "0"


@pytest.mark.skipif(os.name != "posix", reason="Descendant deadline contract uses POSIX process groups")
def test_command_timeout_stops_descendant_before_fixture_cleanup(tmp_path, monkeypatch):
    monkeypatch.setattr(MODULE, "COMMAND_TIMEOUT", 1)
    marker = tmp_path / "unexpected-descendant-write"
    child = "import time; from pathlib import Path; time.sleep(1.5); Path(" + repr(str(marker)) + ").touch()"
    parent = "import subprocess,sys,time;subprocess.Popen([sys.executable,'-c'," + repr(child) + "]);time.sleep(20)"
    with pytest.raises(MODULE.IntegrationError, match="synthetic-timeout"):
        MODULE.command(tmp_path, MODULE.isolated_environment(tmp_path), "synthetic-timeout", sys.executable, "-c", parent)
    time.sleep(0.7)
    assert not marker.exists()


def test_existing_receipt_is_never_replaced(tmp_path, monkeypatch):
    receipt = tmp_path / "receipt.json"
    receipt.write_text("existing evidence\n")
    monkeypatch.setattr(MODULE, "run_pipeline", lambda *args, **kwargs: {"status": "passed"})
    assert MODULE.main(["--report", str(receipt)]) == 1
    assert receipt.read_text() == "existing evidence\n"


def test_cli_cleans_disposable_workspace_after_a_failed_stage(monkeypatch):
    seen = []
    def fail(source, root, **options):
        seen.append(root)
        (root / "partial-stage-output").write_text("synthetic")
        raise MODULE.IntegrationError("synthetic-stage: deliberate failure")
    monkeypatch.setattr(MODULE, "run_pipeline", fail)
    assert MODULE.main([]) == 1
    assert seen and all(not root.exists() for root in seen)


def test_synthetic_pdf_has_valid_cross_reference_offsets():
    document = MODULE.minimal_pdf("Synthetic fixture")
    offset = int(document.split(b"startxref\n")[1].splitlines()[0])
    assert document[offset:].startswith(b"xref\n")
    assert document.endswith(b"%%EOF\n")


def test_consistency_report_has_an_explicit_deterministic_clock(tmp_path):
    spec = importlib.util.spec_from_file_location("integration_magazine_audit", ROOT / "scripts/audit-magazine-consistency.py")
    assert spec and spec.loader
    audit = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = audit
    spec.loader.exec_module(audit)
    first, second = tmp_path / "first.md", tmp_path / "second.md"
    audit.write_report([], [], first, MODULE.GENERATED_AT)
    audit.write_report([], [], second, MODULE.GENERATED_AT)
    assert first.read_bytes() == second.read_bytes()
    for invalid in ("", "not-a-time", "2026-02-30T00:00:00Z", "2026-11-14T00:00:00+00:00"):
        with pytest.raises(ValueError):
            audit.write_report([], [], tmp_path / "invalid.md", invalid)
