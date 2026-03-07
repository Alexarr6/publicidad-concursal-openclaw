# publicidad-concursal-openclaw

Automates date-based search in Publicidad Concursal, downloads the daily export, and produces a normalized CSV sorted by date.

## Requirements

- Python 3.11+
- `uv` recommended for project commands
- browser-use runtime dependencies

## Installation

```bash
uv sync --all-extras
```

## CLI Usage

```bash
uv run publicidadconcursal-export --date 2026-03-05 \
  --target-url https://www.publicidadconcursal.es/consulta-publicidad-concursal-new \
  --engine browser-use \
  --output-dir .
```

Key parameters:

- `--date YYYY-MM-DD` (default: today)
- `--target-url` target URL (official URL by default)
- `--engine browser-use` (native mode only)
- `--max-retries` retries for transient UI/network failures
- `--timeout-ms` per-step timeout

## Implemented Flow

1. Run browser-use native automation using explicit plan files:
   - `src/publicidadconcursal_exporter/automation/plans/search_and_export.md`
   - `src/publicidadconcursal_exporter/automation/plans/verify_download.md`
2. Store raw artifact in `artifacts/raw/YYYY-MM-DD/`.
3. Parse and normalize with pandas.
4. Generate daily CSV in `artifacts/csv/`, sorted by date.

## Typed Data Models

The automation contract now uses explicit typed models:

- `ExportRequest`
- `ExportTestSpec`
- `ExportOutput`
- `ExportReport`

All are defined in `src/publicidadconcursal_exporter/models.py`.

## Validations

- If raw export is empty: explicit error.
- If normalized CSV is empty: explicit error.
- Sorts by detected date column (`fecha`, `fecha_publicacion`, `fecha de publicación`, `date`, and similar variants).

## Quality

Contract verification commands:

```bash
uv pip check
uv run pytest -q
uv run ruff check . && uv run mypy src
```

## Pre-commit

Install:

```bash
uv run pre-commit install
```

Run manually:

```bash
uv run pre-commit run --all-files
```

Included hooks:

- hygiene (`trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `check-added-large-files`)
- safety (`detect-private-key`, `check-merge-conflict`)
- lint/format (`ruff`, `ruff-format`)
- type checking (`mypy`)

## Manual Workaround (if site automation is blocked)

1. Open `https://www.publicidadconcursal.es/consulta-publicidad-concursal-new`.
2. Go to date-based search.
3. Enter the target day date (`DD/MM/YYYY` usually works).
4. Click `Buscar`, then `Exportar`.
5. Save the downloaded file into `artifacts/raw/YYYY-MM-DD/`.
6. Normalize it with:

```bash
uv run python -m publicidadconcursal_exporter.manual_normalize \
  --date 2026-03-05 \
  --raw-path artifacts/raw/2026-03-05/archivo_descargado.csv \
  --output-dir .
```

## Context7 REST Wrapper (local workflow)

This repository includes a small Context7 REST wrapper for local coder usage, without MCP client dependency.

Endpoints expected by the wrapper:

- `GET /context7/search?q=...`
- `GET /context7/fetch?id=...`

Run from repo:

```bash
uv run publicidadconcursal-context7 search --q "browser-use agent run"
uv run publicidadconcursal-context7 fetch --id "doc-123"
```

Optional flags:

- `--base-url` (default: `http://127.0.0.1:3000`)
- `--timeout-s` (default: `6.0`)
- `--max-retries` (default: `2`)

Output format is deterministic JSON:

- `sources[]` with `{title, url}`
- `snippets[]`
- `retrieved_at`

## Project Structure

- `src/publicidadconcursal_exporter/automation/`: native browser-use automation + plans
- `src/publicidadconcursal_exporter/context7_client.py`: Context7 REST wrapper client
- `src/publicidadconcursal_exporter/context7_cli.py`: local CLI tool for Context7 wrapper
- `src/publicidadconcursal_exporter/parsing/`: parsing and normalization
- `src/publicidadconcursal_exporter/models.py`: typed contracts for request/test/output/report
- `src/publicidadconcursal_exporter/orchestrator.py`: main pipeline
- `tests/`: unit tests
