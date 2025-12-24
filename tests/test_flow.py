import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from nlp_sql_engine.core.domain.models import NLQuery
from nlp_sql_engine.infra.database.sqlite_adapter import SQLiteAdapter
from nlp_sql_engine.services.sql_generator import SQLGenerationService
from nlp_sql_engine.services.schema_router import SchemaRouter
from nlp_sql_engine.use_cases.ask_question import AskQuestionUseCase
from nlp_sql_engine.config.settings import settings

from tests.mocks import MockEmbeddingAdapter, SmartMockLLM


def test_full_application_flow():
    print("\n>>> 🚀 Starting End-to-End Flow Test...")

    # ---------------------------------------------------------
    # 1. INFRASTRUCTURE SETUP
    # ---------------------------------------------------------
    print(" [1/5] Setting up Database...")
    # Use In-Memory SQLite for speed
    db = SQLiteAdapter(":memory:")
    
    # Seed Data (So we have something to query)
    db.execute_ddl("CREATE TABLE users (id INT, name TEXT, role TEXT)")
    db.execute_ddl("INSERT INTO users VALUES (1, 'Alice', 'Engineer')")
    db.execute_ddl("INSERT INTO users VALUES (2, 'Bob', 'Manager')")
    db.execute_ddl("INSERT INTO users VALUES (3, 'Charlie', 'Designer')")

    print(" [2/5] Setting up Mocks (LLM & Embedder)...")
    llm = SmartMockLLM(settings)       # Returns "SELECT * FROM users"
    embedder = MockEmbeddingAdapter(settings) # Returns dummy vectors

    # ---------------------------------------------------------
    # 2. SERVICE LAYER SETUP
    # ---------------------------------------------------------
    print(" [3/5] Initializing Services & Router...")
    
    # Initialize Router and Index the Table
    router = SchemaRouter(db, embedder)
    router.index_tables()  # <--- CRITICAL: This pulls schema from DB
    
    # Verify Router actually found our table
    assert "users" in router._table_schemas, "Router failed to index 'users' table!"
    
    sql_service = SQLGenerationService(llm)

    # ---------------------------------------------------------
    # 3. USE CASE (The Application)
    # ---------------------------------------------------------
    print(" [4/5] Building Use Case...")
    app = AskQuestionUseCase(db, sql_service, router)

    # ---------------------------------------------------------
    # 4. EXECUTION
    # ---------------------------------------------------------
    print(" [5/5] Executing Query: 'Show me all users'...")
    query_model = NLQuery(question="Show me all users")
    
    # We iterate because the app yields results (Streaming)
    results = list(app.execute(query_model))

    # ---------------------------------------------------------
    # 5. ASSERTIONS (Did it work?)
    # ---------------------------------------------------------
    print("\n>>> 🔍 Verifying Results...")
    
    assert len(results) == 1, "Expected exactly 1 result object"
    pipeline_result = results[0]

    # Check 1: Did we get no errors?
    if pipeline_result.error:
        pytest.fail(f"Pipeline returned error: {pipeline_result.error}")

    # Check 2: Did we generate SQL?
    assert pipeline_result.sql_query is not None, "sql_query should not be None"
    print(f"    Generated SQL: {pipeline_result.sql_query.query}")
    assert "SELECT" in pipeline_result.sql_query.query.upper()

    # Check 3: Did we get rows?
    # Note: 'rows' is a generator, so we convert to list to check content
    assert pipeline_result.result is not None, "result should not be None in success case"
    assert pipeline_result.result.rows is not None, "rows generator should not be None"
    rows = list(pipeline_result.result.rows)
    print(f"    Rows Returned: {rows}")
    
    assert len(rows) == 3, "Expected 3 users (Alice, Bob, Charlie)"
    assert rows[0][1] == "Alice", "First user should be Alice"

    print("\n>>> ✅ SUCCESS: Whole Flow is Working!")

if __name__ == "__main__":
    test_full_application_flow()