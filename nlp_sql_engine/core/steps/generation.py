from langchain_core.prompts import ChatPromptTemplate

from nlp_sql_engine.core.context.pipeline import PipelineContext
from nlp_sql_engine.core.steps.base import BaseLLMStep


class SQLGenerationStep(BaseLLMStep):
    def execute(self, context: PipelineContext) -> PipelineContext:
        print(f"   >>> [Step: Generation] using {self.role_name}...")

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "user",
                    "### Role: SQL Developer\n"
                    "Write valid SQLite code based on the Architect's Plan.\n"
                    "Rules:\n"
                    "1. **Output:** Output ONLY the raw SQL query. No Markdown. No Explanations.\n"
                    "2. **Strict Column Names** Use the EXACT column names from the schema. DO NOT invent prefixes (e.g. use `name`, NOT `category_name` or `c_name`).\n"
                    "3. **Text Smarts:** NEVER use '=' for strings. ALWAYS use `LIKE '%value%'` or if whitespaces: `LIKE %value1%value2%` for case-insensitive matching. Correct user typos (e.g., 'Coffe' -> 'Coffee') inside the SQL.\n"
                    "4. **Dates:** Use SQLite `strftime` for partial dates: `strftime('%Y', col) = '2023'`.\n"
                    "5. **Ambiguity:** If the plan is unclear, verify columns against the schema below.\n"
                    "\n"
                    "### Schema (Reference for Column Names):\n{schema}\n\n"
                    "### Architect's Plan:\n{plan}\n\n"
                    "### Request:\n{question}\n\n"
                    "### SQL:",
                )
            ]
        )

        context.sql_query = self._invoke_llm(
            prompt,
            {
                "schema": context.schema,
                "plan": context.plan,
                "question": context.question,
            },
        )
        return context
