from config.settings import Settings
from src.app.factories.infrastructure import InfrastructureFactory
from src.core.domain.models import NLQuery, PipelineResult, SQLQuery, QueryResult
from typing import List, Any

from src.core.interfaces.llm import ILLMProvider
from src.core.interfaces.db import IDatabaseConnector


class NLPSQLPipeline:
    def __init__(self, llm_provider: ILLMProvider, db_provider: IDatabaseConnector):
        self.llm = llm_provider
        self.db = db_provider
        self._setup_sample_db()

    def _setup_sample_db(self):
        # Create a sample table for demo
        self.db.execute_ddl("CREATE TABLE users (id INTEGER, name TEXT, age INTEGER)")
        self.db.execute_ddl("INSERT INTO users VALUES (1, 'Alice', 30), (2, 'Bob', 25)")

    def process_query(self, nl_query: NLQuery) -> PipelineResult:
        # Get database schema
        schema = self.db.get_schema()

        # Generate SQL
        system_prompt = f"You are an expert SQL query generator. Given the database schema:\n{schema}\nGenerate a SQL query for the user's question."
        user_prompt = nl_query.question
        messages = [("system", system_prompt), ("user", user_prompt)]
        sql_str = self.llm.invoke(messages)

        sql_query = SQLQuery(query=sql_str)

        # Execute query
        try:
            rows = list(self.db.execute_query(sql_str))
            if rows:
                # Assume first row has column names or infer
                columns = [f"col_{i}" for i in range(len(rows[0]))] if rows else []
            else:
                columns = []
        except Exception as e:
            # If query fails, return error
            rows = []
            columns = ["error"]
            rows.append([str(e)])

        result = QueryResult(columns=columns, rows=rows)

        return PipelineResult(sql_query=sql_query, result=result)
