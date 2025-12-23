from nlp_sql_engine.core.interfaces.llm import ILLMProvider
from nlp_sql_engine.core.domain.models import SQLQuery

class SQLGenerationService:
    def __init__(self, llm: ILLMProvider):
        self.llm = llm

    def generate_sql(self, schema_text: str, user_question: str) -> SQLQuery:
        system_prompt = (
            "You are a SQL Expert. Convert the question to SQL.\n"
            f"Schema:\n{schema_text}"
        )
        messages = [("system", system_prompt), ("user", user_question)]
        
        raw_response = self.llm.invoke(messages)
        
        # Strip markdown if present
        clean_sql = raw_response.replace("```sql", "").replace("```", "").strip()
        return SQLQuery(query=clean_sql)