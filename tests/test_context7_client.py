from __future__ import annotations

import httpx
import pytest

from publicidadconcursal_exporter.context7_client import Context7Client, Context7Error


class DummyResponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError("http error")

    def json(self) -> dict:
        return self._payload


class DummyClient:
    def __init__(self, responses: list[DummyResponse]) -> None:
        self._responses = responses

    def __enter__(self) -> DummyClient:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        return None

    def get(self, url: str, params: dict[str, str]) -> DummyResponse:
        del url, params
        return self._responses.pop(0)


def test_search_returns_structured_payload(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    payload = {
        "sources": [{"title": "browser-use docs", "url": "https://docs.browser-use.com"}],
        "snippets": ["Agent(task=...)", "await agent.run()"],
    }

    monkeypatch.setattr(
        "publicidadconcursal_exporter.context7_client.httpx.Client",
        lambda timeout: DummyClient([DummyResponse(payload)]),
    )

    client = Context7Client(base_url="http://localhost:3000")
    result = client.search("browser-use")

    assert result.sources[0].title == "browser-use docs"
    assert result.sources[0].url == "https://docs.browser-use.com"
    assert len(result.snippets) == 2
    assert result.retrieved_at


def test_fetch_retries_then_fails(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    class FailingClient:
        def __enter__(self) -> FailingClient:
            return self

        def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
            return None

        def get(self, url: str, params: dict[str, str]):  # type: ignore[no-untyped-def]
            del url, params
            raise httpx.ConnectError("boom")

    monkeypatch.setattr(
        "publicidadconcursal_exporter.context7_client.httpx.Client",
        lambda timeout: FailingClient(),
    )

    client = Context7Client(base_url="http://localhost:3000", max_retries=1, retry_delay_s=0)

    with pytest.raises(Context7Error, match="Context7 request failed"):
        client.fetch("doc-1")
