"""
Embedding Service

Handles embedding generation with support for multiple providers.
Simplified version focusing on OpenAI with extensibility for other providers.
"""

import asyncio
import os
from dataclasses import dataclass, field
from typing import Any

import openai
from openai import AsyncOpenAI

from ..config.logging import get_logger, safe_span
from ..utils import get_env_int, get_env_str
from .embedding_exceptions import (
    EmbeddingAPIError,
    EmbeddingError,
    EmbeddingQuotaExhaustedError,
    EmbeddingRateLimitError,
)

logger = get_logger(__name__)


@dataclass
class EmbeddingBatchResult:
    """Result of batch embedding creation with success/failure tracking."""

    embeddings: list[list[float]] = field(default_factory=list)
    failed_items: list[dict[str, Any]] = field(default_factory=list)
    success_count: int = 0
    failure_count: int = 0
    texts_processed: list[str] = field(default_factory=list)

    def add_success(self, embedding: list[float], text: str):
        """Add a successful embedding."""
        self.embeddings.append(embedding)
        self.texts_processed.append(text)
        self.success_count += 1

    def add_failure(self, text: str, error: Exception, batch_index: int | None = None):
        """Add a failed item with error details."""
        error_dict = {
            "text": text[:200] if text else None,
            "error": str(error),
            "error_type": type(error).__name__,
            "batch_index": batch_index,
        }

        if isinstance(error, EmbeddingError):
            error_dict.update(error.to_dict())

        self.failed_items.append(error_dict)
        self.failure_count += 1

    @property
    def has_failures(self) -> bool:
        return self.failure_count > 0

    @property
    def total_requested(self) -> int:
        return self.success_count + self.failure_count


