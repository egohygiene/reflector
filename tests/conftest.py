# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Shared pytest fixtures for the reflector runtime test suite."""

from __future__ import annotations

import io
from typing import Generator

import pytest
from rich.console import Console

from reflector.schemas.audit import AuditEntry, CheckResult, InvariantResult
from reflector.schemas.milestone import (
    MilestoneDefinition,
    MilestoneStatus,
    MilestoneValidation,
)
from reflector.synchronization.boundaries import BoundaryType, SynchronizationBoundary


# ---------------------------------------------------------------------------
# Rich console helpers
# ---------------------------------------------------------------------------


@pytest.fixture()
def string_console() -> tuple[Console, io.StringIO]:
    """Return a Rich Console that writes to a StringIO buffer.

    Useful for capturing Rich-rendered output in unit tests without
    relying on sys.stdout patching.
    """
    buf = io.StringIO()
    console = Console(file=buf, highlight=False, markup=False, no_color=True)
    return console, buf


# ---------------------------------------------------------------------------
# Audit fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def passing_invariant() -> InvariantResult:
    """A single invariant result with a PASS status."""
    return InvariantResult(id="INV-TEST", name="test_invariant", result=CheckResult.PASS)


@pytest.fixture()
def failing_invariant() -> InvariantResult:
    """A single invariant result with a FAIL status."""
    return InvariantResult(
        id="INV-FAIL",
        name="failing_invariant",
        result=CheckResult.FAIL,
        detail="Test failure detail.",
    )


@pytest.fixture()
def audit_entry_pass(passing_invariant: InvariantResult) -> AuditEntry:
    """An audit entry that represents a passing action."""
    return AuditEntry(
        agent_id="test-agent",
        action="test_action",
        target="test/target",
        scope_check=CheckResult.PASS,
        invariants_checked=[passing_invariant],
        drift_score=0.0,
        drift_alert=False,
        milestone="M1",
        phase="scaffold",
    )


@pytest.fixture()
def audit_entry_fail(failing_invariant: InvariantResult) -> AuditEntry:
    """An audit entry that represents a failing action."""
    return AuditEntry(
        agent_id="test-agent",
        action="scope_violation",
        target="infrastructure/",
        scope_check=CheckResult.FAIL,
        invariants_checked=[failing_invariant],
        drift_score=0.5,
        drift_alert=True,
        milestone="M1",
        phase="scaffold",
    )


# ---------------------------------------------------------------------------
# Milestone fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def pending_milestone() -> MilestoneDefinition:
    """A milestone in PENDING state."""
    return MilestoneDefinition(
        id="TEST-M1",
        name="Test Milestone",
        description="A test milestone in pending state.",
        validation=MilestoneValidation(tests_pass=True, lint_clean=True),
        status=MilestoneStatus.PENDING,
        phase=1,
    )


@pytest.fixture()
def in_progress_milestone() -> MilestoneDefinition:
    """A milestone in IN_PROGRESS state."""
    return MilestoneDefinition(
        id="TEST-M2",
        name="In-progress Milestone",
        description="A test milestone currently in progress.",
        validation=MilestoneValidation(tests_pass=True, coverage_threshold=60),
        status=MilestoneStatus.IN_PROGRESS,
        phase=2,
    )


@pytest.fixture()
def awaiting_review_milestone() -> MilestoneDefinition:
    """A milestone in AWAITING_REVIEW state."""
    return MilestoneDefinition(
        id="TEST-M3",
        name="Review Milestone",
        description="A test milestone awaiting human review.",
        validation=MilestoneValidation(tests_pass=True),
        status=MilestoneStatus.AWAITING_REVIEW,
        phase=3,
    )


# ---------------------------------------------------------------------------
# Synchronization boundary fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def active_boundary() -> SynchronizationBoundary:
    """An active synchronization boundary requiring approval."""
    return SynchronizationBoundary(
        id="SB-TEST-001",
        name="Test Active Boundary",
        boundary_type=BoundaryType.MILESTONE,
        description="A test boundary that is currently active.",
        requires_approval=True,
        active=True,
    )


@pytest.fixture()
def inactive_boundary() -> SynchronizationBoundary:
    """An inactive synchronization boundary."""
    return SynchronizationBoundary(
        id="SB-TEST-002",
        name="Test Inactive Boundary",
        boundary_type=BoundaryType.RECURSION_LIMIT,
        description="A test boundary that is currently inactive.",
        requires_approval=False,
        active=False,
    )


# ---------------------------------------------------------------------------
# Repository metadata fixture
# ---------------------------------------------------------------------------


@pytest.fixture()
def metadata_yaml_path(tmp_path: pytest.TempPathFactory) -> Generator:
    """Write a minimal repository.yaml and yield its path."""
    content = """\
future_integrations:
  huggingface:
    enabled: true
    space_url: "https://huggingface.co/spaces/test/reflector"
"""
    path = tmp_path / "repository.yaml"
    path.write_text(content, encoding="utf-8")
    yield path


@pytest.fixture()
def metadata_yaml_path_disabled(tmp_path: pytest.TempPathFactory) -> Generator:
    """Write a repository.yaml with Hugging Face disabled and yield its path."""
    content = """\
future_integrations:
  huggingface:
    enabled: false
"""
    path = tmp_path / "repository.yaml"
    path.write_text(content, encoding="utf-8")
    yield path
