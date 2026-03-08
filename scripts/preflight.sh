#!/usr/bin/env bash
set -euo pipefail

fail=0

check_bin() {
  local cmd="$1"
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "[ok] $cmd found"
  else
    echo "[error] Missing required binary: $cmd"
    fail=1
  fi
}

check_bin git
check_bin gh
check_bin uv
check_bin docker

if docker compose version >/dev/null 2>&1; then
  echo "[ok] docker compose plugin found"
else
  echo "[error] docker compose plugin not available"
  fail=1
fi

if command -v gh >/dev/null 2>&1; then
  if gh auth status >/dev/null 2>&1; then
    echo "[ok] gh auth status"
  else
    if [ "${GH_AUTH_REQUIRED:-0}" = "1" ]; then
      echo "[error] gh is not authenticated. Run: gh auth login"
      fail=1
    else
      echo "[warn] gh is not authenticated. Run: gh auth login if GitHub API is needed."
    fi
  fi
fi

if command -v docker >/dev/null 2>&1; then
  if docker info >/dev/null 2>&1; then
    echo "[ok] docker daemon available"
  else
    echo "[error] docker daemon unavailable. Start Docker and retry."
    fail=1
  fi
fi

if [ "$fail" -ne 0 ]; then
  echo "Preflight failed."
  exit 1
fi

echo "Preflight passed."
