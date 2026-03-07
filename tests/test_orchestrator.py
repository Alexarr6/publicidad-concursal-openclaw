from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from publicidadconcursal_exporter.config import ExportConfig
from publicidadconcursal_exporter.models import ExportOutput, ExportRequest, ExportTestSpec
from publicidadconcursal_exporter.orchestrator import run_export


class FakeRunner:
    def run(self, request: ExportRequest, test: ExportTestSpec) -> ExportOutput:
        del test
        raw = request.download_dir / f"raw-{request.run_date.isoformat()}.csv"
        pd.DataFrame(
            {
                "fecha": ["05/03/2026", "01/03/2026"],
                "expediente": [2, 1],
            }
        ).to_csv(raw, index=False)
        return ExportOutput(file_path=raw, plan_name="search_and_export")


def test_run_export_generates_raw_and_sorted_csv(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        "publicidadconcursal_exporter.orchestrator._resolve_runner", lambda _engine: FakeRunner()
    )

    cfg = ExportConfig(
        target_url="https://example.com",
        run_date=date(2026, 3, 5),
        output_dir=tmp_path,
        engine="browser-use",
    )

    raw, csv = run_export(cfg)

    assert raw.exists()
    assert csv.exists()

    out = pd.read_csv(csv)
    assert len(out) == 2
    assert out["expediente"].tolist() == [1, 2]


class FlakyRunner:
    def __init__(self) -> None:
        self.calls = 0

    def run(self, request: ExportRequest, test: ExportTestSpec) -> ExportOutput:
        del test
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("transient failure")
        raw = request.download_dir / f"raw-{request.run_date.isoformat()}.csv"
        pd.DataFrame({"fecha": ["05/03/2026"], "expediente": [1]}).to_csv(raw, index=False)
        return ExportOutput(file_path=raw, plan_name="search_and_export")


def test_run_export_retries_and_succeeds(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    flaky = FlakyRunner()
    monkeypatch.setattr(
        "publicidadconcursal_exporter.orchestrator._resolve_runner", lambda _engine: flaky
    )

    cfg = ExportConfig(
        target_url="https://example.com",
        run_date=date(2026, 3, 5),
        output_dir=tmp_path,
        engine="browser-use",
        max_retries=2,
    )

    raw, csv = run_export(cfg)

    assert raw.exists()
    assert csv.exists()
    assert flaky.calls == 2
