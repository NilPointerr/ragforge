"""
Base interfaces for Ragforge providers and strategies.

All providers and strategies must implement these interfaces to ensure
compatibility and allow easy swapping of implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseLLM(ABC):
    """
    Abstract base class for LLM providers.
    
    All LLM implementations must inherit from this class and implement
    the generate_response method.
    """

    @abstractmethod
    def generate_response(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float = 0.1,
        top_p: float = 1.0,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generates a response from the LLM.
        
        Args:
            prompt: The user query + context.
            system_prompt: Instructions for the LLM behavior.
            temperature: Sampling temperature (0.0 to 2.0).
            top_p: Nucleus sampling parameter.
            max_tokens: Maximum tokens to generate.
            **kwargs: Additional provider-specific parameters.
            
        Returns:
            The raw string response from the LLM.
            
        Raises:
            ProviderError: If the LLM provider fails to generate a response.
        """
        pass


class BaseVectorStore(ABC):
    """
    Abstract base class for vector store providers.
    
    All vector store implementations must inherit from this class.
    """

    @abstractmethod
    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """
        Embeds and adds texts to the vector store.
        
        Args:
            texts: List of string documents to add.
            metadatas: Optional list of metadata dictionaries (one per text).
            ids: Optional list of document IDs. If None, will be auto-generated.
            
        Raises:
            IngestionError: If document ingestion fails.
        """
        pass

    @abstractmethod
    def search(
        self,
        query: str,
        limit: int = 5,
        filter: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[str]:
        """
        Searches for relevant texts using semantic similarity.
        
        Args:
            query: The search query.
            limit: Number of results to return.
            filter: Optional metadata filter dictionary.
            **kwargs: Additional provider-specific parameters.
            
        Returns:
            List of relevant text chunks.
            
        Raises:
            RetrievalError: If search fails.
        """
        pass

    @abstractmethod
    def delete(self, ids: List[str]) -> None:
        """
        Delete documents by their IDs.
        
        Args:
            ids: List of document IDs to delete.
            
        Raises:
            RetrievalError: If deletion fails.
        """
        pass

    @abstractmethod
    def update(
        self,
        id: str,
        text: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update an existing document.
        
        Args:
            id: Document ID to update.
            text: Optional new text content.
            metadata: Optional new metadata.
            
        Raises:
            RetrievalError: If update fails.
        """
        pass


class BaseGraphStore(ABC):
    """
    Abstract base class for graph store providers.
    
    All graph store implementations must inherit from this class.
    """

    @abstractmethod
    def add_document_to_graph(
        self,
        text: str,
        doc_id: Optional[str] = None
    ) -> None:
        """
        Add a document to the knowledge graph by extracting and storing entities and relationships.
        
        Args:
            text: The document text to process.
            doc_id: Optional document identifier.
            
        Raises:
            GraphError: If graph construction fails.
        """
        pass

    @abstractmethod
    def get_graph_context(
        self,
        query: str,
        max_entities: int = 5
    ) -> str:
        """
        Retrieve graph context for a query.
        
        Args:
            query: The search query.
            max_entities: Maximum number of entities to retrieve.
            
        Returns:
            Formatted string containing graph context.
            
        Raises:
            GraphError: If graph query fails.
        """
        pass

    @abstractmethod
    def clear_graph(self) -> None:
        """
        Clear all nodes and relationships from the graph.
        
        Raises:
            GraphError: If clearing fails.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the graph store is available and connected.
        
        Returns:
            True if available, False otherwise.
        """
        pass


class BaseChunkingStrategy(ABC):
    """
    Abstract base class for text chunking strategies.
    """

    @abstractmethod
    def chunk(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int = 0,
        **kwargs
    ) -> List[str]:
        """
        Split text into chunks.
        
        Args:
            text: The text to chunk.
            chunk_size: Size of each chunk in characters.
            chunk_overlap: Number of characters to overlap between chunks.
            **kwargs: Strategy-specific parameters.
            
        Returns:
            List of text chunks.
        """
        pass


class BaseRetrievalStrategy(ABC):
    """
    Abstract base class for retrieval strategies.
    """

    @abstractmethod
    def retrieve(
        self,
        query: str,
        vector_store: BaseVectorStore,
        graph_store: Optional[BaseGraphStore] = None,
        limit: int = 5,
        **kwargs
    ) -> List[str]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: The search query.
            vector_store: Vector store instance to use.
            graph_store: Optional graph store instance.
            limit: Maximum number of results.
            **kwargs: Strategy-specific parameters.
            
        Returns:
            List of retrieved text chunks.
        """
        pass
