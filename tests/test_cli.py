from publicidadconcursal_exporter.cli import build_parser


def test_cli_has_date_option() -> None:
    parser = build_parser()
    args = parser.parse_args(["--date", "2026-03-05", "--engine", "browser-use"])
    assert args.run_date == "2026-03-05"
    assert args.engine == "browser-use"
