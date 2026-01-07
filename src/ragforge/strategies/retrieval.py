"""
Retrieval strategies for Ragforge.
"""

from typing import List, Optional
from ragforge.core.base import BaseRetrievalStrategy, BaseVectorStore, BaseGraphStore


class VectorOnlyRetrievalStrategy(BaseRetrievalStrategy):
    """
    Simple vector-only retrieval strategy.
    """
    
    def retrieve(
        self,
        query: str,
        vector_store: BaseVectorStore,
        graph_store: Optional[BaseGraphStore] = None,
        limit: int = 5,
        **kwargs
    ) -> List[str]:
        """
        Retrieve documents using only vector search.
        
        Args:
            query: The search query.
            vector_store: Vector store instance.
            graph_store: Ignored (not used).
            limit: Maximum number of results.
            **kwargs: Additional parameters.
            
        Returns:
            List of retrieved text chunks.
        """
        filter_dict = kwargs.get('filter')
        return vector_store.search(query, limit=limit, filter=filter_dict)


class HybridRetrievalStrategy(BaseRetrievalStrategy):
    """
    Hybrid retrieval strategy combining vector search and graph traversal.
    """
    
    def retrieve(
        self,
        query: str,
        vector_store: BaseVectorStore,
        graph_store: Optional[BaseGraphStore] = None,
        limit: int = 5,
        max_entities: int = 5,
        **kwargs
    ) -> List[str]:
        """
        Retrieve documents using both vector search and graph traversal.
        
        Args:
            query: The search query.
            vector_store: Vector store instance.
            graph_store: Optional graph store instance.
            limit: Maximum number of vector results.
            max_entities: Maximum number of entities to retrieve from graph.
            **kwargs: Additional parameters.
            
        Returns:
            List of retrieved text chunks (vector results first, then graph context).
        """
        results = []
        
        # 1. Vector retrieval
        filter_dict = kwargs.get('filter')
        vector_results = vector_store.search(query, limit=limit, filter=filter_dict)
        results.extend(vector_results)
        
        # 2. Graph retrieval (if available)
        if graph_store and graph_store.is_available():
            try:
                graph_context = graph_store.get_graph_context(query, max_entities=max_entities)
                if graph_context:
                    # Add graph context as additional context (not as separate results)
                    # In practice, this would be formatted differently, but for simplicity:
                    results.append(f"[Graph Context] {graph_context}")
            except Exception:
                # Silently fallback if graph retrieval fails
                pass
        
        return results
