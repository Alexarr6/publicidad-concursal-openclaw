from datetime import date

from publicidadconcursal_exporter.db.csv_mapping import (
    map_payload_to_columns,
    normalize_column_key,
    parse_date_raw,
)


def test_normalize_column_key_accents_symbols() -> None:
    assert normalize_column_key("Nº procedimiento / Nº expediente") == (
        "numero_procedimiento_numero_expediente"
    )
    assert normalize_column_key("Tipo resolución") == "tipo_resolucion"


def test_parse_date_raw_valid_and_invalid() -> None:
    raw, parsed = parse_date_raw("08/03/2026")
    assert raw == "08/03/2026"
    assert parsed == date(2026, 3, 8)

    raw_bad, parsed_bad = parse_date_raw("no-date")
    assert raw_bad == "no-date"
    assert parsed_bad is None


def test_map_payload_to_columns() -> None:
    mapped = map_payload_to_columns(
        {
            "NIF sujeto": "A123",
            "Sujeto": "Empresa X",
            "Tipo resolución": "Auto",
            "Fecha resolución": "08/03/2026",
            "Nº procedimiento / Nº expediente": "ABC/2026",
            "Sección": "Primera",
        }
    )

    assert mapped["nif_sujeto"] == "A123"
    assert mapped["tipo_resolucion"] == "Auto"
    assert mapped["fecha_resolucion_raw"] == "08/03/2026"
    assert mapped["fecha_resolucion"] == date(2026, 3, 8)
    assert mapped["numero_procedimiento_expediente"] == "ABC/2026"
