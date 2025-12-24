from typing import Generator, Any
from nlp_sql_engine.core.interfaces.db import IDatabaseConnector
from nlp_sql_engine.services.sql_generator import SQLGenerationService
from nlp_sql_engine.services.schema_router import SchemaRouter
from nlp_sql_engine.core.domain.models import NLQuery, PipelineResult, QueryResult


class AskQuestionUseCase:
    def __init__(
        self,
        db: IDatabaseConnector,
        sql_service: SQLGenerationService,
        schema_router: SchemaRouter,
    ):
        self.db = db
        self.sql_service = sql_service
        self.schema_router = schema_router

    def execute(self, query: NLQuery) -> Generator[PipelineResult, None, None]:
        try:
            # Get relevant schema using the Schema Router
            relevant_schemas = self.schema_router.get_relevant_schemas(query.question)

            # Generate SQL using only the relevant schemas
            sql_query_model = self.sql_service.generate(
                relevant_schemas, query.question
            )

            # Execute & Stream
            rows_gen = self.db.execute_query(sql_query_model.query)

            result_wrapper = QueryResult(
                columns=[], rows=rows_gen
            )  # TODO: Implement something to get the columns
            yield PipelineResult(sql_query=sql_query_model, result=result_wrapper)
        except Exception as e:
            yield PipelineResult(error=f"Schema Routing Error: {str(e)}")
