"""
Custom exceptions for embedding operations

Provides specific exception types for better error handling.
"""


class EmbeddingError(Exception):
    """Base exception for embedding-related errors"""

    def __init__(self, message: str, text_preview: str = None, original_error: Exception = None):
        self.message = message
        self.text_preview = text_preview[:100] if text_preview else None
        self.original_error = original_error
        super().__init__(self.message)

    def to_dict(self):
        """Convert exception to dictionary for logging"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "text_preview": self.text_preview,
            "original_error": str(self.original_error) if self.original_error else None,
        }


class EmbeddingAPIError(EmbeddingError):
    """Exception for API-related embedding errors"""
    pass


class EmbeddingRateLimitError(EmbeddingError):
    """Exception for rate limit errors"""
    pass


class EmbeddingQuotaExhaustedError(EmbeddingError):
    """Exception for quota exhausted errors"""

    def __init__(self, message: str, text_preview: str = None, tokens_used: int = None):
        super().__init__(message, text_preview)
        self.tokens_used = tokens_used

    def to_dict(self):
        data = super().to_dict()
        data["tokens_used"] = self.tokens_used
        return data
