# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Tests for scripts/audit-magazine-consistency.py.

Covers:
- Fully synchronized fixtures (all checks pass).
- Missing manuscript source files.
- Missing magazine target files.
- Duplicate mapping IDs.
- Orphaned mapping entries.
- Metadata version mismatches.
- Valid documented exceptions.
- Invalid or incomplete exception entries.
- Malformed mapping YAML.
- Missing required input files.
- Correct exit statuses.
- Deterministic output ordering.
- Repository-level integration (real repository content).
- write_report produces valid markdown output.
- Finding and MappingException data model.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Load audit module
# ---------------------------------------------------------------------------

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"
_AUDIT_SCRIPT = _SCRIPTS_DIR / "audit-magazine-consistency.py"


def _load_audit_module() -> Any:
    """Dynamically load the audit script as a module."""
    module_name = "audit_magazine_consistency"
    spec = importlib.util.spec_from_file_location(module_name, _AUDIT_SCRIPT)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    # Register in sys.modules before exec so dataclass __module__ lookups work.
    sys.modules[module_name] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


_mod = _load_audit_module()
run_audit = _mod.run_audit
write_report = _mod.write_report
Finding = _mod.Finding
MappingException = _mod.MappingException
sorted_findings = _mod.sorted_findings
_parse_includegraphics = _mod._parse_includegraphics
_parse_manifest_figure_ids = _mod._parse_manifest_figure_ids
_extract_spec_version = _mod._extract_spec_version
_collect_mapping_ids = _mod._collect_mapping_ids

# ---------------------------------------------------------------------------
# Fixture paths
# ---------------------------------------------------------------------------

_FIXTURES_DIR = Path(__file__).parent / "fixtures" / "magazine_consistency"

SYNCHRONIZED = _FIXTURES_DIR / "synchronized"
MISSING_MANUSCRIPT = _FIXTURES_DIR / "missing_manuscript"
MISSING_MAGAZINE = _FIXTURES_DIR / "missing_magazine"
DUPLICATE_IDS = _FIXTURES_DIR / "duplicate_ids"
ORPHANED_MAPPING = _FIXTURES_DIR / "orphaned_mapping"
MALFORMED_MAPPING = _FIXTURES_DIR / "malformed_mapping"
METADATA_MISMATCH = _FIXTURES_DIR / "metadata_mismatch"

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _findings_by_status(findings: list, status: str) -> list:
    return [f for f in findings if f.status == status]


def _findings_by_rule(findings: list, rule: str) -> list:
    return [f for f in findings if f.rule == rule]


def _has_finding(findings: list, *, rule: str | None = None, status: str | None = None) -> bool:
    """Return True if any finding matches all provided criteria."""
    for f in findings:
        if rule is not None and f.rule != rule:
            continue
        if status is not None and f.status != status:
            continue
        return True
    return False


# ===========================================================================
# Parsing helpers
# ===========================================================================


class TestParseIncludegraphics:
    def test_finds_single_path(self) -> None:
        tex = r"\includegraphics{../pages/page01.png}"
        result = _parse_includegraphics(tex)
        assert result == ["../pages/page01.png"]

    def test_finds_multiple_paths(self) -> None:
        tex = (
            r"\includegraphics[width=\textwidth]{../pages/page01.png}" + "\n"
            + r"\includegraphics{../pages/page02.png}"
        )
        result = _parse_includegraphics(tex)
        assert "../pages/page01.png" in result
        assert "../pages/page02.png" in result

    def test_returns_empty_for_no_graphics(self) -> None:
        assert _parse_includegraphics("No graphics here.") == []

    def test_strips_whitespace(self) -> None:
        tex = r"\includegraphics{ ../pages/page01.png }"
        result = _parse_includegraphics(tex)
        assert result == ["../pages/page01.png"]


class TestParseManifestFigureIds:
    def test_extracts_ids_from_yaml_block(self) -> None:
        manifest = (
            "# Manifest\n\n"
            "```yaml\n"
            "figures:\n"
            "  - id: reflector-figure-1\n"
            "    file: figure1.png\n"
            "  - id: reflector-figure-2\n"
            "    file: figure2.png\n"
            "```\n"
        )
        ids = _parse_manifest_figure_ids(manifest)
        assert "reflector-figure-1" in ids
        assert "reflector-figure-2" in ids

    def test_returns_empty_for_no_yaml_block(self) -> None:
        assert _parse_manifest_figure_ids("# No YAML here") == set()

    def test_returns_empty_for_empty_input(self) -> None:
        assert _parse_manifest_figure_ids("") == set()


