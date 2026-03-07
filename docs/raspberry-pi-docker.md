# Raspberry Pi + Docker Operations

This project can run on Raspberry Pi 4/5 (64-bit) using Docker.

## Prerequisites

- Raspberry Pi OS 64-bit (recommended)
- Docker Engine + Docker Compose plugin
- At least 2 GB RAM (4 GB recommended)
- Free disk space: at least 2 GB for image build + artifacts

## Build and Sanity Checks

```bash
docker build -t publicidadconcursal-exporter:local .
docker compose config
docker compose run --rm app --help
```

## Run Daily Export in Container

```bash
docker compose run --rm app \
  --date 2026-03-05 \
  --target-url https://www.publicidadconcursal.es/consulta-publicidad-concursal-new \
  --output-dir /app
```

Artifacts are written to host `./artifacts` through the compose volume mount.

## Resource Notes for Pi

- Use a lightweight desktop or headless mode to reduce memory pressure.
- Keep only one export run at a time on low-memory devices.
- If browser automation is slow, increase `--timeout-ms` and retries.

## Troubleshooting

### Docker build is slow

- Run builds on wired network if possible.
- Rebuild without cache only when required:

```bash
docker build --no-cache -t publicidadconcursal-exporter:local .
```

### Permission problems writing artifacts

- Ensure project folder is writable by your current user.
- If needed, run docker commands with a user that owns the repo path.

### Export command times out

- Increase timeout and retries:

```bash
docker compose run --rm app --date 2026-03-05 --timeout-ms 60000 --max-retries 3 --output-dir /app
```
