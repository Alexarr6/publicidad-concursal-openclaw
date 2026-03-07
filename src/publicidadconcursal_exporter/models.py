from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class ExportRequest:
    """Input contract for one automation export run."""

    target_url: str
    run_date: date
    download_dir: Path
    timeout_ms: int


@dataclass(frozen=True)
class ExportTestSpec:
    """Checks that the browser automation should satisfy before returning output."""

    must_download_file: bool = True
    allowed_suffixes: tuple[str, ...] = (".csv", ".xls", ".xlsx")


@dataclass(frozen=True)
class NormalizedRecordSchema:
    """Deterministic normalized output schema requirements."""

    required_columns: tuple[str, ...] = ("run_date",)
    required_any_date_columns: tuple[str, ...] = (
        "fecha",
        "fecha_publicacion",
        "fecha publicación",
        "fecha de publicación",
        "publicacion_fecha",
        "date",
    )


@dataclass(frozen=True)
class ExportOutput:
    """Output produced by browser automation."""

    file_path: Path
    plan_name: str
    evidence: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ExportReport:
    """Execution report that can be logged or serialized."""

    request: ExportRequest
    test: ExportTestSpec
    schema: NormalizedRecordSchema
    output: ExportOutput
