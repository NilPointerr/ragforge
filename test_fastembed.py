from ragforge.vector import get_vector_store
from ragforge.settings import settings
import shutil
import os

# Clean up previous data to avoid conflicts between manual vectors and fastembed
if os.path.exists(settings.qdrant_path):
    shutil.rmtree(settings.qdrant_path)

print("Initializing Vector Store...")
store = get_vector_store()

print("Adding texts...")
texts = ["FastEmbed is fast.", "Qdrant is a vector database."]
store.add_texts(texts)

print("Searching...")
results = store.search("What is FastEmbed?")
print(f"Results: {results}")

assert len(results) > 0
assert "FastEmbed is fast." in results
print("Verification successful!")
