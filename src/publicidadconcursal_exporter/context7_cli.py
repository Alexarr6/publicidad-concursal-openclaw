from __future__ import annotations

import argparse
import json

from publicidadconcursal_exporter.context7_client import Context7Client, Context7Error


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="publicidadconcursal-context7",
        description="Context7 REST wrapper for local coder workflow.",
    )
    parser.add_argument(
        "--base-url", default="http://127.0.0.1:3000", help="Context7 REST base URL"
    )
    parser.add_argument(
        "--timeout-s", type=float, default=6.0, help="Request timeout in seconds"
    )
    parser.add_argument(
        "--max-retries", type=int, default=2, help="Retry count on transient errors"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    search = subparsers.add_parser("search", help="Call /context7/search?q=...")
    search.add_argument("--q", required=True, help="Search query")

    fetch = subparsers.add_parser("fetch", help="Call /context7/fetch?id=...")
    fetch.add_argument("--id", dest="doc_id", required=True, help="Document id")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    client = Context7Client(
        base_url=args.base_url,
        timeout_s=max(1.0, args.timeout_s),
        max_retries=max(0, args.max_retries),
    )

    try:
        result = client.search(args.q) if args.command == "search" else client.fetch(args.doc_id)
    except Context7Error as exc:
        raise SystemExit(f"Context7 wrapper error: {exc}") from exc

    payload = {
        "sources": [{"title": item.title, "url": item.url} for item in result.sources],
        "snippets": result.snippets,
        "retrieved_at": result.retrieved_at,
    }
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
