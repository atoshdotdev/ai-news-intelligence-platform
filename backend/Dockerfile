FROM python:3.13-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.11.14 /uv /uvx /bin/

WORKDIR /app

RUN useradd -m appuser \
    && mkdir -p /cache/huggingface \
    && chown -R appuser:appuser /app /cache

ENV UV_LINK_MODE=copy
ENV PATH="/app/.venv/bin:$PATH"

USER appuser

COPY --chown=appuser:appuser pyproject.toml uv.lock ./

ARG UV_GROUP

RUN uv sync \
    --only-group ${UV_GROUP} \
    --no-install-project

COPY --chown=appuser:appuser . .
