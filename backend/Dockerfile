FROM python:3.13-slim-bookworm

RUN useradd -m appuser

COPY --from=ghcr.io/astral-sh/uv:0.11.14 /uv /uvx /bin/

WORKDIR /app

ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./

RUN uv sync

ENV PATH="/app/.venv/bin:$PATH"

COPY --chown=appuser:appuser . .
