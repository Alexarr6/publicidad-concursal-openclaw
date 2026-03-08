#!/usr/bin/env bash
set -euo pipefail

state_dir="artifacts/state"
mkdir -p "$state_dir"

status_file="$state_dir/last_status"
fails_file="$state_dir/consecutive_failures"
error_file="$state_dir/last_error"
updated_file="$state_dir/last_run_utc"
alert_file="$state_dir/last_alert_utc"

failures=0
if [ -f "$fails_file" ]; then
  failures="$(cat "$fails_file")"
fi

run_once() {
  if [ "${RUN_DAILY_FORCE_FAIL:-0}" = "1" ]; then
    return 1
  fi
  make run-and-load-today
}

set +e
run_once
rc=$?
if [ $rc -ne 0 ]; then
  sleep 2
  run_once
  rc=$?
fi
set -e

now="$(date -u +%FT%TZ)"
echo "$now" > "$updated_file"

if [ $rc -eq 0 ]; then
  echo "ok" > "$status_file"
  echo "0" > "$fails_file"
  : > "$error_file"
  echo "daily run succeeded"
  exit 0
fi

failures=$((failures + 1))
echo "$failures" > "$fails_file"
echo "failed" > "$status_file"
echo "run-and-load-today failed after retry" > "$error_file"

if [ "$failures" -ge 2 ]; then
  cooldown_min="${ALERT_COOLDOWN_MINUTES:-720}"
  should_alert=1
  if [ -f "$alert_file" ]; then
    last_epoch=$(date -u -d "$(cat "$alert_file")" +%s 2>/dev/null || echo 0)
    now_epoch=$(date -u +%s)
    elapsed_min=$(((now_epoch - last_epoch) / 60))
    if [ "$elapsed_min" -lt "$cooldown_min" ]; then
      should_alert=0
    fi
  fi

  if [ "$should_alert" -eq 1 ]; then
    msg="Reminder: publicidad-concursal daily pipeline has failed ${failures} times consecutively (with one retry each run). Last failure at ${now}."
    bash scripts/send_alert.sh "$msg"
    echo "$now" > "$alert_file"
  fi
fi

exit 1