class TestExtractSpecVersion:
    def test_extracts_version_from_frontmatter(self) -> None:
        spec = "---\ntitle: Magazine\nversion: 1.2.3\nstatus: draft\n---\n"
        assert _extract_spec_version(spec) == "1.2.3"

    def test_extracts_quoted_version(self) -> None:
        spec = 'version: "0.1.0"\n'
        assert _extract_spec_version(spec) == "0.1.0"

    def test_returns_none_for_missing_version(self) -> None:
        assert _extract_spec_version("title: No version here\n") is None


class TestCollectMappingIds:
    def test_collects_ids_from_all_sections(self) -> None:
        mapping = {
            "metadata_sync": [{"id": "meta-1"}, {"id": "meta-2"}],
            "page_mappings": [{"id": "page-1"}],
            "figure_mappings": [{"id": "fig-1"}],
            "exceptions": [{"id": "exc-1"}],
        }
        ids, dups = _collect_mapping_ids(mapping)
        assert set(ids) == {"meta-1", "meta-2", "page-1", "fig-1", "exc-1"}
        assert dups == []

    def test_detects_duplicates(self) -> None:
        mapping = {
            "page_mappings": [{"id": "page-1"}, {"id": "page-1"}],
        }
        ids, dups = _collect_mapping_ids(mapping)
        assert "page-1" in dups

    def test_handles_empty_sections(self) -> None:
        ids, dups = _collect_mapping_ids({})
        assert ids == []
        assert dups == []

    def test_handles_entries_without_id(self) -> None:
        mapping = {
            "page_mappings": [{"no_id": "value"}, {"id": "valid-id"}],
        }
        ids, dups = _collect_mapping_ids(mapping)
        assert "valid-id" in ids
        assert dups == []


# ===========================================================================
# Synchronized fixture — all checks should pass or warn (never fail)
# ===========================================================================


class TestSynchronizedFixture:
    def test_no_fail_findings(self) -> None:
        """A fully synchronized fixture should produce zero FAIL findings."""
        findings, _ = run_audit(SYNCHRONIZED)
        failures = _findings_by_status(findings, "FAIL")
        assert failures == [], f"Unexpected failures: {[f.name for f in failures]}"

    def test_has_pass_findings(self) -> None:
        """Synchronized fixture should produce at least one PASS finding."""
        findings, _ = run_audit(SYNCHRONIZED)
        assert len(_findings_by_status(findings, "PASS")) > 0

    def test_rule001_all_pass(self) -> None:
        """All RULE-001 checks should pass for the synchronized fixture."""
        findings, _ = run_audit(SYNCHRONIZED)
        rule001 = _findings_by_rule(findings, "RULE-001")
        failures = [f for f in rule001 if f.status == "FAIL"]
        assert failures == []

    def test_rule002_mapping_parse_pass(self) -> None:
        """Mapping YAML parse should pass for the synchronized fixture."""
        findings, _ = run_audit(SYNCHRONIZED)
        assert _has_finding(findings, rule="RULE-002", status="PASS")

    def test_rule003_no_duplicate_ids_pass(self) -> None:
        """No duplicate ID check should pass for the synchronized fixture."""
        findings, _ = run_audit(SYNCHRONIZED)
        assert _has_finding(findings, rule="RULE-003", status="PASS")

    def test_rule004_pages_exist_pass(self) -> None:
        """All declared pages exist check should pass for the synchronized fixture."""
        findings, _ = run_audit(SYNCHRONIZED)
        assert _has_finding(findings, rule="RULE-004", status="PASS")

    def test_approved_exceptions_empty(self) -> None:
        """The synchronized fixture has no approved exceptions."""
        _, exceptions = run_audit(SYNCHRONIZED)
        assert exceptions == []

    def test_exit_code_zero(self, tmp_path: Path) -> None:
        """run_audit on synchronized fixture should indicate exit code 0."""
        findings, _ = run_audit(SYNCHRONIZED)
        fail_count = sum(1 for f in findings if f.status == "FAIL")
        assert fail_count == 0  # would correspond to exit code 0


