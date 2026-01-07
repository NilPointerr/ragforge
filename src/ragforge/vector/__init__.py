from ragforge.vector.qdrant import VectorStore
from ragforge.core.base import BaseVectorStore
from ragforge.core.registry import VectorStoreRegistry

# Register default providers
VectorStoreRegistry.register("qdrant", VectorStore)

def get_vector_store() -> BaseVectorStore:
    """
    Returns the singleton instance of the VectorStore.
    Uses the registry to get the configured provider.
    
    Returns:
        BaseVectorStore: The singleton vector store instance.
        
    Raises:
        RetrievalError: If vector store initialization fails.
    """
    return VectorStoreRegistry.get_provider(use_singleton=True)
