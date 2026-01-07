from qdrant_client.http import models
import pydantic

print("Inspecting models.Document...")
try:
    print(models.Document.model_json_schema())
except Exception as e:
    print(e)

print("\nTrying with 'text' field...")
try:
    doc = models.Document(text="Hello", model="sentence-transformers/all-MiniLM-L6-v2")
    print(f"Success: {doc}")
except Exception as e:
    print(f"Failed: {e}")
