from __future__ import annotations

import shutil
from collections.abc import Callable
from pathlib import Path

from publicidadconcursal_exporter.automation.base import AutomationRunner
from publicidadconcursal_exporter.automation.browser_use_runner import BrowserUseRunner
from publicidadconcursal_exporter.config import ExportConfig
from publicidadconcursal_exporter.logging_utils import setup_logger
from publicidadconcursal_exporter.models import (
    ExportOutput,
    ExportReport,
    ExportRequest,
    ExportTestSpec,
    NormalizedRecordSchema,
)
from publicidadconcursal_exporter.parsing.normalize import (
    EmptyExportError,
    export_daily_csv,
    load_export,
    normalize_dataframe,
)


def run_export(config: ExportConfig) -> tuple[Path, Path]:
    """Run automation + normalization and return `(raw_file, normalized_csv)` paths."""

    artifacts_base = config.output_dir / "artifacts"
    logger = setup_logger(artifacts_base)
    raw_dir = artifacts_base / "raw" / config.run_date.isoformat()
    raw_dir.mkdir(parents=True, exist_ok=True)

    runner = _resolve_runner(config.engine)
    request = ExportRequest(
        target_url=config.target_url,
        run_date=config.run_date,
        download_dir=raw_dir / "tmp",
        timeout_ms=config.timeout_ms,
    )
    test = ExportTestSpec()

    output = _retry_automation(config, request, test, runner.run, logger.info)
    report = ExportReport(
        request=request,
        test=test,
        schema=NormalizedRecordSchema(),
        output=output,
    )

    raw_file = _move_to_raw_dir(report.output, raw_dir)
    logger.info("Raw export saved to %s", raw_file)
    logger.info("Automation plan=%s evidence=%s", report.output.plan_name, report.output.evidence)

    df = load_export(raw_file)
    normalized = normalize_dataframe(df, config.run_date)
    if normalized.empty:
        raise EmptyExportError("Final CSV is empty")

    csv_output = artifacts_base / "csv" / f"publicidadconcursal-{config.run_date.isoformat()}.csv"
    export_daily_csv(normalized, csv_output)
    logger.info("Normalized CSV saved to %s (%s rows)", csv_output, len(normalized))

    return raw_file, csv_output


def _resolve_runner(_engine: str) -> AutomationRunner:
    """Instantiate the browser-use native runner."""

    return BrowserUseRunner()


def _retry_automation(
    config: ExportConfig,
    request: ExportRequest,
    test: ExportTestSpec,
    automation_fn: Callable[[ExportRequest, ExportTestSpec], ExportOutput],
    log: Callable[..., None],
) -> ExportOutput:
    """Retry automation and return the output metadata on success."""

    last_error: Exception | None = None
    for attempt in range(1, config.max_retries + 1):
        try:
            request.download_dir.mkdir(parents=True, exist_ok=True)
            return automation_fn(request, test)
        except Exception as exc:
            last_error = exc
            log("Attempt %s/%s failed: %s", attempt, config.max_retries, exc)

    message = (
        f"Could not complete export after {config.max_retries} attempts. "
        f"Last error: {last_error}"
    )
    raise RuntimeError(message) from last_error


def _move_to_raw_dir(output: ExportOutput, raw_dir: Path) -> Path:
    final_path = raw_dir / output.file_path.name
    shutil.move(str(output.file_path), final_path)
    return final_path
