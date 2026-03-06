# AGENTS.md - publicidad-concursal-openclaw

## Mission
Automatizar búsqueda por fecha y export diario de publicidadconcursal.es con salida CSV confiable.

## Scope Rules
- Mantener cambios dentro de este repositorio.
- No tocar sistemas externos salvo lo mínimo para la automatización web requerida.
- No introducir secretos/credenciales en código o commits.

## Required Quality Gates
- `uv run ruff check .`
- `uv run pytest`
- `uv run mypy .` (si está configurado)
- `pre-commit run --all-files`

## Required Deliverables
- CLI con `--date YYYY-MM-DD` (default: today)
- Export raw del día + CSV normalizado ordenado por fecha
- Validación de salida no vacía
- `.pre-commit-config.yaml` funcional
- README/operational docs con comandos exactos

## Delivery Format
- Branch: `feature/publicidadconcursal-date-export`
- Conventional commits (`feat|fix|chore|docs|test`)
- Resumen final obligatorio: cambios, evidencia de tests, cómo ejecutar, limitaciones

## Safety Defaults
- Si hay ambigüedad, declarar supuestos explícitos.
- Si hay bloqueo por UI/web, documentar fallback y workaround manual reproducible.
