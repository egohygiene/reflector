# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Tests for the reflector CLI (reflector/cli/main.py).

Covers:
- Root help output and version flag.
- Each implemented command: run, synchronize, audit, milestone, status, huggingface.
- Valid argument parsing, missing required arguments, and invalid values.
- Exit status behavior.
- Error reporting for bad parameters.
- Filesystem effects produced by the audit command.
"""

from __future__ import annotations

import io
import json
from pathlib import Path
from unittest.mock import patch

import pytest
from rich.console import Console
from typer.testing import CliRunner

from reflector.cli.main import app

runner = CliRunner()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_console() -> tuple[Console, io.StringIO]:
    """Return a Rich Console that writes to an in-memory buffer."""
    buf = io.StringIO()
    con = Console(file=buf, highlight=False, markup=False, no_color=True)
    return con, buf


# ---------------------------------------------------------------------------
# Root-level help and version
# ---------------------------------------------------------------------------


def test_root_help_lists_commands() -> None:
    """Root --help should exit 0 and list all known commands."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    # Typer renders command names in the help text.
    for cmd in ("run", "synchronize", "audit", "milestone", "status", "huggingface"):
        assert cmd in result.output


def test_version_flag_exits_zero() -> None:
    """--version flag should print the version and exit 0."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "reflector" in result.output


def test_no_args_shows_help() -> None:
    """Invoking the CLI without arguments should show help text."""
    result = runner.invoke(app, [])
    # no_args_is_help=True: typer exits with 0 normally but may use 2 in test runner.
    assert result.exit_code in (0, 2)
    assert "reflector" in result.output


# ---------------------------------------------------------------------------
# run command
# ---------------------------------------------------------------------------


def test_run_help() -> None:
    result = runner.invoke(app, ["run", "--help"])
    assert result.exit_code == 0
    assert "dry-run" in result.output or "dry_run" in result.output or "dry" in result.output


def test_run_dry_run_exits_zero() -> None:
    """run --dry-run should complete without error."""
    con, _ = _make_console()
    with patch("reflector.cli.main.console", con):
        result = runner.invoke(app, ["run", "--dry-run"])
    assert result.exit_code == 0
    assert result.exception is None


def test_run_with_milestone_exits_zero() -> None:
    """run --milestone M1 should complete without error."""
    con, _ = _make_console()
    with patch("reflector.cli.main.console", con):
        result = runner.invoke(app, ["run", "--milestone", "M1"])
    assert result.exit_code == 0
    assert result.exception is None


# ---------------------------------------------------------------------------
# synchronize command
# ---------------------------------------------------------------------------


def test_synchronize_help() -> None:
    result = runner.invoke(app, ["synchronize", "--help"])
    assert result.exit_code == 0
    assert "boundary" in result.output.lower() or "synchroniz" in result.output.lower()


def test_synchronize_list_boundaries_exits_zero() -> None:
    """synchronize --list should display boundaries and exit 0."""
    con, buf = _make_console()
    with patch("reflector.cli.main.console", con):
        result = runner.invoke(app, ["synchronize", "--list"])
    assert result.exit_code == 0
    assert result.exception is None
    output = buf.getvalue()
    # Should contain at least one boundary id from the example boundaries.
    assert "SB-" in output


def test_synchronize_no_args_shows_active_boundaries() -> None:
    """synchronize with no args should evaluate all boundaries and exit 0."""
    con, buf = _make_console()
    with patch("reflector.cli.main.console", con):
        result = runner.invoke(app, ["synchronize"])
    assert result.exit_code == 0
    assert result.exception is None


def test_synchronize_with_known_boundary_id() -> None:
    """synchronize SB-001 should render that specific boundary."""
    con, buf = _make_console()
    with patch("reflector.cli.main.console", con):
        result = runner.invoke(app, ["synchronize", "SB-001"])
    assert result.exit_code == 0
    assert result.exception is None
    output = buf.getvalue()
    assert "SB-001" in output


def test_synchronize_with_unknown_boundary_id_exits_zero() -> None:
    """synchronize with an unknown ID should report not-found but still exit 0."""
    con, buf = _make_console()
    with patch("reflector.cli.main.console", con):
        result = runner.invoke(app, ["synchronize", "SB-UNKNOWN"])
    assert result.exit_code == 0
    assert result.exception is None
    output = buf.getvalue()
    assert "SB-UNKNOWN" in output or "No boundary" in output


def test_sync_alias_exits_zero() -> None:
    """sync (alias for synchronize) should behave identically."""
    con, _ = _make_console()
    with patch("reflector.cli.main.console", con):
        result = runner.invoke(app, ["sync", "--list"])
    assert result.exit_code == 0
    assert result.exception is None


# ---------------------------------------------------------------------------
# audit command
# ---------------------------------------------------------------------------


def test_audit_help() -> None:
    result = runner.invoke(app, ["audit", "--help"])
    assert result.exit_code == 0
    assert "output" in result.output.lower() or "verbose" in result.output.lower()


def test_audit_runs_and_exits_zero() -> None:
    """audit with no options should run pipeline and exit 0."""
    con, _ = _make_console()
    with patch("reflector.cli.main.console", con):
        result = runner.invoke(app, ["audit"])
    assert result.exit_code == 0
    assert result.exception is None


def test_audit_verbose_flag_exits_zero() -> None:
    """audit --verbose should run with extra output and exit 0."""
    con, _ = _make_console()
    with patch("reflector.cli.main.console", con):
        result = runner.invoke(app, ["audit", "--verbose"])
    assert result.exit_code == 0
    assert result.exception is None


def test_audit_output_writes_json_file(tmp_path: Path) -> None:
    """audit --output <path> should write a valid JSON audit report."""
    out_file = tmp_path / "report.json"
    con, _ = _make_console()
    with patch("reflector.cli.main.console", con):
        result = runner.invoke(app, ["audit", "--output", str(out_file)])
    assert result.exit_code == 0
    assert result.exception is None
    assert out_file.is_file()
    report = json.loads(out_file.read_text(encoding="utf-8"))
    # The AuditReport has a known set of fields.
    assert "overall_result" in report
    assert "total_entries" in report
    assert "entries" in report


def test_audit_output_short_flag_writes_json_file(tmp_path: Path) -> None:
    """audit -o <path> should also write a valid JSON audit report."""
    out_file = tmp_path / "report_short.json"
    con, _ = _make_console()
    with patch("reflector.cli.main.console", con):
        result = runner.invoke(app, ["audit", "-o", str(out_file)])
    assert result.exit_code == 0
    assert out_file.is_file()


# ---------------------------------------------------------------------------
# milestone command
# ---------------------------------------------------------------------------


def test_milestone_help() -> None:
    result = runner.invoke(app, ["milestone", "--help"])
    assert result.exit_code == 0
    assert "list" in result.output.lower() or "advance" in result.output.lower()


def test_milestone_list_exits_zero() -> None:
    """milestone --list should render a table and exit 0."""
    con, buf = _make_console()
    with patch("reflector.cli.main.console", con):
        result = runner.invoke(app, ["milestone", "--list"])
    assert result.exit_code == 0
    assert result.exception is None
    output = buf.getvalue()
    # Example milestones M1, M2, M3 should appear.
    assert "M1" in output
    assert "M2" in output
    assert "M3" in output


def test_milestone_inspect_known_id() -> None:
    """milestone M1 should render milestone details and exit 0."""
    con, buf = _make_console()
    with patch("reflector.cli.main.console", con):
        result = runner.invoke(app, ["milestone", "M1"])
    assert result.exit_code == 0
    assert result.exception is None
    output = buf.getvalue()
    assert "M1" in output


def test_milestone_inspect_unknown_id() -> None:
    """milestone UNKNOWN should report not-found and exit 0."""
    con, buf = _make_console()
    with patch("reflector.cli.main.console", con):
        result = runner.invoke(app, ["milestone", "UNKNOWN"])
    assert result.exit_code == 0
    assert result.exception is None
    output = buf.getvalue()
    assert "UNKNOWN" in output or "not found" in output.lower()


def test_milestone_advance_exits_zero() -> None:
    """milestone M1 --advance should advance the milestone and exit 0."""
    con, _ = _make_console()
    with patch("reflector.cli.main.console", con):
        result = runner.invoke(app, ["milestone", "M1", "--advance"])
    assert result.exit_code == 0
    assert result.exception is None


def test_milestone_no_id_shows_hint() -> None:
    """milestone with no ID and no flags should surface a usage hint."""
    con, buf = _make_console()
    with patch("reflector.cli.main.console", con):
        result = runner.invoke(app, ["milestone"])
    assert result.exit_code == 0
    output = buf.getvalue()
    assert "list" in output.lower() or "No milestone" in output or "milestone" in output.lower()


# ---------------------------------------------------------------------------
# status command
# ---------------------------------------------------------------------------


def test_status_help() -> None:
    result = runner.invoke(app, ["status", "--help"])
    assert result.exit_code == 0


def test_status_exits_zero() -> None:
    """status should render a summary table and exit 0."""
    con, buf = _make_console()
    with patch("reflector.cli.main.console", con):
        result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert result.exception is None
    output = buf.getvalue()
    # Status table should include known component names.
    assert "Workflow" in output or "status" in output.lower()


# ---------------------------------------------------------------------------
# huggingface command
# ---------------------------------------------------------------------------


def test_huggingface_help() -> None:
    result = runner.invoke(app, ["huggingface", "--help"])
    assert result.exit_code == 0
    assert "metadata" in result.output.lower() or "check-sdk" in result.output.lower()


def test_huggingface_missing_metadata_file_raises_bad_parameter() -> None:
    """huggingface with a non-existent metadata file should raise BadParameter."""
    con, _ = _make_console()
    with patch("reflector.cli.main.console", con):
        result = runner.invoke(app, ["huggingface", "--metadata", "/nonexistent/path.yaml"])
    # Typer.BadParameter exits with code 2.
    assert result.exit_code == 2


def test_huggingface_valid_metadata_exits_zero(tmp_path: Path) -> None:
    """huggingface with a valid metadata file should display config and exit 0."""
    metadata = tmp_path / "repository.yaml"
    metadata.write_text(
        "future_integrations:\n  huggingface:\n    enabled: true\n",
        encoding="utf-8",
    )
    con, buf = _make_console()
    with patch("reflector.cli.main.console", con):
        result = runner.invoke(app, ["huggingface", "--metadata", str(metadata)])
    assert result.exit_code == 0
    assert result.exception is None
    output = buf.getvalue()
    assert "yes" in output.lower() or "enabled" in output.lower() or "Enabled" in output


def test_huggingface_disabled_metadata(tmp_path: Path) -> None:
    """huggingface with disabled integration shows 'no' for enabled."""
    metadata = tmp_path / "repository.yaml"
    metadata.write_text(
        "future_integrations:\n  huggingface:\n    enabled: false\n",
        encoding="utf-8",
    )
    con, buf = _make_console()
    with patch("reflector.cli.main.console", con):
        result = runner.invoke(app, ["huggingface", "--metadata", str(metadata)])
    assert result.exit_code == 0
    output = buf.getvalue()
    assert "no" in output.lower() or "false" in output.lower()


def test_huggingface_check_sdk_flag(tmp_path: Path) -> None:
    """huggingface --check-sdk should include SDK status in output."""
    metadata = tmp_path / "repository.yaml"
    metadata.write_text(
        "future_integrations:\n  huggingface:\n    enabled: true\n",
        encoding="utf-8",
    )
    con, buf = _make_console()
    with patch("reflector.cli.main.console", con):
        result = runner.invoke(
            app, ["huggingface", "--metadata", str(metadata), "--check-sdk"]
        )
    assert result.exit_code == 0
    output = buf.getvalue()
    # SDK installed row should appear regardless of whether SDK is installed.
    assert "sdk" in output.lower() or "installed" in output.lower()
