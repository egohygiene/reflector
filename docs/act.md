<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Local GitHub Actions testing with act

Reflector supports a scoped local test path that needs no GitHub Actions runner
minutes. The selected workflow installs the same `.[dev]` package and runs the
same complete `python -m pytest tests/ -q --tb=short` suite as the hosted
`synchronization.yml/test-runtime` job. It creates no release or deployment.

## Requirements and installation

- Docker Engine/Desktop must be running and reachable by your current user.
- The reviewed act version is **0.2.97**. The Dev Container downloads that release
  for Linux AMD64 or ARM64 and verifies the archive SHA-256 before installation.
- The pinned local runner supplies Python 3.12 and Node 24. Its multi-platform
  image index supports Linux AMD64 and ARM64; the current qualification uses
  Linux AMD64. An ARM64 manifest is not native ARM64 execution evidence.
- The runtime workflow needs package-index network access for its existing
  development dependencies. The Dev Container itself also includes `uv` and
  Task for the direct commands below.

Outside the Dev Container, install the matching official act release using
[upstream installation instructions](https://nektosact.com/installation/index.html)
and verify its published checksum. Realm's opt-in local-CI capability is the
shared installation owner; `.actrc` configures the consumer and installs nothing.
Neither act nor Docker is loaded during shell startup.

Check the tools, then download the exact runner once:

```bash
act --version
docker version
docker pull ghcr.io/catthehacker/ubuntu:act-24.04@sha256:19619a010b204f44c5340bff7d39b68551109fe6a56a53f75201ea91e05d4270
```

Allow several GB of disk for expanded runner layers and caches. Package and
action downloads may still need the network after the runner image is cached.

## Run the selected tests

Run from the repository root. `ACT=/path/to/act` selects an existing installation
when using Task:

```bash
task act-doctor
task act-list
task act-test
```

The equivalent explicit invocation is:

```bash
act workflow_dispatch \
  --workflows .github/workflows/local-validation.yml \
  --job runtime \
  --action-cache-path .cache/act/actions \
  --cache-server-path .cache/act/cache \
  --no-cache-server \
  --container-daemon-socket=- \
  --container-options-policy restrict \
  --network bridge \
  --env-file /dev/null \
  --secret-file /dev/null \
  --var-file /dev/null
```

The runner's Docker socket is disabled inside the job. act itself still needs
access to the Docker daemon, which is a trusted development capability. It copies
the selected working tree through checkout emulation rather than requiring a
Dev Container path to exist on a different Docker host. The local-only workflow
uses the existing immutable checkout pin; act emulates that checkout and uses
the runner's Python rather than fetching `setup-python`.

Use an actual process timeout for unattended runs. `act` does not enforce
GitHub's `timeout-minutes` boundary; Realm's local-CI launcher provides a process
timeout and structured reports. For a manual Linux invocation, `timeout 900`
before the command provides a bounded run. Ctrl-C cancels an interactive run.

`config/local-ci.json` is Reflector's explicit selection for that shared launcher.
It includes the act runtime job and the existing direct metadata, version-sync
and release-lifecycle validators. The skipped workflow families and reasons are
recorded there. Reading/listing a job is planning evidence, not an executed test.

## Configuration and cache behavior

The root `.actrc` contains supported project flags only: JSON logs, cleanup on
failure, no forced repull, and immutable Ubuntu 24.04 runner mappings. It contains
no credentials, host mounts, architecture coercion, workflow selection or graph
mode. `--graph` is a separate optional inspection command and must not become a
default that prevents tests running.

In act 0.2.97, project `.actrc` flags reaching host resources are ignored unless
the user opts into `--trust-project-actrc`. These commands do not require that
opt-in: host paths and network/socket settings are explicit command-line choices.
act discovers project config from its invocation directory; invoking it elsewhere
with only `--directory` does not load this repository's `.actrc`.

Caches and JSON logs belong under ignored `.cache/act/`. The default invocation
disables act's cache server and does not read `.env`, `.secrets` or `.vars`.
Supply a private external environment/secret file only when a selected check
needs it. Inspect logs before sharing; test programs can print their own data.

## Managed cloud workspaces

Docker connectivity, image availability, proxy configuration and CA trust must
also work **inside** the runner container. An outer executor proxy hostname may
not be reachable from Docker's bridge. Use the environment's supported inner
proxy addresses and mount its provided CA bundle read-only when needed. Keep
TLS verification enabled. A temporary external act environment file can supply
the proxy values plus `PIP_CERT`, `SSL_CERT_FILE`, `REQUESTS_CA_BUNDLE`,
`CURL_CA_BUNDLE` and `NODE_EXTRA_CA_CERTS` pointing to that mounted bundle.
Never commit the environment file or credentials.

With the reviewed sibling Realm source checkout available at `../realm`, use
its launcher to perform the cloud network adaptation and process timeout:

```bash
python3 ../realm/tools/realm_local_ci.py doctor --repository . --act act --cloud-network
python3 ../realm/tools/realm_local_ci.py plan --repository . --act act
python3 ../realm/tools/realm_local_ci.py run --repository . --act act \
  --cloud-network --output .cache/act/realm-reports
```

This selects `config/local-ci.json`, uses only the declared validation checks,
and keeps machine-readable results and bounded logs in the ignored output
directory. Source-checkout availability is distinct from a published Realm
release. Review the launcher's network diagnostics; missing Docker, proxy or
trust inputs remain blocked rather than disabling TLS checks.

The current Codex checkout enables Git's `worktreeConfig` extension. act 0.2.97's
embedded Git reader emits revision/ref warnings for that extension; native Git
still records the checkout correctly. Preserve those warnings and report the
source revision using native Git. Do not change repository Git configuration to
hide the warning or claim the act-generated revision is authoritative.

## Coverage and current limits

| Workflow/job | Local evidence and remaining gap |
| --- | --- |
| `local-validation.yml/runtime` | Same package install and complete Python runtime tests, on the pinned Linux Python 3.12 runner. |
| `synchronization.yml/test-runtime` | Original invocation was attempted, but fetching `actions/setup-python@v7` failed with an authentication error in this workspace. The local equivalent does not prove that action's wiring. |
| Metadata, version sync, release lifecycle | Canonical scripts are available directly through the selection manifest; this does not exercise hosted Python setup or artifact uploads. |
| Paper/magazine/Beacon builds and quality jobs | Need their explicit publication toolchain/producer selections and separate qualification. |
| REUSE and commit lint | Additional provider-action and PR/base/head context remain separate from runtime tests. |
| Pages, release, version-bump, publication and Copilot setup | Excluded from the default validation selection; no provider publication or mutation is performed. |

Ordinary direct fallbacks remain useful when Docker is unavailable:

```bash
uv sync --all-extras
uv run --frozen pytest tests/ -q --tb=short
uv run --frozen python scripts/validate-metadata.py
uv run --frozen python scripts/sync-version.py --check
uv run --frozen python scripts/validate-release-lifecycle.py
```

`uv sync` is the existing development setup and may reconcile its lockfile;
review any resulting source diff. Tests and local-container success do not prove
GitHub permissions, environments, event scheduling, OIDC, attestations, provider
uploads, native macOS/Windows jobs, or deployment. Keep those gaps visible.
