import sqlite3
from typing import Generator, Any
from nlp_sql_engine.core.interfaces.db import IDatabaseConnector
from nlp_sql_engine.app.registry import ProviderRegistry


@ProviderRegistry.register_db("sqlite")
class SQLiteAdapter(IDatabaseConnector):
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.conn = None

    def _connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.connection_string)

    def get_schema(self) -> str:
        self._connect()
        assert self.conn is not None # for type checker
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        schema = ""
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            schema += f"Table: {table_name}\n"
            for col in columns:
                schema += f"  {col[1]} {col[2]}\n"
            schema += "\n"
        return schema

    def execute_query(self, query: str) -> Generator[Any, None, None]:
        self._connect()
        assert self.conn is not None # for type checker
        cursor = self.conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        for row in results:
            yield row

    def execute_ddl(self, query: str):
        self._connect()
        assert self.conn is not None # for type checker
        self.conn.execute(query)
        self.conn.commit()