from ragforge.vector.qdrant import VectorStore

_store_instance = None

def get_vector_store() -> VectorStore:
    """
    Returns the singleton instance of the VectorStore.
    
    This function ensures only one VectorStore instance is created,
    reusing the same Qdrant client connection across the application.
    
    Returns:
        VectorStore: The singleton vector store instance.
        
    Raises:
        RetrievalError: If vector store initialization fails.
    """
    global _store_instance
    if _store_instance is None:
        _store_instance = VectorStore()
    return _store_instance
