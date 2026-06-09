#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-plan}"
SOURCE="${CONVERGER_SOURCE:-replay}"
DESIRED="${DESIRED_PATH:-examples/desired.yaml}"
CONFIG="${CONVERGER_CONFIG:-}"

args=("$MODE" "--desired" "$DESIRED")

if [[ -n "$CONFIG" ]]; then
  args=("-c" "$CONFIG" "${args[@]}")
fi

case "$SOURCE" in
  replay)
    args+=("--replay" "${REPLAY_PATH:-examples/replay.json}")
    ;;
  proxmox|aws|hetzner)
    args+=("-s" "$SOURCE")
    ;;
  *)
    echo "Unsupported CONVERGER_SOURCE: $SOURCE" >&2
    exit 1
    ;;
esac

exec converger "${args[@]}"