# arXiv Packaging Validation Report

Generated at: 2026-08-27T15:30:00Z

## Executive Summary

- Validation target: the exact deterministic staged arXiv source tree, not every file retained in the canonical paper workspace.
- The stage contains only the manifest-declared TeX dependency closure plus 00README.json; reference-library PDFs, website assets, and unused artwork remain canonical-only.
- Total checks: **26**
- Pass: **26**
- Fail: **0**

Overall result: ✅ **arXiv upload-ready**

## Goal Checklist

- [x] Materialize the exact declared submission tree
- [x] Validate the arXiv manifest and declared compiler path
- [x] Verify the full TeX dependency closure is declared
- [x] Exclude hidden, system, and undeclared files
- [x] Enforce file and bundle-size boundaries
- [x] Verify the biber-compatible bibliography path

## Detailed Checks

### Bibliography

| Check | Result | Details |
| --- | --- | --- |
| Bibliography source is present and non-empty | ✅ PASS | 1 bibliography file(s) contain 15 entries. |
| biblatex backend matches the declared biber path | ✅ PASS | The bibliography style and manifest agree on biber. |

### Figure compatibility

| Check | Result | Details |
| --- | --- | --- |
| All staged figures use arXiv-safe formats | ✅ PASS | All 17 staged figures use arXiv-safe formats. |
| No staged source file exceeds the per-file size limit | ✅ PASS | All staged files are at or below 10.00 MB (10000000 bytes). |
| Exact staged arXiv source tree is within the 45 MB headroom target | ✅ PASS | Exact staged source tree is 18.25 MB (18251667 bytes); limit is 45.00 MB (45000000 bytes). |

### Manifest

| Check | Result | Details |
| --- | --- | --- |
| 00README.json is parseable JSON | ✅ PASS | 00README.json is valid JSON in the staged submission. |
| 00README schema references arXiv | ✅ PASS | 00README schema references the arXiv 00readme schema. |
| 00README required root keys are present | ✅ PASS | 00README includes all required root keys. |
| Compiler is arXiv-supported | ✅ PASS | Declared compiler 'pdflatex' is supported by arXiv. |
| Bibliography tool is arXiv-supported | ✅ PASS | Declared bibliography tool 'biber' is supported by arXiv. |
| Deterministic staging is declared | ✅ PASS | process.deterministic is true. |
| TeX Live version is declared | ✅ PASS | process.texlive declares '2025'. |
| Maximum compiler repeats are declared | ✅ PASS | process.max_repeat is 10. |
| Direct pdflatex/biber path is declared | ✅ PASS | The manifest declares pdflatex, biber, then two pdflatex passes. |
| Submission does not rely on TEXINPUTS overrides | ✅ PASS | build.texinputs is empty; staged compilation resolves declared paths directly. |
| Declared staging budget matches the enforced headroom target | ✅ PASS | Manifest and validator both enforce 45.00 MB (45000000 bytes). |

### Source declarations

| Check | Result | Details |
| --- | --- | --- |
| All source usage values are valid | ✅ PASS | All source usage values are valid. |
| Declared sources are safe, unique, and present | ✅ PASS | Every declared source is relative, arXiv-safe, unique, and present. |
| All declared source file types are arXiv-safe | ✅ PASS | All declared source types are arXiv-safe. |
| Every compiled TeX dependency is declared | ✅ PASS | All 40 discovered compilation dependencies are declared. |
| Manifest declarations are the exact TeX dependency closure | ✅ PASS | All 40 declared sources are required by compilation. |

### Staging

| Check | Result | Details |
| --- | --- | --- |
| Exact staged submission directory exists | ✅ PASS | The validator is measuring a materialized arXiv submission directory. |

### Upload structure

| Check | Result | Details |
| --- | --- | --- |
| Staged tree contains exactly the manifest-declared source set | ✅ PASS | The staged tree contains exactly 41 declared source files. |
| No symlinks are present | ✅ PASS | No symlinks are present in the staged submission. |
| No banned system files are present | ✅ PASS | No banned system files are present. |
| No hidden runtime files are present | ✅ PASS | The staged submission does not rely on hidden files. |
