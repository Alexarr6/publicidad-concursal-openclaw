from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Protocol


class AutomationRunner(Protocol):
    def run(self, target_url: str, run_date: date, download_dir: Path, timeout_ms: int) -> Path:
        """Run date search + export and return downloaded file path."""
