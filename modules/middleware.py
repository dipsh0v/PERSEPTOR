"""
PERSEPTOR v2.0 - Flask Middleware
Rate limiting, input validation, and content-type enforcement.
"""

import time
from collections import defaultdict
from threading import Lock
from functools import wraps
from flask import request, jsonify, g
from modules.config import config
from modules.logging_config import get_logger

logger = get_logger("middleware")


class RateLimiter:
    """
    Token bucket rate limiter.
    Thread-safe, in-memory implementation.
    """

    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._buckets = defaultdict(list)
        self._lock = Lock()

    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed for the given key."""
        now = time.time()
        with self._lock:
            # Clean old entries
            self._buckets[key] = [
                t for t in self._buckets[key]
                if now - t < self.window_seconds
            ]
            # Check limit
            if len(self._buckets[key]) >= self.max_requests:
                return False
            # Record request
            self._buckets[key].append(now)
            return True

    def remaining(self, key: str) -> int:
        """Get remaining requests for the key."""
        now = time.time()
        with self._lock:
            self._buckets[key] = [
                t for t in self._buckets[key]
                if now - t < self.window_seconds
            ]
            return max(0, self.max_requests - len(self._buckets[key]))


# Global rate limiter instances
_analysis_limiter = RateLimiter(
    max_requests=config.security.rate_limit_per_minute,
    window_seconds=60,
)
_read_limiter = RateLimiter(
    max_requests=config.security.rate_limit_per_minute * 2,
    window_seconds=60,
)


def rate_limit(limiter_type: str = "read"):
    """
    Rate limiting decorator for Flask routes.

    Args:
        limiter_type: "analysis" for write endpoints, "read" for read endpoints
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            limiter = _analysis_limiter if limiter_type == "analysis" else _read_limiter

            # Use IP + session token as key
            client_key = request.remote_addr or "unknown"
            session_token = request.headers.get("X-Session-Token")
            if session_token:
                client_key = f"{client_key}:{session_token[:8]}"

            if not limiter.is_allowed(client_key):
                remaining = limiter.remaining(client_key)
                logger.warning(f"Rate limit exceeded for {client_key}")
                return jsonify({
                    "error": "Rate limit exceeded. Please try again later.",
                    "remaining": remaining,
                    "retry_after": 60,
                }), 429

            # Add rate limit headers to response
            response = f(*args, **kwargs)
            if hasattr(response, "headers"):
                response.headers["X-RateLimit-Remaining"] = str(
                    limiter.remaining(client_key)
                )
            return response

        return decorated_function
    return decorator


def validate_json_content_type(f):
    """Ensure POST/PUT requests have JSON content type."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ("POST", "PUT", "PATCH"):
            if not request.is_json:
                return jsonify({
                    "error": "Content-Type must be application/json"
                }), 415
        return f(*args, **kwargs)
    return decorated_function


def validate_request_size(max_mb: int = None):
    """Validate request body size."""
    if max_mb is None:
        max_mb = config.security.max_upload_size_mb

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            content_length = request.content_length
            if content_length and content_length > max_mb * 1024 * 1024:
                return jsonify({
                    "error": f"Request too large. Maximum size: {max_mb}MB"
                }), 413
            return f(*args, **kwargs)
        return decorated_function
    return decorator
