# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Offline composition of exact public Aether audit/coherence captures.

This foundation executes transport passes, not an LLM, auditor, validator suite,
human ratification, provider mutation or publication. Owner reports stay in
their repository Git objects; the campaign retains references and metadata.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
LOCK = ROOT / "contracts/audit-campaign-owners.v1.lock.json"
CATALOG = {"repository": "egohygiene/hygiene", "revision": "49639c1845cdfd08fbd5a768261a8b3cf515f80f",
    "tree": "f35e00f075ae5fa53bcf7734392f8d1443eb172d", "path": "catalog/public-repositories.json",
    "sha256": "af9c7186ded0bb57b18741eaa5905314b96d6adb03736946c868e0fc4aa50b26"}
MAX_DOCUMENT = 1048576
MAX_MANIFEST = 8 * MAX_DOCUMENT


def module(name, path):
    specification = importlib.util.spec_from_file_location(name, path)
    require(specification is not None and specification.loader is not None)
    result = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(result)
    return result


def require(value):
    if not value:
        raise ValueError("Campaign admission denied")


contract = module("reflector_campaign_transport_contract", ROOT / "reflector/schemas/audit_campaign.py")


def safe(path):
    value = Path(path).absolute()
    require(".." not in value.parts and not any(item.is_symlink() for item in (value, *value.parents)))
    return value


def pairs(items):
    result = {}
    for key, value in items:
        require(key not in result)
        result[key] = value
    return result


def parse(content):
    value = json.loads(content, object_pairs_hook=pairs, parse_constant=lambda _value: require(False))
    require(isinstance(value, dict))
    return value


def read(path, maximum=MAX_DOCUMENT):
    path = safe(path)
    require(path.is_file() and 0 < path.stat().st_size <= maximum)
    content = path.read_bytes()
    require(len(content) <= maximum)
    return content


def sha256(content):
    return hashlib.sha256(content).hexdigest()


def generator():
    files = ("reflector/orchestration/audit_campaign.py", "reflector/schemas/audit_campaign.py",
             "contracts/audit-campaign-owners.v1.lock.json")
    hashes = {path: sha256(read(ROOT / path)) for path in files}
    revision, immutable = None, False
    try:
        revision = git(ROOT, "rev-parse", "HEAD").decode().strip()
        contract.match(revision, contract.REVISION)
        immutable = all(sha256(blob(ROOT, revision, path)) == checksum for path, checksum in hashes.items())
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError):
        pass
    return {"repository": "egohygiene/reflector", "revision": revision,
            "immutable": immutable, "implementation_sha256": hashes}


def git(root, *arguments):
    # Only immutable-object queries are used. Never hooks, consumer scripts,
    # filters, Git global configuration, replacement objects or network access.
    environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    environment.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
        GIT_NO_REPLACE_OBJECTS="1", GIT_TERMINAL_PROMPT="0", LC_ALL="C.UTF-8")
    command = ["git", "--no-optional-locks", "--no-replace-objects", "-c", "core.hooksPath=/dev/null",
               "-c", "core.fsmonitor=false", "-C", str(safe(root)), *arguments]
    return subprocess.check_output(command, env=environment, stderr=subprocess.DEVNULL, timeout=15)


def blob(root, revision, path, maximum=MAX_DOCUMENT):
    contract.match(revision, contract.REVISION)
    contract.relative(path)
    row = git(root, "ls-tree", revision, "--", path).decode().strip().split()
    require(len(row) == 4 and row[0] == "100644" and row[3] == path)
    size = git(root, "cat-file", "-s", row[2]).strip()
    require(size.isdigit() and 0 < int(size) <= maximum)
    content = git(root, "cat-file", "blob", row[2])
    require(len(content) == int(size))
    return content


def public_catalog(root):
    require(git(root, "rev-parse", CATALOG["revision"] + "^{tree}").decode().strip() == CATALOG["tree"])
    content = blob(root, CATALOG["revision"], CATALOG["path"])
    require(sha256(content) == CATALOG["sha256"])
    value = parse(content)
    require(value.get("schema") == "egohygiene.repository-public-catalog/v1")
    # Exact owner bytes are the public projection, never a mixed registry.
    # Visibility precedes identities and selection, even for this fixed input.
    rows = [row for row in value["repositories"] if isinstance(row, dict) and row.get("visibility") == "public"]
    public = {row["full_name"]: row for row in rows}
    metadata = {key: CATALOG[key] for key in ("repository", "revision", "path", "sha256")}
    metadata["observed_at"] = value["observed_at"]
    return public, metadata


