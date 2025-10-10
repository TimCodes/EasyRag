"""
Basic tests for EasyRag

These tests verify core functionality without requiring external services.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from easyrag.strategies.keyword_extractor import KeywordExtractor, extract_keywords
from easyrag.embeddings.embedding_exceptions import (
    EmbeddingError,
    EmbeddingAPIError,
    EmbeddingRateLimitError,
)


class TestKeywordExtractor:
    """Tests for keyword extraction"""

    def test_extract_basic_keywords(self):
        """Test basic keyword extraction"""
        extractor = KeywordExtractor()
        
        query = "How to implement authentication in Python"
        keywords = extractor.extract_keywords(query)
        
        assert "implement" in keywords
        assert "authentication" in keywords
        assert "python" in keywords
        # Stop words should be filtered
        assert "how" not in keywords
        assert "to" not in keywords
        assert "in" not in keywords

    def test_extract_keywords_min_length(self):
        """Test keyword extraction with minimum length"""
        extractor = KeywordExtractor()
        
        query = "a big data problem"
        keywords = extractor.extract_keywords(query, min_length=3)
        
        assert "big" in keywords
        assert "data" in keywords
        assert "problem" in keywords

    def test_extract_keywords_max_count(self):
        """Test keyword extraction with max count"""
        extractor = KeywordExtractor()
        
        query = "one two three four five six seven eight nine ten"
        keywords = extractor.extract_keywords(query, max_keywords=5)
        
        assert len(keywords) <= 5

    def test_convenience_function(self):
        """Test the convenience function"""
        keywords = extract_keywords("machine learning algorithms")
        
        assert "machine" in keywords
        assert "learning" in keywords
        assert "algorithms" in keywords


class TestEmbeddingExceptions:
    """Tests for embedding exceptions"""

    def test_embedding_error_creation(self):
        """Test creating embedding errors"""
        error = EmbeddingError("Test error", text_preview="sample text")
        
        assert str(error) == "Test error"
        assert error.text_preview == "sample text"

    def test_embedding_error_to_dict(self):
        """Test converting error to dict"""
        error = EmbeddingAPIError("API error", text_preview="test")
        
        error_dict = error.to_dict()
        
        assert error_dict["error_type"] == "EmbeddingAPIError"
        assert error_dict["message"] == "API error"
        assert error_dict["text_preview"] == "test"

    def test_rate_limit_error(self):
        """Test rate limit error"""
        error = EmbeddingRateLimitError("Rate limited")
        
        assert isinstance(error, EmbeddingError)
        assert "Rate limited" in str(error)


@pytest.mark.asyncio
class TestRAGService:
    """Tests for RAG service (mocked)"""

    @patch('easyrag.core.rag_service.get_supabase_client')
    @patch('easyrag.core.rag_service.create_embedding')
    async def test_search_documents_vector(self, mock_create_embedding, mock_get_client):
        """Test vector search with mocked dependencies"""
        from easyrag import RAGService
        
        # Mock embedding creation
        mock_create_embedding.return_value = [0.1] * 1536
        
        # Mock Supabase client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": 1,
                "content": "Test content",
                "metadata": {},
                "similarity": 0.9
            }
        ]
        mock_client.rpc.return_value.execute.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        # Create service and search
        rag = RAGService()
        results = await rag.search_documents("test query")
        
        # Verify results
        assert len(results) == 1
        assert results[0]["content"] == "Test content"
        assert results[0]["similarity"] == 0.9
        
        # Verify embedding was created
        mock_create_embedding.assert_called_once_with("test query")

    @patch('easyrag.core.rag_service.get_supabase_client')
    @patch('easyrag.core.rag_service.create_embedding')
    async def test_search_documents_with_filter(self, mock_create_embedding, mock_get_client):
        """Test search with metadata filtering"""
        from easyrag import RAGService
        
        mock_create_embedding.return_value = [0.1] * 1536
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = []
        mock_client.rpc.return_value.execute.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        rag = RAGService()
        results = await rag.search_documents(
            "test query",
            filter_metadata={"source": "docs"}
        )
        
        # Verify RPC was called with filter
        assert mock_client.rpc.called
        call_args = mock_client.rpc.call_args
        assert "source_filter" in call_args[0][1] or "filter" in call_args[0][1]

    @patch('easyrag.core.rag_service.get_supabase_client')
    @patch('easyrag.core.rag_service.create_embedding')
    async def test_perform_rag_query_success(self, mock_create_embedding, mock_get_client):
        """Test comprehensive RAG query"""
        from easyrag import RAGService
        
        mock_create_embedding.return_value = [0.1] * 1536
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": 1,
                "content": "Test result",
                "metadata": {},
                "similarity": 0.85
            }
        ]
        mock_client.rpc.return_value.execute.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        rag = RAGService()
        success, response = await rag.perform_rag_query("test query")
        
        assert success is True
        assert response["total_found"] == 1
        assert response["query"] == "test query"
        assert len(response["results"]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
