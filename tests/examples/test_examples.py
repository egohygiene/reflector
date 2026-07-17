# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Tests that verify the worked examples in reflector/examples/.

Each test imports and runs the corresponding example function to confirm
that the examples remain executable and produce the expected return values.
Examples are mechanically verified here; output formatting is not asserted.
"""

from __future__ import annotations

from reflector.examples.audit_example import (
    demonstrate_report_interpretation,
    run_audit_example,
)
from reflector.examples.milestone_example import (
    demonstrate_custom_milestone,
    run_milestone_example,
)
from reflector.examples.synchronization_example import (
    demonstrate_custom_boundary,
    run_synchronization_example,
)
from reflector.schemas.audit import AuditReport, CheckResult
from reflector.schemas.milestone import MilestoneStatus


# ---------------------------------------------------------------------------
# Audit example
# ---------------------------------------------------------------------------


def test_audit_example_returns_audit_report() -> None:
    """run_audit_example should return a valid AuditReport instance."""
    report = run_audit_example()
    assert isinstance(report, AuditReport)


def test_audit_example_has_entries() -> None:
    """run_audit_example should produce at least one audit entry."""
    report = run_audit_example()
    assert report.total_entries > 0


def test_audit_example_overall_result_is_valid() -> None:
    """run_audit_example overall_result should be a valid CheckResult."""
    report = run_audit_example()
    assert isinstance(report.overall_result, CheckResult)


def test_audit_example_verbose_mode() -> None:
    """run_audit_example(verbose=True) should still return a valid report."""
    report = run_audit_example(verbose=True)
    assert isinstance(report, AuditReport)


def test_audit_example_demonstrate_interpretation_pass(capsys) -> None:
    """demonstrate_report_interpretation should handle a PASS report."""
    report = run_audit_example()
    demonstrate_report_interpretation(report)
    captured = capsys.readouterr()
    # For the default scaffold (which always passes), check for positive signal.
    assert report.overall_result == CheckResult.PASS
    assert "✅" in captured.out or "passed" in captured.out.lower()


# ---------------------------------------------------------------------------
# Synchronization example
# ---------------------------------------------------------------------------


def test_synchronization_example_returns_dict() -> None:
    """run_synchronization_example should return a summary dict."""
    result = run_synchronization_example()
    assert isinstance(result, dict)
    assert "active_count" in result
    assert "requires_approval" in result


def test_synchronization_example_active_count_is_non_negative() -> None:
    """active_count should be a non-negative integer."""
    result = run_synchronization_example()
    assert isinstance(result["active_count"], int)
    assert result["active_count"] >= 0


def test_synchronization_example_requires_approval_is_bool() -> None:
    """requires_approval should be a boolean."""
    result = run_synchronization_example()
    assert isinstance(result["requires_approval"], bool)


def test_synchronization_example_default_has_active_boundary() -> None:
    """Default example boundaries include SB-001 which is active."""
    result = run_synchronization_example()
    assert result["active_count"] >= 1


def test_synchronization_example_demonstrate_custom_boundary(capsys) -> None:
    """demonstrate_custom_boundary should run without error."""
    demonstrate_custom_boundary()
    captured = capsys.readouterr()
    assert "SB-CUSTOM-001" in captured.out or "Custom" in captured.out


# ---------------------------------------------------------------------------
# Milestone example
# ---------------------------------------------------------------------------


def test_milestone_example_runs_without_error(capsys) -> None:
    """run_milestone_example should complete without raising an exception."""
    run_milestone_example()
    captured = capsys.readouterr()
    assert len(captured.out) > 0


def test_milestone_example_boundary_enforced(capsys) -> None:
    """run_milestone_example should demonstrate the AWAITING_REVIEW boundary."""
    run_milestone_example()
    captured = capsys.readouterr()
    # The example explicitly asserts that the boundary is enforced and prints
    # the confirmation message.
    assert "AWAITING_REVIEW" in captured.out or "boundary" in captured.out.lower()


def test_milestone_example_reaches_complete(capsys) -> None:
    """run_milestone_example should show M2 reaching COMPLETE status."""
    run_milestone_example()
    captured = capsys.readouterr()
    assert "COMPLETE" in captured.out or "complete" in captured.out


def test_milestone_example_demonstrate_custom(capsys) -> None:
    """demonstrate_custom_milestone should run without error."""
    demonstrate_custom_milestone()
    captured = capsys.readouterr()
    assert "CUSTOM-M1" in captured.out or "Feature delivery" in captured.out
