"""
Example demonstrating file ingestion functionality.

This example shows how to ingest text from files into the knowledge base.
Works with both GraphRAG and standard RAG automatically.
"""

import os
import sys
from pathlib import Path
from ragforge import ask, ingest_from_file, ingest_from_directory
from dotenv import load_dotenv

load_dotenv()

def main():
    # Ensure API key is set
    if not os.getenv("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY environment variable not set.")
        sys.exit(1)

    print("=== Ragforge File Ingestion Example ===\n")

    # Example 1: Ingest a single text file
    print("Example 1: Ingesting a single file")
    print("-" * 50)
    
    # Create a sample text file for demonstration
    sample_file = Path("sample_knowledge.txt")
    sample_content = """GraphRAG is an advanced RAG technique developed by Microsoft Research.
It combines knowledge graphs with Large Language Models to improve retrieval.
GraphRAG uses Neo4j for storing knowledge graphs and Qdrant for vector storage.
Shivaji Maharaj was born in Shivneri fort, near Junnar in Pune district.
The Maratha Empire was founded by Shivaji Maharaj in the 17th century.
Ragforge is a Python package that simplifies RAG and GraphRAG implementation."""
    
    # Write sample file
    sample_file.write_text(sample_content)
    print(f"Created sample file: {sample_file}")
    
    try:
        # Ingest the file (automatically uses GraphRAG if Neo4j available)
        ingest_from_file(sample_file)
        print(f"✅ Successfully ingested {sample_file}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    # Example 2: Ingest with chunking (for large files)
    print("Example 2: Ingesting with chunking")
    print("-" * 50)
    
    large_file = Path("large_document.txt")
    large_content = "\n\n".join([
        f"Document section {i}: This is a large document that needs to be chunked. "
        f"Each section contains important information about topic {i}."
        for i in range(1, 6)
    ])
    
    large_file.write_text(large_content)
    print(f"Created large file: {large_file}")
    
    try:
        # Ingest with chunking (1000 chars per chunk, 100 char overlap)
        ingest_from_file(
            large_file,
            chunk_size=1000,
            chunk_overlap=100
        )
        print(f"✅ Successfully ingested {large_file} with chunking\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    # Example 3: Ingest entire directory
    print("Example 3: Ingesting all files from a directory")
    print("-" * 50)
    
    docs_dir = Path("documents")
    docs_dir.mkdir(exist_ok=True)
    
    # Create multiple sample files
    for i in range(1, 4):
        doc_file = docs_dir / f"doc_{i}.txt"
        doc_file.write_text(f"Document {i} content: This is document number {i} with important information.")
    
    print(f"Created {len(list(docs_dir.glob('*.txt')))} files in {docs_dir}/")
    
    try:
        count = ingest_from_directory(
            docs_dir,
            pattern="*.txt",
            recursive=False
        )
        print(f"✅ Successfully ingested {count} file(s) from {docs_dir}/\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    # Example 4: Query the ingested knowledge
    print("Example 4: Querying ingested knowledge")
    print("-" * 50)
    
    questions = [
        "What is GraphRAG?",
        "Where was Shivaji Maharaj born?",
        "What does Ragforge use for storage?",
    ]
    
    for question in questions:
        print(f"\nQuestion: {question}")
        try:
            result = ask(question)
            print(f"Answer: {result['answer']}")
            if result.get('facts'):
                print(f"Facts: {result['facts'][:2]}")
        except Exception as e:
            print(f"Error: {e}")
    
    # Cleanup
    print("\n" + "=" * 50)
    print("Cleaning up sample files...")
    if sample_file.exists():
        sample_file.unlink()
    if large_file.exists():
        large_file.unlink()
    if docs_dir.exists():
        import shutil
        shutil.rmtree(docs_dir)
    print("✅ Cleanup complete")

if __name__ == "__main__":
    main()
