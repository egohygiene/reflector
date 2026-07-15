# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Worked example: Performing a synchronization checkpoint.

Purpose
-------
Demonstrate how to evaluate synchronization boundaries, inspect their state,
and interpret the result as a human governance decision point.

Prerequisites
-------------
- The ``reflector`` package is installed.
- No network access or external credentials are required.

Public interfaces used
----------------------
- :class:`reflector.synchronization.checkpoint.SynchronizationCheckpoint`
- :class:`reflector.synchronization.boundaries.SynchronizationBoundary`,
  :class:`~reflector.synchronization.boundaries.BoundaryType`

Expected output
---------------
Running this file lists all registered synchronization boundaries, evaluates
the active boundary, and demonstrates how to interpret the state::

    === Listing all synchronization boundaries ===
    [table with SB-001, SB-002, SB-003]

    === Evaluating active boundary SB-001 ===
    [boundary detail panel]

    Active boundaries require human review before execution proceeds.
    SB-001 (Post-scaffold review) — ACTIVE — awaiting approval

No files are written by this example.

Cleanup
-------
This example does not write any files or produce persistent state. Each
:class:`~reflector.synchronization.checkpoint.SynchronizationCheckpoint`
is independent and discarded at the end of the function.

Reference
---------
- ``reflector/synchronization/checkpoint.py``
- ``reflector/synchronization/boundaries.py``
- ``specs/reflector.spec.md`` — Synchronization layer
- ``specs/synchronization/synchronization-checkpoint.spec.md``

Usage
-----
Run directly::

    python -m reflector.examples.synchronization_example

Or import as a module::

    from reflector.examples.synchronization_example import run_synchronization_example
    run_synchronization_example()
"""

from __future__ import annotations

import io

from rich.console import Console

from reflector.synchronization.boundaries import BoundaryType, SynchronizationBoundary
from reflector.synchronization.checkpoint import SynchronizationCheckpoint


def run_synchronization_example() -> dict[str, object]:
    """Demonstrate synchronization checkpoint evaluation.

    Illustrates the minimal workflow for the synchronization layer:

    1. Instantiate a :class:`~reflector.synchronization.checkpoint.SynchronizationCheckpoint`.
    2. List all registered boundaries with
       :meth:`~reflector.synchronization.checkpoint.SynchronizationCheckpoint.list_boundaries`.
    3. Evaluate a specific boundary with
       :meth:`~reflector.synchronization.checkpoint.SynchronizationCheckpoint.evaluate`.
    4. Inspect the boundary state to determine whether human approval is needed.

    Returns
    -------
    dict
        A summary with ``active_count`` (int) and ``requires_approval`` (bool) keys
        reflecting the state of the first active boundary found.
    """
    buf = io.StringIO()
    console = Console(file=buf, no_color=True, highlight=False)

    # Step 1 — Instantiate the checkpoint.
    # The checkpoint loads example boundaries from
    # SynchronizationBoundary.example_boundaries().
    checkpoint = SynchronizationCheckpoint()

    # Step 2 — List all registered boundaries.
    # This renders a table with ID, name, type, active status, and approval flag.
    print("=== Listing all synchronization boundaries ===")
    checkpoint.list_boundaries(console)
    print(buf.getvalue())
    buf.truncate(0)
    buf.seek(0)

    # Step 3 — Evaluate the active SB-001 boundary by ID.
    # evaluate() renders a detail panel for the named boundary.
    print("=== Evaluating active boundary SB-001 ===")
    checkpoint.evaluate(boundary_id="SB-001", console=console)
    print(buf.getvalue())
    buf.truncate(0)
    buf.seek(0)

    # Step 4 — Evaluate all active boundaries (no boundary_id argument).
    # When active boundaries exist, evaluate() reports them and indicates
    # that human review is required before execution may proceed.
    print("=== Evaluating all boundaries (no specific ID) ===")
    checkpoint.evaluate(boundary_id=None, console=console)
    print(buf.getvalue())
    buf.truncate(0)
    buf.seek(0)

    # Step 5 — Inspect boundary state programmatically.
    active = [b for b in checkpoint._boundaries if b.active]
    active_count = len(active)
    requires_approval = any(b.requires_approval for b in active)

    if active_count > 0:
        print(
            f"Active boundaries require human review before execution proceeds.\n"
            f"{active[0].id} ({active[0].name}) — ACTIVE — "
            f"{'awaiting approval' if active[0].requires_approval else 'no approval required'}"
        )
    else:
        print("No active boundaries. Execution may proceed autonomously.")

    return {"active_count": active_count, "requires_approval": requires_approval}


def demonstrate_custom_boundary() -> None:
    """Show how to add a custom boundary to a checkpoint instance.

    In a production integration, boundaries would be loaded from a YAML
    governance contract or detected dynamically during workflow execution.
    This example shows the minimal construction pattern.
    """
    # Build a custom boundary representing a manual pause point.
    custom_boundary = SynchronizationBoundary(
        id="SB-CUSTOM-001",
        name="Pre-release review",
        boundary_type=BoundaryType.MANUAL,
        description=(
            "Execution paused before release tagging. "
            "A human must verify the release manifest before proceeding."
        ),
        requires_approval=True,
        active=True,
    )

    checkpoint = SynchronizationCheckpoint()
    # Append the custom boundary to the existing list.
    checkpoint._boundaries.append(custom_boundary)

    buf = io.StringIO()
    console = Console(file=buf, no_color=True, highlight=False)
    checkpoint.evaluate(boundary_id="SB-CUSTOM-001", console=console)

    print("=== Custom boundary evaluation ===")
    print(buf.getvalue())


if __name__ == "__main__":
    print("=" * 60)
    print("reflector — Synchronization Checkpoint Example")
    print("=" * 60)
    print()

    result = run_synchronization_example()
    print()
    demonstrate_custom_boundary()
    print()
    print(
        f"Summary: {result['active_count']} active boundary/boundaries, "
        f"requires_approval={result['requires_approval']}."
    )
    print("Done. No files were written.")
