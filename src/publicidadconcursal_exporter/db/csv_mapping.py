from __future__ import annotations

import re
import unicodedata
from datetime import date
from typing import Any


def normalize_column_key(key: str) -> str:
    text = key.strip().lower().replace("º", "o").replace("ª", "a")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("n.o", "numero").replace("n°", "numero")
    text = text.replace("nº", "numero").replace("no ", "numero ")
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text)
    return text.strip("_")


def parse_date_raw(value: Any) -> tuple[str | None, date | None]:
    if value is None:
        return None, None
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return None, None

    for pattern in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            from datetime import datetime

            return text, datetime.strptime(text, pattern).date()
        except ValueError:
            continue

    return text, None


def map_payload_to_columns(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = {normalize_column_key(k): v for k, v in payload.items()}
    fecha_raw, fecha = parse_date_raw(normalized.get("fecha_resolucion"))

    return {
        "nif_sujeto": _to_str_or_none(normalized.get("nif_sujeto")),
        "sujeto": _to_str_or_none(normalized.get("sujeto")),
        "tipo_resolucion": _to_str_or_none(normalized.get("tipo_resolucion")),
        "fecha_resolucion_raw": fecha_raw,
        "fecha_resolucion": fecha,
        "numero_procedimiento_expediente": _to_str_or_none(
            normalized.get("numero_procedimiento_numero_expediente")
            or normalized.get("numero_procedimiento_expediente")
        ),
        "seccion": _to_str_or_none(normalized.get("seccion")),
    }


def _to_str_or_none(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return None
    return text