def admitted_request(value, public, metadata):
    require(value.get("visibility") == "public" and value.get("organization") == "egohygiene")
    scope = value.get("scope")
    require(isinstance(scope, dict) and isinstance(scope.get("include"), list) and isinstance(scope.get("exclude"), list)
            and isinstance(value.get("repositories"), list))
    include = sorted({name for name in scope["include"] if isinstance(name, str) and name in public})
    exclude = sorted({name for name in scope["exclude"] if isinstance(name, str) and name in public})
    # Explicit selection mode survives projection of unknown/hidden selectors:
    # an empty admitted include slice never expands into the full public roster.
    require(scope.get("selection") in {"all", "include"})
    selected = (set(include) if scope["selection"] == "include" else set(public)) - set(exclude)
    rows = [row for row in value["repositories"]
            if isinstance(row, dict) and isinstance(row.get("repository"), str) and row["repository"] in selected]
    present = {row["repository"] for row in rows}
    rows.extend({"repository": name, "represented_commit": None, "source_observed_at": None, "reports": []}
                for name in sorted(selected - present))
    projected = {**value, "scope": {**scope, "include": include, "exclude": exclude},
                 "repositories": sorted(rows, key=lambda row: row["repository"])}
    require(projected["catalog"] == metadata)
    return contract.validate_request(projected)


def owners(stack, aether_root):
    lock = parse(read(LOCK))
    require(lock.get("schema") == "egohygiene.reflector.audit-campaign-owners/v1"
            and set(lock["sources"]) == {"aether_audit", "aether_sanity"})
    loaded = {}
    for name, pin in lock["sources"].items():
        require(pin["repository"] == "egohygiene/aether"
                and git(aether_root, "rev-parse", pin["revision"] + "^{tree}").decode().strip() == pin["tree"])
        directory = Path(stack.enter_context(tempfile.TemporaryDirectory(prefix="reflector-owner-contract-")))
        for path, checksum in pin["files"].items():
            content = blob(aether_root, pin["revision"], path)
            require(sha256(content) == checksum)
            target = directory / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        loaded[name] = {"helper": module("reflector_pinned_" + name, directory / pin["helper_path"]),
                        "directory": directory, "pin": pin}
    audit = loaded["aether_audit"]
    registry = audit["helper"].parse((audit["directory"] / audit["pin"]["registry_path"]).read_bytes())
    audit["helper"].validate_registry(registry)
    audit["registry"] = registry
    metadata = {name: {key: pin[key] for key in ("repository", "revision", "tree", "files")}
                for name, pin in lock["sources"].items()}
    return loaded, metadata


def source_roots(values, public):
    result = {}
    for value in values:
        name, separator, path = value.partition("=")
        if name not in public:
            continue
        require(separator and path and name not in result)
        # Paths are not inspected until this admitted repository's bounded
        # worker runs; one inaccessible/symlink source must not deny peers.
        result[name] = Path(path)
    return result


