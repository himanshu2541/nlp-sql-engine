import logging
import sys
from .settings import settings

def setup_logging():
    """
    Configures the root logger for the application.
    """
    logging.basicConfig(
        level="DEBUG" if settings.DEBUG else "INFO",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)