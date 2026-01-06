# Ragforge

A zero-configuration, opinionated RAG pipeline for backend developers.

## Installation

```bash
pip install .
```

## Configuration

Set the following environment variable:

```bash
export GROQ_API_KEY="your_groq_api_key"
```

## Usage

```python
from ragforge import ask, ingest

# 1. Add some knowledge (One time setup)
ingest([
    "GraphRAG is a structured, hierarchical approach to Retrieval Augmented Generation (RAG).",
    "It uses knowledge graphs to extract and organize information from raw text.",
    "GraphRAG improves upon standard RAG by providing better context for complex queries."
])

# 2. Ask a question
result = ask("What is GraphRAG?")

print(result["answer"])
# Output: GraphRAG is a structured, hierarchical approach to RAG that uses knowledge graphs...

print(result["facts"])
# Output: ['GraphRAG is a structured...', 'It uses knowledge graphs...']
```

## Distribution

### Sharing with other developers

**Option 1: Git Dependency (Recommended for private/internal use)**

Developers can install directly from your git repository:

```bash
pip install git+https://github.com/yourusername/ragforge.git
# or with uv
uv pip install git+https://github.com/yourusername/ragforge.git
```

**Option 2: Build and Share Wheel**

1. Build the package:

   ```bash
   uv build
   ```

   This creates a `.whl` file in `dist/`.

2. Share the `.whl` file. Others can install it via:

   ```bash
   pip install ragforge-0.1.0-py3-none-any.whl
   ```

**Option 3: Publish to PyPI**

1. Build: `uv build`
2. Publish: `uv publish` (requires PyPI account and configuration)
