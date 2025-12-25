from typing import Generator, Any
from nlp_sql_engine.core.interfaces.manager import IDatabaseManager
from nlp_sql_engine.services.gen_pipeline import SQLPipelineService
from nlp_sql_engine.services.schema_router import SchemaRouter
from nlp_sql_engine.core.domain.models import NLQuery, PipelineResult, QueryResult

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
        try:
            # Get relevant schema using the Schema Router
            relevant_schema, target_db_name = self.schema_router.route(query.question)

            active_adapter = self.db_manager.get_adapter(target_db_name)

            query_model = self.pipeline_service.run(relevant_schema, query.question)

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
                            error=f"Failed on DB '{target_db_name}': {str(e)}"
                        )
        except Exception as e:
            yield PipelineResult(error=f"Schema Routing Error: {str(e)}")
