<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Version-Bump Workflow Validation

**Date:** 2026-07-16
**Issue:** [#227](https://github.com/egohygiene/reflector/issues/227)
**Scope:** Manual semantic-version bump workflow design, implementation, and safeguards

---

## Summary

This audit documents the design decisions, implementation, and expected behavior
of the `.github/workflows/bump-version.yml` workflow added as part of issue #227.

---

## Design Decision — Single Tag Ownership

The bump workflow updates the canonical VERSION and synchronized metadata surfaces,
then commits and pushes to the default branch. **It does not create the release tag.**

Tag creation is owned exclusively by `release-tag.yml`, which triggers automatically
when `VERSION` changes on `main`. This design preserves one unambiguous owner for
tag creation and prevents racing or duplicate tag events.

```
bump-version.yml      (owned: version mutation, metadata sync, commit, push)
    ↓ push to main
release-tag.yml       (owned: annotated tag creation)
    ↓ tag push
publication.yml       (owned: full build, release creation, pages deployment)
```

---

## Workflow Triggers

| Trigger | Value |
|---|---|
| Type | `workflow_dispatch` only |
| Branch restriction | Default branch enforced at runtime (step-level check) |
| Inputs | `bump_type` (major / minor / patch), `dry_run` (true / false) |
| Concurrency group | `publication-version-bump` with `cancel-in-progress: false` |

---

## Safeguards Implemented

| Safeguard | Implementation |
|---|---|
| Default-branch enforcement | Step fails if `github.ref_name != github.event.repository.default_branch` |
| Bump type validation | `case` statement fails on any value other than `major`, `minor`, `patch` |
| Semver format check | `grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'` on current VERSION |
| Required files check | Explicit existence check for 11 canonical publication files |
| Duplicate tag guard | `git rev-parse --verify refs/tags/${TAG}` fails if tag already exists |
| Validation gate | `sync-version.py --check`, `validate-metadata.py`, `validate-release-lifecycle.py` all pass before committing |
| Concurrent bump prevention | `concurrency.cancel-in-progress: false` prevents two bumps racing |
| Dry run mode | `dry_run: true` shows computed next version without modifying any files |
| Partial push prevention | Commit and push are separate steps; push only runs after commit succeeds |

---

## Third-Party Action Usage

The workflow uses only official GitHub Actions, pinned to stable release tags:

| Action | Version | Why |
|---|---|---|
| `actions/checkout@v4` | v4 | Stable release tag; full history fetch with `fetch-depth: 0` |
| `actions/setup-python@v5` | v5 | Stable release tag; Python 3.12 for sync-version.py |

No third-party actions from unstable `@master` references are used.

---

## Permissions

| Permission | Level | Rationale |
|---|---|---|
| `contents: write` | Required | Commit and push the version bump commit |
| All other permissions | Default (read) | No additional permissions required |
| `id-token: write` | Not requested | OIDC is not required |

---

## Version Propagation Verification

After the workflow runs, all surfaces updated by `sync-version.py` must carry
the new version. Validation is enforced by:

1. `python scripts/sync-version.py --check` — confirms no drift after sync.
2. `python scripts/validate-metadata.py` — validates all canonical metadata surfaces.
3. `python scripts/validate-release-lifecycle.py` — validates workflow contracts and
   cross-surface version consistency.

If any of these fail, the workflow exits before creating the commit.

---

## Downstream Workflow Integration

After a successful bump:

| Workflow | Trigger | Action |
|---|---|---|
| `release-tag.yml` | Push to main (VERSION changed) | Creates annotated tag `vX.Y.Z` if absent |
| `publication.yml` | Push to main (VERSION changed) | Full build, packaging, GitHub Release, Pages |
| `synchronization.yml` | Push to main (metadata paths changed) | Re-validates all sync surfaces |

The bump workflow commit message follows the conventional commit format:
```
chore(release): bump version X.Y.Z → A.B.C [patch]
```

The `[skip ci]` token is **not** added; downstream workflows should trigger normally
so the full release pipeline runs exactly once.

---

## Acceptance Criteria Status

| Criterion | Status |
|---|---|
| Triggered only through `workflow_dispatch` | ✅ |
| Accepts `major`, `minor`, `patch` choice | ✅ |
| Runs only from the default branch | ✅ |
| Fetches complete Git history and tags | ✅ (`fetch-depth: 0`) |
| Verifies working tree state before mutation | ✅ (required files check) |
| Updates only the canonical version source directly | ✅ (VERSION written first, sync applied) |
| Runs metadata synchronization tooling | ✅ (`sync-version.py`) |
| Runs version and metadata validation | ✅ (`validate-metadata.py`, `validate-release-lifecycle.py`) |
| Shows previous and next versions before writing | ✅ (compute-next-version step logs both) |
| Creates a conventional version-bump commit | ✅ (`chore(release): bump version ...`) |
| Does not create the release tag directly | ✅ (tag creation delegated to release-tag.yml) |
| Pushes commit safely | ✅ (push runs after successful commit only) |
| Produces a clear GitHub Actions summary | ✅ (workflow summary step) |
| Avoids mutable `@master` action references | ✅ |
| Minimizes permissions | ✅ (`contents: write` only) |
| Dry run mode supported | ✅ |
| Concurrent bump prevention | ✅ (concurrency group) |
| Duplicate tag guard | ✅ (git rev-parse check) |
| Fails before pushing on validation failure | ✅ |

---

## Dry-Run Verification — v0.1.3

The following dry-run calculation confirms the expected next patch version from the
current `VERSION` at the time of issue [#230](https://github.com/egohygiene/reflector/issues/230):

| Field | Value |
|---|---|
| Current VERSION | `0.1.2` |
| Bump type | `patch` |
| Expected next VERSION | `0.1.3` |
| Expected tag | `v0.1.3` |
| Computed by | Python: `int("2") + 1 = 3` → `0.1.3` |

A production bump should not be executed automatically. The maintainer may initiate the
`v0.1.3` release by running `.github/workflows/bump-version.yml` with `bump_type: patch`
from the default branch.

---

## Files created

| File | Description |
|---|---|
| `.github/workflows/bump-version.yml` | Manual semantic-version bump workflow |
| `docs/release-process.md` | Updated with "Manual Semantic-Version Bump" section |