def public_report_scope(value, allowed, public):
    # Do not read report IDs, findings, hashes or human dispositions until the
    # entire represented scope has been admitted as public and selected.
    require(isinstance(value, dict) and value.get("visibility") == "public")
    scope = value.get("scope")
    require(isinstance(scope, dict) and isinstance(scope.get("repositories"), list))
    rows = scope["repositories"]
    require(rows)
    for row in rows:
        if isinstance(row, str):
            # The coherence contract names scope members and binds their
            # source revisions separately. Public admission comes from roster.
            require(row in allowed)
        else:
            require(isinstance(row, dict) and row.get("visibility") == "public")
            require(row.get("full_name") in allowed)
    governance = value.get("governance")
    if governance is not None:
        require(isinstance(governance, dict) and governance.get("visibility") == "public")
        scope = governance.get("scope")
        require(isinstance(scope, dict) and isinstance(scope.get("repositories"), list))
        require(all(isinstance(name, str) and name in allowed for name in scope["repositories"]))
    findings = value.get("findings", [])
    require(isinstance(findings, list))
    for finding in findings:
        require(isinstance(finding, dict) and finding.get("visibility") == "public")
        require(finding.get("repository") in allowed)
    for key in ("sources", "evidence"):
        collection = value.get(key, [])
        require(isinstance(collection, list))
        for source in collection:
            require(isinstance(source, dict))
            if key == "sources":
                require(source.get("visibility") == "public")
            identity = source.get("repository")
            require(identity is None or identity in public)
    visited = 0
    def public_url(text):
        parsed = urlsplit(text)
        require(parsed.scheme == "https" and parsed.hostname and parsed.username is None and parsed.password is None
                and parsed.port in {None, 443} and not parsed.query and "\\" not in text and "%" not in text
                and not any(ord(char) < 33 or ord(char) == 127 for char in text))
        require(not any(part in {".", ".."} for part in parsed.path.split("/")))
        host = parsed.hostname.lower()
        if host in {"github.com", "raw.githubusercontent.com", "api.github.com", "codeload.github.com"}:
            require(parsed.netloc == host)
            parts = parsed.path.split("/")
            if host == "api.github.com":
                require(len(parts) >= 4 and parts[1] == "repos")
                parts = parts[1:]
            require(len(parts) >= 3 and "/".join(parts[1:3]) in public)
            require(not parsed.fragment or re.fullmatch(r"[A-Za-z0-9_.:-]+", parsed.fragment))
    def inspect(item, depth=0):
        nonlocal visited
        visited += 1
        require(visited <= 100000 and depth <= 24)
        if isinstance(item, dict):
            require("visibility" not in item or item["visibility"] == "public")
            for key in ("repository", "full_name"):
                require(key not in item or item[key] is None or item[key] in public)
            for child in item.values():
                inspect(child, depth + 1)
        elif isinstance(item, list):
            for child in item:
                inspect(child, depth + 1)
        elif isinstance(item, str):
            for match in re.finditer(r"egohygiene/(?:\.github|[a-z0-9][a-z0-9.-]*)", item, re.I):
                require(match[0] in public)
            for match in re.finditer(r"https?://[^\s<>\"']+", item, re.I):
                public_url(match[0])
    inspect(value)


def report(args, selection, row, allowed, loaded, registry):
    repository = row["repository"]
    root = args.roots.get(repository)
    require(root is not None)
    content = blob(root, selection["source_revision"], selection["source_path"], args.budgets["maximum_report_bytes"])
    value = parse(content)
    public_report_scope(value, allowed, args.public_names)
    if selection["kind"] == "audit":
        owner = loaded["aether_audit"]["helper"]
        require(set(owner.referenced_repositories(value)) <= args.public_names)
    require(sha256(content) == selection["sha256"])
    findings = []
    if selection["kind"] == "audit":
        owner = loaded["aether_audit"]["helper"]
        owner.validate_report(value, registry)
        require(value["schema"] == "aether.repository-audit-report/v1")
        require(value["profiles"] == args.profiles)
        scope = {item["full_name"]: item["revision"] for item in value["scope"]["repositories"]}
        require(scope.get(repository) == row["represented_commit"])
        require(contract.instant(value["started_at"]) <= contract.instant(args.observed_at))
        require(value["completed_at"] is None or contract.instant(value["completed_at"]) <= contract.instant(args.observed_at))
        completion = value["completion"]["state"]
        require(len(value["findings"]) <= args.budgets["maximum_findings"])
        for finding in value["findings"]:
            if finding["repository"] != repository:
                continue
            findings.append({"repository": repository, "finding_id": finding["id"],
                "report_sha256": selection["sha256"], "source_revision": selection["source_revision"],
                "source_path": selection["source_path"]})
        count = len(findings)
    else:
        owner = loaded["aether_sanity"]["helper"]
        owner.validate_review(value, public_repositories=args.public_names)
        subject = owner.review_subject(value)
        require(value["schema"] == "egohygiene.architecture-coherence-review/v1")
        revisions = {item["repository"]: item["revision"] for item in subject["represented_revisions"]}
        require(revisions.get(repository) == row["represented_commit"])
        require(contract.instant(value["generated_at"]) <= contract.instant(args.observed_at))
        require(subject["completed_at"] is None or contract.instant(subject["completed_at"]) <= contract.instant(args.observed_at))
        completion = value.get("execution", {}).get("status", "unknown")
        count = None
    canonical_url = f"https://github.com/{repository}/blob/{selection['source_revision']}/{selection['source_path']}"
    return {**selection, "owner_schema": value["schema"], "canonical_url": canonical_url,
            "completion": completion, "findings_count": count}, findings


