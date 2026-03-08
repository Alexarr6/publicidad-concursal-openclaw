#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from publicidadconcursal_exporter.db.domain import CsvRecordIngest
from publicidadconcursal_exporter.db.repository import CsvRecordRepository
from publicidadconcursal_exporter.db.session import create_engine_from_env


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Load normalized CSV into PostgreSQL")
    parser.add_argument("--date", required=True, help="Run date YYYY-MM-DD")
    parser.add_argument("--csv-path", default=None, help="Explicit CSV path")
    parser.add_argument("--artifacts-dir", default="artifacts/csv", help="CSV artifact directory")
    return parser


def _canonical_payload(row: dict[str, object]) -> str:
    return json.dumps(row, ensure_ascii=False, sort_keys=True, default=str)


def _row_hash(payload: dict[str, object]) -> str:
    return hashlib.sha256(_canonical_payload(payload).encode("utf-8")).hexdigest()


def main() -> None:
    args = build_parser().parse_args()
    run_date = date.fromisoformat(args.date)

    csv_path = (
        Path(args.csv_path)
        if args.csv_path
        else Path(args.artifacts_dir) / f"publicidadconcursal-{args.date}.csv"
    )
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)
    records: list[CsvRecordIngest] = []
    for idx, row in enumerate(df.to_dict(orient="records"), start=1):
        payload = {str(k): v for k, v in row.items()}
        records.append(
            CsvRecordIngest(
                run_date=run_date,
                source_file=str(csv_path),
                row_number=idx,
                row_hash=_row_hash(payload),
                payload=payload,
            )
        )

    engine = create_engine_from_env()
    with Session(engine) as session:
        repo = CsvRecordRepository(session)
        before = repo.count_for_date(run_date)
        summary = repo.upsert_many(records)
        after = repo.count_for_date(run_date)

    print(
        json.dumps(
            {
                "date": args.date,
                "csv": str(csv_path),
                "rows": len(records),
                "before": before,
                "after": after,
                "inserted": summary.inserted,
                "updated": summary.updated,
                "unchanged": summary.unchanged,
                "errors": summary.errors,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