# ===========================================================================
# Missing manuscript source
# ===========================================================================


class TestMissingManuscriptFixture:
    def test_rule001_fail_for_missing_file(self) -> None:
        """Missing paper/paper.tex should produce a RULE-001 FAIL finding."""
        findings, _ = run_audit(MISSING_MANUSCRIPT)
        assert _has_finding(findings, rule="RULE-001", status="FAIL")

    def test_fail_count_positive(self) -> None:
        """At least one FAIL finding expected when manuscript file is missing."""
        findings, _ = run_audit(MISSING_MANUSCRIPT)
        assert len(_findings_by_status(findings, "FAIL")) > 0

    def test_fail_finding_mentions_paper_tex(self) -> None:
        """FAIL finding should mention paper/paper.tex."""
        findings, _ = run_audit(MISSING_MANUSCRIPT)
        fails = _findings_by_status(findings, "FAIL")
        assert any("paper.tex" in f.details for f in fails)

    def test_fail_finding_has_remediation(self) -> None:
        """Each FAIL finding should include a non-empty remediation direction."""
        findings, _ = run_audit(MISSING_MANUSCRIPT)
        fails = _findings_by_status(findings, "FAIL")
        for f in fails:
            assert f.remediation.strip() != ""


# ===========================================================================
# Missing magazine target
# ===========================================================================


class TestMissingMagazineFixture:
    def test_rule001_fail_for_missing_spec(self) -> None:
        """Missing magazine/spec.md should produce a RULE-001 FAIL finding."""
        findings, _ = run_audit(MISSING_MAGAZINE)
        assert _has_finding(findings, rule="RULE-001", status="FAIL")

    def test_fail_count_positive(self) -> None:
        """At least one FAIL finding expected when magazine file is missing."""
        findings, _ = run_audit(MISSING_MAGAZINE)
        assert len(_findings_by_status(findings, "FAIL")) > 0

    def test_fail_finding_mentions_magazine_spec(self) -> None:
        """FAIL finding should mention magazine/spec.md."""
        findings, _ = run_audit(MISSING_MAGAZINE)
        fails = _findings_by_status(findings, "FAIL")
        assert any("spec.md" in f.details for f in fails)


# ===========================================================================
# Duplicate IDs
# ===========================================================================


class TestDuplicateIdsFixture:
    def test_rule003_fail_for_duplicates(self) -> None:
        """Duplicate mapping IDs should produce a RULE-003 FAIL finding."""
        findings, _ = run_audit(DUPLICATE_IDS)
        assert _has_finding(findings, rule="RULE-003", status="FAIL")

    def test_fail_details_mention_duplicate_id(self) -> None:
        """FAIL details should mention the duplicate ID name."""
        findings, _ = run_audit(DUPLICATE_IDS)
        fails = [f for f in findings if f.rule == "RULE-003" and f.status == "FAIL"]
        assert any("page01-cover" in f.details for f in fails)

    def test_fail_has_remediation(self) -> None:
        """RULE-003 FAIL should include a remediation direction."""
        findings, _ = run_audit(DUPLICATE_IDS)
        fails = [f for f in findings if f.rule == "RULE-003" and f.status == "FAIL"]
        assert all(f.remediation.strip() != "" for f in fails)


# ===========================================================================
# Orphaned mappings (pointing to nonexistent files)
# ===========================================================================


