# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Worked example: Creating and advancing a milestone.

Purpose
-------
Demonstrate how to initialize a :class:`~reflector.orchestration.milestone.MilestoneOrchestrator`,
inspect milestone state, and step a milestone through its lifecycle —
including the enforced synchronization boundary at ``AWAITING_REVIEW``.

Prerequisites
-------------
- The ``reflector`` package is installed.
- No network access or external credentials are required.

Public interfaces used
----------------------
- :class:`reflector.orchestration.milestone.MilestoneOrchestrator`
- :class:`reflector.schemas.milestone.MilestoneDefinition`,
  :class:`~reflector.schemas.milestone.MilestoneStatus`,
  :class:`~reflector.schemas.milestone.MilestoneValidation`

Lifecycle states
----------------
The supported milestone lifecycle follows this state machine::

    PENDING → IN_PROGRESS → AWAITING_REVIEW
                                  ↓ (human approver required)
                               APPROVED → COMPLETE
                 (terminal states: COMPLETE, REJECTED)

The transition from ``AWAITING_REVIEW`` to ``APPROVED`` always requires
explicit human action and is intentionally blocked by the orchestrator.

Expected output
---------------
Running this file shows::

    === Listing all milestones ===
    [table with M1, M2, M3]

    === Advancing M2: PENDING → IN_PROGRESS ===
    Milestone 'M2' advanced to: in_progress
    ...

    === Synchronization boundary at AWAITING_REVIEW ===
    [boundary panel — human approval required, status unchanged]

No files are written by this example.

Cleanup
-------
This example does not write any files or produce persistent state. Each
:class:`~reflector.orchestration.milestone.MilestoneOrchestrator` is
independent and discarded at the end of the function.

Reference
---------
- ``reflector/orchestration/milestone.py``
- ``reflector/schemas/milestone.py``
- ``specs/reflector.spec.md`` — Milestone Boundaries
- ``specs/synchronization/synchronization-checkpoint.spec.md``

Usage
-----
Run directly::

    python -m reflector.examples.milestone_example

Or import as a module::

    from reflector.examples.milestone_example import run_milestone_example
    run_milestone_example()
"""

from __future__ import annotations

import io

from rich.console import Console

from reflector.orchestration.milestone import MilestoneOrchestrator
from reflector.schemas.milestone import (
    MilestoneDefinition,
    MilestoneStatus,
    MilestoneValidation,
)


def run_milestone_example() -> None:
    """Demonstrate the milestone lifecycle from PENDING through AWAITING_REVIEW.

    Walks through:

    1. Listing all available milestones.
    2. Inspecting a single milestone's detail.
    3. Advancing a milestone from PENDING to IN_PROGRESS.
    4. Advancing from IN_PROGRESS to AWAITING_REVIEW.
    5. Attempting to advance from AWAITING_REVIEW (blocked — human review required).
    6. Setting APPROVED externally to simulate human approval, then completing.
    """
    buf = io.StringIO()
    console = Console(file=buf, no_color=True, highlight=False)

    def _flush(label: str = "") -> None:
        content = buf.getvalue()
        if label:
            print(f"=== {label} ===")
        if content.strip():
            print(content)
        buf.truncate(0)
        buf.seek(0)

    # Step 1 — Instantiate the orchestrator.
    # The orchestrator loads example milestones (M1=IN_PROGRESS, M2=PENDING, M3=PENDING).
    orchestrator = MilestoneOrchestrator()
    orchestrator.list_milestones(console)
    _flush("Listing all milestones")

    # Step 2 — Inspect M2 in detail.
    orchestrator.inspect(milestone_id="M2", console=console)
    _flush("Inspecting M2 (initial: PENDING)")

    # Step 3 — Advance M2: PENDING → IN_PROGRESS.
    # The orchestrator transitions to the next status and renders the result.
    orchestrator.advance(milestone_id="M2", console=console)
    _flush("Advancing M2: PENDING → IN_PROGRESS")
    assert orchestrator._milestones["M2"].status == MilestoneStatus.IN_PROGRESS

    # Step 4 — Advance M2: IN_PROGRESS → AWAITING_REVIEW.
    orchestrator.advance(milestone_id="M2", console=console)
    _flush("Advancing M2: IN_PROGRESS → AWAITING_REVIEW")
    assert orchestrator._milestones["M2"].status == MilestoneStatus.AWAITING_REVIEW

    # Step 5 — Attempt to advance M2: AWAITING_REVIEW → APPROVED.
    # The orchestrator enforces the synchronization boundary and blocks this
    # transition. The status remains AWAITING_REVIEW.
    print("=== Attempting to advance M2 from AWAITING_REVIEW (blocked) ===")
    orchestrator.advance(milestone_id="M2", console=console)
    _flush()
    assert orchestrator._milestones["M2"].status == MilestoneStatus.AWAITING_REVIEW, (
        "Status must NOT auto-advance past AWAITING_REVIEW; human approval is required."
    )
    print(
        "✅ Synchronization boundary enforced: M2 remains AWAITING_REVIEW.\n"
        "   Human approval is required to proceed."
    )

    # Step 6 — Simulate human approval by setting APPROVED directly.
    # In a full integration this would be triggered by a GitHub review approval
    # or a human-operated CLI flag with explicit intent.
    print()
    print("=== Simulating human approval (AWAITING_REVIEW → APPROVED) ===")
    orchestrator._milestones["M2"].status = MilestoneStatus.APPROVED
    orchestrator.inspect(milestone_id="M2", console=console)
    _flush()

    # Step 7 — Advance from APPROVED → COMPLETE.
    orchestrator.advance(milestone_id="M2", console=console)
    _flush("Advancing M2: APPROVED → COMPLETE")
    assert orchestrator._milestones["M2"].status == MilestoneStatus.COMPLETE

    print("✅ M2 reached COMPLETE status.")

    # Step 8 — Confirm terminal state blocks further advancement.
    print()
    print("=== Attempting to advance completed M2 (terminal — no change) ===")
    orchestrator.advance(milestone_id="M2", console=console)
    _flush()
    assert orchestrator._milestones["M2"].status == MilestoneStatus.COMPLETE
    print("✅ COMPLETE is a terminal state — no further advancement possible.")


def demonstrate_custom_milestone() -> None:
    """Show how to define and track a custom milestone outside the default set.

    In a full integration, milestones would be loaded from a YAML governance
    contract. This example shows the minimal construction pattern using the
    public schema types.
    """
    # Define a custom milestone for a hypothetical feature delivery.
    custom = MilestoneDefinition(
        id="CUSTOM-M1",
        name="Feature delivery",
        description="All acceptance criteria met and documentation updated.",
        validation=MilestoneValidation(
            tests_pass=True,
            coverage_threshold=80,
            lint_clean=True,
        ),
        status=MilestoneStatus.PENDING,
        phase=4,
    )

    # Register the custom milestone in a fresh orchestrator.
    orchestrator = MilestoneOrchestrator()
    orchestrator._milestones[custom.id] = custom

    buf = io.StringIO()
    console = Console(file=buf, no_color=True, highlight=False)
    orchestrator.inspect(milestone_id="CUSTOM-M1", console=console)

    print("=== Custom milestone detail ===")
    print(buf.getvalue())


if __name__ == "__main__":
    print("=" * 60)
    print("reflector — Milestone Orchestration Example")
    print("=" * 60)
    print()

    run_milestone_example()
    print()
    demonstrate_custom_milestone()
    print()
    print("Done. No files were written.")
