"""
RAG Service - Main Coordinator

Orchestrates multiple RAG strategies and provides a unified interface for document search.
"""

from typing import Any

from ..config.logging import get_logger, safe_span
from ..embeddings.embedding_service import create_embedding
from ..strategies.base_search_strategy import BaseSearchStrategy
from ..strategies.hybrid_search_strategy import HybridSearchStrategy
from ..utils import get_env_bool, get_supabase_client

logger = get_logger(__name__)


class RAGService:
    """
    Coordinator service that orchestrates multiple RAG strategies.

    This service provides a simple interface for document search with
    optional hybrid search capabilities.
    """

    def __init__(self, supabase_client=None):
        """
        Initialize RAG service.

        Args:
            supabase_client: Optional Supabase client (will create one if not provided)
        """
        self.supabase_client = supabase_client or get_supabase_client()

        # Initialize base strategy (always needed)
        self.base_strategy = BaseSearchStrategy(self.supabase_client)

        # Initialize hybrid strategy
        self.hybrid_strategy = HybridSearchStrategy(self.supabase_client, self.base_strategy)

    async def search_documents(
        self,
        query: str,
        match_count: int = 5,
        filter_metadata: dict | None = None,
        use_hybrid_search: bool | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search for documents using the configured strategy.

        Args:
            query: Search query string
            match_count: Number of results to return (default: 5)
            filter_metadata: Optional metadata filter dict
            use_hybrid_search: Whether to use hybrid search (if None, uses env setting)

        Returns:
            List of matching documents with metadata and similarity scores
        """
        # Determine if hybrid search should be used
        if use_hybrid_search is None:
            use_hybrid_search = get_env_bool("USE_HYBRID_SEARCH", False)

        with safe_span(
            "rag_search_documents",
            query_length=len(query),
            match_count=match_count,
            hybrid_enabled=use_hybrid_search,
        ) as span:
            try:
                logger.info(f"Searching for: '{query[:100]}...' (hybrid={use_hybrid_search})")

                # Create embedding for the query
                query_embedding = await create_embedding(query)

                if not query_embedding:
                    logger.error("Failed to create embedding for query")
                    return []

                if use_hybrid_search:
                    # Use hybrid strategy
                    results = await self.hybrid_strategy.search_documents_hybrid(
                        query=query,
                        query_embedding=query_embedding,
                        match_count=match_count,
                        filter_metadata=filter_metadata,
                    )
                    span.set_attribute("search_mode", "hybrid")
                else:
                    # Use basic vector search
                    results = await self.base_strategy.vector_search(
                        query_embedding=query_embedding,
                        match_count=match_count,
                        filter_metadata=filter_metadata,
                    )
                    span.set_attribute("search_mode", "vector")

                span.set_attribute("results_found", len(results))
                logger.info(f"Found {len(results)} results")
                return results

            except Exception as e:
                logger.error(f"Document search failed: {e}", exc_info=True)
                span.set_attribute("error", str(e))
                return []

    async def perform_rag_query(
        self,
        query: str,
        source: str | None = None,
        match_count: int = 5,
        use_hybrid_search: bool | None = None,
    ) -> tuple[bool, dict[str, Any]]:
        """
        Unified RAG query with comprehensive response.

        Args:
            query: The search query
            source: Optional source filter
            match_count: Maximum number of results to return
            use_hybrid_search: Whether to use hybrid search (if None, uses env setting)

        Returns:
            Tuple of (success: bool, result_dict: dict)
        """
        # Determine if hybrid search should be used
        if use_hybrid_search is None:
            use_hybrid_search = get_env_bool("USE_HYBRID_SEARCH", False)

        with safe_span(
            "rag_query_pipeline",
            query_length=len(query),
            source=source,
            match_count=match_count
        ) as span:
            try:
                logger.info(f"RAG query started: {query[:100]}{'...' if len(query) > 100 else ''}")

                # Build filter metadata
                filter_metadata = {"source": source} if source else None

                # Get results
                results = await self.search_documents(
                    query=query,
                    match_count=match_count,
                    filter_metadata=filter_metadata,
                    use_hybrid_search=use_hybrid_search,
                )

                span.set_attribute("raw_results_count", len(results))

                # Format results
                formatted_results = []
                for i, result in enumerate(results):
                    try:
                        formatted_result = {
                            "id": result.get("id", f"result_{i}"),
                            "content": result.get("content", ""),
                            "metadata": result.get("metadata", {}),
                            "similarity_score": result.get("similarity", 0.0),
                        }
                        formatted_results.append(formatted_result)
                    except Exception as format_error:
                        logger.warning(f"Failed to format result {i}: {format_error}")
                        continue

                # Build response
                response_data = {
                    "results": formatted_results,
                    "query": query,
                    "source": source,
                    "match_count": match_count,
                    "total_found": len(formatted_results),
                    "search_mode": "hybrid" if use_hybrid_search else "vector",
                }

                span.set_attribute("final_results_count", len(formatted_results))
                span.set_attribute("success", True)

                logger.info(f"RAG query completed - {len(formatted_results)} results found")
                return True, response_data

            except Exception as e:
                logger.error(f"RAG query failed: {e}", exc_info=True)
                span.set_attribute("error", str(e))
                span.set_attribute("success", False)

                return False, {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "query": query,
                    "source": source,
                }
