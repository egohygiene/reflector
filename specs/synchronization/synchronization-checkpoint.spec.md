<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

---
title: Synchronization Checkpoint Specification
version: 0.1.0
status: draft
category:
  - synchronization
  - governance
  - specification
tags:
  - checkpoints
  - evidence
  - lifecycle
  - traceability
---

# Purpose and Authority

This specification defines explicit checkpoint contracts for Reflector-aligned recursive workflows.

- **Extended master specification:** [`specs/reflector.spec.md`](../reflector.spec.md)
- **Scope authority:** checkpoint lifecycle, evidence requirements, validation, and continuation boundaries.
- **Authority limit:** this specification narrows checkpoint behavior and does not override canonical terminology or core lifecycle semantics defined by the master specification.

---

# Applicability

This specification applies to any workflow that crosses one or more of these boundaries:

- Orient → Align
- Align → Execute
- Execute → Audit
- Audit → Synchronize
- Synchronize → next recursive cycle
- automated execution → human approval boundary

---

# Required Terminology

Use canonical terms from the master specification. This document introduces only checkpoint-local terms:

- **Checkpoint record**: auditable artifact containing required checkpoint evidence.
- **Evidence bundle**: the minimum evidence set required to evaluate checkpoint sufficiency.
- **Checkpoint verdict**: `complete`, `blocked`, `failed`, or `incomplete`.

---

# Checkpoint Lifecycle and States

Each checkpoint MUST be in exactly one state:

1. **planned** — checkpoint is declared for a specific phase transition.
2. **ready** — entry criteria are satisfied.
3. **collecting-evidence** — required artifacts and validations are being gathered.
4. **review-pending** — evidence is complete and awaits decision authority.
5. **complete** — continuation decision is recorded and authorized.
6. **blocked** — continuation cannot proceed due to missing dependencies or unresolved ambiguity.
7. **failed** — evidence demonstrates non-conformance or failing validation.
8. **incomplete** — workflow ended or was interrupted before a valid decision was recorded.

Valid progression is `planned → ready → collecting-evidence → review-pending → complete`, with diversion to `blocked`, `failed`, or `incomplete` as needed.

---

# Entry and Exit Criteria

## Entry Criteria (MUST)

A checkpoint may enter `ready` only when all are true:

1. transition boundary is explicitly identified.
2. scoped objective and expected artifacts are declared.
3. governing specifications are identified.
4. required validation methods are identified.

## Exit Criteria (MUST)

A checkpoint may enter `complete` only when all are true:

1. required evidence bundle is present.
2. validation results are recorded.
3. unresolved blockers are absent.
4. continuation decision and rationale are recorded.
5. required human approval (when applicable) is recorded.

A checkpoint MUST NOT be considered complete only because a command, script, or workflow exited successfully.

---

# Required Synchronization Evidence

Each checkpoint record MUST include:

1. checkpoint identifier, transition boundary, and timestamp.
2. scoped objective and declared artifact surface.
3. artifact snapshot reference (commit SHA, equivalent immutable reference, or both).
4. validation evidence (local and/or CI results with pass/fail state).
5. drift/ambiguity findings and disposition.
6. continuation decision (`continue`, `correct`, `rescope`, or `pause`) with authority identity.

Evidence SHOULD include links to issue, pull request, workflow run, and audit artifact paths when available.

---

# Validation Requirements

- A checkpoint MUST include at least one validation result aligned with scoped changes.
- Validation evidence MUST be reproducible from repository state and referenced commands/workflows.
- If both local and CI validation exist, evidence SHOULD document parity or justified divergence.
- Failing required validations MUST force `failed` or `blocked`; they MUST NOT produce `complete`.

---

# Human Review Requirements

Human approval is REQUIRED when:

- continuation expands scope beyond the declared artifact surface.
- specifications conflict or are ambiguous.
- required evidence is incomplete but continuation is proposed.
- release/publication actions are proposed.
- automation crossed a declared human-gated boundary.

Automated systems MAY prepare evidence and recommendations, but human approval authority remains unchanged.

---

# Failure, Blocked, and Incomplete Behavior

- **failed**: non-conformance or failing required validation; continuation prohibited until corrected.
- **blocked**: missing prerequisite, unresolved ambiguity, or missing decision authority; continuation prohibited until unblocked.
- **incomplete**: interrupted checkpoint without valid decision; continuation prohibited until recovered.

All non-complete terminal states MUST include explicit recovery conditions.

---

# Resume and Recovery

To resume from `blocked`, `failed`, or `incomplete`, a workflow MUST:

1. preserve prior checkpoint evidence.
2. record corrective actions or missing prerequisites now satisfied.
3. rerun or re-collect invalidated validation evidence.
4. produce a new or amended checkpoint record with explicit supersession linkage.

Recovery MUST maintain traceability to the original checkpoint record.

---

# Auditability and Traceability

Checkpoint records MUST be:

- durable (stored in repository history, issue/PR records, workflow logs, or audit archives),
- attributable (decision authority and timestamp are explicit),
- inspectable (evidence references are resolvable),
- linkable (successor checkpoints can trace prior decisions).

---

# Conformance Criteria

An implementation conforms to this specification only if:

- every declared boundary transition has a corresponding checkpoint record,
- each `complete` checkpoint contains the full required evidence bundle,
- command/workflow success is not used as sole completion evidence,
- blocked/failed/incomplete checkpoints include explicit recovery conditions,
- human-gated boundaries show explicit human approval evidence.
