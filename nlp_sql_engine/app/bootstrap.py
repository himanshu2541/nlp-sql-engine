import pkgutil
import importlib
import logging
import nlp_sql_engine.infra

logger = logging.getLogger(__name__)

def scan_and_register_adapters():
    """
    Dynamically discovers and imports all modules in the 'nlp_sql_engine.infra' package.
    This triggers the @register decorators in those files.
    """
    # Get the path of the 'nlp_sql_engine.infra' package
    package = nlp_sql_engine.infra
    path = package.__path__
    prefix = package.__name__ + "."

    logger.info(f"Scanning for adapters in: {path}")

    # Recursive scan of all modules in nlp_sql_engine/infra/
    for _, name, _ in pkgutil.walk_packages(path, prefix):
        try:
            logger.debug(f"Loading module: {name}")
            importlib.import_module(name)
        except Exception as e:
            # We catch errors here so one broken adapter doesn't crash the app start
            logger.error(f"Failed to load adapter module '{name}': {e}")

    logger.info("Adapter registration complete.")