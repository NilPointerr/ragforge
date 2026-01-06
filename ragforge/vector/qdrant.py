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
    """
    
    def __init__(self):
        # Initialize Qdrant Client (Local)
        try:
            os.makedirs(settings.QDRANT_PATH, exist_ok=True)
            self.client = QdrantClient(path=settings.QDRANT_PATH)
            # Set the model on the client to ensure it's loaded/configured
            self.client.set_model(settings.EMBEDDING_MODEL)
            
            # Register cleanup
            atexit.register(self.client.close)
        except Exception as e:
            raise RetrievalError(f"Failed to initialize Qdrant client at {settings.QDRANT_PATH}: {e}")

        self._ensure_collection()

    def _ensure_collection(self):
        """
        Ensures the Qdrant collection exists with the correct configuration.
        """
        try:
            if not self.client.collection_exists(settings.COLLECTION_NAME):
                logger.info(f"Creating collection {settings.COLLECTION_NAME}...")
                # We use unnamed vectors for simplicity with FastEmbed integration via Document
                # 384 is the dimension for all-MiniLM-L6-v2. 
                # TODO: If user changes model, this might break if dimension differs.
                # But for "opinionated defaults", this is fine.
                self.client.create_collection(
                    collection_name=settings.COLLECTION_NAME,
                    vectors_config=models.VectorParams(
                        size=384, 
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
                        model=settings.EMBEDDING_MODEL
                    ),
                    payload={
                        "text": text,
                        "document": text # Redundant but safe for different retrieval patterns
                    }
                )
                for text in texts
            ]

            self.client.upsert(
                collection_name=settings.COLLECTION_NAME,
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
                collection_name=settings.COLLECTION_NAME,
                query=models.Document(
                    text=query, 
                    model=settings.EMBEDDING_MODEL
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
