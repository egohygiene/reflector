#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
# beacon-compatibility.sh — Run the Reflector-owned profile with pinned Beacon.

set -euo pipefail

REPOSITORY_ROOT="$(git rev-parse --show-toplevel)"
LOCK_FILE="${REPOSITORY_ROOT}/dependencies/beacon.lock.json"
PROFILE_DIRECTORY="${REPOSITORY_ROOT}/.beacon/profiles"
ACTION="${1:-plan}"

if [[ $# -gt 0 ]]; then
  shift
fi

read_lock_field() {
  local field="$1"
  python3 -c \
    'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))[sys.argv[2]])' \
    "${LOCK_FILE}" "${field}"
}

BEACON_REPOSITORY="$(read_lock_field "repository")"
BEACON_REVISION="$(read_lock_field "revision")"
BEACON_RUST_TOOLCHAIN="$(read_lock_field "rust_toolchain")"
BEACON_DIRECTORY="${BEACON_ROOT:-${REPOSITORY_ROOT}/.cache/beacon}"

resolve_beacon() {
  if [[ -n "${BEACON_ROOT:-}" ]]; then
    if [[ ! -d "${BEACON_DIRECTORY}/.git" ]]; then
      echo "Error: BEACON_ROOT is not a Git checkout: ${BEACON_DIRECTORY}" >&2
      exit 1
    fi
  elif [[ ! -d "${BEACON_DIRECTORY}/.git" ]]; then
    mkdir -p "$(dirname "${BEACON_DIRECTORY}")"
    git clone --filter=blob:none --no-checkout "${BEACON_REPOSITORY}" "${BEACON_DIRECTORY}"
  fi

  local observed_revision
  observed_revision="$(git -C "${BEACON_DIRECTORY}" rev-parse HEAD 2>/dev/null || true)"
  if [[ "${observed_revision}" != "${BEACON_REVISION}" || ! -f "${BEACON_DIRECTORY}/Cargo.toml" ]]; then
    if [[ -n "${BEACON_ROOT:-}" ]]; then
      echo "Error: BEACON_ROOT must be a materialized checkout pinned at ${BEACON_REVISION}; found ${observed_revision:-none}." >&2
      exit 1
    fi
    if [[ "${observed_revision}" != "${BEACON_REVISION}" ]]; then
      git -C "${BEACON_DIRECTORY}" fetch --depth=1 origin "${BEACON_REVISION}"
    fi
    git -C "${BEACON_DIRECTORY}" checkout --detach "${BEACON_REVISION}"
  fi
}

run_beacon() {
  cargo "+${BEACON_RUST_TOOLCHAIN}" run --quiet --locked \
    --manifest-path "${BEACON_DIRECTORY}/Cargo.toml" \
    -- \
    --templates-directory "${PROFILE_DIRECTORY}" \
    "$@"
}

resolve_beacon

case "${ACTION}" in
  validate)
    run_beacon validate "reflector-compatibility" "$@"
    ;;
  inspect)
    run_beacon inspect "reflector-compatibility" "$@"
    ;;
  doctor)
    run_beacon doctor "reflector-compatibility" --allow-executable-adapter "$@"
    ;;
  plan)
    run_beacon plan "${REPOSITORY_ROOT}" "$@"
    ;;
  build)
    run_beacon build "${REPOSITORY_ROOT}" --allow-executable-adapter "$@"
    ;;
  package)
    run_beacon package "${REPOSITORY_ROOT}" --allow-executable-adapter "$@"
    ;;
  *)
    echo "Usage: $0 [validate|inspect|doctor|plan|build|package] [Beacon options]" >&2
    exit 2
    ;;
esac
