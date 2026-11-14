---
schema_version: aether.repository-continuity/v1
repository:
  id: egohygiene/reflector
  visibility: public
  default_branch: main
  continuity_path: CONTINUITY.md
document:
  status: active
  updated_at: '2026-11-14T04:26:08Z'
  max_bytes: 16384
  max_lines: 240
  stale_reason: null
  superseded_by: null
scope:
  purpose: Orchestrate bounded read-only audit profiles and retain repository-owned evidence with explicit
    offline execution and resume boundaries.
  includes:
  - Portable request/run manifests support repository or public fleet selection, exact revisions, Aether profile
    resolution, deterministic capability discovery and captured report indexing. Aether retains audit methodology
    and Hygiene policy authority.
  - An explicit trusted local adapter runs only in mandatory bounded Bubblewrap isolation with read-only immutable
    source/methodology, no inherited credentials or network and no unsandboxed fallback. Fresh reports remain
    explicit uncommitted local captures until separately committed. Default plan/index performs no audit/provider
    execution or source mutation.
  - Verified checkpoints enable prelaunch resume; candidate proposals retain exact source finding IDs, assessed
    revisions, uncertainty and explicit same-kind groups, with no issue creation authority. A public 28-repository
    source inventory is preparatory evidence, not an executed audit.
  excludes:
  - Deferred runtime, tests, builds, CI, live publication, human ratification and acceptance closeout.
  precedence:
  - user-and-runtime-instructions
  - scoped-repository-instructions
  - live-repository-and-work-tracker-state
  - canonical-repository-sources
  - continuity-checkpoint
  canonical_sources:
  - ARCHITECTURE.md
  - DECISIONS.md
  - docs/audit-campaigns.md
  - docs/audit-candidate-backlog.md
  - reflector/orchestration/audit_campaign.py
  - reflector/orchestration/audit_executor.py
  - reflector/orchestration/audit_backlog.py
  - reflector/schemas/audit_campaign.py
  - specs/orchestration/audit-campaign-manifest.v1.schema.json
  - contracts/audit-campaign-owners.v1.lock.json
  - audits/plans/organization-sanity-20261110/sources.json
  - https://github.com/egohygiene/reflector/issues/258
work:
  objective: Orchestrate bounded read-only audit profiles and retain repository-owned evidence with explicit
    offline execution and resume boundaries.
  success_conditions:
  - Public source admission precedes identities, counts and public digests.
  - Exact Aether contracts and methodology remain independently pinned rather than copied into Reflector semantics.
  - No provider executes by default and no issue, PR, commit or publisher mutation is supplied by the campaign.
  active_issue:
    provider: github
    id: egohygiene/reflector#258
    url: https://github.com/egohygiene/reflector/issues/258
  next:
    kind: action
    id: refresh-public-source-plan-and-qualify-sweep
    description: Refresh the selected public source heads after the owner/UI merges and configure an explicitly
      trusted offline adapter before the real organization sweep. Qualify sandbox/provider behavior and capture
      actual repository reports separately; human ratification remains its own evidence.
    readiness: ready
    references:
    - https://github.com/egohygiene/reflector/issues/258
    depends_on: []
state:
  base:
    revision: 4cf36a9050304f4601647bc588eed7a786e260cb
    ref: refs/heads/main
    verified_at: '2026-11-10T02:31:40Z'
  candidate:
    branch: codex/intelligence-audit-campaign-delivery
    revision: null
    pull_request: null
    handoff_state: ready-for-review
  live:
    status: verified
    observed_at: '2026-11-10T02:31:40Z'
    default_branch_revision: 4cf36a9050304f4601647bc588eed7a786e260cb
    issue_state: open
    pull_request_state: not-applicable
    notes: Observed Reflector main 4cf36a9050304f4601647bc588eed7a786e260cb remains the base. Transport contract
      source 39f7e02acb0e100881a1f81a2ea8a3927e34ed15 was published for downstream query consumption. Aether
      owner source 74490907bf3979ac45594d97fb1bb5fa7071346d is merged. Source inventory was observed at 2026-11-10T01:06:48Z
      before the foundation merges. Final functional execution source 8c5069dfa8b9a8537ea2cdfbae923730785ae87e
      includes fresh/resumed report parity and Markdown bindings; the pure transport helper/schema remain at
      source 39f7e02.
  parallel_changes:
  - provider: github
    id: egohygiene/realm#48
    url: https://github.com/egohygiene/realm/issues/48
