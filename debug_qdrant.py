from qdrant_client import QdrantClient
import os

path = "./qdrant_data"
os.makedirs(path, exist_ok=True)
client = QdrantClient(path=path)
try:
    # Create dummy collection if needed
    from qdrant_client.http import models
    if not client.collection_exists("test"):
        client.create_collection("test", vectors_config=models.VectorParams(size=4, distance=models.Distance.COSINE))
    
    res = client.query_points(collection_name="test", query=[0.1, 0.1, 0.1, 0.1], limit=1)
    print(f"Result type: {type(res)}")
    print(f"Result: {res}")
except Exception as e:
    print(f"Error: {e}")
