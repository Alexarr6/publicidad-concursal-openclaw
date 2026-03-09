from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class CsvRecordIngest(BaseModel):
    run_date: date
    source_file: str
    row_number: int = Field(ge=1)
    row_hash: str
    payload: dict[str, Any]

    nif_sujeto: str | None = None
    sujeto: str | None = None
    tipo_resolucion: str | None = None
    fecha_resolucion_raw: str | None = None
    fecha_resolucion: date | None = None
    numero_procedimiento_expediente: str | None = None
    seccion: str | None = None
