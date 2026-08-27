#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Compatibility entrypoint for staged arXiv submission validation."""

from validate_arxiv_packaging import main


if __name__ == "__main__":
    raise SystemExit(main())
