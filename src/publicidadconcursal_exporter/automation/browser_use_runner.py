from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any

from publicidadconcursal_exporter.automation.action_plan import load_plan
from publicidadconcursal_exporter.date_utils import to_site_date_formats
from publicidadconcursal_exporter.models import ExportOutput, ExportRequest, ExportTestSpec


class BrowserUseRunner:
    """Native browser-use execution runner (no Playwright fallback)."""

    def run(self, request: ExportRequest, test: ExportTestSpec) -> ExportOutput:
        self._run_agent(request)

        downloaded = self._pick_latest_download(request.download_dir)
        self._validate_output(downloaded, test)

        return ExportOutput(
            file_path=downloaded,
            plan_name="search_and_export",
            evidence=("browser-use-native", "verify_download"),
        )

    def _run_agent(self, request: ExportRequest) -> None:
        agent_cls, llm_cls = self._load_browser_use_classes()

        search_plan = load_plan("search_and_export")
        verify_plan = load_plan("verify_download")
        ddmmyyyy = to_site_date_formats(request.run_date)[1]

        task = (
            f"{search_plan}\n\n"
            f"Target URL: {request.target_url}\n"
            f"Run date (required format): {ddmmyyyy}\n"
            f"Download directory (must be used): {request.download_dir.resolve()}\n"
            f"Timeout budget per step: {request.timeout_ms}ms\n\n"
            f"{verify_plan}"
        )

        async def _exec() -> None:
            previous_download_path = os.environ.get("BROWSER_USE_DOWNLOAD_PATH")
            os.environ["BROWSER_USE_DOWNLOAD_PATH"] = str(request.download_dir.resolve())
            try:
                llm = llm_cls()
                agent = agent_cls(task=task, llm=llm)
                await agent.run()
            finally:
                if previous_download_path is None:
                    os.environ.pop("BROWSER_USE_DOWNLOAD_PATH", None)
                else:
                    os.environ["BROWSER_USE_DOWNLOAD_PATH"] = previous_download_path

        asyncio.run(_exec())

    def _load_browser_use_classes(self) -> tuple[type[Any], type[Any]]:
        try:
            from browser_use import Agent, ChatBrowserUse
        except ImportError as exc:
            raise RuntimeError(
                "browser-use is not installed. Install project web extras to run automation."
            ) from exc

        return Agent, ChatBrowserUse

    def _pick_latest_download(self, download_dir: Path) -> Path:
        if not download_dir.exists():
            raise RuntimeError(f"Download directory does not exist: {download_dir}")

        candidates = [path for path in download_dir.iterdir() if path.is_file()]
        if not candidates:
            raise RuntimeError("browser-use run finished without downloaded files")

        candidates.sort(key=lambda path: path.stat().st_mtime, reverse=True)
        return candidates[0]

    def _validate_output(self, file_path: Path, test: ExportTestSpec) -> None:
        if test.must_download_file and not file_path.exists():
            raise RuntimeError(f"Expected downloaded file not found: {file_path}")

        if file_path.suffix.lower() not in test.allowed_suffixes:
            allowed = ", ".join(test.allowed_suffixes)
            raise RuntimeError(
                "Downloaded file has unsupported extension "
                f"{file_path.suffix!r}; expected one of: {allowed}"
            )