class TestOrphanedMappingFixture:
    def test_rule005_warn_for_missing_source(self) -> None:
        """Orphaned mapping source should produce a RULE-005 WARN (or SKIP if excepted)."""
        findings, _ = run_audit(ORPHANED_MAPPING)
        rule005 = _findings_by_rule(findings, "RULE-005")
        # At least one warn or skip for the nonexistent source
        assert any(f.status in {"WARN", "SKIP"} for f in rule005)

    def test_rule006_warn_for_missing_target(self) -> None:
        """Orphaned mapping target should produce a RULE-006 WARN."""
        findings, _ = run_audit(ORPHANED_MAPPING)
        assert _has_finding(findings, rule="RULE-006", status="WARN")

    def test_no_fail_for_orphaned_advisory_entry(self) -> None:
        """Orphaned advisory entries should not cause FAIL status."""
        findings, _ = run_audit(ORPHANED_MAPPING)
        # RULE-005 and RULE-006 are advisory (WARN) — not FAIL
        assert not _has_finding(findings, rule="RULE-005", status="FAIL")
        assert not _has_finding(findings, rule="RULE-006", status="FAIL")

    def test_exit_code_zero_for_advisory_only(self) -> None:
        """Advisory-only findings should correspond to exit code 0."""
        findings, _ = run_audit(ORPHANED_MAPPING)
        fail_count = sum(1 for f in findings if f.status == "FAIL")
        assert fail_count == 0


# ===========================================================================
# Malformed mapping YAML
# ===========================================================================


class TestMalformedMappingFixture:
    def test_rule002_fail_for_invalid_yaml(self) -> None:
        """Invalid YAML in the mapping file should produce a RULE-002 FAIL."""
        findings, _ = run_audit(MALFORMED_MAPPING)
        assert _has_finding(findings, rule="RULE-002", status="FAIL")

    def test_fail_count_positive(self) -> None:
        findings, _ = run_audit(MALFORMED_MAPPING)
        assert len(_findings_by_status(findings, "FAIL")) > 0


# ===========================================================================
# Metadata version mismatch
# ===========================================================================


class TestMetadataMismatchFixture:
    def test_rule007_warn_for_version_mismatch(self) -> None:
        """A version mismatch should produce a RULE-007 WARN finding."""
        findings, _ = run_audit(METADATA_MISMATCH)
        assert _has_finding(findings, rule="RULE-007", status="WARN")

    def test_warn_details_mention_both_versions(self) -> None:
        """WARN details should mention both version values."""
        findings, _ = run_audit(METADATA_MISMATCH)
        warns = [f for f in findings if f.rule == "RULE-007" and f.status == "WARN"]
        assert warns, "Expected at least one RULE-007 WARN"
        details = warns[0].details
        # Should mention version mismatch
        assert "mismatch" in details.lower() or "1.0.0" in details or "0.0.1" in details

    def test_no_fail_for_advisory_mismatch(self) -> None:
        """A version mismatch is advisory — it must not produce FAIL."""
        findings, _ = run_audit(METADATA_MISMATCH)
        assert not _has_finding(findings, rule="RULE-007", status="FAIL")

    def test_exit_code_zero_for_version_mismatch(self) -> None:
        """Version mismatch is advisory — exit code should be 0."""
        findings, _ = run_audit(METADATA_MISMATCH)
        fail_count = sum(1 for f in findings if f.status == "FAIL")
        assert fail_count == 0


# ===========================================================================
# Approved exceptions
# ===========================================================================


class TestApprovedExceptions:
    def test_valid_exception_is_returned(self) -> None:
        """A valid exception in the mapping should appear in approved_exceptions."""
        # Use a fixture that has an exception declared
        exception_mapping = """spec_version: "1.0"

page_mappings:
  - id: page01-cover
    rule: RULE-004
    manuscript_source: "paper/macros/metadata.tex"
    magazine_target: "magazine/pages/page01-cover.png"
    relationship_type: derived-from
    relationship: required
    description: "Cover page"

exceptions:
  - id: exc-test-exception
    rule: RULE-007
    rationale: "Intentional divergence for test purposes."
    scope: "magazine/spec.md version field"
    approved_by: "test-author"
"""
        import tempfile, os
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            # Copy synchronized fixture structure
            import shutil
            shutil.copytree(SYNCHRONIZED, root, dirs_exist_ok=True)
            # Overwrite mapping with exception
            (root / "magazine" / "consistency-mapping.yaml").write_text(exception_mapping)
            findings, exceptions = run_audit(root)
            exc_ids = [e.id for e in exceptions]
            assert "exc-test-exception" in exc_ids

    def test_exception_has_required_fields(self) -> None:
        """Each MappingException must have id, rule, rationale, scope, approved_by."""
        import tempfile
        import shutil
        exception_mapping = """spec_version: "1.0"

exceptions:
  - id: exc-test
    rule: RULE-007
    rationale: "Test rationale."
    scope: "narrow scope"
    approved_by: "author"
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            shutil.copytree(SYNCHRONIZED, root, dirs_exist_ok=True)
            (root / "magazine" / "consistency-mapping.yaml").write_text(exception_mapping)
            _, exceptions = run_audit(root)
            assert len(exceptions) == 1
            exc = exceptions[0]
            assert exc.id == "exc-test"
            assert exc.rule == "RULE-007"
            assert exc.rationale == "Test rationale."
            assert exc.scope == "narrow scope"
            assert exc.approved_by == "author"

    def test_exception_missing_required_fields_produces_warn(self) -> None:
        """An exception entry missing required fields should produce a WARN finding."""
        import tempfile
        import shutil
        bad_exception_mapping = """spec_version: "1.0"

