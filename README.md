# publicidad-concursal-openclaw

Automatiza la búsqueda por fecha en Publicidad Concursal, descarga el export del día y genera un CSV normalizado ordenado por fecha.

## Requisitos

- Python 3.11+
- `uv` recomendado (comandos del proyecto)
- Navegador para Playwright (`playwright install chromium`)

## Instalación

```bash
uv sync --all-extras
uv run playwright install chromium
```

## Uso CLI

```bash
uv run publicidadconcursal-export --date 2026-03-05 \
  --target-url https://www.publicidadconcursal.es/consulta-publicidad-concursal-new \
  --engine auto \
  --output-dir .
```

Parámetros clave:

- `--date YYYY-MM-DD` (default: hoy)
- `--target-url` URL objetivo (default oficial)
- `--engine auto|browser-use|playwright`
- `--max-retries` reintentos ante errores de UI/red
- `--timeout-ms` timeout por paso

## Flujo implementado

1. Click en búsqueda por fecha.
2. Rellenar fecha en formatos compatibles (`YYYY-MM-DD`, `DD/MM/YYYY`, `DD-MM-YYYY`).
3. Click en `Buscar`.
4. Click en `Exportar`.
5. Guardado de artefacto raw en `artifacts/raw/YYYY-MM-DD/`.
6. Parseo + normalización con pandas.
7. Generación de CSV diario en `artifacts/csv/` ordenado por fecha.

## Validaciones

- Si export raw está vacío: error explícito.
- Si CSV normalizado queda vacío: error explícito.
- Ordena por columna de fecha detectada (`fecha`, `fecha_publicacion`, `fecha de publicación`, `date`, etc.).

## Calidad

Comandos del contrato:

```bash
uv run ruff check .
uv run pytest
uv run mypy .
uv run pre-commit run --all-files
```

## Pre-commit

Instalación:

```bash
uv run pre-commit install
```

Ejecución manual:

```bash
uv run pre-commit run --all-files
```

Hooks incluidos:

- hygiene (`trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `check-added-large-files`)
- safety (`detect-private-key`, `check-merge-conflict`)
- lint/formato (`ruff`, `ruff-format`)
- tipado (`mypy`)

## Workaround manual (si la web bloquea automatización)

1. Abrir `https://www.publicidadconcursal.es/consulta-publicidad-concursal-new`.
2. Ir a búsqueda por fecha.
3. Introducir fecha del día objetivo (`DD/MM/YYYY` normalmente funciona).
4. Pulsar `Buscar` y luego `Exportar`.
5. Guardar archivo en `artifacts/raw/YYYY-MM-DD/`.
6. Normalizar con:

```bash
uv run python -m publicidadconcursal_exporter.manual_normalize \
  --date 2026-03-05 \
  --raw-path artifacts/raw/2026-03-05/archivo_descargado.csv \
  --output-dir .
```

## Estructura

- `src/publicidadconcursal_exporter/automation/` runners de automatización
- `src/publicidadconcursal_exporter/parsing/` parseo y normalización
- `src/publicidadconcursal_exporter/orchestrator.py` pipeline principal
- `tests/` cobertura unitaria
