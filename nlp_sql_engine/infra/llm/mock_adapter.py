from typing import Any, List, Tuple
from nlp_sql_engine.config.settings import Settings
from nlp_sql_engine.core.interfaces.llm import ILLMProvider
from nlp_sql_engine.app.registry import ProviderRegistry


@ProviderRegistry.register_llm("mock")
class MockLLMAdapter(ILLMProvider):
    def __init__(self, api_key: str, model_name: str, temperature: float, **kwargs: Any):
        """
        A Test Adapter that maps specific questions to specific SQL queries.
        Useful for validating: 'If the LLM generates X, does the DB return Y?'
        """
        # In a real app, you might load these from a JSON file in settings
        self.scripted_responses = {
            "get all employees": "SELECT * FROM employees;",
            "who is the manager": "SELECT name FROM employees WHERE role = 'Manager';",
            "count the staff": "SELECT count(*) FROM employees;",
            "show me high earners": "SELECT name, salary FROM employees WHERE salary > 50000;",
        }

    def invoke(self, messages: List[Tuple[str, str]]) -> str:
        # Extract the user prompt (usually the last message)
        user_question = messages[-1][1].lower().strip()

        # Simple lookup
        for key, sql in self.scripted_responses.items():
            if key in user_question:
                return sql

        return "-- ERROR: Unknown test question. Please add it to ScriptedLLMAdapter."
