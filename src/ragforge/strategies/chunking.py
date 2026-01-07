"""
Text chunking strategies for Ragforge.
"""

import re
from typing import List
from ragforge.core.base import BaseChunkingStrategy


class SentenceChunkingStrategy(BaseChunkingStrategy):
    """
    Chunks text at sentence boundaries when possible.
    Falls back to character-based chunking if sentences are too long.
    """
    
    def chunk(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int = 0,
        **kwargs
    ) -> List[str]:
        """
        Split text into chunks, preferring sentence boundaries.
        
        Args:
            text: The text to chunk.
            chunk_size: Size of each chunk in characters.
            chunk_overlap: Number of characters to overlap between chunks.
            **kwargs: Additional parameters (ignored).
            
        Returns:
            List of text chunks.
        """
        if chunk_size <= 0:
            return [text]
        
        if chunk_overlap >= chunk_size:
            chunk_overlap = chunk_size - 1
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary if not at end
            if end < text_length and chunk_size > 100:
                # Look for sentence endings in the last 20% of chunk
                search_start = max(0, chunk_size - chunk_size // 5)
                for i in range(len(chunk) - 1, search_start, -1):
                    if chunk[i] in '.!?\n':
                        chunk = chunk[:i+1]
                        end = start + len(chunk)
                        break
            
            chunks.append(chunk.strip())
            
            # Move start position with overlap
            start = end - chunk_overlap if chunk_overlap > 0 else end
            
            # Prevent infinite loop
            if start >= text_length:
                break
        
        return [chunk for chunk in chunks if chunk]  # Remove empty chunks


class CharacterChunkingStrategy(BaseChunkingStrategy):
    """
    Simple character-based chunking without sentence boundary detection.
    """
    
    def chunk(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int = 0,
        **kwargs
    ) -> List[str]:
        """
        Split text into fixed-size chunks.
        
        Args:
            text: The text to chunk.
            chunk_size: Size of each chunk in characters.
            chunk_overlap: Number of characters to overlap between chunks.
            **kwargs: Additional parameters (ignored).
            
        Returns:
            List of text chunks.
        """
        if chunk_size <= 0:
            return [text]
        
        if chunk_overlap >= chunk_size:
            chunk_overlap = chunk_size - 1
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk.strip())
            
            # Move start position with overlap
            start = end - chunk_overlap if chunk_overlap > 0 else end
            
            # Prevent infinite loop
            if start >= text_length:
                break
        
        return [chunk for chunk in chunks if chunk]  # Remove empty chunks
