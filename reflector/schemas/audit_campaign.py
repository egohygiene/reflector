# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Portable public campaign transport contracts; no audit or review semantics."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import re

VERSION = "1.0.0-alpha.1"
REQUEST = "egohygiene.reflector.audit-campaign-request/v1"
MANIFEST = "egohygiene.reflector.audit-campaign-manifest/v1"
REPOSITORY = re.compile(r"egohygiene/(?:\.github|[a-z0-9][a-z0-9.-]*)")
REVISION = re.compile(r"[0-9a-f]{40}")
SHA256 = re.compile(r"[0-9a-f]{64}")
TOKEN = re.compile(r"[a-z0-9][a-z0-9._-]{0,95}")
STATES = {"planned", "indexed", "partial", "blocked", "unavailable", "not-inspected"}
PASS_IDS = ("public-selection", "profile-resolution", "source-binding", "audit-execution",
            "coherence-review", "evidence-index", "candidate-backlog", "human-review")


def require(condition):
    if not condition:
        raise ValueError("Campaign transport is incompatible")


def exact(value, fields):
    require(isinstance(value, dict) and set(value) == set(fields))


def canonical_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n").encode()


def digest(value):
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def instant(value):
    require(isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value))
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def relative(value):
    require(isinstance(value, str) and 1 <= len(value) <= 240 and re.fullmatch(r"[A-Za-z0-9._/-]+", value)
            and not value.startswith("/") and all(part not in {"", ".", "..", ".git"} for part in value.split("/")))
    return value


def match(value, pattern):
    require(isinstance(value, str) and pattern.fullmatch(value))
    return value


def catalog(value):
    exact(value, {"repository", "revision", "path", "sha256", "observed_at"})
    require(value["repository"] == "egohygiene/hygiene")
    match(value["revision"], REVISION)
    require(value["path"] == "catalog/public-repositories.json")
    match(value["sha256"], SHA256)
    instant(value["observed_at"])


def profile_requests(value):
    require(isinstance(value, list) and 1 <= len(value) <= 32)
    seen = set()
    for item in value:
        exact(item, {"id", "version"})
        match(item["id"], TOKEN)
        require(isinstance(item["version"], str) and re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[a-z0-9.-]+)?", item["version"]))
        key = (item["id"], item["version"])
        require(key not in seen)
        seen.add(key)


def report_selection(value):
    exact(value, {"kind", "source_revision", "source_path", "sha256"})
    require(value["kind"] in {"audit", "sanity"})
    match(value["source_revision"], REVISION)
    require(relative(value["source_path"]).endswith(".json"))
    match(value["sha256"], SHA256)


def budgets(value):
    limits = {"maximum_repositories": 64, "maximum_reports_per_repository": 16,
              "maximum_report_bytes": 1048576, "maximum_findings": 4096, "maximum_seconds": 1800,
              "concurrency": 4, "depth": 1}
    exact(value, limits)
    for name, maximum in limits.items():
        require(type(value[name]) is int and (0 if name == "depth" else 1) <= value[name] <= maximum)


def validate_request(value):
    exact(value, {"schema", "contract_version", "campaign_id", "visibility", "organization", "observed_at",
        "catalog", "scope", "profiles", "provider", "budgets", "network_policy", "mutation_authority",
        "candidate_backlog", "report_kinds", "repositories"})
    require(value["schema"] == REQUEST and value["contract_version"] == VERSION
            and value["visibility"] == "public" and value["organization"] == "egohygiene")
    match(value["campaign_id"], TOKEN)
    boundary = instant(value["observed_at"])
    catalog(value["catalog"])
    exact(value["scope"], {"kind", "selection", "include", "exclude"})
    require(value["scope"]["kind"] in {"repository", "organization"}
            and value["scope"]["selection"] in {"all", "include"})
    for key in ("include", "exclude"):
        rows = value["scope"][key]
        require(isinstance(rows, list) and len(rows) <= 64 and len(rows) == len(set(rows)))
        for name in rows:
            match(name, REPOSITORY)
    require(value["scope"]["selection"] != "all" or not value["scope"]["include"])
    profile_requests(value["profiles"])
    kinds = value["report_kinds"]
    require(isinstance(kinds, list) and 1 <= len(kinds) <= 2
            and len(kinds) == len(set(kinds)) and set(kinds) <= {"audit", "sanity"})
    exact(value["provider"], {"adapter", "model"})
    require(value["provider"] == {"adapter": "captured-owner-reports", "model": None}
            and value["network_policy"] == "offline" and value["mutation_authority"] == "none"
            and value["candidate_backlog"] == "disabled")
    budgets(value["budgets"])
    rows = value["repositories"]
    require(isinstance(rows, list) and len(rows) <= value["budgets"]["maximum_repositories"])
    seen = set()
    for row in rows:
        exact(row, {"repository", "represented_commit", "source_observed_at", "reports"})
        match(row["repository"], REPOSITORY)
        require(row["repository"] not in seen)
        seen.add(row["repository"])
        if row["represented_commit"] is not None:
            match(row["represented_commit"], REVISION)
        if row["source_observed_at"] is not None:
            require(instant(row["source_observed_at"]) <= boundary)
        require((row["represented_commit"] is None) == (row["source_observed_at"] is None))
        require(isinstance(row["reports"], list) and len(row["reports"]) <= value["budgets"]["maximum_reports_per_repository"])
        identities = set()
        for report in row["reports"]:
            report_selection(report)
            key = (report["source_revision"], report["source_path"])
            require(key not in identities)
            identities.add(key)
    require(value["scope"]["kind"] != "repository" or value["scope"]["selection"] == "include" and len(rows) <= 1)
    return value


