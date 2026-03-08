# publicidad-concursal-openclaw

Automates date-based search in Publicidad Concursal, downloads the daily export, and produces a normalized CSV sorted by date.

## Requirements

- Python 3.11+
- `uv` recommended for project commands
- Browser for Playwright (`playwright install chromium`) when running browser automation on host
- Docker Engine + Compose plugin for containerized runs

## Installation (host)

```bash
uv sync --all-extras
uv run playwright install chromium
```

## CLI Usage (host)

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

## Docker Quickstart

Build image:

```bash
docker build -t publicidadconcursal-exporter:local .
```

Validate compose and CLI help:

```bash
docker compose config
docker compose run --rm app --help
```

Run export from container:

```bash
docker compose run --rm app \
  --date 2026-03-05 \
  --target-url https://www.publicidadconcursal.es/consulta-publicidad-concursal-new \
  --output-dir /app
```

The compose service mounts host `./artifacts` to `/app/artifacts` in the container.

## Make Workflow

### Phase 2 (PostgreSQL) quickstart

Start Postgres:

```bash
export UID=$(id -u)
export GID=$(id -g)
make db-up
```

Initialize schema:

```bash
make db-init
```

Run export + load into Postgres:

```bash
make run-and-load DATE=2026-03-08
make run-and-load-today
```

Idempotency check (run twice; row count must not increase):

```bash
make db-load DATE=2026-03-08
make db-load DATE=2026-03-08
```

Env vars:

- `DATABASE_URL` (default: `postgresql+psycopg://postgres:postgres@localhost:5432/publicidad`)
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` (compose defaults)
- alerting (used by `scripts/run_daily.sh`):
  - `ALERT_WEBHOOK_URL` (POST JSON `{text: ...}`)
  - or `ALERT_COMMAND` (executed via `bash -lc`, with `MSG` in env)
  - `ALERT_COOLDOWN_MINUTES` (default: 720)

Daily ops wrapper:

```bash
bash scripts/run_daily.sh
```

It retries once on failure and writes state to `artifacts/state/`.


Show available commands:

```bash
make help
```

Run environment checks (required by `make build`, `make run`, `make run-today`):

```bash
make preflight
```

Run build and export:

```bash
make build
make run DATE=2026-03-07
make run-today
```

What `preflight` validates:

- binaries: `git`, `gh`, `uv`, `docker`, `docker compose`
- Docker daemon availability
- `gh auth status` (warning by default in this phase)

If `gh auth status` fails and you need GitHub API access:

```bash
gh auth login
```

## Raspberry Pi Notes

See dedicated operations guide:

- `docs/raspberry-pi-docker.md`

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
uv pip check
uv run pytest -q
uv run ruff check .
uv run mypy src
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
