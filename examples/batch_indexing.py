"""
Batch Indexing Example

Demonstrates how to index multiple documents efficiently using batch processing.
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from easyrag import create_embeddings_batch
from easyrag.utils import get_supabase_client


# Sample documents to index
SAMPLE_DOCUMENTS = [
    {
        "content": "Python is a high-level, interpreted programming language known for its simplicity and readability.",
        "metadata": {"source": "programming", "language": "python", "topic": "introduction"}
    },
    {
        "content": "Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
        "metadata": {"source": "ai", "topic": "machine-learning"}
    },
    {
        "content": "REST APIs use HTTP methods like GET, POST, PUT, and DELETE to perform CRUD operations.",
        "metadata": {"source": "web-development", "topic": "apis"}
    },
    {
        "content": "PostgreSQL is a powerful, open-source object-relational database system with strong SQL compliance.",
        "metadata": {"source": "databases", "topic": "sql"}
    },
    {
        "content": "Docker containers package applications with their dependencies for consistent deployment across environments.",
        "metadata": {"source": "devops", "topic": "containerization"}
    },
    {
        "content": "React is a JavaScript library for building user interfaces, particularly single-page applications.",
        "metadata": {"source": "web-development", "language": "javascript", "topic": "frontend"}
    },
    {
        "content": "JWT (JSON Web Tokens) are a secure way to transmit information between parties as a JSON object.",
        "metadata": {"source": "security", "topic": "authentication"}
    },
    {
        "content": "Git is a distributed version control system for tracking changes in source code during development.",
        "metadata": {"source": "development-tools", "topic": "version-control"}
    },
]


async def index_documents_batch(documents: list[dict]):
    """
    Index multiple documents efficiently using batch processing.
    
    Args:
        documents: List of dicts with 'content' and 'metadata' keys
    """
    print(f"Indexing {len(documents)} documents...")
    
    # Extract content from documents
    texts = [doc["content"] for doc in documents]
    
    # Create embeddings in batch
    print("Creating embeddings...")
    result = await create_embeddings_batch(texts)
    
    # Check for failures
    if result.has_failures:
        print(f"\nWarning: {result.failure_count} embeddings failed to create")
        for failure in result.failed_items:
            print(f"  - {failure['error']}")
    
    print(f"Successfully created {result.success_count} embeddings")
    
    # Prepare records for insertion
    client = get_supabase_client()
    records = []
    
    for text, embedding in zip(result.texts_processed, result.embeddings):
        # Find the original document
        original_doc = next((d for d in documents if d["content"] == text), None)
        if original_doc:
            records.append({
                "content": text,
                "embedding": embedding,
                "metadata": original_doc.get("metadata", {})
            })
    
    # Batch insert into database
    if records:
        print(f"\nInserting {len(records)} documents into database...")
        response = client.table("documents").insert(records).execute()
        
        if response.data:
            print(f"Successfully indexed {len(response.data)} documents!")
            
            # Display indexed documents
            print("\nIndexed documents:")
            for i, doc in enumerate(response.data, 1):
                print(f"  {i}. ID: {doc['id']}")
                print(f"     Content: {doc['content'][:80]}...")
                print(f"     Metadata: {doc['metadata']}")
        else:
            print("Failed to index documents")
    else:
        print("No records to insert")


async def index_with_progress(documents: list[dict]):
    """
    Index documents with progress callback.
    
    Args:
        documents: List of dicts with 'content' and 'metadata' keys
    """
    print(f"\nIndexing {len(documents)} documents with progress tracking...")
    
    texts = [doc["content"] for doc in documents]
    
    # Define progress callback
    async def progress_callback(message: str, progress: float):
        print(f"Progress: {progress:.1f}% - {message}")
    
    # Create embeddings with progress tracking
    result = await create_embeddings_batch(
        texts,
        progress_callback=progress_callback
    )
    
    print(f"\nCompleted! Success: {result.success_count}, Failed: {result.failure_count}")
    
    # Insert into database (same as above)
    if not result.has_failures:
        client = get_supabase_client()
        records = []
        
        for text, embedding in zip(result.texts_processed, result.embeddings):
            original_doc = next((d for d in documents if d["content"] == text), None)
            if original_doc:
                records.append({
                    "content": text,
                    "embedding": embedding,
                    "metadata": original_doc.get("metadata", {})
                })
        
        if records:
            client.table("documents").insert(records).execute()
            print(f"Inserted {len(records)} documents")


async def verify_indexing():
    """Verify that documents were indexed correctly"""
    print("\nVerifying indexed documents...")
    
    client = get_supabase_client()
    
    # Count total documents
    response = client.table("documents").select("id", count="exact").execute()
    total_count = response.count if hasattr(response, 'count') else len(response.data)
    
    print(f"Total documents in database: {total_count}")
    
    # Get a sample of documents
    sample_response = client.table("documents").select("id, content, metadata").limit(5).execute()
    
    if sample_response.data:
        print("\nSample documents:")
        for doc in sample_response.data:
            print(f"  - ID {doc['id']}: {doc['content'][:60]}...")


async def main():
    """Run batch indexing examples"""
    
    print("=" * 60)
    print("EasyRag - Batch Indexing Example")
    print("=" * 60)
    
    # Check environment variables
    if not os.getenv("SUPABASE_URL") or not os.getenv("OPENAI_API_KEY"):
        print("\nError: Please configure SUPABASE_URL and OPENAI_API_KEY in your .env file")
        return
    
    try:
        # Method 1: Basic batch indexing
        print("\n--- Method 1: Basic Batch Indexing ---")
        await index_documents_batch(SAMPLE_DOCUMENTS)
        
        # Method 2: Batch indexing with progress
        print("\n--- Method 2: Batch Indexing with Progress ---")
        more_docs = [
            {
                "content": "Kubernetes orchestrates containerized applications across clusters of machines.",
                "metadata": {"source": "devops", "topic": "orchestration"}
            },
            {
                "content": "FastAPI is a modern Python web framework for building APIs with automatic documentation.",
                "metadata": {"source": "web-development", "language": "python", "topic": "frameworks"}
            },
        ]
        await index_with_progress(more_docs)
        
        # Verify indexing
        await verify_indexing()
        
        print("\n" + "=" * 60)
        print("Batch indexing completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError during indexing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
