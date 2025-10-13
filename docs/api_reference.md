# API Reference

Complete API reference for EasyRag.

## Table of Contents

- [Core Services](#core-services)
  - [RAGService](#ragservice)
- [Embedding Services](#embedding-services)
  - [create_embedding](#create_embedding)
  - [create_embeddings_batch](#create_embeddings_batch)
- [Search Strategies](#search-strategies)
  - [BaseSearchStrategy](#basesearchstrategy)
  - [HybridSearchStrategy](#hybridsearchstrategy)
- [Utilities](#utilities)
  - [Database](#database)
  - [Keyword Extraction](#keyword-extraction)
- [Exceptions](#exceptions)

---

## Core Services

### RAGService

Main coordinator service for document search operations.

```python
from easyrag import RAGService

rag = RAGService(supabase_client=None)
```

#### Constructor Parameters

- `supabase_client` (Client, optional): Supabase client instance. If not provided, creates one from environment variables.

#### Methods

##### search_documents

```python
await rag.search_documents(
    query: str,
    match_count: int = 5,
    filter_metadata: dict | None = None,
    use_hybrid_search: bool | None = None
) -> list[dict]
```

Search for documents using vector or hybrid search.

**Parameters:**
- `query` (str): Search query text
- `match_count` (int): Number of results to return (default: 5)
- `filter_metadata` (dict, optional): Metadata filters (e.g., `{"source": "docs"}`)
- `use_hybrid_search` (bool, optional): Use hybrid search if True, vector search if False. If None, uses `USE_HYBRID_SEARCH` environment variable.

**Returns:** List of result dictionaries with keys:
- `id`: Document ID
- `content`: Document content
- `metadata`: Document metadata
- `similarity`: Similarity score (0-1)
- `match_type` (if hybrid): Type of match ("vector" or "fulltext")

**Example:**
```python
results = await rag.search_documents(
    query="authentication best practices",
    match_count=10,
    filter_metadata={"source": "security"}
)

for result in results:
    print(f"Score: {result['similarity']:.3f}")
    print(f"Content: {result['content']}")
```

##### perform_rag_query

```python
success, response = await rag.perform_rag_query(
    query: str,
    source: str | None = None,
    match_count: int = 5,
    use_hybrid_search: bool | None = None
) -> tuple[bool, dict]
```

Comprehensive RAG query with structured response.

**Parameters:**
- `query` (str): Search query
- `source` (str, optional): Source filter
- `match_count` (int): Number of results (default: 5)
- `use_hybrid_search` (bool, optional): Enable hybrid search

**Returns:** Tuple of (success, response_dict)

Response dict structure on success:
```python
{
    "results": [...],           # List of formatted results
    "query": "...",            # Original query
    "source": "...",           # Source filter (if any)
    "match_count": 5,          # Requested count
    "total_found": 5,          # Actual results found
    "search_mode": "vector",   # "vector" or "hybrid"
}
```

**Example:**
```python
success, response = await rag.perform_rag_query(
    query="database optimization",
    source="documentation",
    match_count=5
)

if success:
    print(f"Found {response['total_found']} results")
    for result in response['results']:
        print(result['content'])
```

---

## Embedding Services

### create_embedding

Create an embedding for a single text.

```python
from easyrag import create_embedding

embedding = await create_embedding(text: str) -> list[float]
```

**Parameters:**
- `text` (str): Text to embed

**Returns:** List of floats representing the embedding vector

**Raises:**
- `EmbeddingQuotaExhaustedError`: When API quota is exhausted
- `EmbeddingRateLimitError`: When rate limited
- `EmbeddingAPIError`: For other API errors

**Example:**
```python
text = "Machine learning is a subset of AI"
embedding = await create_embedding(text)
print(f"Embedding dimension: {len(embedding)}")
```

### create_embeddings_batch

Create embeddings for multiple texts efficiently.

```python
from easyrag import create_embeddings_batch

result = await create_embeddings_batch(
    texts: list[str],
    progress_callback: callable | None = None
) -> EmbeddingBatchResult
```

**Parameters:**
- `texts` (list[str]): List of texts to embed
- `progress_callback` (callable, optional): Async function called with (message, progress_percent)

**Returns:** `EmbeddingBatchResult` object with:
- `embeddings`: List of embedding vectors
- `texts_processed`: Texts that were successfully processed
- `failed_items`: List of failures with error details
- `success_count`: Number of successful embeddings
- `failure_count`: Number of failed embeddings
- `has_failures`: Boolean indicating if any failures occurred

**Example:**
```python
texts = ["Text 1", "Text 2", "Text 3"]

async def progress(message, percent):
    print(f"{percent:.1f}% - {message}")

result = await create_embeddings_batch(texts, progress_callback=progress)

print(f"Success: {result.success_count}")
print(f"Failed: {result.failure_count}")

for text, embedding in zip(result.texts_processed, result.embeddings):
    print(f"Embedded: {text[:50]}... ({len(embedding)} dims)")
```

---

## Search Strategies

### BaseSearchStrategy

Core vector similarity search strategy.

```python
from easyrag.strategies import BaseSearchStrategy

strategy = BaseSearchStrategy(supabase_client)
```

#### Methods

##### vector_search

```python
results = await strategy.vector_search(
    query_embedding: list[float],
    match_count: int,
    filter_metadata: dict | None = None,
    table_rpc: str = "match_documents"
) -> list[dict]
```

Perform vector similarity search.

**Parameters:**
- `query_embedding`: Pre-computed embedding vector
- `match_count`: Number of results
- `filter_metadata`: Optional metadata filters
- `table_rpc`: Database RPC function name

---

### HybridSearchStrategy

Combines vector and full-text search.

```python
from easyrag.strategies import HybridSearchStrategy

strategy = HybridSearchStrategy(supabase_client, base_strategy)
```

#### Methods

##### search_documents_hybrid

```python
results = await strategy.search_documents_hybrid(
    query: str,
    query_embedding: list[float],
    match_count: int,
    filter_metadata: dict | None = None
) -> list[dict]
```

Perform hybrid search combining vector and full-text.

---

## Utilities

### Database

```python
from easyrag.utils import (
    get_supabase_client,
    get_env_bool,
    get_env_int,
    get_env_str
)
```

#### get_supabase_client

```python
client = get_supabase_client() -> Client
```

Get a cached Supabase client instance.

**Raises:** `ValueError` if `SUPABASE_URL` or `SUPABASE_KEY` is not set.

#### get_env_bool

```python
value = get_env_bool(key: str, default: bool = False) -> bool
```

Get boolean value from environment.

#### get_env_int

```python
value = get_env_int(key: str, default: int) -> int
```

Get integer value from environment.

#### get_env_str

```python
value = get_env_str(key: str, default: str = "") -> str
```

Get string value from environment.

---

### Keyword Extraction

```python
from easyrag.strategies import extract_keywords

keywords = extract_keywords(
    query: str,
    min_length: int = 2,
    max_keywords: int = 10
) -> list[str]
```

Extract meaningful keywords from a query.

**Example:**
```python
keywords = extract_keywords("How to implement JWT authentication")
# Returns: ["implement", "jwt", "authentication"]
```

---

## Exceptions

### EmbeddingError

Base exception for embedding-related errors.

```python
from easyrag.embeddings import (
    EmbeddingError,
    EmbeddingAPIError,
    EmbeddingRateLimitError,
    EmbeddingQuotaExhaustedError
)
```

All embedding exceptions include:
- `message`: Error message
- `text_preview`: Preview of the text being processed
- `original_error`: Original exception (if any)

#### Exception Hierarchy

```
EmbeddingError
├── EmbeddingAPIError          # General API errors
├── EmbeddingRateLimitError    # Rate limit errors
└── EmbeddingQuotaExhaustedError # Quota exhausted
```

**Example:**
```python
try:
    embedding = await create_embedding(text)
except EmbeddingQuotaExhaustedError as e:
    print(f"Quota exhausted: {e.message}")
    print(f"Tokens used: {e.tokens_used}")
except EmbeddingRateLimitError as e:
    print(f"Rate limited: {e.message}")
    await asyncio.sleep(60)  # Wait and retry
except EmbeddingAPIError as e:
    print(f"API error: {e.message}")
```

---

## Configuration

All configuration is done via environment variables:

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `SUPABASE_URL` | string | Required | Supabase project URL |
| `SUPABASE_KEY` | string | Required | Supabase API key |
| `OPENAI_API_KEY` | string | Required | OpenAI API key |
| `EMBEDDING_MODEL` | string | `text-embedding-3-small` | OpenAI embedding model |
| `EMBEDDING_DIMENSIONS` | int | 1536 | Embedding dimensions |
| `EMBEDDING_BATCH_SIZE` | int | 100 | Batch size for embeddings |
| `USE_HYBRID_SEARCH` | bool | false | Enable hybrid search by default |
| `LOG_LEVEL` | string | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |

---

## Type Definitions

### Result Dictionary

Result dictionaries returned by search methods:

```python
{
    "id": int,              # Document ID
    "content": str,         # Document content
    "metadata": dict,       # Document metadata
    "similarity": float,    # Similarity score (0-1)
    "match_type": str       # Optional: "vector" or "fulltext"
}
```

### Metadata Dictionary

Metadata can contain any JSON-serializable data:

```python
{
    "source": str,          # Source identifier
    "language": str,        # Programming language
    "topic": str,           # Topic category
    # ... any custom fields
}
```

---

## Best Practices

1. **Reuse RAGService instance**: Create once and reuse for multiple queries
2. **Use batch operations**: Use `create_embeddings_batch` for multiple texts
3. **Handle rate limits**: Implement exponential backoff for rate limit errors
4. **Filter effectively**: Use metadata filters to narrow search scope
5. **Monitor quotas**: Track API usage to avoid quota exhaustion
6. **Index optimization**: Create appropriate database indexes for your use case

---

## Complete Example

```python
import asyncio
from easyrag import RAGService, create_embeddings_batch
from easyrag.utils import get_supabase_client

async def complete_example():
    # 1. Index documents
    documents = [
        {
            "content": "Python is great for data science",
            "metadata": {"source": "blog", "topic": "python"}
        },
        {
            "content": "JavaScript powers modern web apps",
            "metadata": {"source": "blog", "topic": "javascript"}
        }
    ]
    
    texts = [doc["content"] for doc in documents]
    result = await create_embeddings_batch(texts)
    
    if not result.has_failures:
        client = get_supabase_client()
        records = [
            {
                "content": text,
                "embedding": emb,
                "metadata": doc["metadata"]
            }
            for text, emb, doc in zip(
                result.texts_processed,
                result.embeddings,
                documents
            )
        ]
        client.table("documents").insert(records).execute()
        print(f"Indexed {len(records)} documents")
    
    # 2. Search documents
    rag = RAGService()
    
    success, response = await rag.perform_rag_query(
        query="programming languages for web development",
        match_count=5
    )
    
    if success:
        for result in response['results']:
            print(f"Score: {result['similarity_score']:.3f}")
            print(f"Content: {result['content']}")
            print(f"Topic: {result['metadata'].get('topic')}")
            print()

asyncio.run(complete_example())
```
