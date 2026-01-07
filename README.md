# Ragforge

A zero-configuration, opinionated RAG (Retrieval Augmented Generation) pipeline for backend developers. Built with Pydantic for robust configuration management, featuring automatic validation and type safety.

## Features

- 🚀 **Zero Configuration**: Works out of the box with sensible defaults
- 🔒 **Type-Safe Settings**: Pydantic-based configuration with automatic validation
- 🎯 **Simple API**: Just `ask()` and `ingest()` - that's it!
- 🔄 **Singleton Pattern**: Efficient resource management with connection reuse
- 📦 **Local-First**: Uses local Qdrant storage - no external vector DB required
- 🧠 **Smart Embeddings**: Automatic embedding dimension detection

## Installation

```bash
pip install .
```

Or install from source:

```bash
git clone https://github.com/yourusername/ragforge.git
cd ragforge
pip install .
```

## Quick Start

### 1. Set API Key

```bash
export GROQ_API_KEY="your_groq_api_key"
```

Or create a `.env` file:

```bash
GROQ_API_KEY=your_groq_api_key
```

### 2. Use the Package

```python
from ragforge import ask, ingest

# Add knowledge to the system
ingest([
    "GraphRAG is a structured, hierarchical approach to Retrieval Augmented Generation (RAG).",
    "It uses knowledge graphs to extract and organize information from raw text.",
    "GraphRAG improves upon standard RAG by providing better context for complex queries."
])

# Ask questions
result = ask("What is GraphRAG?")

print(result["answer"])
# Output: GraphRAG is a structured, hierarchical approach to RAG that uses knowledge graphs...

print(result["facts"])
# Output: ['GraphRAG is a structured...', 'It uses knowledge graphs...']
```

## Configuration

Ragforge uses Pydantic for configuration management, supporting both environment variables and `.env` files. All settings are validated automatically.

### Required Configuration

- **`GROQ_API_KEY`**: Your Groq API key (required)

### Optional Configuration

#### LLM Settings

- **`RAGFORGE_LLM_MODEL`**: LLM model to use (default: `llama-3.3-70b-versatile`)
- **`RAGFORGE_LLM_TIMEOUT`**: Timeout in seconds for API calls (default: `30`, must be > 0)
- **`RAGFORGE_LLM_RETRIES`**: Maximum retries for API calls (default: `3`, range: 1-10)

#### Vector Store Settings

- **`RAGFORGE_QDRANT_PATH`**: Path to local Qdrant storage (default: `./qdrant_data`)
- **`RAGFORGE_FASTEMBED_CACHE_PATH`**: Path to FastEmbed cache (default: `./.fastembed_cache`)
- **`RAGFORGE_EMBEDDING_MODEL`**: Embedding model identifier (default: `sentence-transformers/all-MiniLM-L6-v2`)

#### RAG Settings

- **`RAGFORGE_MAX_CHUNKS`**: Maximum context chunks to retrieve (default: `5`, range: 1-50)
- **`RAGFORGE_ENABLE_GRAPHRAG`**: Enable GraphRAG functionality (default: `true`)

#### Neo4j Settings (for GraphRAG)

- **`RAGFORGE_NEO4J_URI`**: Neo4j database URI (default: `bolt://localhost:7687`)
- **`RAGFORGE_NEO4J_USER`**: Neo4j username (default: `neo4j`)
- **`RAGFORGE_NEO4J_PASSWORD`**: Neo4j password (required if GraphRAG enabled)
- **`RAGFORGE_NEO4J_DATABASE`**: Neo4j database name (default: `neo4j`)

### Example Configuration

Create a `.env` file:

```bash
GROQ_API_KEY=your_groq_api_key
RAGFORGE_LLM_MODEL=llama-3.3-70b-versatile
RAGFORGE_MAX_CHUNKS=10
RAGFORGE_QDRANT_PATH=./my_qdrant_data

# GraphRAG Settings (optional)
RAGFORGE_ENABLE_GRAPHRAG=true
RAGFORGE_NEO4J_URI=bolt://localhost:7687
RAGFORGE_NEO4J_USER=neo4j
RAGFORGE_NEO4J_PASSWORD=your_neo4j_password
```

