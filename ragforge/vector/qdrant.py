import os
import logging
import uuid
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models

from ragforge.settings import settings
from ragforge.errors import RetrievalError, IngestionError

logger = logging.getLogger(__name__)

import atexit

class VectorStore:
    """
    Manages the Qdrant vector store using FastEmbed for embeddings.
    
    This class handles:
    - Initialization of local Qdrant client
    - Collection creation with proper vector dimensions
    - Document ingestion with automatic embedding
    - Semantic search over ingested documents
    
    The vector store uses a singleton pattern via get_vector_store()
    to ensure only one instance is created.
    """
    
    def __init__(self):
        """
        Initialize the Qdrant vector store client.
        Creates the storage directory if it doesn't exist.
        """
        # Initialize Qdrant Client (Local)
        try:
            os.makedirs(settings.qdrant_path, exist_ok=True)
            self.client = QdrantClient(path=settings.qdrant_path)
            # Set the model on the client to ensure it's loaded/configured
            try:
                self.client.set_model(settings.embedding_model)
            except ValueError as e:
                # Provide helpful error message for unsupported models
                error_msg = str(e)
                if "Unsupported embedding model" in error_msg:
                    raise RetrievalError(
                        f"Unsupported embedding model: '{settings.embedding_model}'. "
                        f"Please check the Qdrant/FastEmbed documentation for supported models. "
                        f"Common models include: 'sentence-transformers/all-MiniLM-L6-v2', "
                        f"'nomic-ai/nomic-embed-text-v1.5', 'BAAI/bge-small-en-v1.5', etc. "
                        f"Original error: {error_msg}"
                    )
                raise
            
            # Register cleanup
            atexit.register(self.client.close)
        except RetrievalError:
            # Re-raise our custom errors
            raise
        except Exception as e:
            raise RetrievalError(f"Failed to initialize Qdrant client at {settings.qdrant_path}: {e}")

        self._ensure_collection()

    def _ensure_collection(self):
        """
        Ensures the Qdrant collection exists with the correct configuration.
        Uses dynamic embedding dimension based on the configured model.
        """
        try:
            if not self.client.collection_exists(settings.collection_name):
                logger.info(f"Creating collection {settings.collection_name}...")
                # Use dynamic embedding dimension from settings
                dimension = settings.embedding_dimension
                logger.info(f"Using embedding dimension {dimension} for model {settings.embedding_model}")
                self.client.create_collection(
                    collection_name=settings.collection_name,
                    vectors_config=models.VectorParams(
                        size=dimension, 
                        distance=models.Distance.COSINE
                    ),
                )
        except Exception as e:
            raise RetrievalError(f"Failed to verify/create collection: {e}")

    def add_texts(self, texts: List[str]) -> None:
        """
        Embeds and adds texts to the vector store using FastEmbed.
        
        Args:
            texts: List of string documents to add.
        """
        if not texts:
            return

        try:
            points = [
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=models.Document(
                        text=text, 
                        model=settings.embedding_model
                    ),
                    payload={
                        "text": text,
                        "document": text # Redundant but safe for different retrieval patterns
                    }
                )
                for text in texts
            ]

            self.client.upsert(
                collection_name=settings.collection_name,
                points=points
            )
        except Exception as e:
            raise IngestionError(f"Failed to add texts to vector store: {e}")

    def search(self, query: str, limit: int = 5) -> List[str]:
        """
        Searches for relevant texts using FastEmbed.
        
        Args:
            query: The question to answer.
            limit: Number of results to return.
            
        Returns:
            List of relevant text chunks.
        """
        try:
            result = self.client.query_points(
                collection_name=settings.collection_name,
                query=models.Document(
                    text=query, 
                    model=settings.embedding_model
                ),
                limit=limit
            )
            
            hits = result.points
            
            # Extract text from payload
            return [
                hit.payload.get("text", hit.payload.get("document", "")) 
                for hit in hits 
                if hit.payload
            ]
        except Exception as e:
            raise RetrievalError(f"Search failed: {e}")
