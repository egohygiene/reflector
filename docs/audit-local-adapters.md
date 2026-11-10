# Explicit local audit adapters

Refs [Reflector #258](https://github.com/egohygiene/reflector/issues/258).
The default `plan`/`index` path never runs a model or consumer program.
`discover` performs deterministic bounded Git-source/capability collection
without a model. `run` adds an explicitly selected local command adapter;
neither mode changes provider state, commits, pushes or ratifies decisions.

An operator supplies a reviewed request with provider adapter `local-command`,
an optional plain model identifier, `--allow-execution`, the trusted executable
`--executor` and exact `--executor-sha256`. The request cannot select executable
paths or shell arguments. Optional resources use repeatable
`--executor-resource name=/trusted/file#sha256`; they are regular files copied,
hashed and frozen privately before use, with a16GiB total bound. No model
provider, package, credential, remote session or billing is configured by this
adapter. A local executable implementing the protocol is replaceable.

`--report-output egohygiene/NAME=/worktrees/NAME` explicitly selects each
repository's owned report worktree. The exact assessed commit must exist in that
worktree. Source files are read from immutable Git objects, not executed or
checked out. New canonical Markdown/JSON and source inventories are written
only below that explicitly selected worktree, through exclusive atomic file
creation; existing different bytes are never overwritten. No Git/provider
mutation follows. Without a valid owned output root, an execution is blocked.
The campaign index itself remains outside inspected sources.

## Execution protocol and isolation

The adapter receives one structured JSON document on stdin with schema
`egohygiene.reflector.audit-executor-request/v1`: public repository/revision,
one independent resolved audit profile (or a coherence job), selected owner
profiles/pins, exact methodology files/digests, bounded source inventory,
provider/model declaration, immutable resource identities and execution limits.
It reads the pinned Aether methodology at `/methodology`: approved
`auditor.spec.md`, draft repository-audit-data spec, the audit skill,
classification/reconciliation/checklist references and report template, or the
coherence skill/spec/template and pinned governance helper. Reflector supplies
no competing auditor taxonomy or assessment methodology.

Only `/source/files` contains source data. All captured files lose executable
mode; symlinks, submodules, binary/oversized files and unsupported paths remain
explicitly omitted. The source pass records root documentation/manifests as
`source-present` or `not-captured`, never as tested capabilities. File/count/byte
bounds and actual source observation times remain separate from model findings.
If audit input is partial, the adapter cannot emit a complete audit. No test,
build, runtime behavior or remote state is inferred from file presence.

Output is one JSON object with schema
`egohygiene.reflector.audit-executor-response/v1` and exactly these fields:
`schema`, `visibility`, `repository`, `represented_commit`, `kind`, `profile`,
`evidence`, `canonical_markdown`. Metadata must equal the requested job. Evidence
must satisfy the exact Aether audit or coherence helper, selected profiles and
assessed revision. An audit supplies nonempty canonical Markdown whose bytes
match its declared hash; its URI stays null until real publication. A coherence
job supplies null Markdown, an AI/tool reviewer and null governance. The adapter
cannot invent a human reviewer, approval, ratification or trusted human proof.

Execution requires fixed system `/usr/bin/bwrap` and `/usr/bin/prlimit`.
Bubblewrap creates new user/PID/network/other namespaces, clears the environment
and makes root/proc, source, methodology, adapter and frozen resources read-only.
Only selected system runtime directories and null/urandom devices are exposed;
host homes, workspace, credentials, sockets and proxy variables are absent.
There is no shell or network fallback. Writable tmpfs mounts are independently
capped at64MiB `/tmp`,16MiB `/output` and16MiB shared memory. CPU, process count,
address space, file size and wall time are bounded. Stdout/stderr use bounded
private regular files; error bodies/model logs never enter public receipts.
Missing/unsupported isolation or denied output remains blocked/failed.

Git reads disable replacement objects, hooks, fsmonitor, global/system config
and lazy fetch. Git stdout is streamed with hard byte caps and kill deadlines;
missing promisor objects never invoke a fetch or consumer remote helper. Git
must support `--no-lazy-fetch`; an unsupported installation fails closed.

`run`/`discover` record actual completion time as the new campaign observation
boundary. Original request/source/report times remain unchanged and separately
bound; honest report completion is never backdated to a pre-execution request.
Per-job receipts distinguish blocked, failed, partial, complete and resumed.
Uncommitted report artifacts retain `source_revision: null` and no invented
GitHub blob URL; proposals separately preserve the assessed `represented_commit`.

Optional grouping input is a closed public object with schema
`egohygiene.reflector.audit-proposal-groups/v1`, `visibility: public` and `groups`.
Groups use exact source finding keys and a public rationale. This produces
proposals for human review, never GitHub issues or canonical obligations.

## Qualification boundary

This implementation was inspected as source. No adapter, model, sandbox,
campaign, source-discovery command, report capture, test, build, CI job or
organization sweep was executed for this change. Namespace/runtime behavior,
local model compatibility, budget/resume/cancellation/error fixtures and actual
end-to-end audit acceptance remain deferred. The prepared28-source inventory
is a read-only source plan; it is not a completed sanity sweep or ratification.
