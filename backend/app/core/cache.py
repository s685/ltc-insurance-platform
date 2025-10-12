"""Caching utilities with support for in-memory and Redis backends."""

import asyncio
import hashlib
import json
import pickle
from collections.abc import Callable
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, TypeVar, Dict, Optional

try:
    from typing import ParamSpec
except ImportError:
    from typing_extensions import ParamSpec

import structlog

from ..config import get_settings

logger = structlog.get_logger(__name__)

P = ParamSpec("P")
T = TypeVar("T")

# In-memory cache storage
_memory_cache: Dict[str, tuple[Any, datetime]] = {}
_cache_lock = asyncio.Lock()


def get_cache_key(*args: Any, **kwargs: Any) -> str:
    """
    Generate a cache key from function arguments.

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        str: MD5 hash of serialized arguments
    """
    try:
        # Serialize arguments to JSON for consistent hashing
        key_data = {
            "args": [str(arg) for arg in args],
            "kwargs": {k: str(v) for k, v in sorted(kwargs.items())},
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    except Exception as e:
        logger.warning("cache_key_generation_failed", error=str(e))
        # Fallback to simpler key
        return hashlib.md5(str((args, kwargs)).encode()).hexdigest()


async def _get_from_memory_cache(key: str) -> Optional[Any]:
    """Get value from in-memory cache."""
    async with _cache_lock:
        if key in _memory_cache:
            value, expiry = _memory_cache[key]
            if datetime.now() < expiry:
                logger.debug("cache_hit", key=key[:8])
                return value
            else:
                # Expired entry
                del _memory_cache[key]
                logger.debug("cache_expired", key=key[:8])
    return None


async def _set_in_memory_cache(key: str, value: Any, ttl: int) -> None:
    """Set value in in-memory cache."""
    async with _cache_lock:
        expiry = datetime.now() + timedelta(seconds=ttl)
        _memory_cache[key] = (value, expiry)
        logger.debug("cache_set", key=key[:8], ttl=ttl)


async def _clear_memory_cache() -> None:
    """Clear all entries from in-memory cache."""
    async with _cache_lock:
        count = len(_memory_cache)
        _memory_cache.clear()
        logger.info("cache_cleared", entries=count)


def cache_result(
    ttl: Optional[int] = None,
    key_prefix: str = "",
    enabled: Optional[bool] = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to cache function results.

    Args:
        ttl: Time-to-live in seconds (uses settings default if None)
        key_prefix: Prefix for cache keys
        enabled: Override cache enable setting

    Returns:
        Decorated function with caching
    """
    settings = get_settings()
    cache_enabled = enabled if enabled is not None else settings.cache_enabled
    cache_ttl = ttl if ttl is not None else settings.cache_ttl

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            if not cache_enabled:
                return await func(*args, **kwargs)

            # Generate cache key
            func_name = f"{func.__module__}.{func.__name__}"
            cache_key = f"{key_prefix}:{func_name}:{get_cache_key(*args, **kwargs)}"

            # Try to get from cache
            cached_value = await _get_from_memory_cache(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            logger.debug("cache_miss", function=func_name)
            result = await func(*args, **kwargs)

            # Store in cache
            await _set_in_memory_cache(cache_key, result, cache_ttl)

            return result

        @wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            if not cache_enabled:
                return func(*args, **kwargs)

            # Generate cache key
            func_name = f"{func.__module__}.{func.__name__}"
            cache_key = f"{key_prefix}:{func_name}:{get_cache_key(*args, **kwargs)}"

            # Try to get from cache (sync version)
            if cache_key in _memory_cache:
                value, expiry = _memory_cache[cache_key]
                if datetime.now() < expiry:
                    logger.debug("cache_hit", key=cache_key[:8])
                    return value
                else:
                    del _memory_cache[cache_key]

            # Execute function
            logger.debug("cache_miss", function=func_name)
            result = func(*args, **kwargs)

            # Store in cache
            expiry = datetime.now() + timedelta(seconds=cache_ttl)
            _memory_cache[cache_key] = (result, expiry)

            return result

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        else:
            return sync_wrapper  # type: ignore

    return decorator


async def clear_cache(pattern: Optional[str] = None) -> int:
    """
    Clear cache entries.

    Args:
        pattern: Optional pattern to match keys (not implemented for memory cache)

    Returns:
        int: Number of entries cleared
    """
    if pattern:
        logger.warning("pattern_matching_not_supported", pattern=pattern)

    await _clear_memory_cache()
    return len(_memory_cache)

