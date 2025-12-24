import pytest
from nlp_sql_engine.infra.database.sqlite_adapter import SQLiteAdapter

@pytest.fixture
def db_adapter():
    """Fixture to create a fresh DB for every test function."""
    adapter = SQLiteAdapter(":memory:")
    adapter.execute_ddl("CREATE TABLE test_users (id INT, name TEXT)")
    adapter.execute_ddl("INSERT INTO test_users VALUES (1, 'Test User')")
    return adapter

def test_get_all_table_names(db_adapter):
    tables = db_adapter.get_all_table_names()
    assert "test_users" in tables
    assert len(tables) == 1

def test_get_table_schema(db_adapter):
    schema = db_adapter.get_table_schema("test_users")
    # Verify exact formatting needed for the LLM
    assert "Table: test_users" in schema
    assert "id INT" in schema
    assert "name TEXT" in schema

def test_memory_efficient_generator(db_adapter):
    """Ensure execute_query returns a generator, not a list."""
    result = db_adapter.execute_query("SELECT * FROM test_users")
    
    # 1. Check type
    import types
    assert isinstance(result, types.GeneratorType)
    
    # 2. Check content
    row = next(result)
    assert row == (1, 'Test User')
    
    # 3. Ensure it stops
    with pytest.raises(StopIteration):
        next(result)