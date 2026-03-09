#!/usr/bin/env bash
set -euo pipefail

state_dir="artifacts/state"
mkdir -p "$state_dir"

status_file="$state_dir/last_status"
fails_file="$state_dir/consecutive_failures"
error_file="$state_dir/last_error"
updated_file="$state_dir/last_run_utc"
alert_file="$state_dir/last_alert_utc"

cooldown_min="${ALERT_COOLDOWN_MINUTES:-720}"

should_alert_now() {
  if [ -f "$alert_file" ]; then
    last_epoch=$(date -u -d "$(cat "$alert_file")" +%s 2>/dev/null || echo 0)
    now_epoch=$(date -u +%s)
    elapsed_min=$(((now_epoch - last_epoch) / 60))
    if [ "$elapsed_min" -lt "$cooldown_min" ]; then
      return 1
    fi
  fi
  return 0
}

send_alert_if_allowed() {
  local msg="$1"
  if should_alert_now; then
    bash scripts/send_alert.sh "$msg"
    date -u +%FT%TZ > "$alert_file"
  fi
}

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

  madrid_date="$(TZ=Europe/Madrid date +%F)"
  madrid_weekday="$(TZ=Europe/Madrid date +%u)"
  csv_path="artifacts/csv/publicidadconcursal-${madrid_date}.csv"

  if [ -f "$csv_path" ]; then
    data_rows=$(( $(wc -l < "$csv_path") - 1 ))
    if [ "$data_rows" -lt 0 ]; then
      data_rows=0
    fi

    if [ "$madrid_weekday" -ge 1 ] && [ "$madrid_weekday" -le 5 ] && [ "$data_rows" -eq 0 ]; then
      msg="Warning: weekday run (${madrid_date}, Europe/Madrid) loaded 0 rows. Please review source availability."
      send_alert_if_allowed "$msg"
      echo "$msg" > "$error_file"
    fi
  fi

  echo "daily run succeeded"
  exit 0
fi

failures=$((failures + 1))
echo "$failures" > "$fails_file"
echo "failed" > "$status_file"
echo "run-and-load-today failed after retry" > "$error_file"

if [ "$failures" -ge 2 ]; then
  msg="Reminder: publicidad-concursal daily pipeline has failed ${failures} times consecutively (with one retry each run). Last failure at ${now}."
  send_alert_if_allowed "$msg"
fi

exit 1
