FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

COPY pyproject.toml uv.lock README.md /app/
COPY src /app/src

RUN uv sync --frozen --all-extras

RUN useradd --create-home --uid 10001 appuser
USER appuser

VOLUME ["/app/artifacts"]

ENTRYPOINT ["uv", "run", "publicidadconcursal-export"]
CMD ["--help"]
