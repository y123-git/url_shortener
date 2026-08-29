"""
Redis Cache Utilities
"""

import json
import threading
from typing import Optional

import redis

from app.config import settings


class CacheManager:
    """Redis cache manager with a fast in-memory fallback when Redis is unavailable."""

    def __init__(self):
        self.redis = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=0.5,
            socket_timeout=0.5,
            socket_keepalive=True,
        )
        self._local_cache = {}
        self._lock = threading.RLock()

    def get(self, key: str) -> Optional[str]:
        """Get value from cache, falling back to local memory if Redis is slow or unavailable."""
        try:
            value = self.redis.get(key)
            if value is not None:
                return value
        except redis.RedisError:
            pass

        with self._lock:
            return self._local_cache.get(key)

    def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL, falling back to local memory when Redis is unavailable."""
        ttl = ttl or settings.CACHE_TTL
        try:
            self.redis.setex(key, ttl, value)
            return True
        except redis.RedisError:
            with self._lock:
                self._local_cache[key] = value
            return True

    def delete(self, key: str) -> bool:
        """Delete from cache."""
        try:
            self.redis.delete(key)
            return True
        except redis.RedisError:
            with self._lock:
                self._local_cache.pop(key, None)
            return True

    def get_json(self, key: str) -> Optional[dict]:
        """Get JSON from cache."""
        value = self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None

    def set_json(self, key: str, value: dict, ttl: Optional[int] = None) -> bool:
        """Set JSON in cache."""
        try:
            return self.set(key, json.dumps(value), ttl)
        except TypeError:
            return False

    def increment(self, key: str, amount: int = 1) -> int:
        """Increment a counter in cache."""
        try:
            return self.redis.incrby(key, amount)
        except redis.RedisError:
            with self._lock:
                current = self._local_cache.get(key, 0)
                value = int(current) + amount
                self._local_cache[key] = str(value)
                return value


# Singleton instance
cache = CacheManager()