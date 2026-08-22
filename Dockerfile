FROM python:3.12-slim

# Install uv binary from official Astral image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# 1. Dependencies installed from pyproject.toml + uv.lock alone with BuildKit cache mount
# This layer only invalidates when a dependency actually changes, not on source edits.
COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

# 2. Copy source code and install project
COPY questions.txt app.py ./
COPY nlp_sql_engine/ ./nlp_sql_engine/
COPY scripts/ ./scripts/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen && python scripts/setup_db.py

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "nlp_sql_engine.web.app:app", "--host", "0.0.0.0", "--port", "8000"]