def get_openai_client() -> AsyncOpenAI:
    """
    Get an OpenAI client instance.

    Returns:
        AsyncOpenAI client

    Raises:
        ValueError: If OPENAI_API_KEY is not set
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    return AsyncOpenAI(api_key=api_key)


async def create_embedding(text: str) -> list[float]:
    """
    Create an embedding for a single text.

    Args:
        text: Text to create an embedding for

    Returns:
        List of floats representing the embedding

    Raises:
        EmbeddingQuotaExhaustedError: When quota is exhausted
        EmbeddingRateLimitError: When rate limited
        EmbeddingAPIError: For other API errors
    """
    try:
        result = await create_embeddings_batch([text])
        if not result.embeddings:
            if result.has_failures and result.failed_items:
                error_info = result.failed_items[0]
                error_msg = error_info.get("error", "Unknown error")
                if "quota" in error_msg.lower():
                    raise EmbeddingQuotaExhaustedError(
                        f"Quota exhausted: {error_msg}", text_preview=text
                    )
                elif "rate" in error_msg.lower():
                    raise EmbeddingRateLimitError(f"Rate limit hit: {error_msg}", text_preview=text)
                else:
                    raise EmbeddingAPIError(f"Failed to create embedding: {error_msg}", text_preview=text)
            else:
                raise EmbeddingAPIError("No embeddings returned from batch creation", text_preview=text)
        return result.embeddings[0]
    except EmbeddingError:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Embedding creation failed: {error_msg}", exc_info=True)

        if "insufficient_quota" in error_msg:
            raise EmbeddingQuotaExhaustedError(f"Quota exhausted: {error_msg}", text_preview=text) from e
        elif "rate_limit" in error_msg.lower():
            raise EmbeddingRateLimitError(f"Rate limit hit: {error_msg}", text_preview=text) from e
        else:
            raise EmbeddingAPIError(f"Embedding error: {error_msg}", text_preview=text, original_error=e) from e


async def create_embeddings_batch(
    texts: list[str],
    progress_callback: Any | None = None,
) -> EmbeddingBatchResult:
    """
    Create embeddings for multiple texts with graceful failure handling.

    Args:
        texts: List of texts to create embeddings for
        progress_callback: Optional callback for progress reporting

    Returns:
        EmbeddingBatchResult with successful embeddings and failure details
    """
    if not texts:
        return EmbeddingBatchResult()

    result = EmbeddingBatchResult()

    # Validate texts
    validated_texts = []
    for i, text in enumerate(texts):
        if isinstance(text, str):
            validated_texts.append(text)
            continue

        logger.error(f"Invalid text type at index {i}: {type(text)}")
        try:
            converted = str(text)
            validated_texts.append(converted)
        except Exception as conversion_error:
            logger.error(f"Failed to convert text at index {i} to string: {conversion_error}")
            result.add_failure(
                repr(text),
                EmbeddingAPIError("Invalid text type", original_error=conversion_error),
                batch_index=None,
            )

    texts = validated_texts

    with safe_span(
        "create_embeddings_batch", text_count=len(texts), total_chars=sum(len(t) for t in texts)
    ) as span:
        try:
            # Get configuration
            embedding_model = get_env_str("EMBEDDING_MODEL", "text-embedding-3-small")
            embedding_dimensions = get_env_int("EMBEDDING_DIMENSIONS", 1536)
            batch_size = get_env_int("EMBEDDING_BATCH_SIZE", 100)

            logger.info(f"Using embedding model: {embedding_model} with {embedding_dimensions} dimensions")

            client = get_openai_client()

            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                batch_index = i // batch_size

                try:
                    retry_count = 0
                    max_retries = 3

                    while retry_count < max_retries:
                        try:
                            # Create embeddings for this batch
                            response = await client.embeddings.create(
                                model=embedding_model,
                                input=batch,
                                dimensions=embedding_dimensions if embedding_dimensions > 0 else None,
                            )

                            for text, item in zip(batch, response.data, strict=False):
                                result.add_success(item.embedding, text)

                            break  # Success, exit retry loop

                        except openai.RateLimitError as e:
                            error_message = str(e)
                            if "insufficient_quota" in error_message:
                                logger.error(f"Quota exhausted at batch {batch_index}!")

                                # Add remaining texts as failures
                                for text in texts[i:]:
                                    result.add_failure(
                                        text,
                                        EmbeddingQuotaExhaustedError("Quota exhausted"),
                                        batch_index,
                                    )

                                span.set_attribute("quota_exhausted", True)
                                return result
                            else:
                                # Regular rate limit - retry
                                retry_count += 1
                                if retry_count < max_retries:
                                    wait_time = 2**retry_count
                                    logger.warning(
                                        f"Rate limit hit for batch {batch_index}, "
                                        f"waiting {wait_time}s before retry {retry_count}/{max_retries}"
                                    )
                                    await asyncio.sleep(wait_time)
                                else:
                                    raise

                except Exception as e:
                    logger.error(f"Batch {batch_index} failed: {e}", exc_info=True)

                    for text in batch:
                        if isinstance(e, EmbeddingError):
                            result.add_failure(text, e, batch_index)
                        else:
                            result.add_failure(
                                text,
                                EmbeddingAPIError(f"Failed to create embedding: {str(e)}", original_error=e),
                                batch_index,
                            )

                # Progress reporting
                if progress_callback:
                    processed = result.success_count + result.failure_count
                    progress = (processed / len(texts)) * 100

                    message = f"Processed {processed}/{len(texts)} texts"
                    if result.has_failures:
                        message += f" ({result.failure_count} failed)"

                    await progress_callback(message, progress)

                await asyncio.sleep(0.01)

            span.set_attribute("embeddings_created", result.success_count)
            span.set_attribute("embeddings_failed", result.failure_count)
            span.set_attribute("success", not result.has_failures)

            return result

        except Exception as e:
            logger.error(f"Catastrophic failure in batch embedding: {e}", exc_info=True)
            span.set_attribute("catastrophic_failure", True)

            # Mark remaining texts as failed
            processed_count = result.success_count + result.failure_count
            for text in texts[processed_count:]:
                result.add_failure(
                    text, EmbeddingAPIError(f"Catastrophic failure: {str(e)}", original_error=e)
                )

            return result
