from __future__ import annotations

from typing import Protocol

from publicidadconcursal_exporter.models import ExportOutput, ExportRequest, ExportTestSpec


class AutomationRunner(Protocol):
    """Contract for automation runners used by the orchestrator."""

    def run(self, request: ExportRequest, test: ExportTestSpec) -> ExportOutput:
        """Run date search + export and return the downloaded output metadata."""
