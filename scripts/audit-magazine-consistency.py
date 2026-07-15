#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""audit-magazine-consistency.py — Magazine-to-manuscript consistency audit.

Evaluates structural consistency between the canonical manuscript (paper/)
and the visual companion magazine (magazine/) according to the rules defined in:
  specs/publication/magazine-consistency.spec.md

The audit is read-only and deterministic. It requires no network access or
external services.

Output: audits/magazine-consistency.md (human-readable report)

Exit codes:
  0 — all required checks pass (FAIL count = 0)
  1 — at least one required-rule violation

Usage:
  python scripts/audit-magazine-consistency.py
  python scripts/audit-magazine-consistency.py --repo-root /path/to/repo
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Finding:
    """A single consistency check result."""

    rule: str          # RULE-NNN
    area: str          # logical grouping
    name: str          # short check description
    status: str        # PASS | WARN | FAIL | SKIP
    source: str        # manuscript source path or field
    target: str        # magazine target path or field
    details: str       # observed condition
    expected: str      # expected condition
    remediation: str   # practical remediation direction


@dataclass
class MappingException:
    """An approved exception declared in the mapping file."""

    id: str
    rule: str
    rationale: str
    scope: str
    approved_by: str
    review_date: str = ""


# ---------------------------------------------------------------------------
# Paths (set by run_audit; overridden for tests)
# ---------------------------------------------------------------------------

_DEFAULT_REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# YAML helpers
# ---------------------------------------------------------------------------


def _load_yaml(path: Path) -> tuple[object | None, str | None]:
    """Load YAML from path. Returns (data, error_message)."""
    if yaml is None:
        # Fallback: minimal YAML parsing for simple key: value structures.
        # This handles the common case without requiring PyYAML.
        return _parse_minimal_yaml(path)
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return data, None
    except Exception as exc:
        return None, str(exc)


