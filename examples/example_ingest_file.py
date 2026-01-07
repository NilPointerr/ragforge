"""
Example demonstrating the new ingest_file() function.

This function is a simplified way to ingest text files with
specified chunk size and gap size parameters.
"""

import os
import sys
from pathlib import Path
from ragforge import ask, ingest_file
from dotenv import load_dotenv

load_dotenv()

def main():
    # Ensure API key is set
    if not os.getenv("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY environment variable not set.")
        sys.exit(1)

    print("=== Ragforge ingest_file() Example ===\n")

    # Create a sample text file
    sample_file = Path("sample_document.txt")
    sample_content = """GraphRAG is an advanced RAG technique developed by Microsoft Research.
It combines knowledge graphs with Large Language Models to improve retrieval.
GraphRAG uses Neo4j for storing knowledge graphs and Qdrant for vector storage.
Shivaji Maharaj was born in Shivneri fort, near Junnar in Pune district.
The Maratha Empire was founded by Shivaji Maharaj in the 17th century.
Ragforge is a Python package that simplifies RAG and GraphRAG implementation.
This is a longer document that will be chunked into smaller pieces.
Each chunk will help improve retrieval accuracy and context understanding."""
    
    sample_file.write_text(sample_content)
    print(f"Created sample file: {sample_file}")
    print(f"File size: {len(sample_content)} characters\n")

    # Example 1: Ingest with chunking and gap
    print("Example 1: Ingest with chunk_size=200 and gap_size=50")
    print("-" * 50)
    try:
        ingest_file(
            sample_file,
            chunk_size=200,
            gap_size=50
        )
        print("✅ Successfully ingested with chunking\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")

    # Example 2: Ingest with chunking but no gap
    print("Example 2: Ingest with chunk_size=300 and gap_size=0 (no overlap)")
    print("-" * 50)
    try:
        ingest_file(
            sample_file,
            chunk_size=300,
            gap_size=0
        )
        print("✅ Successfully ingested without gap\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")

    # Example 3: Query the ingested knowledge
    print("Example 3: Querying ingested knowledge")
    print("-" * 50)
    
    questions = [
        "What is GraphRAG?",
        "Where was Shivaji Maharaj born?",
    ]
    
    for question in questions:
        print(f"\nQuestion: {question}")
        try:
            result = ask(question)
            print(f"Answer: {result['answer']}")
        except Exception as e:
            print(f"Error: {e}")
    
    # Cleanup
    print("\n" + "=" * 50)
    if sample_file.exists():
        sample_file.unlink()
        print("✅ Cleaned up sample file")

if __name__ == "__main__":
    main()
