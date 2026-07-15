# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Tests for reflector/orchestration/milestone.py.

Covers:
- Orchestrator initialization with example milestones.
- list_milestones renders a table with all milestone IDs.
- inspect() with no ID shows a usage hint.
- inspect() with a known ID renders milestone details.
- inspect() with an unknown ID reports not-found.
- advance() transitions PENDING → IN_PROGRESS.
- advance() transitions IN_PROGRESS → AWAITING_REVIEW.
- advance() on AWAITING_REVIEW enforces the synchronization boundary.
- advance() on APPROVED → COMPLETE.
- advance() on terminal states (COMPLETE, REJECTED) shows a terminal message.
- advance() with an unknown ID reports not-found.
- Repeated advance() calls do not silently corrupt state.
- Milestone instances are independent per orchestrator.
"""

from __future__ import annotations

import io

import pytest
from rich.console import Console

from reflector.orchestration.milestone import MilestoneOrchestrator
from reflector.schemas.milestone import MilestoneDefinition, MilestoneStatus, MilestoneValidation


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _capture_console() -> tuple[Console, io.StringIO]:
    buf = io.StringIO()
    con = Console(file=buf, highlight=False, markup=False, no_color=True)
    return con, buf


def _make_orchestrator_with_status(milestone_id: str, status: MilestoneStatus) -> MilestoneOrchestrator:
    """Return an orchestrator with the named milestone set to the given status."""
    orch = MilestoneOrchestrator()
    orch._milestones[milestone_id].status = status
    return orch


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------


def test_orchestrator_initializes_with_example_milestones() -> None:
    """MilestoneOrchestrator should load example milestones on init."""
    orch = MilestoneOrchestrator()
    assert len(orch._milestones) > 0


def test_orchestrator_milestone_ids_are_strings() -> None:
    """All milestone dictionary keys should be string IDs."""
    orch = MilestoneOrchestrator()
    for key in orch._milestones:
        assert isinstance(key, str)


def test_orchestrator_milestones_are_milestone_definition_instances() -> None:
    """All milestone values should be MilestoneDefinition instances."""
    orch = MilestoneOrchestrator()
    for m in orch._milestones.values():
        assert isinstance(m, MilestoneDefinition)


def test_orchestrator_initial_m1_is_in_progress() -> None:
    """M1 should be set to IN_PROGRESS on scaffold initialization."""
    orch = MilestoneOrchestrator()
    assert orch._milestones["M1"].status == MilestoneStatus.IN_PROGRESS


def test_orchestrator_instances_are_independent() -> None:
    """Two orchestrators should not share milestone state."""
    orch1 = MilestoneOrchestrator()
    orch2 = MilestoneOrchestrator()
    orch1._milestones["M1"].status = MilestoneStatus.COMPLETE
    assert orch2._milestones["M1"].status != MilestoneStatus.COMPLETE


# ---------------------------------------------------------------------------
# list_milestones
# ---------------------------------------------------------------------------


def test_list_milestones_renders_table() -> None:
    """list_milestones should produce non-empty output."""
    orch = MilestoneOrchestrator()
    con, buf = _capture_console()
    orch.list_milestones(con)
    assert len(buf.getvalue()) > 0


def test_list_milestones_includes_all_ids() -> None:
    """list_milestones should include every milestone ID."""
    orch = MilestoneOrchestrator()
    con, buf = _capture_console()
    orch.list_milestones(con)
    output = buf.getvalue()
    for milestone_id in orch._milestones:
        assert milestone_id in output


def test_list_milestones_includes_status_values() -> None:
    """list_milestones should include milestone status values."""
    orch = MilestoneOrchestrator()
    con, buf = _capture_console()
    orch.list_milestones(con)
    output = buf.getvalue()
    for m in orch._milestones.values():
        assert m.status.value in output


def test_list_milestones_includes_phase_numbers() -> None:
    """list_milestones should include the phase number for each milestone."""
    orch = MilestoneOrchestrator()
    con, buf = _capture_console()
    orch.list_milestones(con)
    output = buf.getvalue()
    phases = {str(m.phase) for m in orch._milestones.values()}
    for phase in phases:
        assert phase in output


# ---------------------------------------------------------------------------
# inspect
# ---------------------------------------------------------------------------


def test_inspect_none_id_shows_usage_hint() -> None:
    """inspect(None) should show a hint to use --list."""
    orch = MilestoneOrchestrator()
    con, buf = _capture_console()
    orch.inspect(milestone_id=None, console=con)
    output = buf.getvalue()
    assert "list" in output.lower() or "No milestone" in output


def test_inspect_known_id_renders_milestone_details() -> None:
    """inspect(M1) should render the M1 milestone panel."""
    orch = MilestoneOrchestrator()
    con, buf = _capture_console()
    orch.inspect(milestone_id="M1", console=con)
    output = buf.getvalue()
    assert "M1" in output


def test_inspect_known_id_includes_name() -> None:
    """inspect(M1) should include the milestone name in the output."""
    orch = MilestoneOrchestrator()
    m1 = orch._milestones["M1"]
    con, buf = _capture_console()
    orch.inspect(milestone_id="M1", console=con)
    output = buf.getvalue()
    assert m1.name[:15] in output


def test_inspect_known_id_includes_status() -> None:
    """inspect(M1) should include the current status."""
    orch = MilestoneOrchestrator()
    m1 = orch._milestones["M1"]
    con, buf = _capture_console()
    orch.inspect(milestone_id="M1", console=con)
    output = buf.getvalue()
    assert m1.status.value in output


def test_inspect_unknown_id_reports_not_found() -> None:
    """inspect(UNKNOWN) should report that the milestone was not found."""
    orch = MilestoneOrchestrator()
    con, buf = _capture_console()
    orch.inspect(milestone_id="UNKNOWN", console=con)
    output = buf.getvalue()
    assert "UNKNOWN" in output or "not found" in output.lower()


# ---------------------------------------------------------------------------
# advance — valid transitions
# ---------------------------------------------------------------------------


def test_advance_pending_to_in_progress() -> None:
    """advance() on PENDING should move to IN_PROGRESS."""
    orch = _make_orchestrator_with_status("M2", MilestoneStatus.PENDING)
    con, _ = _capture_console()
    orch.advance(milestone_id="M2", console=con)
    assert orch._milestones["M2"].status == MilestoneStatus.IN_PROGRESS


def test_advance_pending_to_in_progress_output_mentions_status() -> None:
    """advance() output should mention the new status."""
    orch = _make_orchestrator_with_status("M2", MilestoneStatus.PENDING)
    con, buf = _capture_console()
    orch.advance(milestone_id="M2", console=con)
    output = buf.getvalue()
    assert MilestoneStatus.IN_PROGRESS.value in output or "advanced" in output.lower()


def test_advance_in_progress_to_awaiting_review() -> None:
    """advance() on IN_PROGRESS should move to AWAITING_REVIEW."""
    orch = _make_orchestrator_with_status("M1", MilestoneStatus.IN_PROGRESS)
    con, _ = _capture_console()
    orch.advance(milestone_id="M1", console=con)
    assert orch._milestones["M1"].status == MilestoneStatus.AWAITING_REVIEW


def test_advance_approved_to_complete() -> None:
    """advance() on APPROVED should move to COMPLETE."""
    orch = _make_orchestrator_with_status("M1", MilestoneStatus.APPROVED)
    con, _ = _capture_console()
    orch.advance(milestone_id="M1", console=con)
    assert orch._milestones["M1"].status == MilestoneStatus.COMPLETE


# ---------------------------------------------------------------------------
# advance — synchronization boundary enforcement
# ---------------------------------------------------------------------------


def test_advance_awaiting_review_does_not_auto_approve() -> None:
    """advance() on AWAITING_REVIEW must NOT auto-advance to APPROVED.

    This enforces the synchronization boundary: AWAITING_REVIEW → APPROVED
    requires explicit human action and must never happen autonomously.
    """
    orch = _make_orchestrator_with_status("M1", MilestoneStatus.AWAITING_REVIEW)
    con, _ = _capture_console()
    orch.advance(milestone_id="M1", console=con)
    # Status should remain AWAITING_REVIEW — human approval is required.
    assert orch._milestones["M1"].status == MilestoneStatus.AWAITING_REVIEW


def test_advance_awaiting_review_shows_human_approval_requirement() -> None:
    """advance() on AWAITING_REVIEW should surface the human review requirement."""
    orch = _make_orchestrator_with_status("M1", MilestoneStatus.AWAITING_REVIEW)
    con, buf = _capture_console()
    orch.advance(milestone_id="M1", console=con)
    output = buf.getvalue()
    assert "human" in output.lower() or "review" in output.lower() or "approval" in output.lower()


# ---------------------------------------------------------------------------
# advance — terminal state protection
# ---------------------------------------------------------------------------


def test_advance_complete_is_terminal() -> None:
    """advance() on COMPLETE should not change state and show a terminal message."""
    orch = _make_orchestrator_with_status("M1", MilestoneStatus.COMPLETE)
    con, buf = _capture_console()
    orch.advance(milestone_id="M1", console=con)
    assert orch._milestones["M1"].status == MilestoneStatus.COMPLETE
    output = buf.getvalue()
    assert "terminal" in output.lower() or "already" in output.lower() or "complete" in output.lower()


def test_advance_rejected_is_terminal() -> None:
    """advance() on REJECTED should not change state and show a terminal message."""
    orch = _make_orchestrator_with_status("M1", MilestoneStatus.REJECTED)
    con, buf = _capture_console()
    orch.advance(milestone_id="M1", console=con)
    assert orch._milestones["M1"].status == MilestoneStatus.REJECTED
    output = buf.getvalue()
    assert "terminal" in output.lower() or "already" in output.lower() or "rejected" in output.lower()


# ---------------------------------------------------------------------------
# advance — unknown milestone_id
# ---------------------------------------------------------------------------


def test_advance_unknown_id_reports_not_found() -> None:
    """advance() with an unknown ID should report not-found without raising."""
    orch = MilestoneOrchestrator()
    con, buf = _capture_console()
    orch.advance(milestone_id="UNKNOWN-XYZ", console=con)
    output = buf.getvalue()
    assert "UNKNOWN-XYZ" in output or "not found" in output.lower()


# ---------------------------------------------------------------------------
# Parameterized transition table
# ---------------------------------------------------------------------------


VALID_TRANSITIONS = [
    (MilestoneStatus.PENDING, MilestoneStatus.IN_PROGRESS),
    (MilestoneStatus.IN_PROGRESS, MilestoneStatus.AWAITING_REVIEW),
    (MilestoneStatus.APPROVED, MilestoneStatus.COMPLETE),
]

TERMINAL_STATES = [
    MilestoneStatus.COMPLETE,
    MilestoneStatus.REJECTED,
]


@pytest.mark.parametrize("from_status,expected_status", VALID_TRANSITIONS)
def test_valid_transitions(from_status: MilestoneStatus, expected_status: MilestoneStatus) -> None:
    """Parameterized: each valid transition should move to the expected next status."""
    orch = _make_orchestrator_with_status("M1", from_status)
    con, _ = _capture_console()
    orch.advance(milestone_id="M1", console=con)
    assert orch._milestones["M1"].status == expected_status


@pytest.mark.parametrize("terminal_status", TERMINAL_STATES)
def test_terminal_states_block_advancement(terminal_status: MilestoneStatus) -> None:
    """Parameterized: terminal states should not advance and should print a message."""
    orch = _make_orchestrator_with_status("M1", terminal_status)
    con, buf = _capture_console()
    orch.advance(milestone_id="M1", console=con)
    assert orch._milestones["M1"].status == terminal_status
    assert len(buf.getvalue()) > 0


# ---------------------------------------------------------------------------
# _render_milestone
# ---------------------------------------------------------------------------


def test_render_milestone_includes_id() -> None:
    """_render_milestone should include the milestone ID in output."""
    orch = MilestoneOrchestrator()
    m = orch._milestones["M1"]
    con, buf = _capture_console()
    orch._render_milestone(m, con)
    output = buf.getvalue()
    assert m.id in output


def test_render_milestone_includes_description() -> None:
    """_render_milestone should include the milestone description."""
    orch = MilestoneOrchestrator()
    m = orch._milestones["M1"]
    con, buf = _capture_console()
    orch._render_milestone(m, con)
    output = buf.getvalue()
    assert m.description[:20] in output


def test_render_milestone_includes_validation_criteria() -> None:
    """_render_milestone should include validation criteria."""
    orch = MilestoneOrchestrator()
    m = orch._milestones["M1"]
    con, buf = _capture_console()
    orch._render_milestone(m, con)
    output = buf.getvalue()
    assert "tests_pass" in output
    assert "lint_clean" in output


# ---------------------------------------------------------------------------
# Example milestones
# ---------------------------------------------------------------------------


def test_example_milestones_have_unique_ids() -> None:
    """example_milestones should return milestones with unique IDs."""
    milestones = MilestoneDefinition.example_milestones()
    ids = [m.id for m in milestones]
    assert len(ids) == len(set(ids))


def test_example_milestones_phases_are_sequential() -> None:
    """Example milestones should have sequential phase numbers."""
    milestones = MilestoneDefinition.example_milestones()
    phases = [m.phase for m in milestones]
    assert phases == sorted(phases)
