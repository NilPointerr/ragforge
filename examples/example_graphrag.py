"""
Example demonstrating GraphRAG functionality with Ragforge.

This example shows how to use GraphRAG for better retrieval
by combining vector search with knowledge graph traversal.

Prerequisites:
1. Neo4j running (see README for Docker setup)
2. GROQ_API_KEY environment variable set
3. RAGFORGE_NEO4J_PASSWORD environment variable set
"""

import os
import sys
from ragforge import ask, ingest
from dotenv import load_dotenv

load_dotenv()

def main():
    # Ensure API key is set
    if not os.getenv("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY environment variable not set.")
        sys.exit(1)
    
    # Check if Neo4j is configured
    neo4j_password = os.getenv("RAGFORGE_NEO4J_PASSWORD")
    if not neo4j_password:
        print("Warning: RAGFORGE_NEO4J_PASSWORD not set. GraphRAG will be disabled.")
        print("Set it to enable GraphRAG functionality.")
        use_graphrag = False
    else:
        use_graphrag = True
        print("GraphRAG enabled! Knowledge graph will be built during ingestion.")

    print("\n=== Ragforge GraphRAG Example ===\n")

    # Knowledge with entities and relationships
    knowledge = [
        "Microsoft Research developed GraphRAG, an advanced RAG technique.",
        "GraphRAG combines knowledge graphs with Large Language Models.",
        "Shivaji Maharaj was born in Shivneri fort, near Junnar in Pune district.",
        "Shivaji Maharaj founded the Maratha Empire in the 17th century.",
        "The Maratha Empire was established in the Deccan region of India.",
        "GraphRAG improves upon standard RAG by using graph structures.",
        "Neo4j is a graph database used for storing knowledge graphs.",
        "Ragforge uses Neo4j for GraphRAG and Qdrant for vector storage.",
        "nilesh rajgor birthdate is 6 of march 2002",
        "nilesh rajgor is a software engineer,he joined infusion analyst on 2 january 2023",
    ]
    
    print("Ingesting knowledge with GraphRAG...")
    ingest(knowledge, use_graphrag=use_graphrag)
    print("Ingestion complete!\n")

    # Test queries that benefit from graph traversal
    queries = [
        "Where was Shivaji Maharaj born?",
        "What is nilesh rajgor's birthdate?",
        "What is nilesh rajgor's company?",
        "What did Microsoft Research develop?",
        "What is the relationship between GraphRAG and knowledge graphs?",
        "What databases does Ragforge use?",
    ]

    for question in queries:
        print(f"Question: {question}")
        result = ask(question, use_graphrag=use_graphrag)
        print(f"Answer: {result['answer']}")
        if result['facts']:
            print(f"Facts: {result['facts'][:2]}")  # Show first 2 facts
        print("-" * 60)
        print()

    print("\n=== GraphRAG Benefits ===")
    print("GraphRAG helps with:")
    print("1. Multi-hop queries (connecting related entities)")
    print("2. Understanding relationships between concepts")
    print("3. Better context from graph structure")
    print("4. Handling complex questions requiring entity connections")

if __name__ == "__main__":
    main()
