import os
import time
import json
import uvicorn
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from nlp_sql_engine.app.container import AppContainer
from nlp_sql_engine.core.domain.models import NLQuery
from nlp_sql_engine.config.settings import settings
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="NLP-SQL Engine",
    description="Production Natural Language to Federated SQL Query Engine",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Application Instance
application = None


def get_app_instance():
    global application
    if application is None:
        application = AppContainer.build()
    return application


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    question: str
    sql: Optional[str] = None
    columns: List[str] = []
    rows: List[Any] = []
    row_count: int = 0
    latency_ms: float = 0.0
    message: Optional[str] = None
    error: Optional[str] = None
    target_db: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    get_app_instance()


@app.get("/health")
def health():
    return {"status": "healthy", "engine": settings.APP_NAME, "environment": settings.ENVIRONMENT}


@app.post("/api/query", response_model=QueryResponse)
def execute_query(req: QueryRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Query question cannot be empty.")

    engine = get_app_instance()
    start_time = time.perf_counter()

    try:
        results = list(engine.execute(NLQuery(question=req.question)))
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        if not results:
            return QueryResponse(question=req.question, latency_ms=elapsed_ms, error="No result generated.")

        res = results[0]
        if res.message:
            return QueryResponse(
                question=req.question,
                latency_ms=elapsed_ms,
                message=res.message,
            )
        if res.error:
            return QueryResponse(
                question=req.question,
                sql=res.sql_query.query if res.sql_query else None,
                latency_ms=elapsed_ms,
                error=res.error,
            )


        sql_text = res.sql_query.query if res.sql_query else ""
        raw_rows = list(res.result.rows) if res.result and res.result.rows else []

        # Format rows into list of dictionaries
        formatted_rows = []
        columns = []

        if raw_rows:
            first_row = raw_rows[0]
            if isinstance(first_row, dict):
                columns = list(first_row.keys())
                formatted_rows = raw_rows
            elif isinstance(first_row, (list, tuple)):
                columns = [f"col_{i+1}" for i in range(len(first_row))]
                for r in raw_rows:
                    formatted_rows.append(dict(zip(columns, r)))
            else:
                columns = ["result"]
                formatted_rows = [{"result": str(r)} for r in raw_rows]

        return QueryResponse(
            question=req.question,
            sql=sql_text,
            columns=columns,
            rows=formatted_rows,
            row_count=len(formatted_rows),
            latency_ms=elapsed_ms,
        )

    except Exception as e:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return QueryResponse(question=req.question, latency_ms=elapsed_ms, error=str(e))


@app.get("/api/schemas")
def get_schemas():
    engine = get_app_instance()
    db_manager = engine.db_manager
    schemas_data = {}

    for db_name, adapter in db_manager.get_all_adapters().items():
        schemas_data[db_name] = {
            "tables": adapter.get_all_table_names(),
            "schema_text": adapter.get_schema(),
        }

    return {
        "databases": schemas_data,
        "virtual_tables": list(getattr(settings, "VIRTUAL_SCHEMA", {}).keys()),
        "relationships": [
            f"{src[0]}.{src[1]} -> {ref[0]}.{ref[1]}"
            for src, ref in getattr(settings, "VIRTUAL_RELATIONSHIPS", [])
        ],
    }


@app.get("/api/sample-questions")
def get_sample_questions():
    questions_file = "questions.txt"
    if os.path.exists(questions_file):
        with open(questions_file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            return {"questions": lines}
    return {"questions": [
        "What products cost more than $100?",
        "List customer names and their order IDs.",
        "Show product names and their average rating.",
        "List all customers from the USA.",
        "How many customers are from the UK?",
    ]}


# Mount Static Files and Serve Frontend
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", response_class=HTMLResponse)
def index():
    html_file = os.path.join(static_dir, "index.html")
    if os.path.exists(html_file):
        with open(html_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>NLP-SQL Engine</h1><p>API is running at <a href='/docs'>/docs</a></p>"


def run():
    uvicorn.run("nlp_sql_engine.web.app:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    run()
