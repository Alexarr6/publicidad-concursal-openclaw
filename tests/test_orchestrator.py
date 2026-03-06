from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from publicidadconcursal_exporter.config import ExportConfig
from publicidadconcursal_exporter.orchestrator import run_export


class FakeRunner:
    def run(self, target_url: str, run_date: date, download_dir: Path, timeout_ms: int) -> Path:
        del target_url, timeout_ms
        raw = download_dir / f"raw-{run_date.isoformat()}.csv"
        pd.DataFrame(
            {
                "fecha": ["05/03/2026", "01/03/2026"],
                "expediente": [2, 1],
            }
        ).to_csv(raw, index=False)
        return raw


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
        engine="auto",
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

    def run(self, target_url: str, run_date: date, download_dir: Path, timeout_ms: int) -> Path:
        del target_url, timeout_ms
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("fallo transitorio")
        raw = download_dir / f"raw-{run_date.isoformat()}.csv"
        pd.DataFrame({"fecha": ["05/03/2026"], "expediente": [1]}).to_csv(raw, index=False)
        return raw


def test_run_export_retries_and_succeeds(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    flaky = FlakyRunner()
    monkeypatch.setattr(
        "publicidadconcursal_exporter.orchestrator._resolve_runner", lambda _engine: flaky
    )

    cfg = ExportConfig(
        target_url="https://example.com",
        run_date=date(2026, 3, 5),
        output_dir=tmp_path,
        engine="auto",
        max_retries=2,
    )

    raw, csv = run_export(cfg)

    assert raw.exists()
    assert csv.exists()
    assert flaky.calls == 2
