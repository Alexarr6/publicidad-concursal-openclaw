from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import httpx


@dataclass(frozen=True)
class Context7Source:
    title: str
    url: str


@dataclass(frozen=True)
class Context7Result:
    sources: list[Context7Source]
    snippets: list[str]
    retrieved_at: str


class Context7Error(RuntimeError):
    """Raised when Context7 wrapper cannot complete a request."""


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _extract_payload(data: dict[str, Any]) -> Context7Result:
    raw_sources = data.get("sources", [])
    raw_snippets = data.get("snippets", [])

    sources: list[Context7Source] = []
    for item in raw_sources:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        url = str(item.get("url", "")).strip()
        if title and url:
            sources.append(Context7Source(title=title, url=url))

    snippets = [str(item).strip() for item in raw_snippets if str(item).strip()]

    return Context7Result(sources=sources, snippets=snippets, retrieved_at=_now_iso())


class Context7Client:
    """Small REST wrapper around a Context7-compatible HTTP service."""

    def __init__(
        self,
        base_url: str,
        timeout_s: float = 6.0,
        max_retries: int = 2,
        retry_delay_s: float = 0.4,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s
        self.max_retries = max(0, max_retries)
        self.retry_delay_s = max(0.0, retry_delay_s)

    def search(self, query: str) -> Context7Result:
        if not query.strip():
            raise Context7Error("Query cannot be empty")
        data = self._request_json("/context7/search", params={"q": query})
        return _extract_payload(data)

    def fetch(self, doc_id: str) -> Context7Result:
        if not doc_id.strip():
            raise Context7Error("Document id cannot be empty")
        data = self._request_json("/context7/fetch", params={"id": doc_id})
        return _extract_payload(data)

    def _request_json(self, path: str, params: dict[str, str]) -> dict[str, Any]:
        last_error: Exception | None = None

        for attempt in range(1, self.max_retries + 2):
            try:
                with httpx.Client(timeout=self.timeout_s) as client:
                    response = client.get(f"{self.base_url}{path}", params=params)
                response.raise_for_status()
                payload = response.json()
                if not isinstance(payload, dict):
                    raise Context7Error("Context7 returned a non-object JSON response")
                return payload
            except (httpx.HTTPError, ValueError, Context7Error) as exc:
                last_error = exc
                if attempt > self.max_retries:
                    break
                import time

                time.sleep(self.retry_delay_s)

        raise Context7Error(f"Context7 request failed for {path}: {last_error}")
