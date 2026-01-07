import json
import logging
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

from ragforge.llm import get_default_llm
from ragforge.vector import get_vector_store
from ragforge.settings import settings
from ragforge.errors import RagforgeError
from ragforge.graph import get_graph_store
from ragforge.strategies.retrieval import (
    VectorOnlyRetrievalStrategy,
    HybridRetrievalStrategy,
)

logger = logging.getLogger(__name__)


class LLMConfig(BaseModel):
    """Configuration for LLM generation parameters."""
    temperature: float = 0.1
    top_p: float = 1.0
    max_tokens: Optional[int] = None


def ask(
    question: str,
    system_prompt: Optional[str] = None,
    use_graphrag: Optional[bool] = None,
    llm_config: Optional[LLMConfig] = None,
    retrieval_strategy: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    The main entry point for the RAG/GraphRAG pipeline.
    
    Automatically uses GraphRAG if Neo4j is configured and available,
    otherwise falls back to standard RAG. No errors or warnings are shown.
    
    Args:
        question: The user's question.
        system_prompt: Optional custom system prompt. If None, uses default from settings.
        use_graphrag: Override GraphRAG (None = auto-detect, True = force enable, False = disable).
        llm_config: Optional LLM configuration (temperature, top_p, max_tokens).
        retrieval_strategy: Optional retrieval strategy name ("vector_only" or "hybrid"). 
                           If None, uses default from settings.
        **kwargs: Additional parameters passed to retrieval strategy.
        
    Returns:
        A dictionary containing "facts" (list) and "answer" (str).
    """
    try:
        # Get system prompt
        system_prompt = system_prompt or settings.default_system_prompt
        
        # Get LLM config
        if llm_config is None:
            llm_config = LLMConfig()
        
        # Auto-detect: use GraphRAG if explicitly enabled OR if Neo4j is available
        if use_graphrag is None:
            graph_store = get_graph_store()
            use_graph = graph_store.is_available()
        else:
            use_graph = use_graphrag
        
        # Get retrieval strategy
        strategy_name = retrieval_strategy or settings.retrieval_strategy
        
        if strategy_name == "vector_only":
            strategy = VectorOnlyRetrievalStrategy()
        elif strategy_name == "hybrid":
            strategy = HybridRetrievalStrategy()
        else:
            logger.warning(f"Unknown retrieval strategy: {strategy_name}, using 'hybrid'")
            strategy = HybridRetrievalStrategy()
        
        # Get stores
        vector_store = get_vector_store()
        graph_store = get_graph_store() if use_graph else None
        
        # Retrieve documents
        retrieved_docs = strategy.retrieve(
            query=question,
            vector_store=vector_store,
            graph_store=graph_store if use_graph else None,
            limit=settings.max_context_chunks,
            **kwargs
        )
        
        if not retrieved_docs:
            return {
                "facts": [],
                "answer": "I could not find any relevant information in the knowledge base to answer your question."
            }
        
        # Build context
        context_parts = []
        if retrieved_docs:
            context_parts.append("Context:")
            context_parts.extend([f"- {doc}" for doc in retrieved_docs])
        
        context_str = "\n".join(context_parts)
        
        # Grounded Prompt
        full_prompt = f"""Context:
{context_str}

Question:
{question}

Answer (in JSON):"""

        # LLM Answer
        llm = get_default_llm()
        raw_response = llm.generate_response(
            full_prompt,
            system_prompt,
            temperature=llm_config.temperature,
            top_p=llm_config.top_p,
            max_tokens=llm_config.max_tokens
        )
        
        # Parse Response
        try:
            # Clean up potential markdown code blocks if the LLM adds them
            cleaned_response = raw_response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]

            parsed_response = json.loads(cleaned_response)

            # Validate structure
            if "facts" not in parsed_response or "answer" not in parsed_response:
                raise ValueError("Missing required keys in JSON response")

            return parsed_response

        except json.JSONDecodeError:
            logger.error(f"Failed to parse LLM response: {raw_response}")
            # Fallback if JSON parsing fails but we have a response
            return {
                "facts": [],
                "answer": raw_response
            }

    except RagforgeError as e:
        logger.error(f"Ragforge error: {e}")
        return {
            "facts": [],
            "answer": f"An error occurred while processing your request: {str(e)}"
        }
    except Exception as e:
        logger.exception("Unexpected error in ask()")
        return {
            "facts": [],
            "answer": "An unexpected system error occurred."
        }


def ingest(
    texts: List[str],
    metadatas: Optional[List[Dict[str, Any]]] = None,
    use_graphrag: Optional[bool] = None
) -> None:
    """
    Add documents to the knowledge base for retrieval.
    
    This function:
    1. Embeds texts and stores them in the vector database (Qdrant) - always
    2. Extracts entities and relationships and builds a knowledge graph (Neo4j) - if available
    
    Automatically uses GraphRAG if Neo4j is configured and available,
    otherwise uses standard RAG. No errors or warnings are shown.
    
    Args:
        texts: List of string documents to add to the knowledge base.
        metadatas: Optional list of metadata dictionaries (one per text).
        use_graphrag: Override GraphRAG (None = auto-detect, True = force enable, False = disable).
        
    Raises:
        IngestionError: If document ingestion fails.
        
    Example:
        >>> ingest([
        ...     "Python is a programming language.",
        ...     "RAG stands for Retrieval Augmented Generation."
        ... ])
        
        >>> # With metadata
        >>> ingest(
        ...     ["Document 1", "Document 2"],
        ...     metadatas=[{"source": "book1"}, {"source": "book2"}]
        ... )
    """
    # Auto-detect: use GraphRAG if explicitly enabled OR if Neo4j is available
    if use_graphrag is None:
        graph_store = get_graph_store()
        use_graph = graph_store.is_available()
    else:
        use_graph = use_graphrag
    
    # 1. Vector Store Ingestion (always)
    store = get_vector_store()
    store.add_texts(texts, metadatas=metadatas)
    
    # 2. Graph Construction (if available)
    if use_graph:
        try:
            graph_store = get_graph_store()
            if graph_store.is_available():
                logger.debug(f"Building knowledge graph for {len(texts)} documents...")
                
                for i, text in enumerate(texts):
                    if text.strip():  # Skip empty texts
                        graph_store.add_document_to_graph(text, doc_id=f"doc_{i}")
                
                logger.debug("Knowledge graph construction complete")
        except Exception:
            # Silently fallback - no error logging
            pass