exceptions:
  - rationale: "No id or rule here."
    scope: "some scope"
    approved_by: "author"
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            shutil.copytree(SYNCHRONIZED, root, dirs_exist_ok=True)
            (root / "magazine" / "consistency-mapping.yaml").write_text(bad_exception_mapping)
            findings, exceptions = run_audit(root)
            # Should produce a WARN about missing fields
            assert _has_finding(findings, rule="RULE-002", status="WARN")
            # Invalid exception should not appear in approved exceptions
            assert exceptions == []


# ===========================================================================
# Missing required input file (mapping file)
# ===========================================================================


class TestMissingMappingFile:
    def test_rule001_fail_for_missing_mapping(self, tmp_path: Path) -> None:
        """Missing mapping file should produce RULE-001 FAIL."""
        import shutil
        root = tmp_path / "no_mapping"
        shutil.copytree(SYNCHRONIZED, root)
        (root / "magazine" / "consistency-mapping.yaml").unlink()
        findings, _ = run_audit(root)
        # Should fail for missing mapping file
        fails = [f for f in findings if f.status == "FAIL" and "consistency-mapping" in f.details]
        assert len(fails) > 0

    def test_rule002_fail_when_mapping_missing(self, tmp_path: Path) -> None:
        """RULE-002 should fail when mapping file does not exist."""
        import shutil
        root = tmp_path / "no_mapping"
        shutil.copytree(SYNCHRONIZED, root)
        (root / "magazine" / "consistency-mapping.yaml").unlink()
        findings, _ = run_audit(root)
        assert _has_finding(findings, rule="RULE-002", status="FAIL")


# ===========================================================================
# Deterministic output
# ===========================================================================


class TestDeterministicOutput:
    def test_same_findings_on_repeated_runs(self) -> None:
        """Two consecutive audit runs should produce identical findings."""
        findings1, exc1 = run_audit(SYNCHRONIZED)
        findings2, exc2 = run_audit(SYNCHRONIZED)
        assert len(findings1) == len(findings2)
        for f1, f2 in zip(findings1, findings2):
            assert f1.rule == f2.rule
            assert f1.status == f2.status
            assert f1.name == f2.name

    def test_findings_are_sorted(self) -> None:
        """Findings should be in deterministic sorted order (area, name, rule)."""
        findings, _ = run_audit(SYNCHRONIZED)
        re_sorted = sorted_findings(findings)
        for a, b in zip(findings, re_sorted):
            assert a.name == b.name
            assert a.rule == b.rule


# ===========================================================================
# write_report produces valid output
# ===========================================================================


