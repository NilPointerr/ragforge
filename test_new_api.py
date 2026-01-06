from qdrant_client import QdrantClient
from qdrant_client.http import models
import os
import shutil

path = "./qdrant_data_test"
if os.path.exists(path):
    shutil.rmtree(path)
os.makedirs(path, exist_ok=True)

client = QdrantClient(path=path)
collection_name = "test_collection"

# Create collection if not exists (FastEmbed needs configuration if we want it to handle embeddings)
# But wait, if we use models.Document, does it automatically use FastEmbed?
# The warning says "inference can be done internally... by wrapping data into models.Document".
# This implies the client needs to be aware of the embedding model.
# When using 'add', we didn't specify the model because it used defaults?
# Let's check if we need to set_model.

print("Setting model...")
client.set_model("sentence-transformers/all-MiniLM-L6-v2") 
# Note: The default in 'add' was "sentence-transformers/all-MiniLM-L6-v2" (or similar default from fastembed).
# We should be explicit.

if not client.collection_exists(collection_name):
    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE)
    )

print("Upserting with PointStruct...")
docs = ["Hello world", "Qdrant is cool"]
import uuid
points = [
    models.PointStruct(
        id=str(uuid.uuid4()),
        vector=models.Document(text=doc, model="sentence-transformers/all-MiniLM-L6-v2"),
        payload={"source": "test", "text": doc} # Store text in payload too if needed, or rely on Qdrant storing it?
        # FastEmbed usually stores it in 'document' field in payload?
        # Let's add it manually to be safe or check if it's auto-added.
    )
    for doc in docs
]

client.upsert(
    collection_name=collection_name,
    points=points
)

print("Querying with models.Document...")
query_text = "What is Qdrant?"

try:
    results = client.query_points(
        collection_name=collection_name,
        query=models.Document(text=query_text, model="sentence-transformers/all-MiniLM-L6-v2"),
        limit=1
    )
    print(f"Results: {results}")
except Exception as e:
    print(f"Query failed: {e}")
