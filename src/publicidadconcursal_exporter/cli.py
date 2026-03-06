from __future__ import annotations

import argparse
from pathlib import Path

from publicidadconcursal_exporter.config import DEFAULT_TARGET_URL, ExportConfig
from publicidadconcursal_exporter.date_utils import parse_cli_date
from publicidadconcursal_exporter.orchestrator import run_export


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser for daily export execution."""

    parser = argparse.ArgumentParser(
        prog="publicidadconcursal-export",
        description="Run date-based search and daily export for Publicidad Concursal.",
    )
    parser.add_argument("--date", dest="run_date", default=None, help="Date in YYYY-MM-DD format")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL, help="Target URL")
    parser.add_argument("--output-dir", default=".", help="Output directory")
    parser.add_argument(
        "--engine",
        choices=["auto", "browser-use", "playwright"],
        default="auto",
        help="Automation engine",
    )
    parser.add_argument("--max-retries", type=int, default=2, help="Number of retry attempts")
    parser.add_argument(
        "--timeout-ms", type=int, default=30_000, help="Per-step timeout in milliseconds"
    )
    return parser


def main() -> None:
    """Execute the export pipeline from CLI arguments."""

    parser = build_parser()
    args = parser.parse_args()

    config = ExportConfig(
        target_url=args.target_url,
        run_date=parse_cli_date(args.run_date),
        output_dir=Path(args.output_dir).resolve(),
        engine=args.engine,
        max_retries=max(1, args.max_retries),
        timeout_ms=max(5_000, args.timeout_ms),
    )

    raw_file, csv_file = run_export(config)
    print(f"RAW={raw_file}")
    print(f"CSV={csv_file}")


if __name__ == "__main__":
    main()
