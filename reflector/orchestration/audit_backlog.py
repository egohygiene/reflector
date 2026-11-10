# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Deterministic proposals from admitted, owner-validated audit findings.

This module neither classifies findings nor opens issues. Callers authenticate
the public roster and validate Aether reports before projecting these records.
Grouping is explicit; no title similarity or severity implies equivalence.
"""

from __future__ import annotations

import hashlib
import ipaddress
import json
import re
from urllib.parse import urlsplit

SCHEMA = "egohygiene.reflector.audit-candidate-backlog/v1"
VERSION = "1.0.0-alpha.1"
MAX_FINDINGS = 4096
MAX_BYTES = 8388608
FIELDS = {"visibility", "repository", "report_sha256", "finding_id", "source_revision", "source_path",
          "title", "classification", "nature", "severity", "confidence", "status", "source_profile",
          "evidence_classification", "missing_evidence", "recommendation", "suggested_validation"}
REPOSITORY = re.compile(r"egohygiene/(?:\.github|[a-z0-9][a-z0-9.-]*)")
TOKEN = re.compile(r"[a-z0-9][a-z0-9._-]{0,95}")
SENSITIVE = re.compile(r"(?i)(?:github_pat_|gh[pousr]_|\b(?:password|token|secret)\s*[:=]\s*[^\s]+|[\w.+-]+@[\w.-]+\.[a-z]{2,}|/(?:home|Users|workspace|tmp)/|[A-Za-z]:\\)")


def require(condition):
    if not condition:
        raise ValueError("Candidate backlog input is incompatible")


def canonical(value):
    content = (json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False,
                          indent=2) + "\n").encode()
    require(len(content) <= MAX_BYTES)
    return content


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def text(value, maximum=4096):
    require(isinstance(value, str) and 1 <= len(value) <= maximum
            and not any(ord(character) < 32 and character not in "\n\t" for character in value))


def strings(value):
    require(isinstance(value, list) and len(value) <= 64)
    for item in value:
        text(item, 2048)
    require(len(value) == len(set(value)))


def finding_key(finding):
    return ":".join((finding["repository"], finding["report_sha256"], finding["finding_id"]))


def public_rationale(value, allowed):
    """Admit newly authored grouping text before it enters public output."""
    text(value, 2048)
    require(not SENSITIVE.search(value))
    for match in re.finditer(r"egohygiene/(?:\.github|[a-z0-9][a-z0-9.-]*)", value, re.I):
        require(match[0] in allowed)
    for match in re.finditer(r"[A-Za-z][A-Za-z0-9+.-]*://[^\s<>\"']+", value):
        uri = match[0].rstrip(".,;)")
        parsed = urlsplit(uri)
        host = parsed.hostname or ""
        require(parsed.scheme == "https" and host and parsed.netloc == host and not host.endswith(".")
                and not parsed.query and "%" not in uri and "\\" not in uri
                and (not parsed.fragment or re.fullmatch(r"[A-Za-z0-9._-]+", parsed.fragment))
                and not host.endswith((".local", ".internal", ".localhost")) and host != "localhost"
                and not any(part in {".", ".."} for part in parsed.path.split("/")))
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            address = None
            require(not re.fullmatch(r"[0-9]+|0x[0-9a-f]+", host.rsplit(".", 1)[-1], re.I))
        require(address is None or address.is_global)
        if host in {"github.com", "api.github.com", "raw.githubusercontent.com", "codeload.github.com"}:
            parts = parsed.path.strip("/").split("/")
            if host == "api.github.com":
                require(bool(parts) and parts.pop(0) == "repos")
            require(len(parts) >= 2 and "/".join(parts[:2]) in allowed)


def source_record(value):
    """Validate transport shape without reproducing owner taxonomy or policy."""
    require(isinstance(value, dict) and set(value) == FIELDS)
    require(value["visibility"] == "public" and isinstance(value["repository"], str)
            and REPOSITORY.fullmatch(value["repository"]))
    for name, size in (("report_sha256", 64), ("source_revision", 40)):
        require(isinstance(value[name], str) and re.fullmatch("[a-f0-9]{" + str(size) + "}", value[name]))
    require(isinstance(value["finding_id"], str) and re.fullmatch(r"[A-Z][A-Z0-9_-]{0,95}", value["finding_id"]))
    path = value["source_path"]
    require(isinstance(path, str) and len(path) <= 240 and re.fullmatch(r"[A-Za-z0-9._/-]+", path)
            and all(part not in {"", ".", "..", ".git"} for part in path.split("/")))
    text(value["title"], 512)
    text(value["recommendation"], 8192)
    for name in ("classification", "nature", "severity", "confidence", "status", "evidence_classification"):
        require(isinstance(value[name], str) and TOKEN.fullmatch(value[name]))
    profile = value["source_profile"]
    require(isinstance(profile, dict) and set(profile) == {"id", "version"})
    require(isinstance(profile["id"], str) and TOKEN.fullmatch(profile["id"]))
    require(isinstance(profile["version"], str) and re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[a-z0-9.-]+)?", profile["version"]))
    strings(value["missing_evidence"])
    strings(value["suggested_validation"])
    return value


def propose_backlog(findings, *, public_repositories, groups=()):
    """Preserve source facts in proposals; caller supplies every equivalence.

    Excluded records are discarded before identities, payload validation,
    counts or digests. The supplied roster must come from the caller's exact
    authenticated Hygiene catalog, never from report claims.
    """
    require(isinstance(public_repositories, (set, frozenset)))
    admitted = {}
    for item in findings:
        if (not isinstance(item, dict) or item.get("visibility") != "public"
                or not isinstance(item.get("repository"), str)
                or item["repository"] not in public_repositories):
            continue
        source_record(item)
        key = finding_key(item)
        require(key not in admitted and len(admitted) < MAX_FINDINGS)
        # Normalize to JSON data so later caller mutation cannot alter evidence.
        admitted[key] = json.loads(canonical(item))
    require(isinstance(groups, (list, tuple)) and len(groups) <= MAX_FINDINGS)
    selected, covered = [], set()
    for group in groups:
        require(isinstance(group, dict) and set(group) == {"finding_keys", "rationale"})
        keys = group["finding_keys"]
        require(isinstance(keys, list) and 2 <= len(keys) <= 64
                and all(isinstance(key, str) for key in keys))
        require(len(set(keys)) == len(keys) and set(keys) <= set(admitted)
                and not set(keys) & covered)
        public_rationale(group["rationale"], public_repositories)
        records = [admitted[key] for key in keys]
        # Explicit grouping cannot erase distinctions between defects, future
        # ideas and positive observations. Every member's full facts survive.
        require(len({(record["classification"], record["nature"]) for record in records}) == 1)
        covered.update(keys)
        selected.append((sorted(keys), "explicit", group["rationale"]))
    selected.extend(([key], "single-finding", None) for key in sorted(set(admitted) - covered))
    proposals = []
    for keys, grouping, rationale in selected:
        proposals.append({"id": "proposal-" + digest(keys)[:24], "status": "proposed",
            "grouping": grouping, "grouping_rationale": rationale, "source_finding_keys": keys,
            "sources": [admitted[key] for key in keys], "review": "required",
            "issue_creation": "not-authorized"})
    proposals.sort(key=lambda item: item["id"])
    result = {"schema": SCHEMA, "contract_version": VERSION, "visibility": "public",
        "mutation_authority": "none", "synthesis": "deterministic-source-projection",
        "findings_count": len(admitted), "proposals": proposals}
    result["digest"] = digest(result)
    return result
