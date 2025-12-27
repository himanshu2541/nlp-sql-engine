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
                    "1. **Output:** Output ONLY the raw SQL query. No Markdown (```sql). No Explanations.\n"
                    "2. **Strict Column Names:** Use the EXACT column names from the schema. Never invent new column names (e.g., use `name`, do not invent `product_name` if it doesn't exist).\n"
                    "3. **Ambiguity & Aliases:** ALWAYS qualify columns with their table name or alias (e.g., `customers.name`, `orders.id`) to prevent 'ambiguous column' errors in joins.\n"
                    '4. **No Backticks:** NEVER use backticks (`). Use standard SQL syntax. Identifiers should be unquoted or use double quotes (") only if necessary.\n'
                    "5. **Text Smarts:** NEVER use '=' for strings. ALWAYS use `LIKE '%value%'` for case-insensitive matching.\n"
                    "6. **Dates:** Use SQLite `strftime` for partial dates: `strftime('%Y', order_date) = '2023'`.\n"
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
