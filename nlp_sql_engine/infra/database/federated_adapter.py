import pandas as pd
import json
import sqlglot
from sqlglot import exp
from typing import Generator, Any, List, Dict, Tuple, Optional
from nlp_sql_engine.config.settings import Settings
from nlp_sql_engine.core.interfaces.db import IDatabaseConnector
from nlp_sql_engine.app.registry import ProviderRegistry

import logging

from nlp_sql_engine.infra.database.sqlalchemy_adapter import SQLAlchemyAdapter

logger = logging.getLogger(__name__)


@ProviderRegistry.register_db("federated")
class FederatedAdapter(IDatabaseConnector):
    """
    A Virtual Adapter that doesn't connect to a DB itself,
    but orchestrates queries across multiple physical adapters.
    """

    @classmethod
    def create(cls, settings: Settings) -> "FederatedAdapter":
        """
        Self-configuration logic for Federation.
        """
        # Parse Physical Attachments
        physicals = {}
        # Get raw config (dict or json string)
        db_configs = getattr(settings, "FEDERATED_ATTACHMENTS", {})
        if isinstance(db_configs, str):
            db_configs = json.loads(db_configs)

        # Instantiate Child Adapters
        # NOTE: For now, we assume children are SQLAlchemyAdapters.
        # If we need mixed types later, you can add a "type" field in the config JSON.
        for alias, uri in db_configs.items():
            physicals[alias] = SQLAlchemyAdapter(uri)

        # Get Virtual Schema & Relationships
        virtual_map = getattr(settings, "VIRTUAL_SCHEMA", {})
        rels = getattr(settings, "VIRTUAL_RELATIONSHIPS", [])

        return cls(
            adapters=physicals, table_mapping=virtual_map, relationship_graph=rels
        )

    def __init__(
        self,
        adapters: Dict[str, IDatabaseConnector],
        table_mapping: Dict[str, str],  # "virtual_table" -> "db_alias.physical_table"
        relationship_graph: List[Tuple] = [],
    ):
        self.adapters = adapters
        self.table_mapping = table_mapping
        self.relationship_graph = (
            relationship_graph  # List of ((table, column), (ref_table, ref_column))
        )

        # Helper: Map "virtual_table" -> "db_alias"
        self.table_to_db = {}
        # Helper: Map "virtual_table" -> "physical_table_name"
        self.table_to_physical = {}

        for v_table, path in table_mapping.items():
            db_alias, p_table = path.split(".", 1)
            self.table_to_db[v_table] = db_alias
            self.table_to_physical[v_table] = p_table

    def get_all_table_names(self) -> List[str]:
        # Expose ONLY virtual names to the LLM
        return list(self.table_mapping.keys())

    def get_table_schema(self, table_name: str) -> str:
        # Resolve Physical DB
        db_alias = self.table_to_db.get(table_name)
        if not db_alias:
            return ""

        real_adapter = self.adapters[db_alias]
        real_table = self.table_to_physical[table_name]

        # Get Real Schema
        # Note: We strip the raw schema and inject our Virtual Name
        raw_schema = real_adapter.get_table_schema(real_table)
        schema = raw_schema.replace(f"Table: {real_table}", f"Table: {table_name}")

        # Inject Virtual Relationships (Critical for LLM to know how to join)
        # (This logic mimics the previous step but is purely python based)
        rels = [r for r in self.relationship_graph if r[0][0] == table_name]
        if rels:
            schema += "  -- Relationships --\n"
            for (src_t, src_c), (ref_t, ref_c) in rels:
                schema += f"  FOREIGN KEY ({src_c}) REFERENCES {ref_t}({ref_c})\n"

        return schema

    def get_schema(self) -> str:
        return "\n\n".join(
            [self.get_table_schema(t) for t in self.get_all_table_names()]
        )

    def execute_query(self, query: str) -> Generator[Any, None, None]:
        """
        The Core Logic: Parse -> Plan -> Execute -> Join
        """
        # Parse SQL to find used tables
        parsed = sqlglot.parse_one(query)
        tables = [t.name for t in parsed.find_all(exp.Table)]

        if not tables:
            raise ValueError("No tables found in query")

        # Identify required Databases
        required_dbs = set()
        for t in tables:
            if t not in self.table_to_db:
                raise ValueError(f"Unknown virtual table: {t}")
            required_dbs.add(self.table_to_db[t])

        # Routing Logic

        # CASE A: Single Database Query (Optimization)
        if len(required_dbs) == 1:
            target_db = list(required_dbs)[0]
            physical_sql = self._transpile_to_physical(parsed, target_db)
            print(f"[Federation] Routing to '{target_db}': {physical_sql}")

            # Execute directly on the physical adapter
            return self.adapters[target_db].execute_query(physical_sql)

        # CASE B: Cross-Database Query
        # For MVP: We assume a simple JOIN between two tables across DBs.
        # Implementation: Fetch both datasets -> Join in Pandas
        else:
            logger.info(
                f"[Federation] Detected Cross-DB Join across {required_dbs}. Executing in Memory..."
            )
            return self._execute_cross_db_join(parsed, tables)

    def _transpile_to_physical(self, expression: exp.Expression, target_db: str) -> str:
        """
        Rewrites the AST: Replaces 'virtual_table' with 'physical_table'
        """

        def transformer(node):
            if isinstance(node, exp.Table):
                virtual_name = node.name
                if virtual_name in self.table_to_physical:
                    # Replace with real name (e.g., 'customers' -> 'tbl_customers_v1')
                    return exp.Table(
                        this=exp.Identifier(
                            this=self.table_to_physical[virtual_name], quoted=False
                        )
                    )
            return node

        new_expression = expression.transform(transformer)
        # Generate SQL for the specific dialect (assuming standard SQL for now)
        # Force dialect="sqlite" to use double quotes (") instead of backticks (`)
        return new_expression.sql(dialect="sqlite")

    def _execute_cross_db_join(self, expression, tables) -> Generator[Any, None, None]:
        """
        Naive Implementation of In-Memory Join.
        1. Decompose query into "SELECT * FROM table" for each table.
        2. Load into Pandas.
        3. Perform Merge.
        """
        # This is complex to generalize. For the MVP, we assume the user
        # requested a simple join. We will fetch the raw tables involved.

        data_frames = {}

        for t in tables:
            db_alias = self.table_to_db[t]
            real_table = self.table_to_physical[t]
            adapter = self.adapters[db_alias]

            # Optimization: In a real system, you'd push down filters (WHERE clauses) here!
            print(f"  -> Fetching data from {db_alias}.{real_table}...")
            rows = list(adapter.execute_query(f"SELECT * FROM {real_table} LIMIT 1000"))

            safe_dicts = []
            for row in rows:
                # SQLAlchemy 1.4+ support
                if hasattr(row, "_mapping"):
                    safe_dicts.append(dict(row._mapping))
                # Legacy SQLAlchemy support
                elif hasattr(row, "_asdict"):
                    safe_dicts.append(row._asdict())
                # Fallback (unsafe)
                else:
                    safe_dicts.append(dict(row))

            df = pd.DataFrame(safe_dicts) if safe_dicts else pd.DataFrame()

            # Get columns (Simplified: simplistic column fetch or assume dictionary cursor)
            # Assuming adapter yields dictionaries or Row objects we can convert
            # If adapter yields tuples, we need column names from schema.
            # For robustness, we assume RowProxy (SQLAlchemy) or similar.
            data_frames[t] = df

        # Now we need to JOIN based on the query 'ON' clause.
        # Parsing the JOIN conditions from 'expression' is tricky in vanilla Python.
        # Strategy: Let PandasSQL (sqldf) or DuckDB handle the final dataframe join
        # OR manual merge if simple.

        # RE-ENABLE DUCKDB FOR IN-MEMORY ONLY?
        # User said "No DuckDB". So we use `pandasql` or native pandas merge.
        # But `pandasql` is slow.

        # Let's assume the LLM gave us a valid SQL. We can try to use `sqlite3` in-memory
        # to act as the joiner if we dump the dataframes there.
        # This is standard Python library, no extra dependencies.

        import sqlite3

        conn = sqlite3.connect(":memory:")
        for tbl_name, df in data_frames.items():
            if not df.empty:
                df.to_sql(tbl_name, conn, index=False)
            else:
                logger.warning(f"Table {tbl_name} is empty.")

        # Execute the original query against this temporary memory DB
        # Since table names in memory match the virtual names, query works as-is!
        try:
            # We must output SQLite dialect for the Python sqlite3 driver
            sql_for_memory = expression.sql(dialect="sqlite")

            # SANITY CHECK: If sqlglot behaves weirdly, manually clean it
            if "`" in sql_for_memory:
                sql_for_memory = sql_for_memory.replace("`", '"')

            logger.info(f"[Federation] Executing In-Memory SQL:\n{sql_for_memory}")
            
            cursor = conn.execute(sql_for_memory)

            # Yield dictionary-like rows to match IDatabaseConnector expectation
            columns = (
                [desc[0] for desc in cursor.description] if cursor.description else []
            )
            for row in cursor:
                # Yield a dict so the CLI loop can print it nicely
                yield dict(zip(columns, row))

        except Exception as e:
            print(f"In-Memory Join Failed: {e}")
            raise e
        finally:
            conn.close()

    def execute_ddl(self, query: str) -> None:
        raise NotImplementedError("Federated DDL not supported yet.")

    def __init_subclass__(cls):
        return super().__init_subclass__()
