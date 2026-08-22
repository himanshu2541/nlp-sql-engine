FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# 1. Install dependencies first (Layer is cached by Docker permanently)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copy source code (Changing code will NOT re-download dependencies)
COPY pyproject.toml README.md questions.txt app.py ./
COPY nlp_sql_engine/ ./nlp_sql_engine/
COPY scripts/ ./scripts/

# 3. Install project and seed initial databases
RUN pip install --no-cache-dir -e . && python scripts/setup_db.py


EXPOSE 8000

CMD ["uvicorn", "nlp_sql_engine.web.app:app", "--host", "0.0.0.0", "--port", "8000"]

