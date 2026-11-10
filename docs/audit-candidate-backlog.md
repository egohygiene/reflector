# Audit candidate backlog projection

Refs [Reflector #258](https://github.com/egohygiene/reflector/issues/258).

`reflector.orchestration.audit_backlog.propose_backlog` creates deterministic
review proposals from Aether-validated public finding records. It reads no
files, runs no provider, and performs no downstream mutations. The caller must
authenticate the exact Hygiene public roster and admit every report source
before invoking it. A report's claimed visibility is insufficient.

Pass `public_repositories` as that authenticated set. Private or excluded
records disappear before identities, payloads, counts and digests. Findings
retain their repository, report digest, immutable source revision/path, owner
finding ID, profile/version, classification, nature, severity, confidence,
status, evidence classification, missing evidence and suggested validation.
Owner recommendations remain attributed source recommendations.

The default creates one proposal per supplied finding. Callers may pass explicit
`groups` containing `finding_keys` and a `rationale`. Keys are
`repository:report_sha256:finding_id`. Groups cannot overlap or combine different
classifications/natures. No title matching silently equates sources, and
experimental ideas cannot become defects through grouping. Each grouped source
retains its own full facts and uncertainty.

The closed `egohygiene.reflector.audit-candidate-backlog/v1` artifact includes
deterministic proposal IDs, required human review, no mutation authority, and a
canonical digest of the document excluding its own `digest`. A proposal is not
proof that work is required. Positive observations and intentional tradeoffs
retain their owner classification. The operator chooses which findings merit
candidate review. Issue creation requires a separately authorized operation.

Source-only validation covered Python syntax, schema definitions and independent
review. Implementation execution, scenarios, tests and CI remain deferred.
