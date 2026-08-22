FROM python:3.12-slim

# Install uv binary from official Astral image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1 \
    PORT=8000

WORKDIR /app

# 1. Install locked dependencies from pyproject.toml & uv.lock (cached layer)
COPY pyproject.toml uv.lock ./
RUN uv pip install --system -r pyproject.toml

# 2. Copy source code
COPY README.md questions.txt app.py ./
COPY nlp_sql_engine/ ./nlp_sql_engine/
COPY scripts/ ./scripts/

# 3. Install project and seed initial SQLite databases
RUN uv pip install --system -e . && python scripts/setup_db.py

EXPOSE 8000

CMD ["uvicorn", "nlp_sql_engine.web.app:app", "--host", "0.0.0.0", "--port", "8000"]
