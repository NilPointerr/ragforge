"""
Utility functions for Ragforge package.
Provides file handling and text processing utilities.
"""

import logging
import os
from typing import List, Optional, Union
from pathlib import Path

from ragforge.rag import ingest
from ragforge.errors import IngestionError

logger = logging.getLogger(__name__)


def ingest_from_file(
    file_path: Union[str, Path],
    chunk_size: Optional[int] = None,
    chunk_overlap: int = 0,
    encoding: str = "utf-8",
    use_graphrag: Optional[bool] = None
) -> None:
    """
    Extract text from a file and ingest it into the knowledge base.
    
    Works with both GraphRAG and standard RAG automatically.
    The function reads the file, optionally chunks it, and calls ingest()
    which handles both vector embeddings and graph construction.
    
    Args:
        file_path: Path to the text file (.txt) to ingest.
        chunk_size: Optional chunk size for splitting large files. 
                   If None, entire file is ingested as one document.
        chunk_overlap: Number of characters to overlap between chunks (default: 0).
        encoding: File encoding (default: 'utf-8').
        use_graphrag: Override GraphRAG setting (None = auto-detect).
        
    Raises:
        FileNotFoundError: If the file doesn't exist.
        IngestionError: If ingestion fails.
        ValueError: If file_path is invalid.
        
    Example:
        >>> # Ingest entire file
        >>> ingest_from_file("documents/knowledge.txt")
        
        >>> # Ingest with chunking (for large files)
        >>> ingest_from_file("documents/large_file.txt", chunk_size=1000, chunk_overlap=100)
        
        >>> # Force standard RAG (no GraphRAG)
        >>> ingest_from_file("documents/knowledge.txt", use_graphrag=False)
    """
    file_path = Path(file_path)
    
    # Validate file exists
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Validate it's a file
    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    
    # Read file content
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()
    except UnicodeDecodeError as e:
        raise IngestionError(
            f"Failed to decode file {file_path} with encoding {encoding}. "
            f"Try a different encoding. Error: {e}"
        )
    except Exception as e:
        raise IngestionError(f"Failed to read file {file_path}: {e}")
    
    if not content.strip():
        logger.warning(f"File {file_path} is empty. Skipping ingestion.")
        return
    
    # Chunk the content if chunk_size is specified
    if chunk_size and chunk_size > 0:
        texts = _chunk_text(content, chunk_size, chunk_overlap)
        logger.info(f"Split file into {len(texts)} chunks")
    else:
        texts = [content]
    
    # Ingest using the main ingest function (handles both vector and graph)
    try:
        ingest(texts, use_graphrag=use_graphrag)
        logger.info(f"Successfully ingested {file_path} ({len(texts)} document(s))")
    except Exception as e:
        raise IngestionError(f"Failed to ingest file {file_path}: {e}")


def ingest_from_directory(
    directory_path: Union[str, Path],
    pattern: str = "*.txt",
    chunk_size: Optional[int] = None,
    chunk_overlap: int = 0,
    encoding: str = "utf-8",
    recursive: bool = True,
    use_graphrag: Optional[bool] = None
) -> int:
    """
    Extract text from all matching files in a directory and ingest them.
    
    Works with both GraphRAG and standard RAG automatically.
    
    Args:
        directory_path: Path to the directory containing text files.
        pattern: File pattern to match (default: '*.txt').
        chunk_size: Optional chunk size for splitting large files.
        chunk_overlap: Number of characters to overlap between chunks.
        encoding: File encoding (default: 'utf-8').
        recursive: Whether to search subdirectories (default: True).
        use_graphrag: Override GraphRAG setting (None = auto-detect).
        
    Returns:
        Number of files successfully ingested.
        
    Raises:
        FileNotFoundError: If the directory doesn't exist.
        IngestionError: If ingestion fails.
        
    Example:
        >>> # Ingest all .txt files in a directory
        >>> count = ingest_from_directory("documents/")
        >>> print(f"Ingested {count} files")
        
        >>> # Ingest only .md files recursively
        >>> ingest_from_directory("docs/", pattern="*.md", recursive=True)
    """
    directory_path = Path(directory_path)
    
    # Validate directory exists
    if not directory_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")
    
    if not directory_path.is_dir():
        raise ValueError(f"Path is not a directory: {directory_path}")
    
    # Find all matching files
    if recursive:
        files = list(directory_path.rglob(pattern))
    else:
        files = list(directory_path.glob(pattern))
    
    if not files:
        logger.warning(f"No files matching pattern '{pattern}' found in {directory_path}")
        return 0
    
    logger.info(f"Found {len(files)} file(s) matching pattern '{pattern}'")
    
    # Ingest each file
    success_count = 0
    for file_path in files:
        try:
            ingest_from_file(
                file_path,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                encoding=encoding,
                use_graphrag=use_graphrag
            )
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to ingest {file_path}: {e}")
            # Continue with other files
    
    logger.info(f"Successfully ingested {success_count}/{len(files)} file(s)")
    return success_count


def ingest_file(
    file_path: Union[str, Path],
    chunk_size: int,
    gap_size: int = 0,
    encoding: str = "utf-8",
    use_graphrag: Optional[bool] = None
) -> None:
    """
    Ingest a text file with specified chunk size and gap size.
    
    A simplified function for ingesting files with chunking parameters.
    Works with both GraphRAG and standard RAG automatically.
    
    Args:
        file_path: Path to the text file to ingest.
        chunk_size: Size of each chunk in characters.
        gap_size: Gap/overlap size between chunks in characters (default: 0).
        encoding: File encoding (default: 'utf-8').
        use_graphrag: Override GraphRAG (None = auto-detect).
        
    Raises:
        FileNotFoundError: If the file doesn't exist.
        IngestionError: If ingestion fails.
        
    Example:
        >>> # Ingest file with 1000 char chunks and 100 char gap
        >>> ingest_file("document.txt", chunk_size=1000, gap_size=100)
        
        >>> # Ingest with no gap between chunks
        >>> ingest_file("document.txt", chunk_size=500, gap_size=0)
    """
    file_path = Path(file_path)
    
    # Validate file exists
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    
    # Read file content
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()
    except UnicodeDecodeError as e:
        raise IngestionError(
            f"Failed to decode file {file_path} with encoding {encoding}. "
            f"Try a different encoding. Error: {e}"
        )
    except Exception as e:
        raise IngestionError(f"Failed to read file {file_path}: {e}")
    
    if not content.strip():
        logger.warning(f"File {file_path} is empty. Skipping ingestion.")
        return
    
    # Chunk the content
    texts = _chunk_text(content, chunk_size, gap_size)
    logger.info(f"Split file {file_path} into {len(texts)} chunks (chunk_size={chunk_size}, gap_size={gap_size})")
    
    # Ingest using the main ingest function
    try:
        ingest(texts, use_graphrag=use_graphrag)
        logger.info(f"Successfully ingested {file_path} ({len(texts)} chunk(s))")
    except Exception as e:
        raise IngestionError(f"Failed to ingest file {file_path}: {e}")


def _chunk_text(text: str, chunk_size: int, chunk_overlap: int = 0) -> List[str]:
    """
    Split text into chunks with optional overlap.
    
    Args:
        text: The text to chunk.
        chunk_size: Size of each chunk in characters.
        chunk_overlap: Number of characters to overlap between chunks.
        
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
