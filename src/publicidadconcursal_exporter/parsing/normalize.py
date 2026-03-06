from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

DATE_CANDIDATES = {
    "fecha",
    "fecha_publicacion",
    "fecha publicación",
    "fecha de publicación",
    "publicacion_fecha",
    "date",
}


class EmptyExportError(RuntimeError):
    """Raised when a raw export cannot produce a usable normalized dataset."""


def load_export(raw_path: Path) -> pd.DataFrame:
    """Load raw export data from CSV/TXT/Excel with light format auto-detection."""

    suffix = raw_path.suffix.lower()
    if suffix in {".xls", ".xlsx"}:
        return pd.read_excel(raw_path)
    if suffix in {".csv", ".txt"}:
        return pd.read_csv(raw_path, sep=None, engine="python")

    try:
        return pd.read_csv(raw_path, sep=None, engine="python")
    except Exception:
        return pd.read_excel(raw_path)


def normalize_dataframe(df: pd.DataFrame, run_date: date) -> pd.DataFrame:
    """Normalize, sort, and annotate an export dataframe for daily output."""

    if df.empty:
        raise EmptyExportError("The exported file is empty")

    normalized = df.copy()
    normalized.columns = pd.Index([str(col).strip() for col in normalized.columns])

    date_col = _pick_date_column(normalized)
    if date_col is not None:
        normalized["_fecha_sort"] = pd.to_datetime(
            normalized[date_col], errors="coerce", dayfirst=True
        )
        normalized = normalized.sort_values("_fecha_sort", ascending=True, na_position="last")
        normalized = normalized.drop(columns=["_fecha_sort"])

    normalized["run_date"] = run_date.isoformat()
    normalized = normalized.reset_index(drop=True)

    if normalized.empty:
        raise EmptyExportError("Normalization produced zero rows")

    return normalized


def export_daily_csv(df: pd.DataFrame, output_path: Path) -> None:
    """Write normalized daily results to CSV."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def _pick_date_column(df: pd.DataFrame) -> str | None:
    """Return the first matching date-like column, if present."""

    for col in df.columns:
        if str(col).strip().lower() in DATE_CANDIDATES:
            return str(col)
    return None
