"""Configuration module for EasyRag"""

from .logging import get_logger, safe_set_attribute, safe_span, search_logger

__all__ = ["get_logger", "safe_span", "safe_set_attribute", "search_logger"]
