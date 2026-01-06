import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """
    Global settings for the Ragforge package.
    Loads configuration from environment variables.
    """
    
    # LLM Settings
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    LLM_MODEL: str = os.getenv("RAGFORGE_LLM_MODEL", "llama-3.3-70b-versatile")
    LLM_TIMEOUT: int = int(os.getenv("RAGFORGE_LLM_TIMEOUT", "30"))
    LLM_MAX_RETRIES: int = int(os.getenv("RAGFORGE_LLM_RETRIES", "3"))

    # Vector Store Settings
    QDRANT_PATH: str = os.getenv("RAGFORGE_QDRANT_PATH", "./qdrant_data")
    COLLECTION_NAME: str = "ragforge_knowledge_base"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # RAG Settings
    MAX_CONTEXT_CHUNKS: int = int(os.getenv("RAGFORGE_MAX_CHUNKS", "5"))

    @classmethod
    def validate(cls) -> None:
        """
        Validates critical configuration.
        """
        if not cls.GROQ_API_KEY:
            # We don't raise here immediately to allow import, 
            # but we will raise when the LLM is initialized.
            pass

settings = Settings()
