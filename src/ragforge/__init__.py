import logging
import sys
from .rag import ask, ingest
from .utils import ingest_from_file, ingest_from_directory, ingest_file

__all__ = ["ask", "ingest", "ingest_from_file", "ingest_from_directory", "ingest_file"]

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
