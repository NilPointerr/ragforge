from ragforge.llm.groq import GroqLLM
from ragforge.llm.base import BaseLLM

def get_default_llm() -> BaseLLM:
    """
    Returns the default LLM provider (Groq).
    """
    return GroqLLM()
