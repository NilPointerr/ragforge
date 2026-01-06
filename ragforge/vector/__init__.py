from ragforge.vector.qdrant import VectorStore

_store_instance = None

def get_vector_store() -> VectorStore:
    """
    Returns the singleton instance of the VectorStore.
    """
    global _store_instance
    if _store_instance is None:
        _store_instance = VectorStore()
    return _store_instance
