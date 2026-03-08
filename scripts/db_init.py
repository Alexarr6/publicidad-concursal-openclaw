#!/usr/bin/env python3
from __future__ import annotations

from publicidadconcursal_exporter.db.session import create_engine_from_env, ensure_schema


def main() -> None:
    engine = create_engine_from_env()
    ensure_schema(engine)
    print("Schema initialized")


if __name__ == "__main__":
    main()
