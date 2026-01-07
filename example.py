import os
import sys
from ragforge import ask, ingest
from dotenv import load_dotenv

load_dotenv()

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
        "Ragforge is a Python package for zero-config RAG pipelines.",
        """Shivaji was born in the hill-fort of Shivneri, near Junnar, which is now in Pune district. Scholars disagree on his date of birth; the Government of Maharashtra lists 19 February as a holiday commemorating Shivaji's birth (Shivaji Jayanti).[a][26][27] Shivaji was named after a local deity, the Goddess Shivai Devi."""
    ]
    ingest(knowledge)
    print("Ingestion complete.")

    # Ask a question
    question = "what is shivaji's birthplace?"
    print(f"\nQuestion: {question}")
    
    result = ask(question)
    
    print("\n--- Result ---")
    print(f"Answer: {result['answer']}")
    print(f"Facts Used: {result['facts']}")

if __name__ == "__main__":
    main()
