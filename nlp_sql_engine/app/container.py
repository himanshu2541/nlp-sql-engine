from nlp_sql_engine.config.settings import Settings
from nlp_sql_engine.app.bootstrap import scan_and_register_adapters
from nlp_sql_engine.app.factories.infrastructure import InfrastructureFactory
from nlp_sql_engine.core.steps.correction import ErrorCorrectionStep
from nlp_sql_engine.core.steps.generation import SQLGenerationStep
from nlp_sql_engine.core.steps.planning import PlanningStep
from nlp_sql_engine.services.gen_pipeline import SQLPipelineService
from nlp_sql_engine.services.schema_router import SchemaRouter
from nlp_sql_engine.use_cases.ask_question import AskQuestionUseCase


class AppContainer:
    """
    Dependency Injection Container.
    Responsibility: Wire all components together and return the main application entry point.
    """

    @staticmethod
    def build() -> AskQuestionUseCase:
        # Run Auto-Discovery (Register all adapters)
        scan_and_register_adapters()

        # Load Configuration
        settings = Settings()

        # Build Infrastructure (via Factory)
        llm_plan = InfrastructureFactory.create_llm(
            provider_name=settings.PLANNER_LLM_PROVIDER,
            model_name=settings.PLANNER_LLM_MODEL_NAME,
            api_key=settings.PLANNER_LLM_API_KEY,
            temperature=settings.PLANNER_LLM_TEMPERATURE,
            base_url=settings.PLANNER_LLM_BASE_URL,
        )
        llm_generation = InfrastructureFactory.create_llm(
            provider_name=settings.GENERATION_LLM_PROVIDER,
            model_name=settings.GENERATION_LLM_MODEL_NAME,
            api_key=settings.GENERATION_LLM_API_KEY,
            temperature=settings.GENERATION_LLM_TEMPERATURE,
            base_url=settings.GENERATION_LLM_BASE_URL,
        )

        llm_debug = InfrastructureFactory.create_llm(
            provider_name=settings.DEBUG_LLM_PROVIDER,
            model_name=settings.DEBUG_LLM_MODEL_NAME,
            api_key=settings.DEBUG_LLM_API_KEY,
            temperature=settings.DEBUG_LLM_TEMPERATURE,
            base_url=settings.DEBUG_LLM_BASE_URL,
        )

        embedder = InfrastructureFactory.create_embedding(settings)
        db = InfrastructureFactory.create_db(settings)

        # Build Steps for Generation Pipeline
        steps = [
            PlanningStep(llm=llm_plan, role_name="Architect/Planner"),
            SQLGenerationStep(llm=llm_generation, role_name="Generator"),
            ErrorCorrectionStep(llm=llm_debug, role_name="Debugger"),
        ]

        # Build Service Layer
        schema_router = SchemaRouter(db, embedder)
        pipeline_service = SQLPipelineService(steps)

        # Initialize index (Important)
        schema_router.index_tables()

        # Build and Return the Use Case (The Application)
        return AskQuestionUseCase(db, pipeline_service, schema_router)
