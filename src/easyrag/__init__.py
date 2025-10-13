"""
EasyRag - A Standalone RAG System

A production-ready Retrieval-Augmented Generation (RAG) system with multi-strategy search,
vector embeddings, and flexible configuration.

Key Features:
- Multiple search strategies (vector, hybrid, agentic)
- Multi-provider embedding support (OpenAI, etc.)
- Optional reranking for improved results
- Clean, modular architecture
- Easy to configure and extend

Usage:
    from easyrag import RAGService

    rag = RAGService()
    results = await rag.search_documents("your query here")
"""

__version__ = "0.1.0"

from .core.rag_service import RAGService
from .embeddings.embedding_service import create_embedding, create_embeddings_batch
from .strategies.base_search_strategy import BaseSearchStrategy

__all__ = [
    "RAGService",
    "BaseSearchStrategy",
    "create_embedding",
    "create_embeddings_batch",
]
