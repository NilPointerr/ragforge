import logging
import sys
from .rag import ask, ingest, LLMConfig
from .utils import ingest_from_file, ingest_from_directory, ingest_file
from .core import (
    BaseLLM,
    BaseVectorStore,
    BaseGraphStore,
    LLMRegistry,
    VectorStoreRegistry,
    GraphStoreRegistry,
)

__all__ = [
    # Main API
    "ask",
    "ingest",
    "ingest_from_file",
    "ingest_from_directory",
    "ingest_file",
    # Configuration
    "LLMConfig",
    # Core abstractions
    "BaseLLM",
    "BaseVectorStore",
    "BaseGraphStore",
    # Registries
    "LLMRegistry",
    "VectorStoreRegistry",
    "GraphStoreRegistry",
]

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
