from __future__ import annotations

import os

from sqlalchemy import Engine, create_engine, text

from publicidadconcursal_exporter.db.models import Base


def get_database_url_from_env() -> str:
    return os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/publicidad")


def create_engine_from_env() -> Engine:
    return create_engine(get_database_url_from_env(), future=True)


def ensure_schema(engine: Engine) -> None:
    Base.metadata.create_all(bind=engine)

    alter_statements = [
        "ALTER TABLE csv_records ADD COLUMN IF NOT EXISTS nif_sujeto VARCHAR(64)",
        "ALTER TABLE csv_records ADD COLUMN IF NOT EXISTS sujeto VARCHAR(512)",
        "ALTER TABLE csv_records ADD COLUMN IF NOT EXISTS tipo_resolucion VARCHAR(256)",
        "ALTER TABLE csv_records ADD COLUMN IF NOT EXISTS fecha_resolucion_raw VARCHAR(32)",
        "ALTER TABLE csv_records ADD COLUMN IF NOT EXISTS fecha_resolucion DATE",
        (
            "ALTER TABLE csv_records ADD COLUMN IF NOT EXISTS "
            "numero_procedimiento_expediente VARCHAR(256)"
        ),
        "ALTER TABLE csv_records ADD COLUMN IF NOT EXISTS seccion VARCHAR(128)",
    ]

    with engine.begin() as conn:
        for stmt in alter_statements:
            conn.execute(text(stmt))
