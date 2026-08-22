import sqlglot
from sqlglot import exp
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class SQLSecurityGuardrail:
    """
    Production AST-level SQL Guardrail.
    Validates queries for safety before executing against physical or federated databases.
    """

    FORBIDDEN_EXPRESSIONS = (
        exp.Drop,
        exp.Delete,
        exp.Update,
        exp.Insert,
        exp.Alter,
        exp.Command,
        exp.Create,
    )

    @classmethod
    def validate_and_sanitize(cls, sql_query: str, max_limit: int = 1000) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validates SQL safety and returns (is_safe, sanitized_sql, error_message).
        """
        if not sql_query or not sql_query.strip():
            return False, None, "Empty SQL query"

        try:
            # Parse all statements in the query string
            parsed_statements = sqlglot.parse(sql_query)
            
            if not parsed_statements:
                return False, None, "Unable to parse SQL query"

            # 1. Multi-statement injection check
            if len(parsed_statements) > 1:
                return False, None, "Multiple SQL statements detected. Only single queries are allowed."

            expression = parsed_statements[0]
            if expression is None:
                return False, None, "Invalid SQL syntax"

            # 2. Strict read-only check (Must be a Select query)
            if not isinstance(expression, (exp.Select, exp.Union)):
                return False, None, f"Dangerous SQL operation blocked. Only SELECT queries are permitted (got {type(expression).__name__})."

            # 3. Check for nested forbidden expressions
            for forbidden_type in cls.FORBIDDEN_EXPRESSIONS:
                if list(expression.find_all(forbidden_type)):
                    return False, None, f"Forbidden SQL operation detected: {forbidden_type.__name__}"

            # 4. Enforce reasonable row limit if not specified
            has_limit = expression.find(exp.Limit) is not None
            if not has_limit:
                # Add default limit of 1000 to prevent client crash
                expression = expression.limit(max_limit)

            sanitized_sql = expression.sql(dialect="sqlite")
            return True, sanitized_sql, None

        except Exception as e:
            logger.error(f"[Guardrail] SQL validation error: {e}")
            return False, None, f"SQL validation failed: {str(e)}"
