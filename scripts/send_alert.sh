#!/usr/bin/env bash
set -euo pipefail

msg="${1:-publicidad-concursal daily run failed twice consecutively}"

if [ -n "${ALERT_WEBHOOK_URL:-}" ]; then
  payload=$(python3 -c 'import json,sys; print(json.dumps({"text": sys.argv[1]}))' "$msg")
  curl -fsS -X POST "$ALERT_WEBHOOK_URL" -H 'Content-Type: application/json' -d "$payload" >/dev/null
  exit 0
fi

if [ -n "${ALERT_COMMAND:-}" ]; then
  MSG="$msg" bash -lc "$ALERT_COMMAND"
  exit 0
fi

echo "[alert] $msg"
