import json
import logging
from typing import Dict, List, Any, Optional

from ragforge.llm import get_default_llm
from ragforge.vector import get_vector_store
from ragforge.settings import settings
from ragforge.errors import RagforgeError
from ragforge.graph import get_graph_store

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a precise and helpful assistant.
You must answer the user's question ONLY using the provided context facts.
Do not use outside knowledge.
If the facts do not contain the answer, state that you cannot answer based on the available information.

Your output must be a valid JSON object with exactly two keys:
1. "facts": A list of strings, where each string is a specific fact from the context used to answer the question.
2. "answer": A string containing the final answer.

Example format:
{
  "facts": ["GraphRAG is a method...", "It uses knowledge graphs..."],
  "answer": "GraphRAG is a method that uses knowledge graphs..."
}
"""

def ask(question: str, use_graphrag: Optional[bool] = None) -> Dict[str, Any]:
    """
    The main entry point for the RAG/GraphRAG pipeline.
    
    Automatically uses GraphRAG if Neo4j is configured and available,
    otherwise falls back to standard RAG. No errors or warnings are shown.
    
    Args:
        question: The user's question.
        use_graphrag: Override GraphRAG (None = auto-detect, True = force enable, False = disable).
        
    Returns:
        A dictionary containing "facts" (list) and "answer" (str).
    """
    try:
        # Auto-detect: use GraphRAG if explicitly enabled OR if Neo4j is available
        if use_graphrag is None:
            # Auto-detect: check if GraphRAG is available
            graph_store = get_graph_store()
            use_graph = (graph_store.driver is not None)
        else:
            use_graph = use_graphrag
        
        # 1. Vector Retrieval
        store = get_vector_store()
        retrieved_docs = store.search(question, limit=settings.max_context_chunks)
        
        # 2. Graph Retrieval (if available)
        graph_context = ""
        if use_graph:
            try:
                graph_store = get_graph_store()
                # Only try graph retrieval if Neo4j is actually connected
                if graph_store.driver is not None:
                    graph_context = graph_store.get_graph_context(question, max_entities=5)
            except Exception:
                # Silently fallback - no error logging
                pass
        
        # 3. Context Construction
        context_parts = []
        
        if retrieved_docs:
            context_parts.append("Vector Search Results:")
            context_parts.extend([f"- {doc}" for doc in retrieved_docs])
        
        if graph_context:
            context_parts.append("")
            context_parts.append(graph_context)
        
        if not context_parts:
            return {
                "facts": [],
                "answer": "I could not find any relevant information in the knowledge base to answer your question."
            }
        
        context_str = "\n".join(context_parts)
        
        # 4. Grounded Prompt
        full_prompt = f"""Context:
{context_str}

Question:
{question}

Answer (in JSON):"""

        # 5. LLM Answer
        llm = get_default_llm()
        raw_response = llm.generate_response(full_prompt, SYSTEM_PROMPT)
        
        # 6. Parse Response
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
                "answer": raw_response # Return raw response as best effort, or fallback error
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

def ingest(texts: List[str], use_graphrag: Optional[bool] = None) -> None:
    """
    Add documents to the knowledge base for retrieval.
    
    This function:
    1. Embeds texts and stores them in the vector database (Qdrant) - always
    2. Extracts entities and relationships and builds a knowledge graph (Neo4j) - if available
    
    Automatically uses GraphRAG if Neo4j is configured and available,
    otherwise uses standard RAG. No errors or warnings are shown.
    
    Args:
        texts: List of string documents to add to the knowledge base.
        use_graphrag: Override GraphRAG (None = auto-detect, True = force enable, False = disable).
        
    Raises:
        IngestionError: If document ingestion fails.
        
    Example:
        >>> ingest([
        ...     "Python is a programming language.",
        ...     "RAG stands for Retrieval Augmented Generation."
        ... ])
    """
    # Auto-detect: use GraphRAG if explicitly enabled OR if Neo4j is available
    if use_graphrag is None:
        # Auto-detect: check if GraphRAG is available
        graph_store = get_graph_store()
        use_graph = (graph_store.driver is not None)
    else:
        use_graph = use_graphrag
    
    # 1. Vector Store Ingestion (always)
    store = get_vector_store()
    store.add_texts(texts)
    
    # 2. Graph Construction (if available)
    if use_graph:
        try:
            graph_store = get_graph_store()
            # Check if GraphStore actually has a connection (Neo4j might be unavailable)
            if graph_store.driver is not None:
                logger.debug(f"Building knowledge graph for {len(texts)} documents...")
                
                for i, text in enumerate(texts):
                    if text.strip():  # Skip empty texts
                        graph_store.add_document_to_graph(text, doc_id=f"doc_{i}")
                
                logger.debug("Knowledge graph construction complete")
        except Exception:
            # Silently fallback - no error logging
            pass