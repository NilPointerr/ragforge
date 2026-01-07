from ragforge.llm.groq import GroqLLM
from ragforge.core.base import BaseLLM
from ragforge.core.registry import LLMRegistry

# Register default providers
LLMRegistry.register("groq", GroqLLM)

def get_default_llm() -> BaseLLM:
    """
    Returns the singleton instance of the default LLM provider.
    Uses the registry to get the configured provider.
    
    Returns:
        BaseLLM: The singleton LLM instance.
    """
    return LLMRegistry.get_provider(use_singleton=True)
