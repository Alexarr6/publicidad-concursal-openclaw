from __future__ import annotations

from contextlib import suppress
from datetime import date
from importlib.util import find_spec
from pathlib import Path
from typing import Any

from publicidadconcursal_exporter.date_utils import to_site_date_formats


class BrowserUseRunner:
    """Runner gated by `browser-use` availability, implemented with Playwright actions."""

    def run(self, target_url: str, run_date: date, download_dir: Path, timeout_ms: int) -> Path:
        if find_spec("browser_use") is None:
            raise RuntimeError("browser-use is not installed. Use --engine playwright.")

        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise RuntimeError(
                "browser-use compatibility flow requires playwright to be installed"
            ) from exc

        date_candidates = to_site_date_formats(run_date)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()
            page.goto(target_url, timeout=timeout_ms)
            self._run_ui_flow(page, date_candidates, timeout_ms)
            with page.expect_download(timeout=timeout_ms) as download_info:
                self._click_export(page)
            download = download_info.value
            default_name = f"publicidadconcursal-{run_date.isoformat()}.bin"
            safe_name = download.suggested_filename or default_name
            out_path = download_dir / safe_name
            download.save_as(str(out_path))
            context.close()
            browser.close()
            return out_path

    def _run_ui_flow(self, page: Any, date_candidates: list[str], timeout_ms: int) -> None:
        self._dismiss_cookie_banner(page)
        self._click_search_by_date(page)
        self._fill_date(page, date_candidates)
        page.get_by_role("button", name="Buscar").first.click(timeout=timeout_ms)

    def _dismiss_cookie_banner(self, page: Any) -> None:
        # Klaro cookie modal can intercept pointer events and block UI actions.
        # Try common consent actions and then wait for overlay to disappear.
        for label in [
            "Aceptar",
            "Aceptar todo",
            "Aceptar todas",
            "Aceptar cookies",
            "Rechazar",
            "Rechazar todo",
            "Guardar preferencias",
            "Entendido",
        ]:
            try:
                btn = page.get_by_role("button", name=label).first
                if btn.count() > 0:
                    btn.click(timeout=3000)
                    break
            except Exception:
                continue

        for selector in ["#klaro-cookie-notice", "#klaro .cm-bg"]:
            # If not found/hidden already, continue silently.
            with suppress(Exception):
                page.locator(selector).first.wait_for(state="hidden", timeout=5000)

    def _click_search_by_date(self, page: Any) -> None:
        for query in [
            "buscar por fecha",
            "búsqueda por fecha",
            "fecha",
        ]:
            loc = page.get_by_text(query, exact=False).first
            if loc.count() > 0:
                loc.click()
                return

    def _fill_date(self, page: Any, date_candidates: list[str]) -> None:
        for selector in ["input[type='date']", "input[name*='fecha']", "input[id*='fecha']"]:
            loc = page.locator(selector).first
            if loc.count() == 0:
                continue
            for candidate in date_candidates:
                try:
                    loc.fill(candidate)
                    return
                except Exception:
                    continue
        raise RuntimeError("Date input field not found for search")

    def _click_export(self, page: Any) -> None:
        for text in ["Exportar", "Descargar", "CSV", "Excel"]:
            loc = page.get_by_text(text, exact=False).first
            if loc.count() > 0:
                loc.click()
                return
        raise RuntimeError("Export button not found")