Or set environment variables:

```bash
export GROQ_API_KEY="your_groq_api_key"
export RAGFORGE_MAX_CHUNKS=10
```

## Infrastructure Setup

Ragforge uses local Qdrant storage by default, but you can also use Docker containers for development.

### 1. Start Qdrant (Optional - for remote Qdrant)

If you want to use a remote Qdrant instance instead of local storage:

```bash
docker run -d \
  -p 6333:6333 \
  -p 6334:6334 \
  -v $(pwd)/data/qdrant:/qdrant/storage \
  qdrant/qdrant
```

### 2. Start Neo4j (Required for GraphRAG)

```bash
docker run -d \
  --name neo4j \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5
```

**Note**: 
- Ragforge uses local Qdrant storage by default (no Docker needed)
- Neo4j is required only if you want to use GraphRAG functionality
- GraphRAG is enabled by default but can be disabled via `RAGFORGE_ENABLE_GRAPHRAG=false`
- If Neo4j is not available, Ragforge falls back to vector-only RAG

## API Reference

### `ingest(texts: List[str]) -> None`

Add documents to the knowledge base for retrieval.

**Parameters:**
- `texts`: List of string documents to add

**Example:**
```python
ingest([
    "Python is a programming language.",
    "RAG stands for Retrieval Augmented Generation."
])
```

### `ask(question: str) -> Dict[str, Any]`

Ask a question and get an answer with supporting facts.

**Parameters:**
- `question`: The question to answer

**Returns:**
- `dict` with keys:
  - `"answer"`: The generated answer (str)
  - `"facts"`: List of facts used to generate the answer (List[str])

**Example:**
```python
result = ask("What is Python?")
print(result["answer"])
print(result["facts"])
```

## Distribution & Sharing

There are several ways to share your package with others. Choose the method that best fits your needs.

### Option 1: Git Repository (Recommended for Private/Internal Use)

This is the easiest method for sharing with a team or making it available on GitHub/GitLab.

#### Step 1: Push to Git Repository

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit"

# Push to your repository (GitHub, GitLab, etc.)
git remote add origin https://github.com/yourusername/ragforge.git
git push -u origin main
```

#### Step 2: Others Install from Git

Users can install directly from your repository:

```bash
# Using pip
pip install git+https://github.com/yourusername/ragforge.git

# Using uv (faster)
uv pip install git+https://github.com/yourusername/ragforge.git

# Install specific branch/tag
pip install git+https://github.com/yourusername/ragforge.git@v0.1.0
```

**Pros:**
- ✅ Easy to update (just push new commits)
- ✅ Version control built-in
- ✅ No build step required
- ✅ Works with private repositories (with authentication)

**Cons:**
- ❌ Requires git to be installed
- ❌ Slightly slower installation

---

### Option 2: Build and Share Wheel File

Best for sharing via email, file sharing, or when git is not available.

#### Step 1: Build the Package

```bash
# Install build tools if needed
pip install build

# Build the package
python -m build
# OR using uv (recommended)
uv build
```

This creates distribution files in the `dist/` directory:
- `ragforge-0.1.0-py3-none-any.whl` (wheel file - recommended)
- `ragforge-0.1.0.tar.gz` (source distribution)

#### Step 2: Share the Wheel File

Share the `.whl` file via:
- Email attachment
- File sharing service (Google Drive, Dropbox, etc.)
- Internal file server
- USB drive

#### Step 3: Others Install the Wheel

```bash
# Download the wheel file first, then:
pip install ragforge-0.1.0-py3-none-any.whl

