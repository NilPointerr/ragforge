class RagforgeError(Exception):
    """Base exception for all Ragforge errors."""
    pass

class ConfigurationError(RagforgeError):
    """Raised when configuration is missing or invalid."""
    pass

class ProviderError(RagforgeError):
    """Raised when an LLM provider fails (API errors, timeouts)."""
    pass

class RetrievalError(RagforgeError):
    """Raised when vector retrieval fails."""
    pass

class IngestionError(RagforgeError):
    """Raised when document ingestion fails."""
    pass

class GraphError(RagforgeError):
    """Raised when graph operations fail."""
    pass