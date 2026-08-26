# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0

"""Tests for the repository-owned Beacon compatibility adapter."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
ADAPTER_PATH = (
    REPOSITORY_ROOT
    / ".beacon"
    / "profiles"
    / "reflector-compatibility"
    / "scripts"
    / "build.py"
)


def load_adapter() -> ModuleType:
    """Load the hidden compatibility adapter as an importable test module."""
    spec = importlib.util.spec_from_file_location("reflector_beacon_compatibility", ADAPTER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CompatibilityTests(unittest.TestCase):
    """Exercise dependency-pin and non-deployment evidence contracts."""

    def test_dependency_pin_matches_profile(self) -> None:
        """Keep the project envelope, profile, and dependency lock synchronized."""
        adapter = load_adapter()
        lock = adapter.load_lock(REPOSITORY_ROOT)

        self.assertEqual(lock["compatibility_profile"], adapter.PROFILE_ID)
        self.assertEqual(lock["compatibility_profile_version"], adapter.PROFILE_VERSION)
        self.assertEqual(len(lock["revision"]), 40)

    def test_report_is_non_deploying_and_records_provenance(self) -> None:
        """Record dependency pins without claiming publication side effects."""
        adapter = load_adapter()
        lock = json.loads((REPOSITORY_ROOT / adapter.LOCK_PATH).read_text(encoding="utf-8"))

        def fake_git_output(_project: Path, *arguments: str) -> str:
            if arguments == ("rev-parse", "HEAD"):
                return "1" * 40
            return ""

        with patch.object(adapter, "git_output", side_effect=fake_git_output):
            report = adapter.compatibility_report(REPOSITORY_ROOT, lock, [])

        self.assertEqual(report["beacon_dependency"]["revision"], lock["revision"])
        self.assertEqual(
            report["reflector_source"],
            {
                "dirty": False,
                "repository": "https://github.com/egohygiene/reflector",
                "revision": "1" * 40,
            },
        )
        self.assertEqual(
            report["side_effects"],
            {
                "deploys": False,
                "publishes": False,
                "releases": False,
            },
        )
        self.assertEqual(
            {exception["owner"] for exception in report["exceptions"]},
            {"beacon", "reflector"},
        )


if __name__ == "__main__":
    unittest.main()
