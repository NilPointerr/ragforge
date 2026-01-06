from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseLLM(ABC):
    """
    Abstract base class for LLM providers.
    Enforces a consistent interface for the RAG pipeline.
    """

    @abstractmethod
    def generate_response(self, prompt: str, system_prompt: str) -> str:
        """
        Generates a response from the LLM.
        
        Args:
            prompt: The user query + context.
            system_prompt: Instructions for the LLM.
            
        Returns:
            The raw string response from the LLM.
        """
        pass
