# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Tests for reflector/audits/pipeline.py.

Covers:
- Successful pipeline execution and report structure.
- Invariant validation (pass and fail cases).
- Drift detection logic and threshold behavior.
- Audit trail assembly and aggregation.
- Diagnostic output via print_report.
- Verbose mode event capture.
- Empty and single-entry edge cases.
"""

from __future__ import annotations

import io

import pytest
from rich.console import Console

from reflector.audits.pipeline import AuditPipeline, _DEFAULT_INVARIANTS, _DRIFT_ALERT_THRESHOLD
from reflector.schemas.audit import AuditEntry, AuditReport, CheckResult, InvariantResult


# ---------------------------------------------------------------------------
# Pipeline execution
# ---------------------------------------------------------------------------


def test_pipeline_run_returns_audit_report() -> None:
    """run() should return an AuditReport instance."""
    pipeline = AuditPipeline()
    report = pipeline.run()
    assert isinstance(report, AuditReport)


def test_pipeline_run_has_entries() -> None:
    """Default pipeline run should produce at least one audit entry."""
    pipeline = AuditPipeline()
    report = pipeline.run()
    assert report.total_entries > 0
    assert len(report.entries) == report.total_entries


def test_pipeline_run_overall_result_is_pass_for_default_events() -> None:
    """Default scaffold events should produce an overall PASS result."""
    pipeline = AuditPipeline()
    report = pipeline.run()
    assert report.overall_result == CheckResult.PASS


def test_pipeline_run_has_recommendations() -> None:
    """Report should include at least one recommendation."""
    pipeline = AuditPipeline()
    report = pipeline.run()
    assert len(report.recommendations) >= 1


def test_pipeline_run_pass_count_matches_entries() -> None:
    """pass_count should equal entries where scope_check=PASS and no drift alert."""
    pipeline = AuditPipeline()
    report = pipeline.run()
    expected_pass = sum(
        1 for e in report.entries
        if e.scope_check == CheckResult.PASS and not e.drift_alert
    )
    assert report.pass_count == expected_pass


def test_pipeline_run_fail_count_zero_for_default_events() -> None:
    """Default scaffold events should produce no failures."""
    pipeline = AuditPipeline()
    report = pipeline.run()
    assert report.fail_count == 0


def test_pipeline_run_drift_alerts_zero_for_default_events() -> None:
    """Default scaffold events should not trigger any drift alerts."""
    pipeline = AuditPipeline()
    report = pipeline.run()
    assert report.drift_alerts == 0
    assert report.max_drift_score == 0.0


def test_pipeline_run_verbose_exits_without_error(capsys: pytest.CaptureFixture) -> None:
    """Verbose mode should emit stage info without raising exceptions."""
    pipeline = AuditPipeline(verbose=True)
    report = pipeline.run()
    assert isinstance(report, AuditReport)
    captured = capsys.readouterr()
    assert "Stage 1" in captured.out


# ---------------------------------------------------------------------------
# Stage 1 — Event Capture
# ---------------------------------------------------------------------------


def test_stage_event_capture_returns_list() -> None:
    """_stage_event_capture should return a non-empty list of event dicts."""
    pipeline = AuditPipeline()
    events = pipeline._stage_event_capture()
    assert isinstance(events, list)
    assert len(events) > 0


def test_stage_event_capture_each_event_has_required_keys() -> None:
    """Each event should have at minimum 'action' and 'agent_id' keys."""
    pipeline = AuditPipeline()
    events = pipeline._stage_event_capture()
    for event in events:
        assert "action" in event
        assert "agent_id" in event


# ---------------------------------------------------------------------------
# Stage 2 — Invariant Validation
# ---------------------------------------------------------------------------


def test_stage_invariant_validation_adds_invariants_to_events() -> None:
    """After invariant validation, each event should have an 'invariants' key."""
    pipeline = AuditPipeline()
    events = pipeline._stage_event_capture()
    validated = pipeline._stage_invariant_validation(events)
    for event in validated:
        assert "invariants" in event
        assert isinstance(event["invariants"], list)


def test_stage_invariant_validation_adds_scope_check() -> None:
    """Each validated event should have a 'scope_check' field."""
    pipeline = AuditPipeline()
    events = pipeline._stage_event_capture()
    validated = pipeline._stage_invariant_validation(events)
    for event in validated:
        assert "scope_check" in event
        assert isinstance(event["scope_check"], CheckResult)


def test_stage_invariant_validation_checks_all_default_invariants() -> None:
    """Each event should be validated against all default invariants."""
    pipeline = AuditPipeline()
    events = pipeline._stage_event_capture()
    validated = pipeline._stage_invariant_validation(events)
    expected_ids = {inv["id"] for inv in _DEFAULT_INVARIANTS}
    for event in validated:
        actual_ids = {inv.id for inv in event["invariants"]}
        assert expected_ids == actual_ids


def test_stage_invariant_validation_default_results_are_pass() -> None:
    """Scaffold invariants should all pass for default events."""
    pipeline = AuditPipeline()
    events = pipeline._stage_event_capture()
    validated = pipeline._stage_invariant_validation(events)
    for event in validated:
        for inv in event["invariants"]:
            assert inv.result == CheckResult.PASS


# ---------------------------------------------------------------------------
# Stage 3 — Drift Detection
# ---------------------------------------------------------------------------


def test_stage_drift_detection_adds_drift_score() -> None:
    """Each event should receive a 'drift_score' after drift detection."""
    pipeline = AuditPipeline()
    events = pipeline._stage_event_capture()
    validated = pipeline._stage_invariant_validation(events)
    drifted = pipeline._stage_drift_detection(validated)
    for event in drifted:
        assert "drift_score" in event
        assert isinstance(event["drift_score"], float)


def test_stage_drift_detection_adds_drift_alert_flag() -> None:
    """Each event should receive a 'drift_alert' boolean."""
    pipeline = AuditPipeline()
    events = pipeline._stage_event_capture()
    validated = pipeline._stage_invariant_validation(events)
    drifted = pipeline._stage_drift_detection(validated)
    for event in drifted:
        assert "drift_alert" in event
        assert isinstance(event["drift_alert"], bool)


def test_stage_drift_detection_alert_threshold_constant_is_positive() -> None:
    """The drift alert threshold should be a positive float between 0 and 1."""
    assert 0.0 < _DRIFT_ALERT_THRESHOLD < 1.0


def test_stage_drift_detection_alert_is_false_when_score_at_threshold() -> None:
    """drift_alert should be False when drift_score equals the threshold."""
    event = {"action": "test", "agent_id": "a"}
    event["drift_score"] = _DRIFT_ALERT_THRESHOLD
    result = AuditPipeline._stage_drift_detection([event])
    assert result[0]["drift_alert"] is False


def test_stage_drift_detection_scaffold_events_have_zero_drift() -> None:
    """Default scaffold events should have zero drift."""
    pipeline = AuditPipeline()
    events = pipeline._stage_event_capture()
    validated = pipeline._stage_invariant_validation(events)
    drifted = pipeline._stage_drift_detection(validated)
    for event in drifted:
        assert event["drift_score"] == 0.0


# ---------------------------------------------------------------------------
# Stage 4 — Audit Trail Append
# ---------------------------------------------------------------------------


def test_stage_audit_trail_append_returns_report() -> None:
    """_stage_audit_trail_append should return an AuditReport."""
    pipeline = AuditPipeline()
    events = pipeline._stage_event_capture()
    validated = pipeline._stage_invariant_validation(events)
    drifted = pipeline._stage_drift_detection(validated)
    report = pipeline._stage_audit_trail_append(drifted)
    assert isinstance(report, AuditReport)


def test_stage_audit_trail_entry_count_matches_events() -> None:
    """Number of audit entries should match number of input events."""
    pipeline = AuditPipeline()
    events = pipeline._stage_event_capture()
    validated = pipeline._stage_invariant_validation(events)
    drifted = pipeline._stage_drift_detection(validated)
    report = pipeline._stage_audit_trail_append(drifted)
    assert report.total_entries == len(events)


def test_stage_audit_trail_fail_count_for_scope_violation() -> None:
    """A scope-violation event should produce fail_count=1 and overall FAIL."""
    events = [
        {
            "action": "infra_write",
            "agent_id": "test-agent",
            "target": "infrastructure/main.tf",
            "scope_check": CheckResult.FAIL,
            "invariants": [],
            "drift_score": 0.0,
            "drift_alert": False,
            "milestone": "M1",
            "phase": "scaffold",
        }
    ]
    report = AuditPipeline._stage_audit_trail_append(events)
    assert report.fail_count == 1
    assert report.overall_result == CheckResult.FAIL


def test_stage_audit_trail_warn_for_drift_alert() -> None:
    """A drift-alert event (no scope violation) should produce warn_count=1 and WARN."""
    events = [
        {
            "action": "drift_action",
            "agent_id": "test-agent",
            "target": "reflector/",
            "scope_check": CheckResult.PASS,
            "invariants": [],
            "drift_score": 0.5,
            "drift_alert": True,
            "milestone": "M1",
            "phase": "scaffold",
        }
    ]
    report = AuditPipeline._stage_audit_trail_append(events)
    assert report.drift_alerts == 1
    assert report.overall_result == CheckResult.WARN


def test_stage_audit_trail_empty_events_produces_valid_report() -> None:
    """An empty event list should produce a valid report with zero counts."""
    report = AuditPipeline._stage_audit_trail_append([])
    assert report.total_entries == 0
    assert report.pass_count == 0
    assert report.fail_count == 0
    assert report.warn_count == 0
    assert report.overall_result == CheckResult.PASS


def test_stage_audit_trail_recommendations_on_failure() -> None:
    """Failure events should include an investigative recommendation."""
    events = [
        {
            "action": "violation",
            "agent_id": "a",
            "scope_check": CheckResult.FAIL,
            "invariants": [],
            "drift_score": 0.0,
            "drift_alert": False,
        }
    ]
    report = AuditPipeline._stage_audit_trail_append(events)
    assert any("scope" in r.lower() or "milestone" in r.lower() for r in report.recommendations)


def test_stage_audit_trail_max_drift_score() -> None:
    """max_drift_score should reflect the highest drift score in the entries."""
    events = [
        {
            "action": "a1",
            "agent_id": "a",
            "scope_check": CheckResult.PASS,
            "invariants": [],
            "drift_score": 0.1,
            "drift_alert": False,
        },
        {
            "action": "a2",
            "agent_id": "a",
            "scope_check": CheckResult.PASS,
            "invariants": [],
            "drift_score": 0.4,
            "drift_alert": True,
        },
    ]
    report = AuditPipeline._stage_audit_trail_append(events)
    assert report.max_drift_score == pytest.approx(0.4)


# ---------------------------------------------------------------------------
# print_report
# ---------------------------------------------------------------------------


def test_print_report_renders_without_error() -> None:
    """print_report should complete without raising exceptions."""
    pipeline = AuditPipeline()
    report = pipeline.run()
    buf = io.StringIO()
    console = Console(file=buf, highlight=False, markup=False, no_color=True)
    AuditPipeline.print_report(report, console)
    output = buf.getvalue()
    assert len(output) > 0


def test_print_report_includes_overall_result() -> None:
    """print_report output should mention the overall result."""
    pipeline = AuditPipeline()
    report = pipeline.run()
    buf = io.StringIO()
    console = Console(file=buf, highlight=False, markup=False, no_color=True)
    AuditPipeline.print_report(report, console)
    output = buf.getvalue()
    assert report.overall_result.value in output


def test_print_report_includes_entry_counts() -> None:
    """print_report should show total entry count in the output."""
    pipeline = AuditPipeline()
    report = pipeline.run()
    buf = io.StringIO()
    console = Console(file=buf, highlight=False, markup=False, no_color=True)
    AuditPipeline.print_report(report, console)
    output = buf.getvalue()
    assert str(report.total_entries) in output


def test_print_report_includes_recommendations() -> None:
    """print_report should render the recommendations table when present."""
    pipeline = AuditPipeline()
    report = pipeline.run()
    buf = io.StringIO()
    console = Console(file=buf, highlight=False, markup=False, no_color=True)
    AuditPipeline.print_report(report, console)
    output = buf.getvalue()
    # The default pipeline produces a recommendation — it should appear.
    assert any(rec[:20] in output for rec in report.recommendations)


# ---------------------------------------------------------------------------
# Report field ordering and determinism
# ---------------------------------------------------------------------------


def test_pipeline_run_is_deterministic() -> None:
    """Two consecutive runs should produce the same number of entries and result."""
    p1, p2 = AuditPipeline(), AuditPipeline()
    r1, r2 = p1.run(), p2.run()
    assert r1.total_entries == r2.total_entries
    assert r1.overall_result == r2.overall_result
    assert r1.pass_count == r2.pass_count
    assert r1.fail_count == r2.fail_count
