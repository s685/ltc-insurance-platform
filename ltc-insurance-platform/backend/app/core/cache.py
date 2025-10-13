"""Caching utilities with Redis support."""

import json
import logging
from functools import wraps
from typing import Any, Callable, Optional
import redis
from redis.exceptions import RedisError

from app.config import settings
from app.core.exceptions import CacheError

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages caching operations with Redis backend."""
    
    def __init__(self):
        self._redis_client: Optional[redis.Redis] = None
        self._memory_cache: dict = {}
        
        if settings.redis_enabled and settings.cache_enabled:
            try:
                self._redis_client = redis.from_url(
                    settings.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5
                )
                # Test connection
                self._redis_client.ping()
                logger.info("Redis connection established")
            except RedisError as e:
                logger.warning(f"Redis connection failed, falling back to memory cache: {e}")
                self._redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not settings.cache_enabled:
            return None
        
        try:
            # Try Redis first
            if self._redis_client:
                value = self._redis_client.get(key)
                if value:
                    logger.debug(f"Cache hit (Redis): {key}")
                    return json.loads(value)
            
            # Fallback to memory cache
            if key in self._memory_cache:
                logger.debug(f"Cache hit (memory): {key}")
                return self._memory_cache[key]
            
            logger.debug(f"Cache miss: {key}")
            return None
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache with optional TTL."""
        if not settings.cache_enabled:
            return
        
        ttl = ttl or settings.cache_ttl
        
        try:
            # Try Redis first
            if self._redis_client:
                self._redis_client.setex(
                    key,
                    ttl,
                    json.dumps(value, default=str)
                )
                logger.debug(f"Cache set (Redis): {key} (TTL: {ttl}s)")
            else:
                # Fallback to memory cache (no TTL support in simple dict)
                self._memory_cache[key] = value
                logger.debug(f"Cache set (memory): {key}")
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {e}")
    
    def delete(self, key: str):
        """Delete value from cache."""
        try:
            if self._redis_client:
                self._redis_client.delete(key)
            if key in self._memory_cache:
                del self._memory_cache[key]
            logger.debug(f"Cache deleted: {key}")
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
    
    def clear(self):
        """Clear all cache."""
        try:
            if self._redis_client:
                self._redis_client.flushdb()
            self._memory_cache.clear()
            logger.info("Cache cleared")
        except Exception as e:
            logger.warning(f"Cache clear error: {e}")


# Global cache manager instance
cache_manager = CacheManager()


def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """Decorator to cache function results."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix}{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

