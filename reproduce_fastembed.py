import os
import shutil
from fastembed import TextEmbedding

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def test_default():
    print("Testing default initialization...")
    try:
        model = TextEmbedding(model_name=MODEL_NAME)
        print("Success!")
    except Exception as e:
        print(f"Failed: {e}")

def test_custom_cache():
    print("\nTesting custom cache initialization...")
    cache_dir = "./local_fastembed_cache"
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
    
    try:
        model = TextEmbedding(model_name=MODEL_NAME, cache_dir=cache_dir)
        print("Success!")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_default()
    test_custom_cache()
