from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import logging

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from publicidadconcursal_exporter.db.domain import CsvRecordIngest
from publicidadconcursal_exporter.db.models import CsvRecord

logger = logging.getLogger(__name__)


@dataclass
class IngestSummary:
    inserted: int = 0
    updated: int = 0
    unchanged: int = 0
    errors: int = 0


class CsvRecordRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def count_for_date(self, run_date: date) -> int:
        stmt = select(func.count()).where(CsvRecord.run_date == run_date)
        return int(self.session.execute(stmt).scalar_one())

    def upsert_many(self, rows: list[CsvRecordIngest]) -> IngestSummary:
        summary = IngestSummary()
        if not rows:
            return summary

        for row in rows:
            try:
                existing = self.session.execute(
                    select(CsvRecord).where(
                        CsvRecord.run_date == row.run_date,
                        CsvRecord.row_hash == row.row_hash,
                    )
                ).scalar_one_or_none()

                if existing is None:
                    self.session.add(
                        CsvRecord(
                            run_date=row.run_date,
                            source_file=row.source_file,
                            row_number=row.row_number,
                            row_hash=row.row_hash,
                            payload=row.payload,
                        )
                    )
                    summary.inserted += 1
                    continue

                if existing.payload == row.payload:
                    summary.unchanged += 1
                    continue

                existing.payload = row.payload
                existing.source_file = row.source_file
                existing.row_number = row.row_number
                summary.updated += 1
            except Exception as exc:
                summary.errors += 1
                logger.exception("Failed to upsert row %s: %s", row.row_number, exc)

        self.session.commit()
        return summary
