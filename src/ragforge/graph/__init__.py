from ragforge.graph.neo4j_store import GraphStore

_graph_instance = None

def get_graph_store() -> GraphStore:
    """
    Returns the singleton instance of the GraphStore.
    
    This function ensures only one GraphStore instance is created,
    reusing the same Neo4j connection across the application.
    
    If Neo4j is unavailable, returns a GraphStore instance with driver=None,
    which gracefully falls back to vector-only RAG.
    
    Returns:
        GraphStore: The singleton graph store instance (may have driver=None if Neo4j unavailable).
    """
    global _graph_instance
    if _graph_instance is None:
        _graph_instance = GraphStore()
    return _graph_instance

__all__ = ["GraphStore", "get_graph_store"]
