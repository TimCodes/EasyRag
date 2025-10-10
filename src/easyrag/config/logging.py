"""
Simplified logging configuration for EasyRag

Provides a clean logging setup without external dependencies.
"""

import logging
import os
from contextlib import contextmanager
from typing import Any


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Configure if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Set level from environment or default to INFO
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        logger.setLevel(getattr(logging, log_level, logging.INFO))

    return logger


# Create a default logger for search operations
search_logger = get_logger("easyrag.search")


class NoOpSpan:
    """No-op span for when tracing is not available"""

    def set_attribute(self, key: str, value: Any) -> None:
        """No-op attribute setter"""
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


@contextmanager
def safe_span(operation_name: str, **attributes):
    """
    Create a safe span context that works without external tracing.

    Args:
        operation_name: Name of the operation
        **attributes: Additional attributes to log

    Yields:
        NoOpSpan instance
    """
    logger = get_logger("easyrag.trace")

    # Log the operation start
    if attributes:
        logger.debug(f"Starting {operation_name} with {attributes}")
    else:
        logger.debug(f"Starting {operation_name}")

    span = NoOpSpan()
    try:
        yield span
    except Exception as e:
        logger.error(f"Error in {operation_name}: {e}", exc_info=True)
        raise
    finally:
        logger.debug(f"Completed {operation_name}")


def safe_set_attribute(span: Any, key: str, value: Any) -> None:
    """
    Safely set an attribute on a span.

    Args:
        span: Span object (can be None)
        key: Attribute key
        value: Attribute value
    """
    if span and hasattr(span, 'set_attribute'):
        try:
            span.set_attribute(key, value)
        except Exception:
            pass
