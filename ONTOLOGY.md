---
schema: aether.architecture-document/v1
id: reflector-ontology
title: Reflector Ontology
kind: architecture-document
version: 0.1.0
status: draft
owners:
  - egohygiene
created: 2026-08-19
updated: 2026-08-19
governed_by:
  - architecture-ontology
depends_on:
  - reflector-purpose
  - reflector-vision
  - reflector-principles
  - reflector-epistemology
related:
  - reflector-pillars
  - reflector-manifesto
  - reflector-ai-constitution
  - reflector-personal-model
supersedes: []
---

# Reflector Ontology

## Domain scope

Reflector models the concepts needed for make recursive AI-assisted software work observable, bounded, auditable, and publishable. The ontology names conceptual entities and relationships; it is not a source-code class model, API schema, or database design.

## Canonical concepts

| Concept | Meaning |
| --- | --- |
| Recursive loop | A canonical concept in the Reflector domain whose exact fields belong to specifications or schemas, not this ontology. |
| Checkpoint | A canonical concept in the Reflector domain whose exact fields belong to specifications or schemas, not this ontology. |
| Drift | A canonical concept in the Reflector domain whose exact fields belong to specifications or schemas, not this ontology. |
| Audit | A canonical concept in the Reflector domain whose exact fields belong to specifications or schemas, not this ontology. |
| Artifact | A canonical concept in the Reflector domain whose exact fields belong to specifications or schemas, not this ontology. |
| Publication | A canonical concept in the Reflector domain whose exact fields belong to specifications or schemas, not this ontology. |
| Human review | A canonical concept in the Reflector domain whose exact fields belong to specifications or schemas, not this ontology. |
| Synchronization contract | A canonical concept in the Reflector domain whose exact fields belong to specifications or schemas, not this ontology. |
| Evidence | A canonical concept in the Reflector domain whose exact fields belong to specifications or schemas, not this ontology. |

## Core relationships

- A repository or person provides source context to one or more domain artifacts.
- A specification constrains how an artifact is interpreted or produced.
- A plan separates proposed action from execution.
- Evidence supports a claim; a decision authorizes a durable direction.
- Provenance connects derived artifacts to their inputs and processing context.
- A consumer integrates through an explicit interface rather than internal structure.

## Boundaries

- Conceptual identity is distinct from filesystem path, database identifier, or display label.
- Observed state is distinct from desired state.
- Proposed relationships are not accepted facts.
- Neighboring repositories retain ownership of their domain concepts.

## Evidence and uncertainty

- **Observed:** The repository README and checked-in implementation establish an open research repository and reference platform for governable recursive AI-assisted engineering.
- **Decided for this draft:** The repository owns the bounded concern described here and participates through versioned contracts.
- **Proposed:** Target systems and later roadmap phases remain proposals until accepted and implemented.
- **Open question:** Which parts of this draft should become active in the first independently versioned release?