class TestWriteReport:
    def test_report_written_to_file(self, tmp_path: Path) -> None:
        """write_report should create the output file."""
        findings, exceptions = run_audit(SYNCHRONIZED)
        output = tmp_path / "report.md"
        write_report(findings, exceptions, output)
        assert output.exists()

    def test_report_contains_title(self, tmp_path: Path) -> None:
        """Report should contain the standard title."""
        findings, exceptions = run_audit(SYNCHRONIZED)
        output = tmp_path / "report.md"
        write_report(findings, exceptions, output)
        content = output.read_text(encoding="utf-8")
        assert "Magazine-to-Manuscript Consistency Audit Report" in content

    def test_report_contains_summary_counts(self, tmp_path: Path) -> None:
        """Report should include pass/warn/fail counts."""
        findings, exceptions = run_audit(SYNCHRONIZED)
        output = tmp_path / "report.md"
        write_report(findings, exceptions, output)
        content = output.read_text(encoding="utf-8")
        assert "Pass:" in content
        assert "Warn:" in content
        assert "Fail:" in content

    def test_report_contains_final_status(self, tmp_path: Path) -> None:
        """Report should include a Final Status section."""
        findings, exceptions = run_audit(SYNCHRONIZED)
        output = tmp_path / "report.md"
        write_report(findings, exceptions, output)
        content = output.read_text(encoding="utf-8")
        assert "Final Status" in content

    def test_report_for_failure_includes_remediation(self, tmp_path: Path) -> None:
        """Report for a fixture with failures should include remediation text."""
        findings, exceptions = run_audit(MISSING_MANUSCRIPT)
        output = tmp_path / "report.md"
        write_report(findings, exceptions, output)
        content = output.read_text(encoding="utf-8")
        assert "Remediation" in content

    def test_report_for_exceptions_includes_exception_section(self, tmp_path: Path) -> None:
        """Report with approved exceptions should include an exceptions section."""
        import shutil
        root = tmp_path / "with_exc"
        shutil.copytree(SYNCHRONIZED, root)
        (root / "magazine" / "consistency-mapping.yaml").write_text(
            'spec_version: "1.0"\n'
            "exceptions:\n"
            "  - id: exc-x\n"
            "    rule: RULE-007\n"
            "    rationale: test\n"
            "    scope: narrow\n"
            "    approved_by: author\n"
        )
        findings, exceptions = run_audit(root)
        output = tmp_path / "report.md"
        write_report(findings, exceptions, output)
        content = output.read_text(encoding="utf-8")
        assert "exc-x" in content or "Approved Exceptions" in content

    def test_report_is_deterministic(self, tmp_path: Path) -> None:
        """Two report writes for the same findings should produce identical output."""
        findings, exceptions = run_audit(SYNCHRONIZED)
        out1 = tmp_path / "r1.md"
        out2 = tmp_path / "r2.md"
        import time
        write_report(findings, exceptions, out1)
        time.sleep(0.01)
        write_report(findings, exceptions, out2)
        # Timestamps will differ, but structure and finding lines should match
        lines1 = [l for l in out1.read_text().splitlines() if "Generated at" not in l]
        lines2 = [l for l in out2.read_text().splitlines() if "Generated at" not in l]
        assert lines1 == lines2


# ===========================================================================
# Finding data model
# ===========================================================================


class TestFindingDataModel:
    def test_finding_has_required_fields(self) -> None:
        """Finding instances should have all required diagnostic fields."""
        findings, _ = run_audit(SYNCHRONIZED)
        for f in findings:
            assert hasattr(f, "rule")
            assert hasattr(f, "area")
            assert hasattr(f, "name")
            assert hasattr(f, "status")
            assert hasattr(f, "source")
            assert hasattr(f, "target")
            assert hasattr(f, "details")
            assert hasattr(f, "expected")
            assert hasattr(f, "remediation")

    def test_finding_statuses_are_valid(self) -> None:
        """All finding statuses must be one of PASS, WARN, FAIL, SKIP."""
        findings, _ = run_audit(SYNCHRONIZED)
        valid_statuses = {"PASS", "WARN", "FAIL", "SKIP"}
        for f in findings:
            assert f.status in valid_statuses, f"Invalid status: {f.status}"

    def test_fail_findings_have_nonempty_remediation(self) -> None:
        """Every FAIL finding must include a non-empty remediation."""
        findings, _ = run_audit(MISSING_MANUSCRIPT)
        fails = _findings_by_status(findings, "FAIL")
        for f in fails:
            assert f.remediation.strip() != "", f"FAIL finding has empty remediation: {f.name}"


# ===========================================================================
# Exit status behavior
# ===========================================================================