def repository_index(args, row, allowed, loaded, registry, inspect):
    input_sha = contract.digest({"selection": row, "profiles": args.profiles, "owner_inputs": args.owner_inputs,
                                 "report_kinds": args.report_kinds, "budgets": args.budgets})
    result = {"repository": row["repository"], "represented_commit": row["represented_commit"],
        "source_observed_at": row["source_observed_at"], "state": "planned", "reason": None,
        "input_sha256": input_sha, "reports": [], "resume": "new"}
    if not inspect:
        result.update(state="not-inspected", reason="cancelled", resume="not-inspected")
        return result, []
    if row["represented_commit"] is None:
        result.update(state="unavailable", reason="source-not-selected")
        return result, []
    if args.mode == "plan":
        return result, []
    if not row["reports"]:
        result.update(state="unavailable", reason="reports-not-selected")
        return result, []
    try:
        root = args.roots.get(row["repository"])
        require(root is not None and git(root, "rev-parse", "--verify", row["represented_commit"] + "^{commit}").decode().strip()
                == row["represented_commit"])
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError):
        result.update(state="unavailable", reason="source-unavailable")
        return result, []
    findings = []
    for selection in row["reports"]:
        if time.monotonic() >= args.deadline:
            result["reason"] = "budget-exhausted"
            break
        if selection["kind"] not in args.report_kinds:
            continue
        try:
            accepted, records = report(args, selection, row, allowed, loaded, registry)
            result["reports"].append(accepted)
            remaining = args.budgets["maximum_findings"] - len(findings)
            findings.extend(records[:remaining])
            if len(records) > remaining:
                result["reason"] = "report-limit"
        except (OSError, ValueError, KeyError, TypeError, RecursionError, subprocess.SubprocessError):
            result["reason"] = "report-incompatible"
    kinds = {item["kind"] for item in result["reports"]}
    complete = kinds >= set(args.report_kinds) and all(item["completion"] in {
        "complete", "completed", "not_applicable"} for item in result["reports"])
    result["state"] = "indexed" if complete and result["reason"] is None else "partial" if result["reports"] else "unavailable"
    if not complete and result["reason"] is None:
        result["reason"] = "reports-not-selected"
    return result, findings


def write_output(path, manifest, findings):
    path = safe(path)
    require(not path.exists())
    path.parent.mkdir(parents=True, exist_ok=True)
    contract.validate_manifest(manifest)
    backlog = {"schema": "egohygiene.reflector.candidate-backlog/v1", "state": "disabled", "mutation_authority": "none", "items": []}
    summary = (f"# Campaign {manifest['campaign_id']}\n\n"
        f"Mode: {manifest['mode']}. State: {manifest['status']}. Observation boundary: {manifest['observed_at']}.\n\n"
        "This index references external owner captures; Reflector did not execute an AI audit or human ratification. "
        "Candidate issue synthesis and provider mutations are disabled. Repository report prose remains canonical at its source.\n")
    documents = {"manifest.json": contract.canonical_bytes(manifest),
        "repositories.json": contract.canonical_bytes({"repositories": manifest["repositories"]}),
        "findings.json": contract.canonical_bytes({"schema": "egohygiene.reflector.campaign-finding-index/v1",
            "truncated": any(row["reason"] == "report-limit" for row in manifest["repositories"]), "findings": findings}),
        "candidate-backlog.json": contract.canonical_bytes(backlog), "summary.md": summary.encode()}
    require(all(len(content) <= MAX_MANIFEST for content in documents.values()))
    with tempfile.TemporaryDirectory(prefix="reflector-campaign-write-", dir=path.parent) as temporary:
        staging = Path(temporary) / "result"
        staging.mkdir()
        for name, content in documents.items():
            (staging / name).write_bytes(content)
        os.rename(staging, path)


