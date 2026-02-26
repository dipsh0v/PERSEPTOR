"""
PERSEPTOR v2.0 - Response Cache
In-memory LRU cache with TTL for AI responses to avoid duplicate API calls.
"""

import hashlib
import threading
import time
from typing import Any, Optional
from collections import OrderedDict
from modules.logging_config import get_logger
from modules.config import AppConfig

logger = get_logger("cache")


class ResponseCache:
    """Thread-safe LRU cache with TTL for AI responses."""

    def __init__(self, max_size: int = None, ttl_seconds: int = None):
        config = AppConfig()
        self._max_size = max_size or config.cache.max_size
        self._ttl = ttl_seconds or config.cache.default_ttl
        self._cache: OrderedDict[str, dict] = OrderedDict()
        self._lock = threading.Lock()
        self._hit_count = 0
        self._miss_count = 0

    @staticmethod
    def _make_key(*args, **kwargs) -> str:
        """Create a deterministic cache key from arguments."""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.sha256(key_data.encode()).hexdigest()[:32]

    def get(self, key: str) -> Optional[Any]:
        """Get a cached value if it exists and hasn't expired."""
        with self._lock:
            if key not in self._cache:
                self._miss_count += 1
                return None

            entry = self._cache[key]
            if time.time() - entry["timestamp"] > self._ttl:
                # Expired
                del self._cache[key]
                self._miss_count += 1
                logger.debug(f"Cache expired for key {key[:8]}...")
                return None

            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._hit_count += 1
            logger.debug(f"Cache hit for key {key[:8]}...")
            return entry["value"]

    def set(self, key: str, value: Any) -> None:
        """Store a value in the cache."""
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                self._cache[key] = {"value": value, "timestamp": time.time()}
            else:
                if len(self._cache) >= self._max_size:
                    # Remove oldest entry
                    evicted_key, _ = self._cache.popitem(last=False)
                    logger.debug(f"Cache evicted key {evicted_key[:8]}...")
                self._cache[key] = {"value": value, "timestamp": time.time()}

    def invalidate(self, key: str) -> bool:
        """Remove a specific key from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> int:
        """Clear all cached entries. Returns count of cleared entries."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"Cache cleared: {count} entries removed")
            return count

    def stats(self) -> dict:
        """Return cache statistics."""
        with self._lock:
            total = self._hit_count + self._miss_count
            return {
                "size": len(self._cache),
                "max_size": self._max_size,
                "ttl_seconds": self._ttl,
                "hits": self._hit_count,
                "misses": self._miss_count,
                "hit_rate": self._hit_count / total if total > 0 else 0,
            }


# Global cache instance
_response_cache = None


def get_cache() -> ResponseCache:
    """Get or create the global response cache."""
    global _response_cache
    if _response_cache is None:
        _response_cache = ResponseCache()
    return _response_cache
