from __future__ import annotations

import argparse
from pathlib import Path

from publicidadconcursal_exporter.config import DEFAULT_TARGET_URL, ExportConfig
from publicidadconcursal_exporter.date_utils import parse_cli_date
from publicidadconcursal_exporter.orchestrator import run_export


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="publicidadconcursal-export",
        description="Automatiza búsqueda por fecha y export diario de Publicidad Concursal.",
    )
    parser.add_argument("--date", dest="run_date", default=None, help="Fecha en formato YYYY-MM-DD")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL, help="URL objetivo")
    parser.add_argument("--output-dir", default=".", help="Directorio de salida")
    parser.add_argument(
        "--engine",
        choices=["auto", "browser-use", "playwright"],
        default="auto",
        help="Motor de automatización",
    )
    parser.add_argument("--max-retries", type=int, default=2, help="Reintentos de automatización")
    parser.add_argument("--timeout-ms", type=int, default=30_000, help="Timeout por paso en ms")
    return parser


def main() -> None:
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
