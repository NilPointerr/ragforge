from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseLLM(ABC):
    """
    Abstract base class for LLM providers.
    Enforces a consistent interface for the RAG pipeline.
    
    All LLM implementations must inherit from this class and implement
    the generate_response method.
    """

    @abstractmethod
    def generate_response(self, prompt: str, system_prompt: str) -> str:
        """
        Generates a response from the LLM.
        
        Args:
            prompt: The user query + context.
            system_prompt: Instructions for the LLM behavior.
            
        Returns:
            The raw string response from the LLM.
            
        Raises:
            ProviderError: If the LLM provider fails to generate a response.
        """
        pass
