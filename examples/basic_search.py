"""
Basic Search Example

Demonstrates basic document search using EasyRag.
"""

import asyncio
import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from easyrag import RAGService  # noqa: E402


async def basic_search_example():
    """Example of basic document search"""

    # Initialize the RAG service
    print("Initializing RAG service...")
    rag = RAGService()

    # Example query
    query = "How do I implement authentication in my application?"
    print(f"\nSearching for: '{query}'")
    print("-" * 60)

    # Perform search
    results = await rag.search_documents(
        query=query,
        match_count=5
    )

    # Display results
    if results:
        print(f"\nFound {len(results)} results:\n")

        for i, result in enumerate(results, 1):
            print(f"Result {i}:")
            print(f"  Similarity: {result.get('similarity', 0):.3f}")
            print(f"  Content: {result.get('content', '')[:200]}...")

            metadata = result.get('metadata', {})
            if metadata:
                print(f"  Metadata: {metadata}")

            print()
    else:
        print("No results found.")


async def search_with_filtering():
    """Example of search with metadata filtering"""

    rag = RAGService()

    query = "database indexing best practices"
    source_filter = "documentation"

    print(f"\nSearching for: '{query}'")
    print(f"Filtering by source: {source_filter}")
    print("-" * 60)

    # Search with metadata filter
    results = await rag.search_documents(
        query=query,
        match_count=5,
        filter_metadata={"source": source_filter}
    )

    print(f"\nFound {len(results)} results from source '{source_filter}'")

    for i, result in enumerate(results, 1):
        print(f"\n{i}. Similarity: {result.get('similarity', 0):.3f}")
        print(f"   {result.get('content', '')[:150]}...")


async def comprehensive_rag_query():
    """Example using the comprehensive RAG query method"""

    rag = RAGService()

    query = "What are the security considerations for API development?"

    print(f"\nPerforming comprehensive RAG query: '{query}'")
    print("-" * 60)

    # Use the comprehensive query method
    success, response = await rag.perform_rag_query(
        query=query,
        match_count=3,
        use_hybrid_search=False  # Can enable hybrid search here
    )

    if success:
        print("\nQuery successful!")
        print(f"Search mode: {response['search_mode']}")
        print(f"Total found: {response['total_found']}")
        print("\nResults:")

        for i, result in enumerate(response['results'], 1):
            print(f"\n{i}. Score: {result['similarity_score']:.3f}")
            print(f"   {result['content'][:200]}...")
    else:
        print(f"Query failed: {response.get('error', 'Unknown error')}")


async def main():
    """Run all examples"""

    print("=" * 60)
    print("EasyRag - Basic Search Examples")
    print("=" * 60)

    # Check if required environment variables are set
    if not os.getenv("SUPABASE_URL"):
        print("\nError: SUPABASE_URL not set. Please configure your .env file.")
        return

    if not os.getenv("OPENAI_API_KEY"):
        print("\nError: OPENAI_API_KEY not set. Please configure your .env file.")
        return

    try:
        # Run examples
        await basic_search_example()
        await search_with_filtering()
        await comprehensive_rag_query()

        print("\n" + "=" * 60)
        print("Examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
