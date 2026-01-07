import json
import logging
from typing import Dict, List, Any

from ragforge.llm import get_default_llm
from ragforge.vector import get_vector_store
from ragforge.settings import settings
from ragforge.errors import RagforgeError

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

def ask(question: str) -> Dict[str, Any]:
    """
    The main entry point for the RAG pipeline.
    
    Args:
        question: The user's question.
        
    Returns:
        A dictionary containing "facts" (list) and "answer" (str).
    """
    try:
        # 1. Vector Retrieval
        store = get_vector_store()
        retrieved_docs = store.search(question, limit=settings.max_context_chunks)
        
        if not retrieved_docs:
            return {
                "facts": [],
                "answer": "I could not find any relevant information in the knowledge base to answer your question."
            }

        # 2. Context Construction
        context_str = "\n".join([f"- {doc}" for doc in retrieved_docs])
        
        # 3. Grounded Prompt
        full_prompt = f"""Context:
{context_str}

Question:
{question}

Answer (in JSON):"""

        # 4. LLM Answer
        llm = get_default_llm()
        raw_response = llm.generate_response(full_prompt, SYSTEM_PROMPT)
        
        # 5. Parse Response
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

def ingest(texts: List[str]) -> None:
    """
    Add documents to the knowledge base for retrieval.
    
    This function embeds the provided texts and stores them in the vector database.
    After ingestion, these documents can be retrieved when answering questions.
    
    Args:
        texts: List of string documents to add to the knowledge base.
        
    Raises:
        IngestionError: If document ingestion fails.
        
    Example:
        >>> ingest([
        ...     "Python is a programming language.",
        ...     "RAG stands for Retrieval Augmented Generation."
        ... ])
    """
    store = get_vector_store()
    store.add_texts(texts)
