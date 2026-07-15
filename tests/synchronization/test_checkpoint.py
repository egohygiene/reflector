# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Tests for reflector/synchronization/checkpoint.py.

Covers:
- Checkpoint initialization with example boundaries.
- list_boundaries renders a table of all registered boundaries.
- evaluate() with no boundary ID shows active boundaries.
- evaluate() with a known boundary ID renders that boundary.
- evaluate() with an unknown boundary ID reports not-found.
- Inactive boundary evaluation does not raise errors.
- Boundary state is isolated per checkpoint instance.
"""

from __future__ import annotations

import io

from rich.console import Console

from reflector.synchronization.boundaries import BoundaryType, SynchronizationBoundary
from reflector.synchronization.checkpoint import SynchronizationCheckpoint


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _capture_console() -> tuple[Console, io.StringIO]:
    buf = io.StringIO()
    con = Console(file=buf, highlight=False, markup=False, no_color=True)
    return con, buf


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------


def test_checkpoint_initializes_with_example_boundaries() -> None:
    """SynchronizationCheckpoint should load example boundaries on init."""
    cp = SynchronizationCheckpoint()
    # Example boundaries are defined in SynchronizationBoundary.example_boundaries()
    assert len(cp._boundaries) > 0


def test_checkpoint_boundaries_are_synchronization_boundary_instances() -> None:
    """All loaded boundaries should be SynchronizationBoundary instances."""
    cp = SynchronizationCheckpoint()
    for boundary in cp._boundaries:
        assert isinstance(boundary, SynchronizationBoundary)


def test_checkpoint_instances_are_independent() -> None:
    """Two checkpoint instances should not share boundary state."""
    cp1 = SynchronizationCheckpoint()
    cp2 = SynchronizationCheckpoint()
    # Mutate one instance's boundary list
    cp1._boundaries[0].active = not cp1._boundaries[0].active
    # The other instance should be unaffected
    original_active = SynchronizationBoundary.example_boundaries()[0].active
    assert cp2._boundaries[0].active == original_active


# ---------------------------------------------------------------------------
# list_boundaries
# ---------------------------------------------------------------------------


def test_list_boundaries_renders_table() -> None:
    """list_boundaries should render a table without raising exceptions."""
    cp = SynchronizationCheckpoint()
    con, buf = _capture_console()
    cp.list_boundaries(con)
    output = buf.getvalue()
    assert len(output) > 0


def test_list_boundaries_includes_all_boundary_ids() -> None:
    """list_boundaries output should include every registered boundary ID."""
    cp = SynchronizationCheckpoint()
    con, buf = _capture_console()
    cp.list_boundaries(con)
    output = buf.getvalue()
    for boundary in cp._boundaries:
        assert boundary.id in output


def test_list_boundaries_includes_boundary_names() -> None:
    """list_boundaries output should include boundary names."""
    cp = SynchronizationCheckpoint()
    con, buf = _capture_console()
    cp.list_boundaries(con)
    output = buf.getvalue()
    for boundary in cp._boundaries:
        # At least part of the name should appear in the output
        assert boundary.name[:10] in output


def test_list_boundaries_includes_boundary_types() -> None:
    """list_boundaries output should include boundary type labels."""
    cp = SynchronizationCheckpoint()
    con, buf = _capture_console()
    cp.list_boundaries(con)
    output = buf.getvalue()
    # Rich may truncate long values in narrow columns; check for a prefix
    # that is long enough to uniquely identify the type.
    for boundary in cp._boundaries:
        # Use first 10 characters so truncated cells still match.
        prefix = boundary.boundary_type.value[:10]
        assert prefix in output, (
            f"Expected prefix {prefix!r} of type {boundary.boundary_type.value!r} "
            f"not found in table output"
        )


# ---------------------------------------------------------------------------
# evaluate — no boundary_id
# ---------------------------------------------------------------------------


def test_evaluate_no_id_reports_active_boundaries() -> None:
    """evaluate(None) should report on boundaries that are active."""
    cp = SynchronizationCheckpoint()
    active_count = sum(1 for b in cp._boundaries if b.active)
    con, buf = _capture_console()
    cp.evaluate(boundary_id=None, console=con)
    output = buf.getvalue()
    assert len(output) > 0
    if active_count > 0:
        # Some indication of active boundaries should appear.
        assert "active" in output.lower() or str(active_count) in output


def test_evaluate_no_id_no_active_shows_proceed_message() -> None:
    """When no boundaries are active, evaluate should indicate execution may proceed."""
    cp = SynchronizationCheckpoint()
    # Deactivate all boundaries for this test.
    for b in cp._boundaries:
        b.active = False
    con, buf = _capture_console()
    cp.evaluate(boundary_id=None, console=con)
    output = buf.getvalue()
    # Should indicate no active boundaries.
    assert "No active" in output or "proceed" in output.lower()


# ---------------------------------------------------------------------------
# evaluate — known boundary_id
# ---------------------------------------------------------------------------


def test_evaluate_known_boundary_id_renders_boundary() -> None:
    """evaluate(SB-001) should render the SB-001 boundary detail panel."""
    cp = SynchronizationCheckpoint()
    con, buf = _capture_console()
    cp.evaluate(boundary_id="SB-001", console=con)
    output = buf.getvalue()
    assert "SB-001" in output


def test_evaluate_known_boundary_includes_description() -> None:
    """The rendered boundary panel should include the boundary description."""
    cp = SynchronizationCheckpoint()
    boundary = cp._find("SB-001")
    assert boundary is not None
    con, buf = _capture_console()
    cp.evaluate(boundary_id="SB-001", console=con)
    output = buf.getvalue()
    # At least part of the description should appear.
    assert boundary.description[:20] in output


def test_evaluate_inactive_boundary_id_renders_without_error() -> None:
    """evaluate(SB-002) should render the inactive boundary without errors."""
    cp = SynchronizationCheckpoint()
    con, buf = _capture_console()
    cp.evaluate(boundary_id="SB-002", console=con)
    output = buf.getvalue()
    assert "SB-002" in output


# ---------------------------------------------------------------------------
# evaluate — unknown boundary_id
# ---------------------------------------------------------------------------


def test_evaluate_unknown_boundary_id_reports_not_found() -> None:
    """evaluate with an unknown ID should report not-found."""
    cp = SynchronizationCheckpoint()
    con, buf = _capture_console()
    cp.evaluate(boundary_id="SB-DOES-NOT-EXIST", console=con)
    output = buf.getvalue()
    assert "SB-DOES-NOT-EXIST" in output or "No boundary" in output


# ---------------------------------------------------------------------------
# _find helper
# ---------------------------------------------------------------------------


def test_find_returns_boundary_for_known_id() -> None:
    """_find should return the correct SynchronizationBoundary for a known ID."""
    cp = SynchronizationCheckpoint()
    boundary = cp._find("SB-001")
    assert boundary is not None
    assert boundary.id == "SB-001"


def test_find_returns_none_for_unknown_id() -> None:
    """_find should return None for an ID that doesn't exist."""
    cp = SynchronizationCheckpoint()
    result = cp._find("SB-NONEXISTENT")
    assert result is None


