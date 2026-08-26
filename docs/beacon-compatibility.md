<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Beacon Compatibility

Reflector consumes Beacon as a pinned, non-deploying compatibility layer. Reflector's
native paper, magazine, metadata, Pages, DOI, archive, and release contracts remain
authoritative until a separately reviewed migration proves parity.

## Authority boundaries

| Concern | Authoritative owner | Beacon role |
| --- | --- | --- |
| Paper source and styling | `paper/` and `scripts/build-paper.sh` | Invoke the native build and package `reflector.pdf`. |
| Magazine source and styling | `magazine/` and `scripts/build-magazine.sh` | Invoke the native digital/print build and package both PDFs. |
| Publication metadata | `metadata/`, `publication.json`, and `release-manifest.json` | Run native validation and package the validated JSON. |
| Pages and public URLs | `.github/workflows/pages.yml` | No deployment access or behavior. |
| Releases, DOI, Zenodo, and arXiv | Reflector's publication workflows and human gates | No publication, submission, tag, or release behavior. |
| Compatibility evidence | `.beacon/profiles/reflector-compatibility/` | Emit a deterministic mapping and exception report. |

The compatibility profile deliberately adapts the existing project. It is not a
starter template and refuses Beacon `init` execution.

## Dependency and trust model

[`dependencies/beacon.lock.json`](../dependencies/beacon.lock.json) pins the exact
Beacon repository revision, CLI version, Rust toolchain, profile ID, and profile version. The runner
rejects an explicitly supplied `BEACON_ROOT` unless its checked-out revision exactly
matches that pin.

The profile is stored in Reflector's external registry. Beacon therefore permits
inspection and planning without trust, but requires the explicit
`--allow-executable-adapter` acknowledgement before doctor, build, or package. The
repository runner adds that acknowledgement only for its reviewed local adapter.

## Usage

The runner resolves the pinned checkout into the ignored `.cache/beacon/` directory
unless `BEACON_ROOT` points to an already pinned checkout.

```bash
./scripts/beacon-compatibility.sh validate
./scripts/beacon-compatibility.sh inspect
./scripts/beacon-compatibility.sh doctor
./scripts/beacon-compatibility.sh plan
./scripts/beacon-compatibility.sh package
```

The package command performs Reflector's native metadata validation, paper build,
and both magazine builds. Beacon then verifies and packages:

- `reflector.pdf`
- `reflector-magazine.pdf`
- `reflector-magazine-print.pdf`
- `publication.json`
- `release-manifest.json`
- `compatibility-report.json`
- `beacon-package.json`
- `SHA256SUMS`

By default, Beacon-owned build output is written under
`build/beacon-compatibility/`, and the package is written under
`dist/reflector-compatibility-0.1.0/`. Both locations are ignored build products.

## Compatibility policy

Compatibility means Beacon can inspect, plan, validate, build, and package the
declared Reflector artifacts through Reflector's own contracts. It does not mean that
Reflector has been rewritten to use Beacon's built-in starter sources.

The current exceptions are intentional:

1. Reflector keeps its bespoke LaTeX style, macros, biblatex, and biber pipeline.
2. Reflector's image-first magazine keeps its prompt-to-page provenance and paired
   digital/print sources.
3. Reflector's Pages, DOI, Zenodo, arXiv, artifact names, and release history are not
   transferred.

The machine-readable `compatibility-report.json` records those boundaries, their
owners, the pinned Beacon revision, the observed Reflector revision, artifact
checksums, and an explicit declaration that no deployment or publication occurs.

## Canary

`.github/workflows/beacon-compatibility.yml` recreates the trusted environment from a
clean checkout, installs the native toolchain, checks out the locked Beacon commit,
inspects the plan, packages all declared artifacts, verifies `SHA256SUMS`, and uploads
the package as a review artifact. It has read-only repository permissions and contains
no deployment or release job.
