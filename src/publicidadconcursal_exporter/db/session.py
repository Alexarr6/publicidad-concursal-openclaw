from __future__ import annotations

import os

from sqlalchemy import Engine, create_engine

from publicidadconcursal_exporter.db.models import Base


def get_database_url_from_env() -> str:
    return os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/publicidad")


def create_engine_from_env() -> Engine:
    return create_engine(get_database_url_from_env(), future=True)


def ensure_schema(engine: Engine) -> None:
    Base.metadata.create_all(bind=engine)