# Or install directly from URL (if hosted online)
pip install https://example.com/path/to/ragforge-0.1.0-py3-none-any.whl
```

**Pros:**
- ✅ No git required
- ✅ Fast installation
- ✅ Works offline
- ✅ Can be shared via any method

**Cons:**
- ❌ Manual updates (need to rebuild and reshare)
- ❌ File size considerations

---

### Option 3: Publish to PyPI (Public Packages)

Best for open-source packages you want to make publicly available.

#### Step 1: Create PyPI Account

1. Go to [pypi.org](https://pypi.org) and create an account
2. Verify your email
3. (Optional) Create an API token for publishing

#### Step 2: Update Package Metadata

Make sure your `pyproject.toml` has correct information:

```toml
[project]
name = "ragforge"  # Must be unique on PyPI
version = "0.1.0"
description = "A zero-configuration, opinionated RAG pipeline."
readme = "README.md"
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
license = {text = "MIT"}
```

#### Step 3: Build and Publish

```bash
# Build the package
uv build

# Publish to PyPI (requires credentials)
uv publish

# Or using twine (alternative)
pip install twine
twine upload dist/*
```

#### Step 4: Others Install from PyPI

Once published, anyone can install it:

```bash
pip install ragforge

# Install specific version
pip install ragforge==0.1.0
```

**Pros:**
- ✅ Easy installation for users (`pip install ragforge`)
- ✅ Automatic dependency resolution
- ✅ Version management
- ✅ Discoverable by others

**Cons:**
- ❌ Package name must be unique
- ❌ Public (unless using private PyPI)
- ❌ Requires PyPI account setup

---

### Option 4: Private PyPI Server

For enterprise/internal use with better control.

Use services like:
- **Gemfury**: Private PyPI hosting
- **DevPI**: Self-hosted PyPI server
- **Artifactory**: Enterprise artifact repository

Installation is similar to public PyPI but with custom index:

```bash
pip install --index-url https://your-private-pypi.com/simple ragforge
```

---

### Quick Comparison

| Method | Best For | Setup Difficulty | Update Ease |
|--------|----------|------------------|-------------|
| **Git Repository** | Teams, private projects | ⭐ Easy | ⭐⭐⭐ Very Easy |
| **Wheel File** | One-off sharing, offline | ⭐⭐ Medium | ⭐ Manual |
| **Public PyPI** | Open source, public | ⭐⭐⭐ Moderate | ⭐⭐⭐ Easy |
| **Private PyPI** | Enterprise, large teams | ⭐⭐⭐⭐ Complex | ⭐⭐⭐ Easy |

---

### Version Management Tips

1. **Use Git Tags for Releases:**
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

2. **Update Version in `pyproject.toml`:**
   ```toml
   version = "0.1.1"  # Increment for new releases
   ```

3. **Create a CHANGELOG.md** to document changes between versions

---

### Installation Instructions for Users

Once you've shared your package, provide these instructions to users:

#### For Git Installation:
```bash
pip install git+https://github.com/yourusername/ragforge.git
```

#### For Wheel File:
```bash
# Download the .whl file, then:
pip install ragforge-0.1.0-py3-none-any.whl
```

#### For PyPI:
```bash
pip install ragforge
```

#### After Installation:
```python
from ragforge import ask, ingest

# Set your API key
export GROQ_API_KEY="your_key_here"

# Use the package
ingest(["Your knowledge here"])
result = ask("Your question")
```

## GraphRAG vs Standard RAG

Ragforge supports both standard RAG and GraphRAG:

- **Standard RAG**: Uses vector similarity search only (works without Neo4j)
- **GraphRAG**: Combines vector search with knowledge graph traversal (requires Neo4j)

GraphRAG provides:
- Better handling of complex, multi-hop queries
- Entity relationship understanding
- Context from graph structure
- Improved answers for questions requiring understanding of connections

To disable GraphRAG and use standard RAG only:
```bash
export RAGFORGE_ENABLE_GRAPHRAG=false
```

## Architecture

- **Settings**: Pydantic-based configuration with automatic validation
- **Vector Store**: Local Qdrant with FastEmbed for embeddings
- **Graph Store**: Neo4j knowledge graph for entity and relationship storage
- **LLM**: Groq API integration with retry logic for both generation and entity extraction
- **Singleton Pattern**: Efficient resource management for vector store, graph store, and LLM
- **Hybrid Retrieval**: Combines vector similarity and graph traversal for optimal context

## License

MIT License