# publicidad-concursal-openclaw

Automates date-based search in Publicidad Concursal, downloads the daily export, and produces a normalized CSV sorted by date.

## Requirements

- Python 3.11+
- `uv` recommended for project commands
- Browser for Playwright (`playwright install chromium`)

## Installation

```bash
uv sync --all-extras
uv run playwright install chromium
```

## CLI Usage

```bash
uv run publicidadconcursal-export --date 2026-03-05 \
  --target-url https://www.publicidadconcursal.es/consulta-publicidad-concursal-new \
  --engine auto \
  --output-dir .
```

Key parameters:

- `--date YYYY-MM-DD` (default: today)
- `--target-url` target URL (official URL by default)
- `--engine auto|browser-use|playwright`
- `--max-retries` retries for transient UI/network failures
- `--timeout-ms` per-step timeout

## Implemented Flow

1. Click date-based search.
2. Fill the date with supported formats (`YYYY-MM-DD`, `DD/MM/YYYY`, `DD-MM-YYYY`).
3. Click `Buscar`.
4. Click `Exportar`.
5. Store raw artifact in `artifacts/raw/YYYY-MM-DD/`.
6. Parse and normalize with pandas.
7. Generate daily CSV in `artifacts/csv/`, sorted by date.

## Validations

- If raw export is empty: explicit error.
- If normalized CSV is empty: explicit error.
- Sorts by detected date column (`fecha`, `fecha_publicacion`, `fecha de publicación`, `date`, and similar variants).

## Quality

Contract verification commands:

```bash
uv run ruff check .
uv run pytest
uv run mypy .
uv run pre-commit run --all-files
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

## Manual Workaround (if automation is blocked by the site)

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

## browser-use Integration Note

- The `browser-use` engine is currently a compatibility-gated runner.
- It validates that `browser_use` is installed, then executes the existing Playwright-based deterministic flow.
- This keeps behavior stable while preserving an explicit dependency path for future native browser-use agent migration.

## Project Structure

- `src/publicidadconcursal_exporter/automation/`: automation runners
- `src/publicidadconcursal_exporter/parsing/`: parsing and normalization
- `src/publicidadconcursal_exporter/orchestrator.py`: main pipeline
- `tests/`: unit tests
