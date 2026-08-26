#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0

"""Reject initialization because this profile adopts an existing Reflector repository."""

from __future__ import annotations

import argparse


def main() -> int:
    """Explain the compatibility profile's adoption-only boundary."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--destination", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--author", required=True)
    parser.parse_args()
    parser.error(
        "reflector-compatibility adopts an existing Reflector repository; "
        "initialize new publications from Beacon's built-in profiles"
    )


if __name__ == "__main__":
    raise SystemExit(main())
