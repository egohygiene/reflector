#!/usr/bin/env bash

set -euo pipefail

if ! command -v latexindent >/dev/null 2>&1; then
  echo "latexindent not found; skipping LaTeX formatting."
  exit 0
fi

for file in "$@"; do
  latexindent -w -l .latexindent.yml "${file}"
  find "$(dirname "${file}")" -maxdepth 1 -name "$(basename "${file}").bak*" -delete
done
