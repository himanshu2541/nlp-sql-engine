import sys
import os

# Fix import path so we can run this script directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from nlp_sql_engine.infra.database.sqlite_adapter import SQLiteAdapter
from nlp_sql_engine.infra.llm.mock_adapter import MockLLMAdapter as ScriptedLLMAdapter
from nlp_sql_engine.config.settings import settings

# For real LLM testing, uncomment below
# from nlp_sql_engine.infra.llm.openai_adapter import OpenAIAdapter
from nlp_sql_engine.services.sql_generator import SQLGenerationService
from nlp_sql_engine.services.schema_router import SchemaRouter
from nlp_sql_engine.use_cases.ask_question import AskQuestionUseCase
from nlp_sql_engine.core.domain.models import NLQuery
from tests.mocks import MockEmbeddingAdapter  # Reuse mock embedder

# ==========================================
# 1. DEFINE YOUR CUSTOM DATA HERE
# ==========================================
SAMPLE_DATA_SQL = """
    -- Clean up
    DROP TABLE IF EXISTS employees;
    DROP TABLE IF EXISTS departments;

    -- Create Tables
    CREATE TABLE departments (
        id INTEGER PRIMARY KEY,
        dept_name TEXT
    );

    CREATE TABLE employees (
        id INTEGER PRIMARY KEY,
        name TEXT,
        salary INTEGER,
        dept_id INTEGER,
        role TEXT,
        FOREIGN KEY(dept_id) REFERENCES departments(id)
    );

    -- Insert Data
    INSERT INTO departments VALUES (1, 'Engineering'), (2, 'Sales');
    
    INSERT INTO employees VALUES (101, 'Alice', 90000, 1, 'Manager');
    INSERT INTO employees VALUES (102, 'Bob', 80000, 1, 'Engineer');
    INSERT INTO employees VALUES (103, 'Charlie', 45000, 2, 'Associate');
    INSERT INTO employees VALUES (104, 'Diana', 120000, 2, 'Director');
"""

# ==========================================
# 2. DEFINE TEST CASES
# ==========================================
TEST_SCENARIOS = [
    {
        "question": "Who is the manager?",
        "expected_sql_snippet": "WHERE role = 'Manager'",
        "expected_row_count": 1,
    },
    {
        "question": "Show me high earners",
        "expected_sql_snippet": "salary > 50000",
        "expected_row_count": 3,  # Alice, Bob, Diana
    },
]


def run_validation():
    print("\n>>> Starting Data Validation Test...")

    # 1. Setup Infrastructure
    # Use :memory: for fast testing, or "test.db" to see the file
    db = SQLiteAdapter(":memory:")

    # 2. Load the Data
    print(">>> Loading Sample Data...")
    for statement in SAMPLE_DATA_SQL.split(";"):
        if statement.strip():
            db.execute_ddl(statement)
    print("    Data Loaded Successfully.")

    # 3. Setup Components
    # NOTE: Switch to OpenAIAdapter(Settings()) here to test REAL generation
    llm = ScriptedLLMAdapter(settings)

    embedder = MockEmbeddingAdapter(settings)

    # 4. Initialize Router (Phase 2)
    router = SchemaRouter(db, embedder)
    router.index_tables()

    # 5. Build Pipeline
    sql_service = SQLGenerationService(llm)
    app = AskQuestionUseCase(db, sql_service, router)

    # 6. Run Scenarios
    print("\n>>> 🏃 Running Scenarios...")

    for scenario in TEST_SCENARIOS:
        q = scenario["question"]
        print(f"\n[Test] Question: '{q}'")

        query_model = NLQuery(question=q)

        # Execute Pipeline
        results = list(app.execute(query_model))
        result = results[0]

        # Validation Logic
        if result.error:
            print(f"    ❌ ERROR: {result.error}")
            continue

        generated_sql = result.sql_query.query  # type: ignore
        rows = list(result.result.rows)  # type: ignore

        print(f"    Generated SQL: {generated_sql}")
        print(f"    Rows Returned: {rows}")

        # Assertions
        if scenario["expected_sql_snippet"] in generated_sql:
            print("    SQL Structure: Valid")
        else:
            print(
                f"    SQL Structure Mismatch. Expected snippet: '{scenario['expected_sql_snippet']}'"
            )

        if len(rows) == scenario["expected_row_count"]:
            print(f"    Data Count: Correct ({len(rows)})")
        else:
            print(
                f"    Data Count Fail: Expected {scenario['expected_row_count']}, got {len(rows)}"
            )


if __name__ == "__main__":
    run_validation()
