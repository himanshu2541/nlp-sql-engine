from typing import Generator, Any, List
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import ArgumentError
from nlp_sql_engine.config.settings import Settings
from nlp_sql_engine.core.interfaces.db import IDatabaseConnector
from nlp_sql_engine.app.registry import ProviderRegistry

import logging
logger = logging.getLogger(__name__)

@ProviderRegistry.register_db("sqlalchemy")
class SQLAlchemyAdapter(IDatabaseConnector):
    @classmethod
    def create(cls, settings: Settings) -> 'SQLAlchemyAdapter':
        """
        Factory method to instantiate from global settings.
        """
        # Get Connection String
        # Support both single DB config or specific keys
        conn_string = getattr(settings, "DB_CONNECTION_STRING", "")
        if not conn_string:
            # Fallback for when used as a standalone or default
            logger.warning("DB_CONNECTION_STRING not set in settings. Using in-memory SQLite.")
            conn_string = "sqlite:///:memory:"
            
        return cls(connection_string=conn_string)
    
    def __init__(self, connection_string: str):
        # Supports 'postgresql://...', 'mysql://...', 'sqlite://...'
        try:
            self.engine = create_engine(connection_string)
            self.inspector = inspect(self.engine)
            
        except ArgumentError as e:
            logger.error(f"Failed to create engine with connection string: {connection_string}")
            raise ValueError(
                f"Invalid Database Connection String: '{connection_string}'.\n"
                f"SQLAlchemy requires a standard URI format.\n"
                f"Examples:\n"
                f"  - SQLite: 'sqlite:///commerce.db' (Note the 3 slashes for relative path)\n"
                f"  - Postgres: 'postgresql://user:password@localhost/dbname'\n"
                f"  - MySQL: 'mysql://user:password@localhost/dbname'\n"
                f"Original Error: {str(e)}"
            ) from e

    def get_all_table_names(self) -> List[str]:
        return self.inspector.get_table_names()

    def get_table_schema(self, table_name: str) -> str:
        """
        Introspects the DB to generate a CREATE TABLE-style description
        including columns, types, and FOREIGN KEYS.
        """
        columns = self.inspector.get_columns(table_name)
        if not columns:
            return ""

        # Columns
        schema = f"Table: {table_name}\n"
        for col in columns:
            # col: {'name': 'id', 'type': INTEGER(), 'nullable': False...}
            schema += f"  {col['name']} {col['type']}\n"

        # Foreign Keys
        fks = self.inspector.get_foreign_keys(table_name)
        if fks:
            schema += "  -- Relationships --\n"
            for fk in fks:
                # fk: {'constrained_columns': ['uid'], 'referred_table': 'users', ...}
                src = ", ".join(fk['constrained_columns'])
                ref_table = fk['referred_table']
                ref_cols = ", ".join(fk['referred_columns'])
                schema += f"  FOREIGN KEY ({src}) REFERENCES {ref_table}({ref_cols})\n"

        return schema.strip()

    def get_schema(self) -> str:
        """Aggregates all table schemas."""
        tables = self.get_all_table_names()
        return "\n\n".join([self.get_table_schema(t) for t in tables])

    def execute_query(self, query: str) -> Generator[Any, None, None]:
        """
        Yields results row-by-row to satisfy memory efficiency.
        """
        with self.engine.connect() as conn:
            # SQLAlchemy 'text' object is required for raw SQL
            result = conn.execute(text(query))
            
            if result.returns_rows:
                for row in result:
                    # Converts SQLAlchemy Row object to tuple/dict
                    yield row
            else:
                conn.commit()

    def execute_ddl(self, query: str) -> None:
        with self.engine.begin() as conn: # 'begin' auto-commits on exit
            conn.execute(text(query))