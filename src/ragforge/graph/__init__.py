from ragforge.graph.neo4j_store import GraphStore
from ragforge.core.base import BaseGraphStore
from ragforge.core.registry import GraphStoreRegistry

# Register default providers
GraphStoreRegistry.register("neo4j", GraphStore)

def get_graph_store() -> BaseGraphStore:
    """
    Returns the singleton instance of the GraphStore.
    Uses the registry to get the configured provider.
    
    If Neo4j is unavailable, returns a GraphStore instance with driver=None,
    which gracefully falls back to vector-only RAG.
    
    Returns:
        BaseGraphStore: The singleton graph store instance (may have driver=None if Neo4j unavailable).
    """
    return GraphStoreRegistry.get_provider(use_singleton=True)

__all__ = ["GraphStore", "get_graph_store", "BaseGraphStore"]
