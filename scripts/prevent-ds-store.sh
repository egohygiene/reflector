#!/usr/bin/env bash

set -euo pipefail

if git diff --cached --name-only --diff-filter=AM | grep -Eq '(^|/)\.DS_Store$'; then
  echo "Do not commit .DS_Store files." >&2
  exit 1
fi
