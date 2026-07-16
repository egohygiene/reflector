# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import argparse
import importlib.util
import subprocess
from pathlib import Path

import pytest


SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent / "scripts" / "generate_pdf_previews.py"
)
SPEC = importlib.util.spec_from_file_location("generate_pdf_previews", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_parse_preview_spec_rejects_missing_equals() -> None:
    with pytest.raises(argparse.ArgumentTypeError):
        MODULE.parse_preview_spec("paper-cover")


def test_main_generates_expected_preview_commands(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[list[str]] = []

    def fake_which(name: str) -> str | None:
        mapping = {
            "pdftoppm": "/usr/bin/pdftoppm",
            "cwebp": "/usr/bin/cwebp",
        }
        return mapping.get(name)

    def fake_run(cmd: list[str], check: bool) -> subprocess.CompletedProcess[str]:
        calls.append(cmd)
        if cmd[0] == "/usr/bin/pdftoppm":
            Path(cmd[-1] + ".png").write_bytes(b"png")
        elif cmd[0] == "/usr/bin/cwebp":
            Path(cmd[-1]).write_bytes(b"webp")
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(MODULE.shutil, "which", fake_which)
    monkeypatch.setattr(MODULE.subprocess, "run", fake_run)

    pdf_path = tmp_path / "reflector.pdf"
    pdf_path.write_bytes(b"%PDF-1.7")
    output_dir = tmp_path / "previews"

    result = MODULE.main(
        [
            "--output-dir",
            str(output_dir),
            "--preview",
            f"paper-cover={pdf_path}",
        ]
    )

    assert result == 0
    assert output_dir.joinpath("paper-cover.webp").is_file()
    assert calls[0][0] == "/usr/bin/pdftoppm"
    assert str(pdf_path) in calls[0]
    assert calls[1][0] == "/usr/bin/cwebp"
    assert calls[1][-1] == str(output_dir / "paper-cover.webp")
