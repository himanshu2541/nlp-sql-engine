import sys
from nlp_sql_engine.use_cases.ask_question import AskQuestionUseCase
from nlp_sql_engine.core.domain.models import NLQuery

import logging
logger = logging.getLogger(__name__)

def run_cli(app: AskQuestionUseCase):
    """
    Runs the Command Line Interface loop.
    """
    print("\n>>> NLP-SQL Engine Ready. (Type 'exit' to quit)")
    print("-" * 50)

    while True:
        try:
            user_input = input("\nUser: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ["exit", "quit"]:
                logger.info("Exiting CLI.")
                sys.exit(0)

            print("Thinking...")
            
            query_model = NLQuery(question=user_input)
            
            for result in app.execute(query_model):
                if result.error:
                    logger.error(f"Error: {result.error}")
                elif result.sql_query:
                    print(f"Generated SQL: {result.sql_query.query}")
                    
                    if result.result and result.result.rows:
                        print("Results:")
                        for row in result.result.rows:
                            print(f"   -> {row}")
                    else:
                        print("(No rows returned)")
                        
        except KeyboardInterrupt:
            logger.info("Exiting CLI.")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Critical Error: {e}")