def validate_manifest(value):
    """Validate orchestration metadata without asserting owner report truth."""
    exact(value, {"schema", "contract_version", "campaign_id", "visibility", "organization", "observed_at",
        "mode", "status", "mutation_authority", "analysis_execution", "catalog", "owner_inputs", "profiles",
        "budgets", "passes", "repositories", "request_sha256", "candidate_backlog", "generator"})
    require(value["schema"] == MANIFEST and value["contract_version"] == VERSION
        and value["visibility"] == "public" and value["organization"] == "egohygiene"
        and value["mode"] in {"plan", "index"} and value["status"] in {"planned", "indexed", "partial", "cancelled"}
        and value["mutation_authority"] == "none" and value["analysis_execution"] == "external-captures-only"
        and value["candidate_backlog"] == "disabled")
    match(value["campaign_id"], TOKEN)
    boundary = instant(value["observed_at"])
    catalog(value["catalog"])
    generator = value["generator"]
    exact(generator, {"repository", "revision", "immutable", "implementation_sha256"})
    require(generator["repository"] == "egohygiene/reflector" and type(generator["immutable"]) is bool)
    if generator["revision"] is not None:
        match(generator["revision"], REVISION)
    require(not generator["immutable"] or generator["revision"] is not None)
    exact(generator["implementation_sha256"], {"reflector/orchestration/audit_campaign.py", "reflector/schemas/audit_campaign.py",
        "contracts/audit-campaign-owners.v1.lock.json"})
    for checksum in generator["implementation_sha256"].values():
        match(checksum, SHA256)
    match(value["request_sha256"], SHA256)
    exact(value["owner_inputs"], {"aether_audit", "aether_sanity"})
    for pin in value["owner_inputs"].values():
        exact(pin, {"repository", "revision", "tree", "files"})
        require(pin["repository"] == "egohygiene/aether")
        match(pin["revision"], REVISION)
        match(pin["tree"], REVISION)
        require(isinstance(pin["files"], dict) and 1 <= len(pin["files"]) <= 16)
        for path, checksum in pin["files"].items():
            relative(path)
            match(checksum, SHA256)
    profiles = value["profiles"]
    exact(profiles, {"registry_version", "registry_sha256", "requested", "resolved"})
    require(isinstance(profiles["registry_version"], str) and re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", profiles["registry_version"]))
    match(profiles["registry_sha256"], SHA256)
    profile_requests(profiles["requested"])
    profile_requests(profiles["resolved"])
    budgets(value["budgets"])
    require(isinstance(value["passes"], list) and len(value["passes"]) == len(PASS_IDS))
    for row, expected in zip(value["passes"], PASS_IDS):
        exact(row, {"id", "state"})
        require(row["id"] == expected and row["state"] in {
            "selected", "resolved", "declared", "not-executed", "external-captures", "indexed", "partial", "disabled", "not-requested"})
    require(isinstance(value["repositories"], list) and len(value["repositories"]) <= value["budgets"]["maximum_repositories"])
    names = set()
    for row in value["repositories"]:
        exact(row, {"repository", "represented_commit", "source_observed_at", "state", "reason",
            "input_sha256", "reports", "resume"})
        match(row["repository"], REPOSITORY)
        require(row["repository"] not in names)
        names.add(row["repository"])
        require(row["state"] in STATES and row["resume"] in {"new", "unchanged", "not-inspected"}
                and row["reason"] in {None, "source-not-selected", "source-unavailable", "reports-not-selected",
                "report-unavailable", "report-incompatible", "report-boundary", "report-limit", "budget-exhausted", "cancelled"})
        match(row["input_sha256"], SHA256)
        if row["represented_commit"] is not None:
            match(row["represented_commit"], REVISION)
        if row["source_observed_at"] is not None:
            require(instant(row["source_observed_at"]) <= boundary)
        require((row["represented_commit"] is None) == (row["source_observed_at"] is None))
        require(isinstance(row["reports"], list) and len(row["reports"]) <= value["budgets"]["maximum_reports_per_repository"])
        for report in row["reports"]:
            report_selection({key: report.get(key) for key in ("kind", "source_revision", "source_path", "sha256")})
            exact(report, {"kind", "owner_schema", "source_revision", "source_path", "sha256", "canonical_url", "completion", "findings_count"})
            expected_schema = {"audit": "aether.repository-audit-report/v1", "sanity": "egohygiene.architecture-coherence-review/v1"}
            require(report["owner_schema"] == expected_schema[report["kind"]])
            require(report["canonical_url"] == f"https://github.com/{row['repository']}/blob/{report['source_revision']}/{report['source_path']}")
            require(report["completion"] in {"complete", "partial", "blocked", "failed", "unsupported", "not_applicable", "unknown"})
            if report["kind"] == "sanity":
                require(report["findings_count"] is None)
            else:
                require(type(report["findings_count"]) is int
                        and 0 <= report["findings_count"] <= value["budgets"]["maximum_findings"])
    require(value["status"] != "indexed" or value["mode"] == "index" and bool(value["repositories"])
            and all(row["state"] == "indexed" for row in value["repositories"]))
    return value
