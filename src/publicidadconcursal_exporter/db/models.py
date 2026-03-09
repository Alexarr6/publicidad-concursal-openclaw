from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import JSON, Date, DateTime, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class CsvRecord(Base):
    __tablename__ = "csv_records"
    __table_args__ = (
        UniqueConstraint("run_date", "row_hash", name="uq_csv_records_run_date_row_hash"),
        Index("ix_csv_records_run_date_nif_sujeto", "run_date", "nif_sujeto"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_date: Mapped[date] = mapped_column(Date, index=True)
    source_file: Mapped[str] = mapped_column(String(512))
    row_number: Mapped[int] = mapped_column(Integer)
    row_hash: Mapped[str] = mapped_column(String(64), index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)

    nif_sujeto: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    sujeto: Mapped[str | None] = mapped_column(String(512), nullable=True)
    tipo_resolucion: Mapped[str | None] = mapped_column(String(256), nullable=True)
    fecha_resolucion_raw: Mapped[str | None] = mapped_column(String(32), nullable=True)
    fecha_resolucion: Mapped[date | None] = mapped_column(Date, nullable=True)
    numero_procedimiento_expediente: Mapped[str | None] = mapped_column(String(256), nullable=True)
    seccion: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
