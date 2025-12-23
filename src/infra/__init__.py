import pkgutil
import importlib
import logging

logger = logging.getLogger(__name__)

def discover(package):
    """
    Explicit plugin discovery.
    This is infrastructure-only and must be called explicitly.
    """
    if isinstance(package, str):
        package = importlib.import_module(package)

    logger.info(f"Discovering providers in: {package.__name__}")

    prefix = package.__name__ + "."
    for _, module_name, _ in pkgutil.walk_packages(package.__path__, prefix):
        try:
            logger.debug(f"Loading module: {module_name}")
            importlib.import_module(module_name)
        except Exception as e:
            logger.error(f"Failed to load {module_name}: {e}")
            raise  # fail fast (important)