from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

DEFAULT_TARGET_URL = "https://www.publicidadconcursal.es/consulta-publicidad-concursal-new"


@dataclass(frozen=True)
class ExportConfig:
    target_url: str
    run_date: date
    output_dir: Path
    engine: str = "auto"
    max_retries: int = 2
    timeout_ms: int = 30_000