def execute(args):
    require(args.mode in {"plan", "index"})
    public, metadata = public_catalog(args.catalog_root)
    args.public_names = set(public)
    request = admitted_request(parse(read(args.request)), public, metadata)
    args.budgets = request["budgets"]
    args.observed_at = request["observed_at"]
    args.report_kinds = request["report_kinds"]
    args.roots = source_roots(args.repository_root, {row["repository"] for row in request["repositories"]})
    output = safe(args.output)
    require(not output.exists())
    protected = [safe(args.catalog_root), safe(args.aether_root), *(path.absolute() for path in args.roots.values())]
    require(not any(output.is_relative_to(root) for root in protected))
    require(args.stop_after is None or 0 <= args.stop_after <= len(request["repositories"]))
    previous = {}
    if args.previous_manifest is not None:
        content = read(args.previous_manifest, MAX_MANIFEST)
        require(args.previous_sha256 is not None and sha256(content) == args.previous_sha256)
        value = parse(content)
        require(value.get("visibility") == "public")
        admitted = {row["repository"] for row in request["repositories"]}
        value["repositories"] = [row for row in value.get("repositories", [])
            if isinstance(row, dict) and row.get("repository") in admitted]
        contract.validate_manifest(value)
        previous = {row["repository"]: row for row in value["repositories"]}
    else:
        require(args.previous_sha256 is None)
    with ExitStack() as stack:
        loaded, args.owner_inputs = owners(stack, args.aether_root)
        audit = loaded["aether_audit"]
        args.profiles = audit["helper"].resolve_profiles(request["profiles"], audit["registry"])
        allowed = {row["repository"] for row in request["repositories"]}
        rows, findings = [], []
        args.deadline = time.monotonic() + args.budgets["maximum_seconds"]
        width = args.budgets["concurrency"]
        with ThreadPoolExecutor(max_workers=args.budgets["concurrency"]) as executor:
            for offset in range(0, len(request["repositories"]), width):
                # Bound both active work and buffered finding metadata; do not
                # retain a completed result for every repository in a queue.
                batch = request["repositories"][offset:offset + width]
                jobs = [executor.submit(repository_index, args, row, allowed, loaded, audit["registry"],
                    args.stop_after is None or offset + number < args.stop_after)
                    for number, row in enumerate(batch)]
                for job in jobs:
                    row, records = job.result()
                    remaining = args.budgets["maximum_findings"] - len(findings)
                    if len(records) > remaining:
                        records = records[:remaining]
                        row.update(state="partial", reason="report-limit")
                    prior = previous.get(row["repository"])
                    if prior is not None and {key: value for key, value in prior.items() if key != "resume"} == {
                            key: value for key, value in row.items() if key != "resume"}:
                        row["resume"] = "unchanged"
                    rows.append(row)
                    findings.extend(records)
        cancelled = any(row["state"] == "not-inspected" for row in rows)
        status = "cancelled" if cancelled else "planned" if args.mode == "plan" else "indexed" if rows and all(
            row["state"] == "indexed" for row in rows) else "partial"
        report_kinds = {report["kind"] for row in rows for report in row["reports"]}
        states = ("selected", "resolved", "declared", "external-captures" if "audit" in report_kinds else "not-executed",
                  "external-captures" if "sanity" in report_kinds else "not-executed",
                  "indexed" if status == "indexed" else "partial", "disabled", "not-requested")
        manifest = {"schema": contract.MANIFEST, "contract_version": contract.VERSION,
            "campaign_id": request["campaign_id"], "visibility": "public", "organization": "egohygiene",
            "observed_at": request["observed_at"], "mode": args.mode, "status": status,
            "mutation_authority": "none", "analysis_execution": "external-captures-only", "catalog": metadata,
            "owner_inputs": args.owner_inputs, "profiles": args.profiles, "budgets": args.budgets,
            "generator": generator(),
            "passes": [{"id": name, "state": state} for name, state in zip(contract.PASS_IDS, states)],
            "repositories": rows, "request_sha256": contract.digest(request), "candidate_backlog": "disabled"}
        write_output(output, manifest, findings)
    return manifest


def parser():
    result = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    result.add_argument("mode", choices=("plan", "index"))
    for name in ("request", "catalog-root", "aether-root", "output"):
        result.add_argument("--" + name, type=Path, required=True)
    result.add_argument("--repository-root", action="append", default=[])
    result.add_argument("--previous-manifest", type=Path)
    result.add_argument("--previous-sha256")
    result.add_argument("--stop-after", type=int)
    return result


def main():
    try:
        manifest = execute(parser().parse_args())
    except Exception:
        print("Campaign source, profile or report admission denied; no completed run is claimed", file=sys.stderr)
        return 3
    print("Campaign transport retained: " + manifest["status"] + "; analysis execution and mutations disabled")
    return 0 if manifest["status"] in {"planned", "indexed"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
