from ragforge.llm.groq import GroqLLM
from ragforge.llm.base import BaseLLM

_llm_instance = None

def get_default_llm() -> BaseLLM:
    """
    Returns the singleton instance of the default LLM provider (Groq).
    Reuses the same instance across calls to avoid creating multiple connections.
    
    Returns:
        BaseLLM: The singleton LLM instance.
    """
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = GroqLLM()
    return _llm_instance
