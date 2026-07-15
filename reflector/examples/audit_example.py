# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Worked example: Running the reflective audit pipeline.

Purpose
-------
Demonstrate how to run the four-stage reflective audit pipeline, inspect
the resulting :class:`~reflector.schemas.audit.AuditReport`, and interpret
its outcome.

Prerequisites
-------------
- The ``reflector`` package is installed (``pip install reflector`` or
  ``uv sync`` in a development checkout).
- No network access or external credentials are required.

Public interfaces used
----------------------
- :class:`reflector.audits.pipeline.AuditPipeline`
- :class:`reflector.schemas.audit.AuditReport`, :class:`~reflector.schemas.audit.CheckResult`

Expected output
---------------
Running this file produces a console summary of the audit report, similar to::

    Audit result:  PASS
    Total entries: 3
    Pass:          3
    Warn:          0
    Fail:          0
    Drift alerts:  0
    Recommendation: All invariants passed. Proceed to synchronization ...

No files are written by this example. State is held in memory only.

Reference
---------
- ``reflector/audits/pipeline.py``
- ``specs/reflector.spec.md`` — Reflective Audit stage

Usage
-----
Run directly::

    python -m reflector.examples.audit_example

Or import as a module in tests::

    from reflector.examples.audit_example import run_audit_example
    report = run_audit_example()
"""

from __future__ import annotations

import io

from rich.console import Console

from reflector.audits.pipeline import AuditPipeline
from reflector.schemas.audit import AuditReport, CheckResult


def run_audit_example(*, verbose: bool = False) -> AuditReport:
    """Run the audit pipeline and return the resulting report.

    This function demonstrates the minimal usage pattern for
    :class:`~reflector.audits.pipeline.AuditPipeline`:

    1. Instantiate the pipeline (optionally with ``verbose=True``).
    2. Call :meth:`~reflector.audits.pipeline.AuditPipeline.run` to execute
       all four stages and receive an :class:`~reflector.schemas.audit.AuditReport`.
    3. Inspect the report fields to interpret the outcome.
    4. Optionally render the report to a console with
       :meth:`~reflector.audits.pipeline.AuditPipeline.print_report`.

    Parameters
    ----------
    verbose:
        When ``True``, the pipeline emits stage-level progress messages.

    Returns
    -------
    AuditReport
        The fully populated audit report from the pipeline run.
    """
    # Step 1 — Instantiate the pipeline.
    # verbose=True enables per-stage diagnostic output to stdout.
    pipeline = AuditPipeline(verbose=verbose)

    # Step 2 — Execute all four audit stages.
    # Stage 1: Event Capture  — records agent actions as structured events.
    # Stage 2: Invariant Validation — checks governance invariants per event.
    # Stage 3: Drift Detection — computes a drift score for each event.
    # Stage 4: Audit Trail Append — assembles the signed AuditReport.
    report = pipeline.run()

    # Step 3 — Inspect report fields.
    # overall_result: PASS, WARN, or FAIL based on scope checks and drift.
    # total_entries: number of agent actions captured in this audit pass.
    # pass_count: entries with scope_check=PASS and no drift alert.
    # fail_count: entries with scope_check=FAIL (governance violation).
    # drift_alerts: entries where drift_score exceeded the threshold (0.3).
    # recommendations: actionable next steps from the pipeline.
    assert isinstance(report.overall_result, CheckResult)
    assert report.total_entries == len(report.entries)

    # Step 4 — Render the report to the console for human review.
    buf = io.StringIO()
    console = Console(file=buf, no_color=True, highlight=False)
    AuditPipeline.print_report(report, console)
    output = buf.getvalue()

    print(f"Audit result:  {report.overall_result.value}")
    print(f"Total entries: {report.total_entries}")
    print(f"Pass:          {report.pass_count}")
    print(f"Warn:          {report.warn_count}")
    print(f"Fail:          {report.fail_count}")
    print(f"Drift alerts:  {report.drift_alerts}")
    if report.recommendations:
        print(f"Recommendation: {report.recommendations[0]}")

    return report


def demonstrate_report_interpretation(report: AuditReport) -> None:
    """Show how to branch on audit outcome in application code.

    This demonstrates the recommended way to act on an
    :class:`~reflector.schemas.audit.AuditReport` result:

    - ``PASS``: All invariants passed; proceed to the synchronization checkpoint.
    - ``WARN``: Drift detected; review before proceeding.
    - ``FAIL``: Scope violation; halt and investigate before any further action.

    Parameters
    ----------
    report:
        An :class:`~reflector.schemas.audit.AuditReport` from a previous
        :meth:`~reflector.audits.pipeline.AuditPipeline.run` call.
    """
    match report.overall_result:
        case CheckResult.PASS:
            print("✅ Audit passed — proceed to synchronization checkpoint.")
        case CheckResult.WARN:
            print(
                f"⚠️  Audit warning — {report.drift_alerts} drift alert(s) detected. "
                "Review before proceeding."
            )
        case CheckResult.FAIL:
            print(
                f"❌ Audit failed — {report.fail_count} scope violation(s). "
                "Halt execution and investigate."
            )
        case _:
            print(f"ℹ️  Audit result: {report.overall_result.value}")


if __name__ == "__main__":
    print("=" * 60)
    print("reflector — Audit Pipeline Example")
    print("=" * 60)
    print()

    report = run_audit_example(verbose=True)
    print()
    demonstrate_report_interpretation(report)
    print()
    print("Done. No files were written.")
