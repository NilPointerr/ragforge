"""
Provider registry system for Ragforge.

Allows dynamic registration and retrieval of providers (LLM, Vector Store, Graph Store)
without hard-coding specific implementations.
"""

from typing import Dict, Type, Optional, TypeVar, List
from ragforge.errors import ConfigurationError

# Type variable for base classes
T = TypeVar('T')


class BaseRegistry:
    """
    Base registry class for provider management.
    """
    
    _providers: Dict[str, Type] = {}
    _instances: Dict[str, object] = {}
    
    @classmethod
    def register(cls, name: str, provider_class: Type[T]) -> None:
        """
        Register a provider class.
        
        Args:
            name: Provider name (e.g., "groq", "openai").
            provider_class: Provider class that implements the base interface.
        """
        cls._providers[name] = provider_class
    
    @classmethod
    def get_provider(cls, name: Optional[str] = None, use_singleton: bool = True) -> T:
        """
        Get a provider instance.
        
        Args:
            name: Provider name. If None, uses default from settings.
            use_singleton: If True, returns singleton instance. If False, creates new instance.
            
        Returns:
            Provider instance.
            
        Raises:
            ConfigurationError: If provider is not registered.
        """
        if name is None:
            name = cls._get_default_name()
        
        if name not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ConfigurationError(
                f"Unknown provider: '{name}'. Available providers: {available}"
            )
        
        if use_singleton:
            if name not in cls._instances:
                cls._instances[name] = cls._providers[name]()
            return cls._instances[name]
        else:
            return cls._providers[name]()
    
    @classmethod
    def list_providers(cls) -> List[str]:
        """
        List all registered provider names.
        
        Returns:
            List of provider names.
        """
        return list(cls._providers.keys())
    
    @classmethod
    def _get_default_name(cls) -> str:
        """
        Get the default provider name from settings.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _get_default_name()")
    
    @classmethod
    def clear_instances(cls) -> None:
        """
        Clear all singleton instances (useful for testing).
        """
        cls._instances.clear()


class LLMRegistry(BaseRegistry):
    """Registry for LLM providers."""
    
    @classmethod
    def _get_default_name(cls) -> str:
        from ragforge.settings import settings
        return getattr(settings, 'llm_provider', 'groq')


class VectorStoreRegistry(BaseRegistry):
    """Registry for Vector Store providers."""
    
    @classmethod
    def _get_default_name(cls) -> str:
        from ragforge.settings import settings
        return getattr(settings, 'vector_store_provider', 'qdrant')


class GraphStoreRegistry(BaseRegistry):
    """Registry for Graph Store providers."""
    
    @classmethod
    def _get_default_name(cls) -> str:
        from ragforge.settings import settings
        return getattr(settings, 'graph_store_provider', 'neo4j')
