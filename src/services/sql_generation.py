from src.core.domain.models import SQLQuery
from src.core.interfaces.llm import ILLMProvider

class SQLGenerationService:
    def __init__(self, llm: ILLMProvider):
        self.llm = llm

    def generate(self, schema: str, question: str) -> SQLQuery:
        system_prompt = f"...{schema}..."
        messages = [
            ("system", system_prompt),
            ("human", question)
        ]
        return SQLQuery(query=self.llm.invoke(messages))
