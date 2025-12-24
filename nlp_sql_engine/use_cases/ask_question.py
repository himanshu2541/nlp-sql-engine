from typing import Generator, Any
from nlp_sql_engine.core.interfaces.db import IDatabaseConnector
from nlp_sql_engine.services.gen_pipeline import SQLPipelineService
from nlp_sql_engine.services.schema_router import SchemaRouter
from nlp_sql_engine.core.domain.models import NLQuery, PipelineResult, QueryResult

import logging
logger = logging.getLogger(__name__)

class AskQuestionUseCase:
    def __init__(
        self,
        db: IDatabaseConnector,
        pipeline_service: SQLPipelineService,
        schema_router: SchemaRouter,
    ):
        self.db = db
        self.pipeline_service = pipeline_service
        self.schema_router = schema_router

    def execute(self, query: NLQuery) -> Generator[PipelineResult, None, None]:
        try:
            # Get relevant schema using the Schema Router
            relevant_schemas = self.schema_router.get_relevant_schemas(query.question)

            # Generate SQL using only the relevant schemas
            query_model = self.pipeline_service.run(relevant_schemas, query.question)

            attempt = 0
            max_retries = 2

            while attempt <= max_retries:
                try:
                    rows = self.db.execute_query(query_model.query)
                    yield PipelineResult(
                        sql_query=query_model, result=QueryResult(rows=rows, columns=[])
                    )
                    return
                except Exception as e:
                    attempt += 1
                    if attempt <= max_retries:
                        logger.warning(f"Error: {e}. Feedback loop triggered.")
                        query_model = self.pipeline_service.refine(
                            schema=relevant_schemas,
                            question=query.question,
                            sql=query_model.query,
                            error=str(e),
                        )
                    else:
                        yield PipelineResult(error=f"Final Failure: {e}")

            # Execute & Stream
            rows_gen = self.db.execute_query(query_model.query)

            result_wrapper = QueryResult(
                columns=[], rows=rows_gen
            )  # TODO: Implement something to get the columns
            yield PipelineResult(sql_query=query_model, result=result_wrapper)
        except Exception as e:
            yield PipelineResult(error=f"Schema Routing Error: {str(e)}")