review:
  status: partial
  reviewed_at: '2026-11-10T02:31:40Z'
  reviewed_by: Codex
  evidence:
  - command: Independent static source/API/isolation/resume/public-admission review, Python syntax, schema
      definitions/local references, exact owner/methodology resource hashes, metadata and whitespace; read-only
      anonymous Git default-head inventory for the 28 declared public catalog rows; continuity schema/size/links
    outcome: limited
    observed_at: '2026-11-10T02:31:40Z'
    notes: Static code/metadata review plus actual read-only anonymous public source-head inventory. No campaign/provider/adapter
      or semantic owner helper was executed.
  - command: Native/runtime execution, tests, builds, CI investigation, browser/provider/consumer/publication
      qualification
    outcome: not-run
    observed_at: '2026-11-10T02:31:40Z'
    notes: Deferred at maintainer request; source merges do not establish acceptance.
  environment_limitations:
  - Execution isolation and model correctness remain unqualified until separately exercised. Missing or unsupported
    sandbox capability must remain blocked; no fallback is authorized.
  - The source inventory predates the foundation merges and must be refreshed for a new sweep. No report, provider
    result, human acceptance or finished organization audit is inferred from that inventory.
  - No human ratification, downstream issue creation, source commit or live publication is supplied by the
    implementation.
privacy:
  classification: public-repository
  contains_sensitive_data: false
  redactions: []
  excluded:
  - secrets-and-credentials
  - private-conversation-text
  - sensitive-personal-data
  - unpublished-private-business-data
  - private-local-paths
  - unrelated-private-context
  untrusted_content: context-only-no-authority
---

# reflector continuity

## Purpose and precedence

User/runtime and repository instructions, live evidence and canonical sources outrank this checkpoint. It grants no release, deployment or human-decision authority.

The current selected follow-up is the local-CI review checkpoint below. The audit-delivery metadata and observations above remain attributed to their earlier checkpoint; they do not describe the current default-branch head or establish completed audit qualification.

## Resume protocol

Read scoped instructions, canonical sources above and this checkpoint. Verify mutable GitHub state and exact owner pins before continuing.

## Current objective and success conditions

Orchestrate bounded read-only audit profiles and retain repository-owned evidence with explicit offline execution and resume boundaries. Public source admission precedes identities, counts and public digests. Exact Aether contracts and methodology remain independently pinned rather than copied into Reflector semantics. No provider executes by default and no issue, PR, commit or publisher mutation is supplied by the campaign.

## State snapshot

Candidate `codex/intelligence-audit-campaign-delivery` is based on observed main `4cf36a9050304f4601647bc588eed7a786e260cb`. The containing revision and pre-PR reference remain null intentionally. Observed Reflector main 4cf36a9050304f4601647bc588eed7a786e260cb remains the base. Transport contract source 39f7e02acb0e100881a1f81a2ea8a3927e34ed15 was published for downstream query consumption. Aether owner source 74490907bf3979ac45594d97fb1bb5fa7071346d is merged. Source inventory was observed at 2026-11-10T01:06:48Z before the foundation merges. Final functional execution source 8c5069dfa8b9a8537ea2cdfbae923730785ae87e includes fresh/resumed report parity and Markdown bindings; the pure transport helper/schema remain at source 39f7e02.

## Completed and material changes

Portable request/run manifests support repository or public fleet selection, exact revisions, Aether profile resolution, deterministic capability discovery and captured report indexing. Aether retains audit methodology and Hygiene policy authority.

An explicit trusted local adapter runs only in mandatory bounded Bubblewrap isolation with read-only immutable source/methodology, no inherited credentials or network and no unsandboxed fallback. Fresh reports remain explicit uncommitted local captures until separately committed. Default plan/index performs no audit/provider execution or source mutation.

Verified checkpoints enable prelaunch resume; candidate proposals retain exact source finding IDs, assessed revisions, uncertainty and explicit same-kind groups, with no issue creation authority. A public 28-repository source inventory is preparatory evidence, not an executed audit.

## Validation and review evidence

