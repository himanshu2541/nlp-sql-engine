from langchain_core.prompts import ChatPromptTemplate

from nlp_sql_engine.core.context.pipeline import PipelineContext
from nlp_sql_engine.core.steps.base import BaseLLMStep


class ErrorCorrectionStep(BaseLLMStep):
    def execute(self, context: PipelineContext) -> PipelineContext:
        # Only run if there is an error
        if not context.error:
            return context

        print(f"   >>> [Step: Correction] using {self.role_name}...")

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "user",
                    "### Role: SQL Debugger\n"
                    "The previous query failed. Fix the SQL based on the error message.\n"
                    "Rules:\n"
                    "1. **Syntax:** Output ONLY valid SQLite. No Markdown. No Backticks (`).\n"
                    "2. **Fixes:**\n"
                    "   - 'no such column': Check the Schema below. Did you hallucinate a name? (e.g. used `category` instead of `category_id`?)\n"
                    "   - 'ambiguous column name': You MUST add table prefixes (e.g. `orders.id` instead of just `id`).\n"
                    "   - 'near \"`\"': Remove all backticks.\n"
                    "\n"
                    "### Error:\n{error}\n\n"
                    "### Bad SQL:\n{sql}\n\n"
                    "### Schema:\n{schema}\n\n"
                    "### Corrected SQL:",
                )
            ]
        )

        context.sql_query = self._invoke_llm(
            prompt,
            {
                "schema": context.schema,
                "sql": context.sql_query,
                "error": context.error,
            },
        )
        return context
