import os
from typing import Optional, Dict
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Embedding model dimensions mapping
EMBEDDING_DIMENSIONS: Dict[str, int] = {
    "sentence-transformers/all-MiniLM-L6-v2": 384,
    "sentence-transformers/all-mpnet-base-v2": 768,
    "sentence-transformers/all-MiniLM-L12-v2": 384,
    # Add more models as needed
}


class Settings(BaseSettings):
    """
    Global settings for the Ragforge package.
    Loads configuration from environment variables with validation.
    """
    
    # LLM Settings
    groq_api_key: Optional[str] = Field(None, env="GROQ_API_KEY", description="Groq API key for LLM access")
    llm_model: str = Field(
        "llama-3.3-70b-versatile", 
        env="RAGFORGE_LLM_MODEL",
        description="LLM model to use for generation"
    )
    llm_timeout: int = Field(
        30, 
        env="RAGFORGE_LLM_TIMEOUT", 
        gt=0,
        description="Timeout in seconds for LLM API calls"
    )
    llm_max_retries: int = Field(
        3, 
        env="RAGFORGE_LLM_RETRIES", 
        ge=1, 
        le=10,
        description="Maximum number of retries for LLM API calls"
    )

    # Vector Store Settings
    qdrant_path: str = Field(
        "./qdrant_data", 
        env="RAGFORGE_QDRANT_PATH",
        description="Path to local Qdrant storage directory"
    )
    fastembed_cache_path: str = Field(
        "./.fastembed_cache", 
        env="RAGFORGE_FASTEMBED_CACHE_PATH",
        description="Path to FastEmbed model cache directory"
    )
    collection_name: str = Field(
        "ragforge_knowledge_base",
        description="Name of the Qdrant collection"
    )
    embedding_model: str = Field(
        "sentence-transformers/all-MiniLM-L6-v2",
        env="RAGFORGE_EMBEDDING_MODEL",
        description="Embedding model identifier. Must be a supported FastEmbed model."
    )
    
    # RAG Settings
    max_context_chunks: int = Field(
        5, 
        env="RAGFORGE_MAX_CHUNKS", 
        ge=1, 
        le=50,
        description="Maximum number of context chunks to retrieve"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    @property
    def embedding_dimension(self) -> int:
        """
        Returns the embedding dimension for the configured model.
        
        Returns:
            The dimension size for the embedding model, or 384 as fallback.
        """
        return EMBEDDING_DIMENSIONS.get(self.embedding_model, 384)
    
    def validate_config(self) -> None:
        """
        Validates critical configuration.
        Note: API key validation happens at LLM initialization to allow import without key.
        """
        # Additional validation can be added here if needed
        pass


# Create global settings instance
settings = Settings()

# Set the environment variable for FastEmbed to ensure it uses the configured cache path
os.environ["FASTEMBED_CACHE_PATH"] = settings.fastembed_cache_path
