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
    
    Uses hybrid retrieval combining vector search and knowledge graph traversal
    when GraphRAG is enabled.
    
    Args:
        question: The user's question.
        use_graphrag: Override GraphRAG setting (None uses settings.enable_graphrag).
        
    Returns:
        A dictionary containing "facts" (list) and "answer" (str).
    """
    try:
        use_graph = use_graphrag if use_graphrag is not None else settings.enable_graphrag
        
        # 1. Vector Retrieval
        store = get_vector_store()
        retrieved_docs = store.search(question, limit=settings.max_context_chunks)
        
        # 2. Graph Retrieval (if enabled)
        graph_context = ""
        if use_graph:
            try:
                graph_store = get_graph_store()
                graph_context = graph_store.get_graph_context(question, max_entities=5)
                if graph_context:
                    logger.info("Retrieved graph context for query")
            except Exception as e:
                logger.warning(f"GraphRAG retrieval failed, continuing with vector search only: {e}")
        
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
    1. Embeds texts and stores them in the vector database (Qdrant)
    2. Extracts entities and relationships and builds a knowledge graph (Neo4j) if GraphRAG is enabled
    
    After ingestion, these documents can be retrieved when answering questions using
    both vector similarity search and graph traversal.
    
    Args:
        texts: List of string documents to add to the knowledge base.
        use_graphrag: Override GraphRAG setting (None uses settings.enable_graphrag).
        
    Raises:
        IngestionError: If document ingestion fails.
        GraphError: If graph construction fails (when GraphRAG is enabled).
        
    Example:
        >>> ingest([
        ...     "Python is a programming language.",
        ...     "RAG stands for Retrieval Augmented Generation."
        ... ])
    """
    use_graph = use_graphrag if use_graphrag is not None else settings.enable_graphrag
    
    # 1. Vector Store Ingestion (always)
    store = get_vector_store()
    store.add_texts(texts)
    
    # 2. Graph Construction (if enabled)
    if use_graph:
        try:
            graph_store = get_graph_store()
            logger.info(f"Building knowledge graph for {len(texts)} documents...")
            
            for i, text in enumerate(texts):
                if text.strip():  # Skip empty texts
                    graph_store.add_document_to_graph(text, doc_id=f"doc_{i}")
                    logger.debug(f"Processed document {i+1}/{len(texts)} for graph")
            
            logger.info("Knowledge graph construction complete")
        except Exception as e:
            logger.error(f"Graph construction failed: {e}")
            # Don't fail completely - vector search still works
            if settings.enable_graphrag:
                raise  # Only raise if GraphRAG was explicitly enabled