"""
Core abstractions and interfaces for Ragforge.

This module provides base classes and interfaces that all providers must implement,
ensuring a consistent API across different implementations.
"""

from ragforge.core.base import (
    BaseLLM,
    BaseVectorStore,
    BaseGraphStore,
    BaseChunkingStrategy,
    BaseRetrievalStrategy,
)
from ragforge.core.registry import (
    LLMRegistry,
    VectorStoreRegistry,
    GraphStoreRegistry,
)

__all__ = [
    "BaseLLM",
    "BaseVectorStore",
    "BaseGraphStore",
    "BaseChunkingStrategy",
    "BaseRetrievalStrategy",
    "LLMRegistry",
    "VectorStoreRegistry",
    "GraphStoreRegistry",
]
