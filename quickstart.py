"""
Quick Start Guide for EasyRag

This file provides a minimal example to get started quickly.
"""

import asyncio
import os


async def quick_start():
    """Minimal example to get started with EasyRag"""

    # Check if environment variables are set
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print("⚠️  Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease create a .env file with these variables.")
        print("See .env.template for an example.")
        return

    # Import after checking env vars
    from easyrag import RAGService, create_embedding
    from easyrag.utils import get_supabase_client

    print("=" * 60)
    print("EasyRag Quick Start")
    print("=" * 60)

    # Step 1: Store a sample document
    print("\n1. Storing a sample document...")

    sample_content = "Python is a high-level programming language known for its simplicity and readability."
    sample_metadata = {"source": "quickstart", "language": "python"}

    try:
        # Create embedding
        embedding = await create_embedding(sample_content)
        print(f"   ✓ Created embedding (dimension: {len(embedding)})")

        # Store in database
        client = get_supabase_client()
        result = client.table("documents").insert({
            "content": sample_content,
            "embedding": embedding,
            "metadata": sample_metadata
        }).execute()

        if result.data:
            doc_id = result.data[0]['id']
            print(f"   ✓ Stored document with ID: {doc_id}")
        else:
            print("   ✗ Failed to store document")
            return

    except Exception as e:
        print(f"   ✗ Error storing document: {e}")
        print("\n   Make sure your database is set up correctly.")
        print("   See docs/database_setup.md for instructions.")
        return

    # Step 2: Search for the document
    print("\n2. Searching for documents...")

    try:
        rag = RAGService()

        query = "What is Python programming?"
        results = await rag.search_documents(query, match_count=3)

        print(f"   ✓ Found {len(results)} results for: '{query}'")

        if results:
            print("\n   Top result:")
            print(f"   - Similarity: {results[0].get('similarity', 0):.3f}")
            print(f"   - Content: {results[0].get('content', '')[:100]}...")
        else:
            print("   No results found")

    except Exception as e:
        print(f"   ✗ Error searching: {e}")
        return

    # Step 3: Success!
    print("\n" + "=" * 60)
    print("✓ Quick start completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Check out examples/ for more usage patterns")
    print("2. Read docs/database_setup.md for full setup")
    print("3. Customize for your use case")


if __name__ == "__main__":
    asyncio.run(quick_start())
