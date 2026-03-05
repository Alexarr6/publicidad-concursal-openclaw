from datetime import date

import pytest

from publicidadconcursal_exporter.date_utils import parse_cli_date, to_site_date_formats


def test_parse_cli_date_default_today() -> None:
    assert parse_cli_date(None) == date.today()


def test_parse_cli_date_valid() -> None:
    assert parse_cli_date("2026-03-05") == date(2026, 3, 5)


def test_parse_cli_date_invalid() -> None:
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        parse_cli_date("05/03/2026")


def test_to_site_date_formats() -> None:
    assert to_site_date_formats(date(2026, 3, 5)) == ["2026-03-05", "05/03/2026", "05-03-2026"]
