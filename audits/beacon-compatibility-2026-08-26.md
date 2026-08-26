<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Beacon Compatibility Audit

**Date:** 2026-08-26
**Issue:** [#247](https://github.com/egohygiene/reflector/issues/247)
**Reflector baseline:** `d04549a3df171d3cd0008ab74a46fb0549deebeb`
**Beacon pin:** `eba8415f440e0eb403a2431828cb5191d78ba4fd`

## Decision

Adopt Beacon around Reflector through a thin, repository-owned compatibility profile.
Do not replace Reflector's publication implementation during this slice.

Reflector is already a live reference implementation with stable artifact names,
public URLs, version/DOI metadata, paper and magazine renderers, Pages assembly, and
release history. A direct template rewrite would combine compatibility proof with a
high-risk publication migration. The adapter instead proves the common Beacon
inspect/plan/build/package seam while preserving every externally visible contract.

## System inventory

| Surface | Reflector contract observed | Beacon mapping | Disposition |
| --- | --- | --- | --- |
| Research paper | `paper/paper.tex`, `paper/styles/reflector.sty`, biblatex/biber, `scripts/build-paper.sh` | `research-paper` capability via native adapter | Supported with exception `REF-B01`. |
| Digital magazine | Image-first `magazine/tex/magazine.tex`, 14 page PNGs, prompt provenance | `magazine` digital capability via native adapter | Supported with exception `REF-B02`. |
| Print magazine | `magazine/tex/magazine-print.tex`, stable print artifact name | `magazine` print capability via native adapter | Supported with exception `REF-B02`. |
| Publication metadata | `metadata/`, `publication.json`, `release-manifest.json`, `scripts/validate-metadata.py` | Validated JSON package inputs | Supported. |
| Package integrity | Native release staging plus checksums | `beacon-package.json` and `SHA256SUMS` | Supported without changing native release packaging. |
| Pages | Existing composed Pages workflow and canonical routes | None in this slice | Preserved; `REF-B03`. |
| DOI and Zenodo | Existing synchronized metadata and human-gated archival lifecycle | None in this slice | Preserved; `REF-B03`. |
| arXiv | Existing manifest, validation, and release bundle workflow | None in this slice | Preserved; `REF-B03`. |

## Compatibility assets

| Asset | Purpose |
| --- | --- |
| `beacon-project.toml` | Pins Reflector to the repository-owned compatibility profile. |
| `dependencies/beacon.lock.json` | Pins the immutable Beacon source revision, CLI/profile versions, and Rust toolchain. |
| `.beacon/profiles/reflector-compatibility/beacon-template.toml` | Declares native outputs, requirements, capabilities, and package artifacts. |
| `.beacon/profiles/reflector-compatibility/scripts/build.py` | Runs native contracts, verifies PDFs, stages artifacts, and emits evidence. |
| `scripts/beacon-compatibility.sh` | Resolves or verifies the pin and applies external-adapter trust explicitly. |
| `.github/workflows/beacon-compatibility.yml` | Runs the clean, read-only, non-deploying compatibility canary. |
| `docs/beacon-compatibility.md` | Documents operator usage, ownership, and migration boundaries. |

## Exceptions and ownership

| ID | Owner | Intentional boundary | Follow-up trigger |
| --- | --- | --- | --- |
| `REF-B01` | Reflector | Bespoke style, macros, biblatex, and biber remain native. | A Beacon component can be adopted only after visual, citation, and PDF parity tests pass. |
| `REF-B02` | Beacon | The built-in magazine starter does not yet model Reflector's image-first prompt-to-page provenance. | Add a page-manifest import seam before considering source migration. |
| `REF-B03` | Reflector | Pages, DOI, Zenodo, arXiv, names, URLs, and release history stay native. | Open a separate migration issue with rollback and public-route preservation criteria. |

## Non-disruption guarantees

- No manuscript, bibliography, style, macro, image, prompt, or magazine source is
  rewritten.
- No committed PDF or public artifact path is renamed.
- No existing workflow is removed or made dependent on Beacon.
- The canary receives only `contents: read` and has no deploy, tag, release, DOI,
  Zenodo, or arXiv step.
- Beacon build and package directories are ignored and replaceable only through
  Beacon's ownership marker.
- The compatibility report records the live Reflector revision instead of placing a
  stale branch revision in `beacon-project.toml`.

## Validation evidence

The implementation was checked locally against the pinned Beacon CLI contract:

- `beacon validate reflector-compatibility`: pass
- `beacon inspect reflector-compatibility`: pass
- `beacon plan .`: pass
- `python3 scripts/validate-metadata.py`: pass
- `scripts/build-magazine.sh build-all`: pass for both 14-page variants
- `.beacon/tests/test_compatibility.py`: 2 pass
- shell syntax, Python byte compilation, and whitespace checks: pass

The clean [Beacon Compatibility run #2](https://github.com/egohygiene/reflector/actions/runs/33006800152)
also passes the native paper build with `biber`, both magazine builds, PDF inspection,
Beacon packaging, manifest parsing, and `SHA256SUMS` verification. The package is uploaded
as a 14-day review artifact; no publication or deployment job runs.

The broader synchronization workflow also exposed a pre-existing arXiv size failure:
the current `paper/` bundle is 86 MB against the validator's 50 MB limit. The other six
synchronization jobs pass, and the compatibility change does not modify `paper/`.
Remediation is isolated in [#249](https://github.com/egohygiene/reflector/issues/249)
so the publication debt is visible without coupling figure optimization to Beacon.

## Next migration-safe steps

1. Use this canary as the regression boundary while polishing the Reflector manuscript.
2. Compare individual Reflector components with Beacon equivalents and upstream only
   components that have parity evidence.
3. Add a first-class Beacon import seam for image-first magazine page manifests.
4. Restore arXiv bundle headroom through issue #249.
5. Audit Antidote against the proven contract before moving or restructuring its source.
6. Scope any transfer of Pages, DOI, archival, or release ownership as a separate issue.
