import re
from typing import Dict, List, Tuple, Any
from nlp_sql_engine.core.interfaces.db import IDatabaseConnector
import logging

logger = logging.getLogger(__name__)


class AutoSchemaDiscoverer:
    """
    Automatically introspects connected physical databases,
    maps virtual tables, and infers cross-database relational joins.
    """

    @staticmethod
    def discover_virtual_schema(adapters: Dict[str, IDatabaseConnector]) -> Dict[str, str]:
        """
        Discovers all tables across physical database adapters and assigns virtual table names.
        Format: {"virtual_table": "db_alias.physical_table"}
        """
        virtual_schema: Dict[str, str] = {}
        for db_alias, adapter in adapters.items():
            for table in adapter.get_all_table_names():
                # By default, virtual table name matches physical table name
                virtual_schema[table] = f"{db_alias}.{table}"
        return virtual_schema

    @staticmethod
    def infer_relationships(
        adapters: Dict[str, IDatabaseConnector],
        virtual_schema: Dict[str, str],
    ) -> List[Tuple[Tuple[str, str], Tuple[str, str]]]:
        """
        Infers foreign key and cross-database relationships using schema introspection
        and smart semantic naming heuristics (e.g., customer_id -> customers.id).
        """
        relationships: List[Tuple[Tuple[str, str], Tuple[str, str]]] = []
        table_columns: Dict[str, List[str]] = {}

        # 1. Extract all columns per virtual table
        for v_table, path in virtual_schema.items():
            db_alias, p_table = path.split(".", 1)
            adapter = adapters[db_alias]
            raw_schema = adapter.get_table_schema(p_table)

            # Extract column names from schema text
            cols = []
            for line in raw_schema.splitlines():
                line = line.strip()
                # Matches "- column_name (TYPE)" or "column_name TYPE"
                m = re.match(r"^[-*]?\s*([a-zA-Z0-9_]+)\s+", line)
                if m and m.group(1).lower() not in ["table:", "create", "primary", "foreign", "index", "--"]:
                    cols.append(m.group(1).lower())
            table_columns[v_table] = cols

        # 2. Heuristic Cross-Table FK Inference
        for src_table, columns in table_columns.items():
            for col in columns:
                if col.endswith("_id") and col != "id":
                    prefix = col[:-3]  # e.g., 'customer' from 'customer_id'

                    # Candidate target table names: 'customers', 'customer', 'customer_items'
                    candidates = [f"{prefix}s", f"{prefix}es", prefix]
                    matched_target = None
                    for cand in candidates:
                        if cand in virtual_schema and cand != src_table:
                            matched_target = cand
                            break

                    if matched_target:
                        target_cols = table_columns.get(matched_target, [])
                        target_pk = "id" if "id" in target_cols else (f"{prefix}_id" if f"{prefix}_id" in target_cols else "id")
                        rel = ((src_table, col), (matched_target, target_pk))
                        if rel not in relationships:
                            relationships.append(rel)
                            logger.info(f"[AutoSchema] Inferred Relation: {src_table}.{col} -> {matched_target}.{target_pk}")

        return relationships
