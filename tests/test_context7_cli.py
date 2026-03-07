from __future__ import annotations

import json

import pytest

from publicidadconcursal_exporter.context7_cli import build_parser, main
from publicidadconcursal_exporter.context7_client import Context7Result, Context7Source


def test_parser_has_search_and_fetch() -> None:
    parser = build_parser()
    args = parser.parse_args(["search", "--q", "browser-use"])
    assert args.command == "search"
    assert args.q == "browser-use"

    args = parser.parse_args(["fetch", "--id", "doc-123"])
    assert args.command == "fetch"
    assert args.doc_id == "doc-123"


def test_main_prints_structured_json(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = Context7Result(
        sources=[Context7Source(title="t", url="u")],
        snippets=["s1"],
        retrieved_at="2026-03-07T16:00:00+00:00",
    )

    class FakeClient:
        def __init__(self, base_url: str, timeout_s: float, max_retries: int) -> None:
            del base_url, timeout_s, max_retries

        def search(self, q: str) -> Context7Result:
            del q
            return result

        def fetch(self, doc_id: str) -> Context7Result:
            del doc_id
            return result

    monkeypatch.setattr("publicidadconcursal_exporter.context7_cli.Context7Client", FakeClient)
    monkeypatch.setattr("sys.argv", ["prog", "search", "--q", "x"])

    main()

    out = capsys.readouterr().out.strip()
    payload = json.loads(out)
    assert payload["sources"][0]["title"] == "t"
    assert payload["snippets"] == ["s1"]
    assert payload["retrieved_at"] == "2026-03-07T16:00:00+00:00"
