<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

---
title: Repository Architecture Specification
version: 0.1.0
status: draft
category:
  - repository
  - architecture
  - specification
tags:
  - portability
  - conformance
  - layering
  - validation
---

# Purpose and Authority

Define a portable repository architecture baseline for Reflector-aligned workflows without requiring a fixed directory tree.

- **Extended master specification:** [`specs/reflector.spec.md`](../reflector.spec.md)
- **Scope authority:** repository layers, documentation surfaces, metadata ownership, and validation expectations.
- **Authority limit:** this specification defines architectural responsibilities, not repository-specific implementation layouts.

---

# Normative and Non-Normative Language

- **Normative requirements** use **MUST**, **MUST NOT**, **SHOULD**, and **MAY**.
- **Recommended conventions** are marked as SHOULD guidance.
- **Repository-specific examples** are explicitly labeled non-normative.
- **Optional extensions** are additive and MUST NOT weaken normative requirements.

---

# Portability Expectations

A conforming repository MUST preserve equivalent architecture responsibilities even when path names differ.

Path names shown in this document are examples unless explicitly marked required by a local contract.

---

# Canonical Repository Layers

A Reflector-aligned repository MUST expose these layers:

1. **Specification layer** — contracts that define behavior and boundaries.
2. **Semantic content layer** — source intent/content independent from rendering/presentation.
3. **Rendering/tooling layer** — compilation, rendering, style, or transformation mechanisms.
4. **Orchestration layer** — scripts/automation that execute bounded workflows.
5. **Validation/audit layer** — inspectable evidence of conformance and synchronization.
6. **Documentation layer** — orientation and operational guidance for humans and AI systems.

---

# Documentation Entry-Point Responsibilities

A conforming repository MUST provide discoverable entry points that:

- identify where canonical architecture/specification contracts live,
- identify where execution and validation commands are defined,
- distinguish stable canonical sources from generated outputs,
- provide orientation paths for new human and AI contributors.

Entry-point documents SHOULD include an internal orientation surface and an external discovery surface.

---

# Specification Organization

A conforming repository MUST:

1. identify one master specification surface.
2. identify subordinate specifications and their narrower authority.
3. avoid re-defining canonical terms in conflicting ways.
4. provide measurable conformance criteria for normative requirements.

Subordinate specifications SHOULD reference related implementation surfaces and related specifications.

---

# Audit Artifact Organization

A conforming repository MUST maintain an inspectable location (or equivalent traceable surfaces) for:

- validation outputs,
- checkpoint evidence,
- synchronization and readiness reports,
- remediation notes when conformance fails.

Audit artifacts MAY be distributed across repository history, issue/PR evidence, and CI logs, but discoverability MUST be preserved.

---

# Metadata Ownership and Canonical-Source Rules

- Canonical metadata fields MUST have a single declared source of truth.
- Derived metadata artifacts MUST trace to canonical sources.
- Conflicting metadata declarations MUST be treated as non-conformance until reconciled.
- Ownership of metadata surfaces (authoritative vs derived) MUST be explicit.

---

# Separation of Concerns

Conforming repositories MUST preserve clear separation between:

1. semantic content,
2. rendering/presentation concerns,
3. orchestration/automation logic,
4. generated artifacts.

Generated artifacts MUST NOT become implicit canonical sources unless explicitly declared and governed.

---

# Local and CI Validation Parity

- Required validation checks MUST be runnable in at least one deterministic environment.
- If checks run in both local and CI contexts, parity expectations MUST be documented.
- CI-only validation is acceptable only when local equivalents are infeasible and rationale is documented.

---

# AI Onboarding Expectations

A conforming repository MUST provide AI-orientation guidance that:

- points to authoritative specification and documentation entry points,
- identifies guarded boundaries requiring human approval,
- defines expected validation and synchronization behavior before continuation.

---

# Required Components vs Optional Extensions

## Required Components (MUST)

- master specification surface
- subordinate specification surfaces (where used)
- documentation orientation entry points
- validation/audit evidence surface
- explicit canonical metadata ownership rules

## Optional Extensions (MAY)

- additional style, domain, or process specifications
- repository-specific automation helpers
- generated dashboards or synchronization summaries

Optional extensions MUST NOT weaken required conformance behavior.

---

# Non-Normative Repository-Specific Example

The reflector repository currently maps these responsibilities to:

- `specs/` (specification layer)
- `paper/` and `docs/` (semantic and documentation layers)
- `scripts/` and `.github/workflows/` (orchestration/validation)
- `audits/` (audit evidence surface)

This mapping is an example, not a universal directory requirement.

---

# Conformance Criteria

A repository conforms to this specification only if:

- all required architecture layers are represented by discoverable surfaces,
- canonical metadata ownership is explicit and auditable,
- semantic/render/orchestration/generated concerns are distinguishable,
- documentation entry points and AI onboarding surfaces are present,
- validation evidence can be traced to repository state and governing specifications.
