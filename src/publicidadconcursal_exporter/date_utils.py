from __future__ import annotations

from datetime import date, datetime


def parse_cli_date(value: str | None) -> date:
    if not value:
        return date.today()
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("--date debe tener formato YYYY-MM-DD") from exc


def to_site_date_formats(run_date: date) -> list[str]:
    return [
        run_date.strftime("%Y-%m-%d"),
        run_date.strftime("%d/%m/%Y"),
        run_date.strftime("%d-%m-%Y"),
    ]
