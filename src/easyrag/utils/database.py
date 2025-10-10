"""
Utility functions for EasyRag

Provides database connection and other utilities.
"""

import os
from functools import lru_cache

from dotenv import load_dotenv
from supabase import Client, create_client

from ..config.logging import get_logger

# Load environment variables
load_dotenv()

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """
    Get a Supabase client instance.

    This function is cached to return the same client instance across calls.

    Returns:
        Supabase Client instance

    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY is not set
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url:
        raise ValueError("SUPABASE_URL environment variable is not set")

    if not supabase_key:
        raise ValueError("SUPABASE_KEY environment variable is not set")

    logger.info(f"Initializing Supabase client for {supabase_url}")

    return create_client(supabase_url, supabase_key)


def get_env_bool(key: str, default: bool = False) -> bool:
    """
    Get a boolean value from environment variables.

    Args:
        key: Environment variable key
        default: Default value if not set

    Returns:
        Boolean value
    """
    value = os.getenv(key, "false" if not default else "true")
    return value.lower() in ("true", "1", "yes", "on")


def get_env_int(key: str, default: int) -> int:
    """
    Get an integer value from environment variables.

    Args:
        key: Environment variable key
        default: Default value if not set or invalid

    Returns:
        Integer value
    """
    try:
        return int(os.getenv(key, str(default)))
    except (ValueError, TypeError):
        logger.warning(f"Invalid integer value for {key}, using default: {default}")
        return default


def get_env_str(key: str, default: str = "") -> str:
    """
    Get a string value from environment variables.

    Args:
        key: Environment variable key
        default: Default value if not set

    Returns:
        String value
    """
    return os.getenv(key, default)