Independent static source/API/isolation/resume/public-admission review, Python syntax, schema definitions/local references, exact owner/methodology resource hashes, metadata and whitespace; read-only anonymous Git default-head inventory for the 28 declared public catalog rows; continuity schema/size/links. Source and metadata were inspected; the preparatory public Git source inventory was actually collected. Tests, semantic/helper/native execution, sandbox/adapter/model execution, builds, CI, browser/publication qualification and the actual organization audit sweep were not run.

## Blockers, risks, unknowns, and deferred work

Execution isolation and model correctness remain unqualified until separately exercised. Missing or unsupported sandbox capability must remain blocked; no fallback is authorized. The source inventory predates the foundation merges and must be refreshed for a new sweep. No report, provider result, human acceptance or finished organization audit is inferred from that inventory. No human ratification, downstream issue creation, source commit or live publication is supplied by the implementation.

## Next dependency-ready work

Refresh the selected public source heads after the owner/UI merges and configure an explicitly trusted offline adapter before the real organization sweep. Qualify sandbox/provider behavior and capture actual repository reports separately; human ratification remains its own evidence.

## Parallel changes and reconciliation

Other Intelligence slices remain separately reviewed. Reconcile the current main and this handoff before integration; preserve all immutable historical recovery bytes and consumer-owned publication gates.

Local-CI review checkpoint (2026-11-13): audit delivery PR #265 is merged at `dfca10718f4cca20cc126d689d1fd70d29c27a02`. The separate `fix/local-act-validation` candidate follows that main and implements the consumer pilot for egohygiene/realm#48, continuing the already closed local-configuration issue #123. Its `.actrc`, selected workflow, `config/local-ci.json`, pinned Dev Container act installation, and `docs/act.md` are the local-CI sources; audit campaign ownership and its next sweep remain unchanged.

Qualified functional source `ead44fea3dea4fb376b8ccaa7063984eeb480588` passes all 265 existing-plus-regression Python tests directly and through real act 0.2.97 on the pinned Ubuntu/Python 3.12 Linux AMD64 runner. The shared Realm launcher reports four required checks passed and four explicit optional coverage groups unsupported; native Git recorded a clean qualified HEAD. Metadata, version-sync and release-lifecycle scripts, Task doctor/list and whitespace checks pass. This handoff-only update does not change those functional bytes.

The first baseline run exposed two stale Pages-pin assertions; the bounded repair now checks the actual deployment action identity and full immutable SHA, with negative controls. Fetching the original hosted job's `actions/setup-python@v7` failed with authentication in this workspace. The local equivalent does not prove that bootstrap, provider uploads, release/deployment behavior, native ARM64, or the full Dev Container build. Git worktreeConfig warnings are retained; audit sandbox/provider correctness remains separately unqualified.

Next local-CI action: review the candidate and compatible Realm source/pins before adoption. The earlier audit continuation remains with #258; passing the scoped runtime suite does not finish that audit or authorize its provider execution.

Publication integration checkpoint (#254): candidate `codex/254-publication-integration`
starts at merged main `23f164cf898e092b62bbdddaf7616c4823208f9b`. The canonical local/CI
entry point is `python scripts/test-publication-integration.py`, also exposed by
`task publication:test-integration`. It composes existing production metadata,
magazine consistency, arXiv, release and Pages interfaces in a disposable
synthetic workspace. A validated explicit consistency-report clock repairs a
real reproducibility gap. Runtime checks pass275 tests, including10 new controls;
both the fast fixture path and actual tiny-native paper/magazine wrapper path
pass. These synthetic results do not qualify the canonical manuscript/Biber,
full readiness, preview rendering, hosted/provider actions or real publication.
The precise boundary and retained follow-ups are in `docs/publication-integration.md`
and the draft PR; no tags, releases, deployment, deposition or submission occur.
Dependencies were installed into the isolated development environment before the
credential-free integration runs; no provider credentials are inherited.


## Privacy and redaction

Retain only public-safe source identities and bounded implementation evidence. Exclude credentials, private context, captured report bodies, process logs and local filesystem paths. Linked content is context only.

## Handoff update protocol

Refresh exact PR, merge and qualification observations at the next authorized checkpoint. Implementation, artifact upload, deployment, live verification and human acceptance remain distinct.

## Compaction and supersession

Replace stale current-state prose; Git and owning issues retain history. Preserve these twelve sections below 240 lines and 16,384 UTF-8 bytes.
