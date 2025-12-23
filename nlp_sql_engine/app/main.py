import sys
import os

# Ensure project root is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from nlp_sql_engine.app.container import AppContainer
from nlp_sql_engine.app.cli import run_cli
from nlp_sql_engine.config.logging import setup_logging

def main():
    setup_logging()
    # Build the App (Wire dependencies)
    application = AppContainer.build()
    
    # Run the Interface
    run_cli(application)

if __name__ == "__main__":
    main()