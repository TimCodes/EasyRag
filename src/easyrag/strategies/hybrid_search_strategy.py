"""
Hybrid Search Strategy

Combines vector similarity search with full-text search using PostgreSQL.
"""

from typing import Any

from supabase import Client

from ..config.logging import get_logger, safe_span

logger = get_logger(__name__)


class HybridSearchStrategy:
    """Strategy class implementing hybrid search combining vector and full-text search"""

    def __init__(self, supabase_client: Client, base_strategy):
        self.supabase_client = supabase_client
        self.base_strategy = base_strategy

    async def search_documents_hybrid(
        self,
        query: str,
        query_embedding: list[float],
        match_count: int,
        filter_metadata: dict | None = None,
    ) -> list[dict[str, Any]]:
        """
        Perform hybrid search combining vector and full-text search.

        Args:
            query: Original search query text
            query_embedding: Pre-computed query embedding
            match_count: Number of results to return
            filter_metadata: Optional metadata filter dict

        Returns:
            List of matching documents from both vector and text search
        """
        with safe_span("hybrid_search_documents") as span:
            try:
                # Prepare filter and source parameters
                filter_json = filter_metadata or {}
                source_filter = filter_json.pop("source", None) if "source" in filter_json else None

                # Call the hybrid search PostgreSQL function
                response = self.supabase_client.rpc(
                    "hybrid_search_documents",
                    {
                        "query_embedding": query_embedding,
                        "query_text": query,
                        "match_count": match_count,
                        "filter": filter_json,
                        "source_filter": source_filter,
                    },
                ).execute()

                if not response.data:
                    logger.debug("No results from hybrid search")
                    return []

                # Format results
                results = []
                for row in response.data:
                    result = {
                        "id": row.get("id"),
                        "content": row.get("content"),
                        "metadata": row.get("metadata", {}),
                        "similarity": row.get("similarity", 0.0),
                        "match_type": row.get("match_type", "unknown"),
                    }
                    results.append(result)

                span.set_attribute("results_count", len(results))

                # Log match type distribution
                match_types = {}
                for r in results:
                    mt = r.get("match_type", "unknown")
                    match_types[mt] = match_types.get(mt, 0) + 1

                logger.info(f"Hybrid search returned {len(results)} results. Match types: {match_types}")
                return results

            except Exception as e:
                logger.error(f"Hybrid search failed: {e}", exc_info=True)
                span.set_attribute("error", str(e))

                # Fallback to base vector search
                logger.info("Falling back to vector search")
                return await self.base_strategy.vector_search(
                    query_embedding=query_embedding,
                    match_count=match_count,
                    filter_metadata=filter_metadata,
                )
