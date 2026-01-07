import logging
import sys
from .rag import ask, ingest

__all__ = ["ask", "ingest"]

# Configure logging for the package
def _configure_logging():
    """Configure basic logging for ragforge package."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

# Configure logging on import
_configure_logging()
