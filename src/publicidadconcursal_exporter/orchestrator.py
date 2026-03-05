from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path
from typing import Callable

from publicidadconcursal_exporter.automation.browser_use_runner import BrowserUseRunner
from publicidadconcursal_exporter.automation.playwright_runner import PlaywrightRunner
from publicidadconcursal_exporter.config import ExportConfig
from publicidadconcursal_exporter.logging_utils import setup_logger
from publicidadconcursal_exporter.parsing.normalize import (
    EmptyExportError,
    export_daily_csv,
    load_export,
    normalize_dataframe,
)


def run_export(config: ExportConfig) -> tuple[Path, Path]:
    artifacts_base = config.output_dir / "artifacts"
    logger = setup_logger(artifacts_base)
    raw_dir = artifacts_base / "raw" / config.run_date.isoformat()
    raw_dir.mkdir(parents=True, exist_ok=True)

    runner = _resolve_runner(config.engine)
    raw_file = _retry_automation(config, raw_dir, runner.run, logger.info)
    logger.info("Raw export guardado en %s", raw_file)

    df = load_export(raw_file)
    normalized = normalize_dataframe(df, config.run_date)
    if normalized.empty:
        raise EmptyExportError("CSV final vacío")

    csv_output = artifacts_base / "csv" / f"publicidadconcursal-{config.run_date.isoformat()}.csv"
    export_daily_csv(normalized, csv_output)
    logger.info("CSV normalizado guardado en %s (%s filas)", csv_output, len(normalized))

    return raw_file, csv_output


def _resolve_runner(engine: str) -> BrowserUseRunner | PlaywrightRunner | "AutoRunner":
    if engine == "browser-use":
        return BrowserUseRunner()
    if engine == "playwright":
        return PlaywrightRunner()

    return AutoRunner()


class AutoRunner:
    def __init__(self) -> None:
        self._browser_use = BrowserUseRunner()
        self._playwright = PlaywrightRunner()

    def run(self, target_url: str, run_date: date, download_dir: Path, timeout_ms: int) -> Path:
        try:
            return self._browser_use.run(target_url, run_date, download_dir, timeout_ms)
        except Exception:
            return self._playwright.run(target_url, run_date, download_dir, timeout_ms)


def _retry_automation(
    config: ExportConfig,
    raw_dir: Path,
    automation_fn: Callable[[str, date, Path, int], Path],
    log: Callable[[str, object], None],
) -> Path:
    last_error: Exception | None = None
    for attempt in range(1, config.max_retries + 1):
        try:
            tmp_download = raw_dir / "tmp"
            tmp_download.mkdir(parents=True, exist_ok=True)
            raw_path = automation_fn(
                config.target_url,
                config.run_date,
                tmp_download,
                config.timeout_ms,
            )
            final_path = raw_dir / raw_path.name
            shutil.move(str(raw_path), final_path)
            return final_path
        except Exception as exc:
            last_error = exc
            log("Intento %s/%s falló: %s", attempt, config.max_retries, exc)

    raise RuntimeError("No se pudo completar la exportación tras reintentos") from last_error