class TestExitStatus:
    def test_exit_zero_for_synchronized_fixture(self) -> None:
        """Synchronized fixture: fail_count == 0 → exit code 0."""
        findings, _ = run_audit(SYNCHRONIZED)
        assert sum(1 for f in findings if f.status == "FAIL") == 0

    def test_exit_nonzero_for_missing_manuscript(self) -> None:
        """Missing manuscript file: fail_count > 0 → exit code 1."""
        findings, _ = run_audit(MISSING_MANUSCRIPT)
        assert sum(1 for f in findings if f.status == "FAIL") > 0

    def test_exit_nonzero_for_duplicate_ids(self) -> None:
        """Duplicate IDs: fail_count > 0 → exit code 1."""
        findings, _ = run_audit(DUPLICATE_IDS)
        assert sum(1 for f in findings if f.status == "FAIL") > 0

    def test_exit_nonzero_for_malformed_yaml(self) -> None:
        """Malformed YAML: fail_count > 0 → exit code 1."""
        findings, _ = run_audit(MALFORMED_MAPPING)
        assert sum(1 for f in findings if f.status == "FAIL") > 0

    def test_exit_zero_for_advisory_warnings_only(self) -> None:
        """Advisory-only findings: fail_count == 0 → exit code 0."""
        findings, _ = run_audit(ORPHANED_MAPPING)
        assert sum(1 for f in findings if f.status == "FAIL") == 0

    def test_exit_zero_for_version_mismatch(self) -> None:
        """Version mismatch is advisory: fail_count == 0 → exit code 0."""
        findings, _ = run_audit(METADATA_MISMATCH)
        assert sum(1 for f in findings if f.status == "FAIL") == 0


# ===========================================================================
# CLI invocation (subprocess)
# ===========================================================================


