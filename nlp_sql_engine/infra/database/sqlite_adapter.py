import sqlite3
from typing import Generator, Any, List
from nlp_sql_engine.core.interfaces.db import IDatabaseConnector
from nlp_sql_engine.app.registry import ProviderRegistry

@ProviderRegistry.register_db("sqlite")
class SQLiteAdapter(IDatabaseConnector):
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.conn = None

    def _connect(self):
        """Lazy connection to the database."""
        if self.conn is None:
            # check_same_thread=False is needed if we run this in a multi-threaded web app later
            self.conn = sqlite3.connect(self.connection_string, check_same_thread=False)

    def get_table_schema(self, table_name: str) -> str:
        """
        Fetches schema for a SINGLE table. 
        Used by the Router to retrieve details only for relevant tables.
        """
        self._connect()
        assert self.conn is not None
        cursor = self.conn.cursor()
        
        # Safe formatting for table name (PRAGMA statements don't support standard parameter substitution)
        # In production, Validate table_name strictly to prevent injection.
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        if not columns:
            return ""

        schema = f"Table: {table_name}\n"
        for col in columns:
            # col[1] is name, col[2] is type
            schema += f"  {col[1]} {col[2]}\n"
        
        return schema.strip()

    def get_all_table_names(self) -> List[str]:
        """Returns a list of all table names in the database."""
        self._connect()
        assert self.conn is not None
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        return [table[0] for table in tables]

    def get_schema(self) -> str:
        """
        Returns the FULL schema. 
        Note: In Phase 2, try to use get_table_schema with the Router instead of this.
        """
        tables = self.get_all_table_names()
        full_schema = []
        for table in tables:
            full_schema.append(self.get_table_schema(table))
        return "\n\n".join(full_schema)

    def execute_query(self, query: str) -> Generator[Any, None, None]:
        """
        Executes SQL and yields results row by row.
        Satisfies Challenge #2: Memory Efficient Handle.
        """
        self._connect()
        assert self.conn is not None
        cursor = self.conn.cursor()
        cursor.execute(query)
        
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            yield row

    def execute_ddl(self, query: str) -> None:
        """Executes DDL statements like CREATE, INSERT, etc."""
        self._connect()
        assert self.conn is not None
        cursor = self.conn.cursor()
        cursor.execute(query)
        self.conn.commit()