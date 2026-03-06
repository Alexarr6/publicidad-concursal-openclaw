from __future__ import annotations

from datetime import date, datetime


def parse_cli_date(value: str | None) -> date:
    """Parse a CLI date value in YYYY-MM-DD format."""

    if not value:
        return date.today()
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("--date must use YYYY-MM-DD format") from exc


def to_site_date_formats(run_date: date) -> list[str]:
    """Return date variants accepted by the target website form."""

    return [
        run_date.strftime("%Y-%m-%d"),
        run_date.strftime("%d/%m/%Y"),
        run_date.strftime("%d-%m-%Y"),
    ]
