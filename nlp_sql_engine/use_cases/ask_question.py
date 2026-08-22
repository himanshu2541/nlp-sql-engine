import time
from typing import Generator, Any
from nlp_sql_engine.core.interfaces.manager import IDatabaseManager
from nlp_sql_engine.services.gen_pipeline import SQLPipelineService
from nlp_sql_engine.services.schema_router import SchemaRouter
from nlp_sql_engine.core.domain.models import NLQuery, PipelineResult, QueryResult, SQLQuery
from nlp_sql_engine.core.security.guardrail import SQLSecurityGuardrail
from nlp_sql_engine.core.security.intent_guardrail import IntentGuardrail

import logging

logger = logging.getLogger(__name__)


class AskQuestionUseCase:
    def __init__(
        self,
        db_manager: IDatabaseManager,
        pipeline_service: SQLPipelineService,
        schema_router: SchemaRouter,
    ):
        self.db_manager = db_manager
        self.pipeline_service = pipeline_service
        self.schema_router = schema_router

    def execute(self, query: NLQuery) -> Generator[PipelineResult, None, None]:
        # 0. Intent Guardrail Check (Intercept Greetings / Help / Non-Queries)
        is_non_query, guard_msg = IntentGuardrail.evaluate(query.question)
        if is_non_query:
            yield PipelineResult(message=guard_msg)
            return

        try:
            # 1. Get relevant schema using the Schema Router
            relevant_schema, target_db_name = self.schema_router.route(query.question)
            active_adapter = self.db_manager.get_adapter(target_db_name)

            # 2. Run Generation Pipeline
            query_model = self.pipeline_service.run(relevant_schema, query.question)


            # 3. Security Guardrail Check
            is_safe, sanitized_sql, guard_error = SQLSecurityGuardrail.validate_and_sanitize(query_model.query)
            if not is_safe:
                yield PipelineResult(
                    sql_query=query_model,
                    error=f"Security Guardrail Blocked Query: {guard_error}",
                )
                return

            query_model = SQLQuery(query=sanitized_sql)

            # 4. Execution & Self-Correction Feedback Loop
            attempt = 0
            max_retries = 2

            while attempt <= max_retries:
                try:
                    rows = active_adapter.execute_query(query_model.query)
                    yield PipelineResult(
                        sql_query=query_model, result=QueryResult(rows=rows, columns=[])
                    )
                    return
                except Exception as e:
                    attempt += 1
                    if attempt <= max_retries:
                        logger.warning(
                            f"Error on DB '{target_db_name}': {str(e)}. Feedback loop triggered. Retrying..."
                        )
                        query_model = self.pipeline_service.refine(
                            schema=relevant_schema,
                            question=query.question,
                            sql=query_model.query,
                            error=str(e),
                        )
                    else:
                        yield PipelineResult(
                            sql_query=query_model,
                            error=f"Failed on DB '{target_db_name}': {str(e)}"
                        )
        except Exception as e:
            yield PipelineResult(error=f"Execution Error: {str(e)}")