# ---------------------------------------------------------------------------
# _render_boundary
# ---------------------------------------------------------------------------


def test_render_boundary_active_includes_awaiting_review() -> None:
    """An active boundary should mention that it is awaiting human review."""
    cp = SynchronizationCheckpoint()
    boundary = SynchronizationBoundary(
        id="TEST-ACTIVE",
        name="Active Test Boundary",
        boundary_type=BoundaryType.MILESTONE,
        description="Test active boundary.",
        requires_approval=True,
        active=True,
    )
    con, buf = _capture_console()
    cp._render_boundary(boundary, con)
    output = buf.getvalue()
    assert "awaiting" in output.lower() or "ACTIVE" in output


def test_render_boundary_inactive_does_not_show_active_status() -> None:
    """An inactive boundary should not say 'awaiting human review'."""
    cp = SynchronizationCheckpoint()
    boundary = SynchronizationBoundary(
        id="TEST-INACTIVE",
        name="Inactive Test Boundary",
        boundary_type=BoundaryType.RECURSION_LIMIT,
        description="Test inactive boundary.",
        requires_approval=False,
        active=False,
    )
    con, buf = _capture_console()
    cp._render_boundary(boundary, con)
    output = buf.getvalue()
    assert "Inactive" in output or "awaiting" not in output.lower()


# ---------------------------------------------------------------------------
# Example boundaries coverage
# ---------------------------------------------------------------------------


def test_example_boundaries_count() -> None:
    """example_boundaries should return at least two boundaries for meaningful tests."""
    boundaries = SynchronizationBoundary.example_boundaries()
    assert len(boundaries) >= 2


def test_example_boundaries_have_unique_ids() -> None:
    """Each example boundary should have a unique ID."""
    boundaries = SynchronizationBoundary.example_boundaries()
    ids = [b.id for b in boundaries]
    assert len(ids) == len(set(ids))


def test_example_boundaries_have_valid_types() -> None:
    """All example boundary types should be valid BoundaryType enum values."""
    boundaries = SynchronizationBoundary.example_boundaries()
    for b in boundaries:
        assert isinstance(b.boundary_type, BoundaryType)
