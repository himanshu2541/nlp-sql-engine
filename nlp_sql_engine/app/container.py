from nlp_sql_engine.config.settings import Settings
from nlp_sql_engine.app.bootstrap import scan_and_register_adapters
from nlp_sql_engine.app.factories.infrastructure import InfrastructureFactory
from nlp_sql_engine.services.sql_generator import SQLGenerationService
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
        llm = InfrastructureFactory.create_llm(settings)
        db = InfrastructureFactory.create_db(settings)
        
        # Build Services
        sql_service = SQLGenerationService(llm)
        
        # Build and Return the Use Case (The Application)
        return AskQuestionUseCase(db, sql_service)