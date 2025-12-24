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
                    "Common Fixes:\n"
                    "- 'no such column': You likely used a hallucinated name (e.g. `category_name` instead of `name`). Check the schema!\n"
                    "- 'ambiguous column name': Add a table alias (e.g. `p.id`).\n"
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
