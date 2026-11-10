# Public audit campaigns

Refs [Reflector #258](https://github.com/egohygiene/reflector/issues/258),
[Aether #86](https://github.com/egohygiene/aether/issues/86),
[Aether #87](https://github.com/egohygiene/aether/issues/87) and
[Hygiene #59](https://github.com/egohygiene/hygiene/issues/59).

This first checkpoint supplies portable campaign intent, immutable local
source/owner admission and captured-report indexing. It is separate from
`reflector audit`, whose historical action/invariant/drift example is synthetic.
It does not execute an AI audit or human ratification. Aether owns audit
profiles, report semantics and architecture reviews; Hygiene owns policy,
applicability and the public roster. Reflector composes transport passes.
Observatory and Relay retain normalized read models and publication ownership.
[ADR-0004](../DECISIONS.md#adr-0004-compose-owner-defined-audit-captures-through-a-read-only-campaign)
remains proposed.

## Portable entrypoints

```sh
reflector audit-campaign --mode plan \
  --request audits/plans/organization-sanity-20261110/request.json \
  --catalog-root /sources/hygiene --aether-root /sources/aether \
  --output /review/organization-sanity-plan
```

The equivalent stdlib-only entrypoint is
`python3 reflector/orchestration/audit_campaign.py plan ...`.
Use `index` instead of `plan` to admit existing captures, with repeatable
`--repository-root egohygiene/NAME=/sources/NAME`. This does not run repository
programs. Source roots must already contain the exact requested Git objects;
there is no implicit network, checkout, latest-branch resolution or provider.
The new output directory must lie outside inspected Git roots and never
replace an existing run. Commands above are usage examples, not executed proof.

`reflector/schemas/audit_campaign.py` exports pure stdlib
`validate_request`, `validate_manifest`, `canonical_bytes` and `digest`.
The standalone schemas live in `specs/orchestration/`. JSON schema handles
structure; helper checks additionally bind source URL/path/revision, clocks,
unique identities, exact owner metadata and supported transport states.

## Public selection and owner trust

The fixed source is Hygiene's exact public projection at
`49639c1845cdfd08fbd5a768261a8b3cf515f80f`, SHA-256
`af9c7186ded0bb57b18741eaa5905314b96d6adb03736946c868e0fc4aa50b26`.
It is read from its Git blob; no second registry or mixed catalog is imported.
An explicit `scope.selection` of `all` or `include` survives public projection.
Unknown/excluded selectors and their source paths are omitted before path
lookup, source/report identity validation, hashing or counts. An empty admitted
include set never expands to the full roster. Scope cannot authorize mutation.

`contracts/audit-campaign-owners.v1.lock.json` selects exact Aether Git trees,
helper/registry/schema hashes and coherence governance dependencies. Trusted
owner code is materialized only from these verified Git blobs into private
temporary directories. Consumer source is data and is never imported or run.
The coherence helper composes the exact Hygiene governance contract; no policy
or human decision is copied into Reflector semantics.

Each report selection is a JSON Git blob with an exact source revision, path
and original byte SHA-256. Before owner helpers or report hashes, admission
checks public report/scope/finding visibility, selected scope membership,
structured source ownership, and every GitHub/API/raw source URL against the
fixed public roster. Encoded/query/credential/case ambiguities are denied.
Bounded namespace scanning rejects excluded organization references even in
prose; this is an admission guard, not a private-to-public redaction engine.
Arbitrary public prose still requires source-owner privacy review.

Audit captures must use the exact resolved requested profiles and represented
source. Findings are indexed only under their actual repository. Sanity
captures retain architecture-review execution separately from governance;
the adapter calls `validate_review(public_repositories=...)` and never supplies
trusted human evidence or infers ratification. Recommendations, suggestions,
policy applicability and actual acceptance are not transport verdicts.

## Artifacts, bounds and checkpoints

The output contains `manifest.json`, `repositories.json`, `findings.json`,
`candidate-backlog.json` and `summary.md`. Reports/prose remain canonical in
their owning Git sources; the index retains source references and bounded
finding IDs. Constructed GitHub blob URLs identify declared immutable source
locations; local object admission does not prove hosted availability or human
acceptance. Raw file SHA-256 and semantic JSON digests remain distinct.

Transport passes expose public selection, profile resolution, declared source
binding, external audit/coherence captures, index state, disabled backlog
synthesis and an unrequested human-review boundary. `indexed` describes capture
admission/completion, never a pass, healthy repository, policy conformance or
completed organization sanity sweep. Missing/failed/partial input remains
explicit and cannot become an observed empty successful audit.

Limits are at most64 repositories,16 selected reports each,1MiB per report,
4,096 finding references, four workers, depth0–1 and a declared bounded time
budget (at most1,800seconds). Immutable Git calls have15-second bounds. Work
and buffered results are bounded per worker batch; finding budget exhaustion
retains a partial index with `truncated: true`. Output files are bounded at8MiB.
Source failures are isolated per admitted repository/report. Shared owner or
catalog trust failures deny the run. Final outputs are written as one new
atomic directory; historical evidence is not overwritten.

`--stop-after N` produces an explicit checkpoint for the firstN sorted public
repository selections; the rest are `not-inspected/cancelled`. Supply exact
`--previous-manifest` and `--previous-sha256` to compare unchanged input/index
metadata on resume. This checkpoint revalidates captured inputs and marks
unchanged references; it does not yet skip a model launch because no model
adapter runs in this checkpoint. External executor and proposed backlog
adapters remain follow-up implementation under #258.

## Prepared organization sweep

[The source plan](../audits/plans/organization-sanity-20261110/README.md) records
all28 fixed-roster default-branch heads from anonymous read-only Git queries.
No audit/review/model run occurred and report selections remain empty. Refresh
these heads after the new foundations merge, select/execute the Aether-owned
profiles and review skill separately, then index their actual owner captures.
Actual human ratification remains a separate evidence-backed action.

Source/JSON-schema/AST/hash inspection is separate from qualification. Tests,
builds, CI, native execution, mixed-state/resume/cancellation fixtures, large
campaign performance, actual model/skill execution, full organization sweep
and hosted publication remain deferred. No issue closeout is claimed.