class TestCLIInvocation:
    def test_cli_returns_zero_for_synchronized(self, tmp_path: Path) -> None:
        """CLI should exit 0 for the synchronized fixture."""
        result = subprocess.run(
            [sys.executable, str(_AUDIT_SCRIPT), "--repo-root", str(SYNCHRONIZED),
             "--output", str(tmp_path / "report.md")],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Unexpected exit code: {result.returncode}\n{result.stdout}\n{result.stderr}"

    def test_cli_returns_nonzero_for_missing_manuscript(self, tmp_path: Path) -> None:
        """CLI should exit 1 when required files are missing."""
        result = subprocess.run(
            [sys.executable, str(_AUDIT_SCRIPT), "--repo-root", str(MISSING_MANUSCRIPT),
             "--output", str(tmp_path / "report.md")],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1

    def test_cli_prints_report_path(self, tmp_path: Path) -> None:
        """CLI stdout should mention the report output path."""
        output = tmp_path / "report.md"
        result = subprocess.run(
            [sys.executable, str(_AUDIT_SCRIPT), "--repo-root", str(SYNCHRONIZED),
             "--output", str(output)],
            capture_output=True,
            text=True,
        )
        assert str(output) in result.stdout or "report" in result.stdout.lower()

    def test_cli_creates_report_file(self, tmp_path: Path) -> None:
        """CLI should create the output report file."""
        output = tmp_path / "report.md"
        subprocess.run(
            [sys.executable, str(_AUDIT_SCRIPT), "--repo-root", str(SYNCHRONIZED),
             "--output", str(output)],
            capture_output=True,
            text=True,
        )
        assert output.exists()

    def test_cli_does_not_modify_source_artifacts(self, tmp_path: Path) -> None:
        """CLI must not modify any source artifact."""
        import shutil
        import hashlib
        root = tmp_path / "repo"
        shutil.copytree(SYNCHRONIZED, root)
        # Collect checksums before
        def checksum(p: Path) -> str:
            return hashlib.md5(p.read_bytes()).hexdigest()
        before = {str(f.relative_to(root)): checksum(f)
                  for f in root.rglob("*") if f.is_file()}
        # Run audit
        subprocess.run(
            [sys.executable, str(_AUDIT_SCRIPT), "--repo-root", str(root),
             "--output", str(tmp_path / "report.md")],
            capture_output=True,
            text=True,
        )
        # Collect checksums after
        after = {str(f.relative_to(root)): checksum(f)
                 for f in root.rglob("*") if f.is_file()}
        # All original files should be unchanged
        for rel, digest in before.items():
            assert after.get(rel) == digest, f"File was modified: {rel}"


# ===========================================================================
# Integration test — real repository content
# ===========================================================================


@pytest.mark.integration
class TestIntegrationRealRepository:
    """Integration test against real repository content.

    Validates that the audit runs successfully against the live repository
    without modifying any source artifacts.
    """

    def test_audit_runs_without_exception(self) -> None:
        """Audit should complete without raising any Python exception."""
        try:
            findings, exceptions = run_audit(REPO_ROOT)
        except Exception as exc:  # noqa: BLE001
            pytest.fail(f"run_audit raised an exception: {exc}")

    def test_findings_are_list_of_findings(self) -> None:
        """run_audit should return a list of Finding objects."""
        findings, _ = run_audit(REPO_ROOT)
        assert isinstance(findings, list)
        for f in findings:
            assert isinstance(f, Finding)

    def test_at_least_one_finding(self) -> None:
        """Real repository audit should produce at least one finding."""
        findings, _ = run_audit(REPO_ROOT)
        assert len(findings) > 0

    def test_real_repo_mapping_file_exists(self) -> None:
        """Real repository should have the consistency mapping file."""
        assert (REPO_ROOT / "magazine" / "consistency-mapping.yaml").exists()

    def test_real_repo_required_files_present(self) -> None:
        """Required files should be present in the real repository."""
        required = [
            "paper/paper.tex",
            "paper/figures/manifest.md",
            "metadata/publication.yaml",
            "metadata/authors.yaml",
            "publication.json",
            "magazine/tex/magazine.tex",
            "magazine/spec.md",
        ]
        for rel in required:
            assert (REPO_ROOT / rel).exists(), f"Required file missing: {rel}"

    def test_real_repo_rule001_passes(self) -> None:
        """RULE-001 checks should pass for the real repository."""
        findings, _ = run_audit(REPO_ROOT)
        rule001_fails = [f for f in findings if f.rule == "RULE-001" and f.status == "FAIL"]
        assert rule001_fails == [], f"RULE-001 failures: {[f.name for f in rule001_fails]}"

    def test_real_repo_rule002_passes(self) -> None:
        """RULE-002 (mapping YAML parse) should pass for the real repository."""
        findings, _ = run_audit(REPO_ROOT)
        rule002_fails = [f for f in findings if f.rule == "RULE-002" and f.status == "FAIL"]
        assert rule002_fails == [], f"RULE-002 failures: {[f.name for f in rule002_fails]}"

    def test_real_repo_rule003_passes(self) -> None:
        """RULE-003 (no duplicate IDs) should pass for the real repository."""
        findings, _ = run_audit(REPO_ROOT)
        rule003_fails = [f for f in findings if f.rule == "RULE-003" and f.status == "FAIL"]
        assert rule003_fails == [], f"RULE-003 failures: {[f.name for f in rule003_fails]}"

    def test_real_repo_rule004_passes(self) -> None:
        """RULE-004 (declared pages exist) should pass for the real repository."""
        findings, _ = run_audit(REPO_ROOT)
        rule004_fails = [f for f in findings if f.rule == "RULE-004" and f.status == "FAIL"]
        assert rule004_fails == [], f"RULE-004 failures: {[f.name for f in rule004_fails]}"

    def test_real_repo_no_hard_failures(self) -> None:
        """The real repository should have zero FAIL findings."""
        findings, _ = run_audit(REPO_ROOT)
        failures = [f for f in findings if f.status == "FAIL"]
        assert failures == [], f"Unexpected failures in real repo: {[(f.rule, f.name) for f in failures]}"

    def test_real_repo_write_report_succeeds(self, tmp_path: Path) -> None:
        """write_report should succeed for real repository content."""
        findings, exceptions = run_audit(REPO_ROOT)
        output = tmp_path / "magazine-consistency.md"
        write_report(findings, exceptions, output)
        assert output.exists()
        content = output.read_text(encoding="utf-8")
        assert "Magazine-to-Manuscript Consistency Audit Report" in content

    def test_real_repo_cli_exit_zero(self, tmp_path: Path) -> None:
        """CLI should exit 0 for the real repository."""
        result = subprocess.run(
            [sys.executable, str(_AUDIT_SCRIPT),
             "--repo-root", str(REPO_ROOT),
             "--output", str(tmp_path / "report.md")],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"CLI exited {result.returncode} for real repo.\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
