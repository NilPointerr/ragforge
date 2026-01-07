# Ragforge Examples

This directory contains example scripts demonstrating how to use Ragforge.

## Examples

### `example.py`
Basic RAG example showing how to use `ingest()` and `ask()` functions.

**Usage:**
```bash
uv run examples/example.py
# or
python examples/example.py
```

**What it demonstrates:**
- Basic text ingestion
- Querying the knowledge base
- Standard RAG functionality

---

### `example_graphrag.py`
GraphRAG example showing how to use knowledge graphs for enhanced retrieval.

**Usage:**
```bash
uv run examples/example_graphrag.py
# or
python examples/example_graphrag.py
```

**What it demonstrates:**
- GraphRAG functionality with Neo4j
- Entity and relationship extraction
- Hybrid retrieval (vector + graph)
- Works with or without Neo4j (auto-detects)

**Requirements:**
- Neo4j running (optional - falls back to standard RAG if unavailable)
- `NEO4J_PASSWORD` environment variable (optional)

---

### `example_file_ingestion.py`
Demonstrates how to ingest text from files and directories.

**Usage:**
```bash
uv run examples/example_file_ingestion.py
# or
python examples/example_file_ingestion.py
```

**What it demonstrates:**
- `ingest_from_file()` - Single file ingestion
- `ingest_from_directory()` - Batch file ingestion
- File chunking for large documents
- Works with both GraphRAG and standard RAG

---

### `example_ingest_file.py`
Demonstrates the simplified `ingest_file()` function with required chunking.

**Usage:**
```bash
uv run examples/example_ingest_file.py
# or
python examples/example_ingest_file.py
```

**What it demonstrates:**
- `ingest_file()` - Simplified file ingestion with chunking
- Chunk size and gap size configuration
- Automatic chunking behavior

---

## Running Examples

All examples require the `GROQ_API_KEY` environment variable to be set:

```bash
export GROQ_API_KEY="your_groq_api_key"
```

Or create a `.env` file in the project root:

```bash
GROQ_API_KEY=your_groq_api_key
```

Then run any example:

```bash
# From project root
uv run examples/example.py

# Or with Python directly
python examples/example.py
```

## Notes

- All examples work with both GraphRAG and standard RAG automatically
- If Neo4j is configured and running, GraphRAG will be used
- If Neo4j is unavailable, examples automatically fall back to standard RAG
- No errors or warnings are shown during fallback
