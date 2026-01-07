from ragforge.graph.neo4j_store import GraphStore

_graph_instance = None

def get_graph_store() -> GraphStore:
    """
    Returns the singleton instance of the GraphStore.
    
    This function ensures only one GraphStore instance is created,
    reusing the same Neo4j connection across the application.
    
    Returns:
        GraphStore: The singleton graph store instance.
        
    Raises:
        GraphError: If graph store initialization fails.
    """
    global _graph_instance
    if _graph_instance is None:
        _graph_instance = GraphStore()
    return _graph_instance

__all__ = ["GraphStore", "get_graph_store"]
