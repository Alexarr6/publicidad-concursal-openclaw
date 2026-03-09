#!/usr/bin/env bash
set -euo pipefail

DATE_INPUT="${1:-}"
DATE_TO_USE="${DATE_INPUT:-$(TZ=Europe/Madrid date +%F)}"

echo "[smoke] DATE=${DATE_TO_USE}"

make db-up
make db-init
make db-load DATE="${DATE_TO_USE}"

DB_USER="${POSTGRES_USER:-postgres}"
DB_NAME="${POSTGRES_DB:-publicidad}"

TABLE_OK=$(docker compose exec -T postgres psql -U "$DB_USER" -d "$DB_NAME" -Atc "SELECT to_regclass('public.csv_records') IS NOT NULL;")
if [ "$TABLE_OK" != "t" ]; then
  echo "[smoke] FAIL: csv_records table not found"
  exit 1
fi

TOTAL=$(docker compose exec -T postgres psql -U "$DB_USER" -d "$DB_NAME" -Atc "SELECT COUNT(*) FROM csv_records;")
echo "[smoke] csv_records total=${TOTAL}"

if ! [[ "$TOTAL" =~ ^[0-9]+$ ]]; then
  echo "[smoke] FAIL: invalid COUNT output"
  exit 1
fi

echo "[smoke] PASS"
