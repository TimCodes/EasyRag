"""Embedding services for EasyRag"""

from .embedding_exceptions import (
    EmbeddingAPIError,
    EmbeddingError,
    EmbeddingQuotaExhaustedError,
    EmbeddingRateLimitError,
)
from .embedding_service import (
    EmbeddingBatchResult,
    create_embedding,
    create_embeddings_batch,
    get_openai_client,
)

__all__ = [
    "create_embedding",
    "create_embeddings_batch",
    "get_openai_client",
    "EmbeddingBatchResult",
    "EmbeddingError",
    "EmbeddingAPIError",
    "EmbeddingRateLimitError",
    "EmbeddingQuotaExhaustedError",
]