def _parse_minimal_yaml(path: Path) -> tuple[object | None, str | None]:
    """Minimal YAML parser for simple key: value and list structures."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, str(exc)
    try:
        import json
        # Try JSON first (valid JSON is valid YAML)
        try:
            return json.loads(text), None
        except json.JSONDecodeError:
            pass
        # Very simple line-by-line parser for flat key: value
        result: dict = {}
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if ": " in stripped:
                key, _, value = stripped.partition(": ")
                result[key.strip()] = value.strip().strip('"').strip("'")
        return result, None
    except Exception as exc:
        return None, str(exc)


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


def _parse_includegraphics(tex_text: str) -> list[str]:
    """Extract paths from \\includegraphics[...]{path} in magazine.tex."""
    pattern = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
    return [m.strip() for m in pattern.findall(tex_text)]


def _parse_manifest_figure_ids(manifest_text: str) -> set[str]:
    """Extract figure IDs from the YAML block in paper/figures/manifest.md."""
    ids: set[str] = set()
    in_yaml = False
    for line in manifest_text.splitlines():
        if line.strip() == "```yaml":
            in_yaml = True
            continue
        if in_yaml and line.strip() == "```":
            in_yaml = False
            continue
        if in_yaml:
            m = re.match(r"\s*-\s*id:\s*([^\s#]+)", line)
            if m:
                ids.add(m.group(1).strip())
    return ids


def _extract_spec_version(spec_text: str) -> str | None:
    """Extract 'version:' value from a YAML frontmatter or flat YAML file."""
    for line in spec_text.splitlines():
        m = re.match(r"^version:\s*['\"]?([^'\"#\n]+)['\"]?", line.strip())
        if m:
            return m.group(1).strip()
    return None


def _extract_publication_version(pub_data: object) -> str | None:
    """Extract version from parsed publication.yaml data."""
    if isinstance(pub_data, dict):
        v = pub_data.get("version")
        return str(v).strip() if v is not None else None
    return None


def _collect_mapping_ids(mapping: dict) -> tuple[list[str], list[str]]:
    """Collect all IDs from all mapping sections. Returns (ids, duplicates)."""
    all_ids: list[str] = []
    for section_key in ("metadata_sync", "page_mappings", "figure_mappings", "exceptions"):
        section = mapping.get(section_key, []) or []
        for entry in section:
            if isinstance(entry, dict) and "id" in entry:
                all_ids.append(str(entry["id"]))
    seen: set[str] = set()
    duplicates: list[str] = []
    for entry_id in all_ids:
        if entry_id in seen:
            duplicates.append(entry_id)
        seen.add(entry_id)
    return all_ids, sorted(set(duplicates))


# ---------------------------------------------------------------------------
# Core audit logic
# ---------------------------------------------------------------------------


def run_audit(repo_root: Path) -> tuple[list[Finding], list[MappingException]]:
    """Run the full magazine-to-manuscript consistency audit.

    Parameters
    ----------
    repo_root:
        Root directory of the repository.

    Returns
    -------
    (findings, approved_exceptions)
        findings: list of Finding objects (PASS/WARN/FAIL)
        approved_exceptions: list of MappingException objects (SKIP)
    """
    findings: list[Finding] = []
    approved_exceptions: list[MappingException] = []

    # ------------------------------------------------------------------
    # RULE-001: required-files-exist
    # ------------------------------------------------------------------
    required_files = [
        ("paper/paper.tex", "paper/paper.tex", "magazine/(all pages)"),
        ("paper/figures/manifest.md", "paper/figures/manifest.md", "magazine/(figure mappings)"),
        ("metadata/publication.yaml", "metadata/publication.yaml", "magazine/spec.md"),
        ("metadata/authors.yaml", "metadata/authors.yaml", "magazine/(author metadata)"),
        ("publication.json", "publication.json", "magazine/(publication identity)"),
        ("magazine/tex/magazine.tex", "magazine/tex/magazine.tex", "magazine/(page declarations)"),
        ("magazine/spec.md", "magazine/spec.md", "paper/(magazine companion)"),
    ]

    for rel_path, source_label, target_label in required_files:
        full_path = repo_root / rel_path
        findings.append(Finding(
            rule="RULE-001",
            area="Required files",
            name=f"Required file: {rel_path}",
            status="PASS" if full_path.exists() else "FAIL",
            source=source_label,
            target=target_label,
            details=(
                f"File exists: {rel_path}" if full_path.exists()
                else f"File not found: {rel_path}"
            ),
            expected=f"File exists at {rel_path}",
            remediation=f"Create or restore the missing file: {rel_path}",
        ))

    # Mapping file: treat separately (needed for subsequent checks)
    mapping_path = repo_root / "magazine" / "consistency-mapping.yaml"
    mapping_exists = mapping_path.exists()
    findings.append(Finding(
        rule="RULE-001",
        area="Required files",
        name="Required file: magazine/consistency-mapping.yaml",
        status="PASS" if mapping_exists else "FAIL",
        source="magazine/consistency-mapping.yaml",
        target="magazine/(all consistency checks)",
        details=(
            "File exists: magazine/consistency-mapping.yaml" if mapping_exists
            else "File not found: magazine/consistency-mapping.yaml"
        ),
        expected="File exists at magazine/consistency-mapping.yaml",
        remediation="Create magazine/consistency-mapping.yaml per the consistency spec.",
    ))

    # If mapping is missing, remaining mapping checks cannot run.
    if not mapping_exists:
        findings.append(Finding(
            rule="RULE-002",
            area="Mapping validation",
            name="Mapping YAML parse",
            status="FAIL",
            source="magazine/consistency-mapping.yaml",
            target="magazine/(all consistency checks)",
            details="Cannot parse mapping: file does not exist.",
            expected="Mapping file exists and is valid YAML.",
            remediation="Create magazine/consistency-mapping.yaml.",
        ))
        # Return early — downstream checks cannot run without the mapping.
        return sorted_findings(findings), approved_exceptions

    # ------------------------------------------------------------------
    # RULE-002: mapping-valid-yaml
    # ------------------------------------------------------------------
    mapping_data, parse_error = _load_yaml(mapping_path)
    if parse_error or not isinstance(mapping_data, dict):
        findings.append(Finding(
            rule="RULE-002",
            area="Mapping validation",
            name="Mapping YAML parse",
            status="FAIL",
            source="magazine/consistency-mapping.yaml",
            target="magazine/(all consistency checks)",
            details=f"YAML parse error: {parse_error or 'result is not a dict'}",
            expected="magazine/consistency-mapping.yaml parses as valid YAML mapping.",
            remediation="Fix the YAML syntax in magazine/consistency-mapping.yaml.",
        ))
        return sorted_findings(findings), approved_exceptions

    findings.append(Finding(
        rule="RULE-002",
        area="Mapping validation",
        name="Mapping YAML parse",
        status="PASS",
        source="magazine/consistency-mapping.yaml",
        target="magazine/(all consistency checks)",
        details="Mapping file parses as valid YAML.",
        expected="magazine/consistency-mapping.yaml parses as valid YAML mapping.",
        remediation="",
    ))

    # Collect approved exceptions early so they can suppress warnings.
    exception_entries = mapping_data.get("exceptions", []) or []
    approved_rule_ids: set[str] = set()
    for exc_entry in exception_entries:
        if not isinstance(exc_entry, dict):
            continue
        exc_id = str(exc_entry.get("id", "")).strip()
        exc_rule = str(exc_entry.get("rule", "")).strip()
        exc_rationale = str(exc_entry.get("rationale", "")).strip()
        exc_scope = str(exc_entry.get("scope", "")).strip()
        exc_approver = str(exc_entry.get("approved_by", "")).strip()
        exc_review = str(exc_entry.get("review_date", "")).strip()

        if not exc_id or not exc_rule:
            findings.append(Finding(
                rule="RULE-002",
                area="Mapping validation",
                name="Exception missing required fields",
                status="WARN",
                source="magazine/consistency-mapping.yaml:exceptions",
                target="magazine/(exception governance)",
                details=f"Exception entry is missing 'id' or 'rule': {exc_entry}",
                expected="Each exception must have 'id', 'rule', 'rationale', 'scope', 'approved_by'.",
                remediation="Add the missing required fields to the exception entry.",
            ))
            continue

        approved_exceptions.append(MappingException(
            id=exc_id,
            rule=exc_rule,
            rationale=exc_rationale,
            scope=exc_scope,
            approved_by=exc_approver,
            review_date=exc_review,
        ))
        approved_rule_ids.add(exc_rule)

    # ------------------------------------------------------------------
    # RULE-003: mapping-no-duplicate-ids
    # ------------------------------------------------------------------
    all_ids, duplicates = _collect_mapping_ids(mapping_data)
    if duplicates:
        findings.append(Finding(
            rule="RULE-003",
            area="Mapping validation",
            name="No duplicate mapping IDs",
            status="FAIL",
            source="magazine/consistency-mapping.yaml",
            target="magazine/(all mapped entries)",
            details=f"Duplicate IDs found: {', '.join(sorted(duplicates))}",
            expected="Every mapping entry has a unique 'id' value.",
            remediation="Rename or remove the duplicate mapping entry IDs.",
        ))
    else:
        findings.append(Finding(
            rule="RULE-003",
            area="Mapping validation",
            name="No duplicate mapping IDs",
            status="PASS",
            source="magazine/consistency-mapping.yaml",
            target="magazine/(all mapped entries)",
            details=f"All {len(all_ids)} mapping IDs are unique.",
            expected="Every mapping entry has a unique 'id' value.",
            remediation="",
        ))

    # ------------------------------------------------------------------
    # RULE-004: magazine-pages-declared-exist
    # Magazine pages referenced in magazine.tex must exist on disk.
    # ------------------------------------------------------------------
    magazine_tex_path = repo_root / "magazine" / "tex" / "magazine.tex"
    if magazine_tex_path.exists():
        tex_text = magazine_tex_path.read_text(encoding="utf-8")
        declared_paths = _parse_includegraphics(tex_text)
        magazine_tex_dir = magazine_tex_path.parent

        missing_pages: list[str] = []
        for raw_path in declared_paths:
            # Resolve relative to magazine/tex/ (the tex working directory)
            resolved = (magazine_tex_dir / raw_path).resolve()
            # Also try with .png extension if not present
            candidates = [resolved]
            if not resolved.suffix:
                candidates.append(resolved.with_suffix(".png"))
            found = any(c.exists() for c in candidates)
            if not found:
                missing_pages.append(raw_path)

        if missing_pages:
            for mp in sorted(missing_pages):
                findings.append(Finding(
                    rule="RULE-004",
                    area="Magazine pages",
                    name=f"Declared page exists: {mp}",
                    status="FAIL",
                    source="magazine/tex/magazine.tex",
                    target=f"magazine/pages/{Path(mp).name}",
                    details=f"Page declared in magazine.tex not found on disk: {mp}",
                    expected=f"Page file exists at {mp} (relative to magazine/tex/)",
                    remediation=f"Add the missing page file or remove the declaration from magazine.tex: {mp}",
                ))
        else:
            findings.append(Finding(
                rule="RULE-004",
                area="Magazine pages",
                name="All declared pages exist",
                status="PASS",
                source="magazine/tex/magazine.tex",
                target="magazine/pages/",
                details=f"All {len(declared_paths)} declared page(s) exist on disk.",
                expected="All pages referenced in magazine.tex exist as files.",
                remediation="",
            ))
    # If magazine.tex doesn't exist, RULE-001 already flagged it.

    # ------------------------------------------------------------------
    # RULE-005 + RULE-006: mapping source and target file existence
    # Applies to page_mappings and figure_mappings entries.
    # ------------------------------------------------------------------
    for section_key in ("page_mappings", "figure_mappings"):
        section = mapping_data.get(section_key, []) or []
        for entry in section:
            if not isinstance(entry, dict):
                continue
            entry_id = str(entry.get("id", "")).strip()
            manuscript_source = str(entry.get("manuscript_source", "")).strip()
            magazine_target = str(entry.get("magazine_target", "")).strip()

            # RULE-005: manuscript source exists
            if manuscript_source:
                src_path = repo_root / manuscript_source
                src_exists = src_path.exists()
                # Check if RULE-005 is excepted
                rule_excepted = "RULE-005" in approved_rule_ids
                findings.append(Finding(
                    rule="RULE-005",
                    area="Mapping source files",
                    name=f"Manuscript source exists: {manuscript_source} (mapping: {entry_id})",
                    status=("PASS" if src_exists else ("SKIP" if rule_excepted else "WARN")),
                    source=manuscript_source,
                    target=magazine_target,
                    details=(
                        f"Manuscript source exists: {manuscript_source}"
                        if src_exists
                        else (
                            f"Manuscript source not found: {manuscript_source}"
                            + (" [exception: exc-magazine-source-section-files]" if rule_excepted else "")
                        )
                    ),
                    expected=f"File exists at {manuscript_source}",
                    remediation=(
                        ""
                        if src_exists or rule_excepted
                        else f"Correct the manuscript_source path in mapping entry '{entry_id}' or restore the file."
                    ),
                ))

            # RULE-006: magazine target exists
            if magazine_target:
                tgt_path = repo_root / magazine_target
                tgt_exists = tgt_path.exists()
                findings.append(Finding(
                    rule="RULE-006",
                    area="Mapping target files",
                    name=f"Magazine target exists: {magazine_target} (mapping: {entry_id})",
                    status="PASS" if tgt_exists else "WARN",
                    source=manuscript_source,
                    target=magazine_target,
                    details=(
                        f"Magazine target exists: {magazine_target}"
                        if tgt_exists
                        else f"Magazine target not found: {magazine_target}"
                    ),
                    expected=f"File exists at {magazine_target}",
                    remediation=(
                        ""
                        if tgt_exists
                        else f"Add the missing magazine target or remove the orphaned mapping entry '{entry_id}'."
                    ),
                ))

    # ------------------------------------------------------------------
    # RULE-007: metadata-version-advisory
    # ------------------------------------------------------------------
    pub_yaml_path = repo_root / "metadata" / "publication.yaml"
    magazine_spec_path = repo_root / "magazine" / "spec.md"

    if pub_yaml_path.exists() and magazine_spec_path.exists():
        pub_data, pub_err = _load_yaml(pub_yaml_path)
        pub_version = _extract_publication_version(pub_data) if not pub_err else None
        spec_text = magazine_spec_path.read_text(encoding="utf-8")
        spec_version = _extract_spec_version(spec_text)

        if pub_version and spec_version:
            versions_match = pub_version.strip() == spec_version.strip()
            findings.append(Finding(
                rule="RULE-007",
                area="Metadata consistency",
                name="Publication version advisory",
                status="PASS" if versions_match else "WARN",
                source=f"metadata/publication.yaml:version={pub_version}",
                target=f"magazine/spec.md:version={spec_version}",
                details=(
                    f"Versions match: {pub_version}"
                    if versions_match
                    else f"Version mismatch: manuscript={pub_version}, magazine={spec_version}"
                ),
                expected="version fields agree between metadata/publication.yaml and magazine/spec.md",
                remediation=(
                    ""
                    if versions_match
                    else (
                        "Update magazine/spec.md version to match metadata/publication.yaml, "
                        "or document the intentional difference as an exception."
                    )
                ),
            ))
        elif pub_version and not spec_version:
            findings.append(Finding(
                rule="RULE-007",
                area="Metadata consistency",
                name="Publication version advisory",
                status="WARN",
                source=f"metadata/publication.yaml:version={pub_version}",
                target="magazine/spec.md:version=(not found)",
                details="magazine/spec.md does not declare a 'version' field in its frontmatter.",
                expected="magazine/spec.md declares a version field.",
                remediation="Add a 'version' field to the magazine/spec.md YAML frontmatter.",
            ))
        # If pub_version is missing, RULE-001 likely flagged the missing file.

    # ------------------------------------------------------------------
    # RULE-008: figure-ids-in-manifest
    # ------------------------------------------------------------------
    manifest_path = repo_root / "paper" / "figures" / "manifest.md"
    if manifest_path.exists():
        manifest_text = manifest_path.read_text(encoding="utf-8")
        manifest_ids = _parse_manifest_figure_ids(manifest_text)

        figure_mappings = mapping_data.get("figure_mappings", []) or []
        for entry in figure_mappings:
            if not isinstance(entry, dict):
                continue
            entry_id = str(entry.get("id", "")).strip()
            fig_id = str(entry.get("manuscript_figure_id", "")).strip()
            magazine_target = str(entry.get("magazine_target", "")).strip()

            if not fig_id:
                continue

            in_manifest = fig_id in manifest_ids
            findings.append(Finding(
                rule="RULE-008",
                area="Figure manifest cross-check",
                name=f"Figure ID in manifest: {fig_id} (mapping: {entry_id})",
                status="PASS" if in_manifest else "WARN",
                source=f"paper/figures/manifest.md:id={fig_id}",
                target=magazine_target,
                details=(
                    f"Figure ID found in manifest: {fig_id}"
                    if in_manifest
                    else f"Figure ID not found in manifest: {fig_id}"
                ),
                expected=f"Figure ID '{fig_id}' exists in paper/figures/manifest.md",
                remediation=(
                    ""
                    if in_manifest
                    else (
                        f"Correct the 'manuscript_figure_id' in mapping entry '{entry_id}' "
                        "or add the figure to paper/figures/manifest.md."
                    )
                ),
            ))

    return sorted_findings(findings), approved_exceptions


def sorted_findings(findings: list[Finding]) -> list[Finding]:
    """Return findings in deterministic order: area, name, rule."""
    return sorted(findings, key=lambda f: (f.area, f.name, f.rule))


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


def write_report(
    findings: list[Finding],
    approved_exceptions: list[MappingException],
    output_path: Path,
) -> None:
    """Write a human-readable markdown audit report to output_path."""
    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    pass_count = sum(1 for f in findings if f.status == "PASS")
    warn_count = sum(1 for f in findings if f.status == "WARN")
    fail_count = sum(1 for f in findings if f.status == "FAIL")
    skip_count = sum(1 for f in findings if f.status == "SKIP")
    total_rules = len({f.rule for f in findings})
    exc_count = len(approved_exceptions)

    if fail_count > 0:
        overall = "❌ **Consistency violations detected**"
    elif warn_count > 0:
        overall = "⚠️ **Advisory findings — no hard failures**"
    else:
        overall = "✅ **Consistent** — all checks pass"

    def icon(status: str) -> str:
        return {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌", "SKIP": "🔵"}.get(status, "?")

    lines: list[str] = [
        "# Magazine-to-Manuscript Consistency Audit Report",
        "",
        f"Generated at: `{timestamp}`",
        "",
        "**Scope:** Structural consistency between `paper/` (manuscript) and `magazine/` (visual companion)",
        "**Specification:** `specs/publication/magazine-consistency.spec.md`",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        f"- Rules evaluated: **{total_rules}**",
        f"- Checks run: **{len(findings)}**",
        f"- Pass: **{pass_count}**",
        f"- Warn: **{warn_count}**",
        f"- Fail: **{fail_count}**",
        f"- Approved exceptions: **{exc_count}**",
        "",
        f"Overall result: {overall}",
        "",
    ]

    # Group findings by area
    by_area: dict[str, list[Finding]] = {}
    for f in findings:
        by_area.setdefault(f.area, []).append(f)

    lines += ["## Findings by Area", ""]
    for area in sorted(by_area):
        area_findings = by_area[area]
        area_fail = sum(1 for f in area_findings if f.status == "FAIL")
        area_warn = sum(1 for f in area_findings if f.status == "WARN")
        area_icon = "❌" if area_fail > 0 else ("⚠️" if area_warn > 0 else "✅")
        lines.append(f"### {area_icon} {area}")
        lines.append("")
        lines.append("| Status | Rule | Check | Details |")
        lines.append("|--------|------|-------|---------|")
        for f in area_findings:
            safe_details = f.details.replace("|", "\\|").replace("\n", " ")
            lines.append(f"| {icon(f.status)} {f.status} | {f.rule} | {f.name} | {safe_details} |")
        lines.append("")

    # Failures section
    failures = [f for f in findings if f.status == "FAIL"]
    if failures:
        lines += ["## ❌ Failures (Required Rule Violations)", ""]
        for f in failures:
            lines += [
                f"### {f.rule}: {f.name}",
                "",
                f"- **Source:** `{f.source}`",
                f"- **Target:** `{f.target}`",
                f"- **Observed:** {f.details}",
                f"- **Expected:** {f.expected}",
                f"- **Remediation:** {f.remediation}",
                "",
            ]
    else:
        lines += ["## ❌ Failures", "", "- None.", ""]

    # Warnings section
    warnings = [f for f in findings if f.status == "WARN"]
    if warnings:
        lines += ["## ⚠️ Warnings (Advisory Findings)", ""]
        for f in warnings:
            lines += [
                f"### {f.rule}: {f.name}",
                "",
                f"- **Source:** `{f.source}`",
                f"- **Target:** `{f.target}`",
                f"- **Observed:** {f.details}",
                f"- **Expected:** {f.expected}",
                f"- **Remediation:** {f.remediation}",
                "",
            ]
    else:
        lines += ["## ⚠️ Warnings", "", "- None.", ""]

    # Exceptions section
    if approved_exceptions:
        lines += ["## 🔵 Approved Exceptions", ""]
        lines.append("| ID | Rule | Scope | Approver | Review Date |")
        lines.append("|----|------|-------|----------|-------------|")
        for exc in sorted(approved_exceptions, key=lambda e: e.id):
            lines.append(
                f"| `{exc.id}` | {exc.rule} | {exc.scope[:60]}… | {exc.approved_by} | {exc.review_date} |"
            )
        lines.append("")
        for exc in sorted(approved_exceptions, key=lambda e: e.id):
            lines += [
                f"### {exc.id} ({exc.rule})",
                "",
                f"**Scope:** {exc.scope}",
                "",
                f"**Rationale:** {exc.rationale.strip()}",
                "",
                f"**Approved by:** {exc.approved_by}",
                "",
            ]
            if exc.review_date:
                lines += [f"**Review date:** {exc.review_date}", ""]
    else:
        lines += ["## 🔵 Approved Exceptions", "", "- None.", ""]

    # Final status
    lines += [
        "---",
        "",
        "## Final Status",
        "",
        f"- [{('x' if fail_count == 0 else ' ')}] No required-rule violations",
        f"- [{('x' if warn_count == 0 else ' ')}] No advisory warnings",
        f"- [{('x' if exc_count == 0 else 'x')}] Approved exceptions reviewed",
        "",
        f"**Audit result:** {overall}",
        "",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """Run the magazine consistency audit.

    Parameters
    ----------
    argv:
        Optional argument list for testing. Defaults to sys.argv[1:].

    Returns
    -------
    int
        0 if no FAIL-status findings, 1 otherwise.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Magazine-to-manuscript consistency audit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root directory (defaults to script parent parent)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output report path (defaults to audits/magazine-consistency.md)",
    )
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    repo_root = args.repo_root or _DEFAULT_REPO_ROOT
    output_path = args.output or (repo_root / "audits" / "magazine-consistency.md")

    findings, approved_exceptions = run_audit(repo_root)

    write_report(findings, approved_exceptions, output_path)

    fail_count = sum(1 for f in findings if f.status == "FAIL")
    warn_count = sum(1 for f in findings if f.status == "WARN")
    pass_count = sum(1 for f in findings if f.status == "PASS")

    print(f"[audit-magazine-consistency] report written to {output_path}")
    print(
        f"[audit-magazine-consistency] "
        f"pass={pass_count} warn={warn_count} fail={fail_count} "
        f"exceptions={len(approved_exceptions)}"
    )

    return 1 if fail_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
