import os
import sys
from ragforge import ask, ingest

def main():
    # Ensure API key is set for the demo
    if not os.getenv("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY environment variable not set.")
        sys.exit(1)

    print("Initializing Ragforge...")

    # Ingest some dummy data
    print("Ingesting knowledge...")
    knowledge = [
        "GraphRAG is an advanced RAG technique developed by Microsoft Research.",
        "It combines knowledge graphs with Large Language Models to improve retrieval.",
        "Standard RAG often fails on global questions that require understanding the whole dataset.",
        "GraphRAG builds a hierarchical summary of the data using community detection.",
        "Ragforge is a Python package for zero-config RAG pipelines."
    ]
    ingest(knowledge)
    print("Ingestion complete.")

    # Ask a question
    question = "What is GraphRAG and how does it differ from standard RAG?"
    print(f"\nQuestion: {question}")
    
    result = ask(question)
    
    print("\n--- Result ---")
    print(f"Answer: {result['answer']}")
    print(f"Facts Used: {result['facts']}")

if __name__ == "__main__":
    main()
