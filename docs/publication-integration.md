<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Local publication contract integration

Run `python scripts/test-publication-integration.py` (or
`task publication:test-integration`). The same Python entry point runs in both
the synchronization runtime job and local act workflow. No provider, network
command, token, Git tag, GitHub Release, Pages deployment, Zenodo deposit or
arXiv submission is selected.

The command copies public production scripts, metadata and route sources into a
temporary directory. It invokes those public interfaces rather than reproducing
their validation or staging logic. The inherited environment is allowlisted:
provider credentials, user Git configuration and TeX search overrides are absent.
Commands receive no stdin; diagnostics identify the failed stage, retain a
bounded log tail and replace the temporary root. Timed-out POSIX commands have
their process groups stopped before temporary cleanup. This is local command
selection, not a network sandbox or proof about arbitrary third-party scripts.

## Declared boundary

| Stage | Actual local execution |
| --- | --- |
| Metadata and version | `validate-metadata.py` and `sync-version.py --check` against isolated canonical metadata copies. |
| Magazine consistency | The existing audit on canonical source copies, before tiny producer fixtures replace build inputs. |
| Paper and magazine producers | Fast mode supplies three valid fixed one-page synthetic PDFs. Native mode calls the existing paper and both magazine build wrappers on tiny synthetic TeX. |
| arXiv | Real dependency-closure staging, deterministic ZIP/TAR.GZ creation and structural packaging validation of the synthetic source. |
| Source fixture | A real local Git archive of a fixed synthetic commit; no tag or remote is created. This is not the workflow's full source archive recipe. |
| Release stage | `stage-publication-release.py` produces the manifest, checksums and inventory. Real `sha256sum --check` verifies the generated checksums. |
| Pages | `stage-pages.py` stages and validates the real route source with the same synthetic PDF bytes. Native checksum verification and byte/hash comparisons bind publication metadata, versions and all three PDFs across release/Pages. |

The complete publication-readiness audit may compile the canonical manuscript
and includes editorial/figure/bibliography requirements. It remains outside this
small fixture boundary; it is not skipped and called passed. Likewise the
workflow-inline release-note/chktex/Zenodo-readiness composition, full source
archive recipe, real bibliography/Biber path, preview rasterization, browser or
device rendering, action setup/upload and hosted/external publication are not
qualified here. Existing validation jobs and the remote `dry_run: true` workflow
remain their owners. No validator is weakened for the fixture.

Canonical metadata may describe the real publication, but its fixture PDFs and
source are explicitly synthetic. Passing this test proves interface composition;
it does not validate the published manuscript, image previews, DOI registration,
archive acceptance, production reliability or human release approval.

## Fast and native modes

Fast mode requires Python 3.10+, PyYAML, Git and `sha256sum`, and normally takes a
few seconds. It creates no binary fixture files in the repository and removes
the disposable repository, home, compiler/source outputs and staging directories
on success or failure. Production source and version files remain unchanged.
The report lists stage outcomes, explicit exclusions, interface hashes and
artifact hashes. Retain it with an unused path:

```sh
python scripts/test-publication-integration.py --report local-integration.json
```

Existing receipts are refused. The report contains relative artifact paths,
public interface digests and explicit synthetic scope; temporary/private roots
and credentials are not included.

The optional native mode requires the repository's local TeX tools:

```sh
python scripts/test-publication-integration.py --native-fixture-builds
# or: task publication:test-integration-native
```

It fails if a required build tool or PDF output is missing. Its deliberately tiny
paper uses basic BibTeX; it does not establish the complete manuscript's Biber
or TeX Live compatibility. The actual production wrappers and configured output
paths are exercised. This optional mode is explicit to keep the normal Python
test loop practical on machines without TeX.

## Regression and acceptance evidence

```sh
uv run --frozen pytest -q tests/test_publication_integration.py
uv run --frozen pytest -q tests/test_stage_publication_release.py tests/test_stage_arxiv_submission.py tests/test_stage_pages.py
```

The integration tests repeat the full declared fast flow and compare every
retained artifact digest. They remove a required PDF, corrupt release bytes and
corrupt a staged Pages PDF, then require the corresponding real staging,
checksum or Pages validator to fail with the artifact/stage identified. Separate
controls cover an explicit deterministic audit clock, environment isolation,
descendant deadlines, receipt preservation and source/temp cleanup.

Unit tests, focused staging smoke tests, this local contract integration, native
fixture builds, hosted workflow dry runs and real release verification are
different evidence. The TODO/audit follow-up retains their remaining boundaries;
no local fixture result closes those external acceptance gates.
