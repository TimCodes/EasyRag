"""
Hybrid Search Example

Demonstrates using hybrid search (combining vector + full-text search).
"""

import asyncio
import os

from dotenv import load_dotenv

load_dotenv()

from easyrag import RAGService  # noqa: E402


async def compare_search_methods():
    """Compare vector search vs hybrid search"""

    rag = RAGService()
    query = "database performance optimization techniques"

    print("=" * 60)
    print("Comparing Vector Search vs Hybrid Search")
    print("=" * 60)
    print(f"\nQuery: '{query}'\n")

    # 1. Vector search only
    print("-" * 60)
    print("1. VECTOR SEARCH ONLY (Semantic Search)")
    print("-" * 60)

    vector_results = await rag.search_documents(
        query=query,
        match_count=5,
        use_hybrid_search=False
    )

    print(f"\nFound {len(vector_results)} results:")
    for i, result in enumerate(vector_results[:3], 1):
        print(f"\n{i}. Similarity: {result.get('similarity', 0):.3f}")
        print(f"   Content: {result.get('content', '')[:150]}...")

    # 2. Hybrid search
    print("\n" + "-" * 60)
    print("2. HYBRID SEARCH (Vector + Full-Text)")
    print("-" * 60)

    hybrid_results = await rag.search_documents(
        query=query,
        match_count=5,
        use_hybrid_search=True
    )

    print(f"\nFound {len(hybrid_results)} results:")
    for i, result in enumerate(hybrid_results[:3], 1):
        match_type = result.get('match_type', 'unknown')
        print(f"\n{i}. Similarity: {result.get('similarity', 0):.3f} [{match_type}]")
        print(f"   Content: {result.get('content', '')[:150]}...")

    # Comparison
    print("\n" + "=" * 60)
    print("COMPARISON")
    print("=" * 60)
    print(f"Vector search results: {len(vector_results)}")
    print(f"Hybrid search results: {len(hybrid_results)}")

    if hybrid_results and 'match_type' in hybrid_results[0]:
        match_types = {}
        for r in hybrid_results:
            mt = r.get('match_type', 'unknown')
            match_types[mt] = match_types.get(mt, 0) + 1

        print("\nHybrid search match types:")
        for match_type, count in match_types.items():
            print(f"  - {match_type}: {count} results")


async def hybrid_search_with_filters():
    """Demonstrate hybrid search with metadata filtering"""

    rag = RAGService()

    print("\n" + "=" * 60)
    print("Hybrid Search with Filtering")
    print("=" * 60)

    query = "authentication and security"
    source = "documentation"

    print(f"\nQuery: '{query}'")
    print(f"Source filter: '{source}'")
    print("-" * 60)

    success, response = await rag.perform_rag_query(
        query=query,
        source=source,
        match_count=5,
        use_hybrid_search=True
    )

    if success:
        print(f"\nSearch mode: {response['search_mode']}")
        print(f"Total found: {response['total_found']}")
        print("\nResults:")

        for i, result in enumerate(response['results'], 1):
            print(f"\n{i}. Score: {result['similarity_score']:.3f}")
            print(f"   Content: {result['content'][:150]}...")
            print(f"   Source: {result.get('metadata', {}).get('source', 'N/A')}")
    else:
        print(f"Search failed: {response.get('error', 'Unknown error')}")


async def keyword_aware_search():
    """Demonstrate search with specific keywords"""

    rag = RAGService()

    print("\n" + "=" * 60)
    print("Keyword-Aware Hybrid Search")
    print("=" * 60)

    # Queries with specific technical terms
    queries = [
        "PostgreSQL indexing strategies",
        "JWT token authentication",
        "Docker container deployment",
    ]

    for query in queries:
        print(f"\nQuery: '{query}'")
        print("-" * 40)

        results = await rag.search_documents(
            query=query,
            match_count=3,
            use_hybrid_search=True
        )

        print(f"Found {len(results)} results:")
        for i, result in enumerate(results[:2], 1):
            match_type = result.get('match_type', 'N/A')
            print(f"  {i}. [{match_type}] Score: {result.get('similarity', 0):.3f}")
            print(f"     {result.get('content', '')[:100]}...")


async def main():
    """Run all hybrid search examples"""

    print("=" * 60)
    print("EasyRag - Hybrid Search Examples")
    print("=" * 60)

    # Check environment variables
    if not os.getenv("SUPABASE_URL") or not os.getenv("OPENAI_API_KEY"):
        print("\nError: Please configure SUPABASE_URL and OPENAI_API_KEY in your .env file")
        return

    # Note about hybrid search
    print("\nNote: Hybrid search requires the hybrid_search_documents() function")
    print("      to be set up in your database. See docs/database_setup.md for")
    print("      instructions on setting up hybrid search.")
    print("\n      If hybrid search is not available, the system will fall back")
    print("      to vector search automatically.")

    try:
        await compare_search_methods()
        await hybrid_search_with_filters()
        await keyword_aware_search()

        print("\n" + "=" * 60)
        print("Examples completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
