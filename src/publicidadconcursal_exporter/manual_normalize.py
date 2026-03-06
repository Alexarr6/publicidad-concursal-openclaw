from __future__ import annotations

import argparse
from pathlib import Path

from publicidadconcursal_exporter.date_utils import parse_cli_date
from publicidadconcursal_exporter.parsing.normalize import (
    export_daily_csv,
    load_export,
    normalize_dataframe,
)


def main() -> None:
    """Normalize an already downloaded raw export into the daily CSV format."""

    parser = argparse.ArgumentParser(
        description="Normalize a manually downloaded Publicidad Concursal export"
    )
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--raw-path", required=True, help="Path to the downloaded raw export")
    parser.add_argument("--output-dir", default=".", help="Base output directory")
    args = parser.parse_args()

    run_date = parse_cli_date(args.date)
    raw_path = Path(args.raw_path).resolve()
    output_dir = Path(args.output_dir).resolve()

    df = load_export(raw_path)
    normalized = normalize_dataframe(df, run_date)

    out_path = output_dir / "artifacts" / "csv" / f"publicidadconcursal-{run_date.isoformat()}.csv"
    export_daily_csv(normalized, out_path)
    print(f"CSV={out_path}")


if __name__ == "__main__":
    main()
