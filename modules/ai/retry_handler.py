"""
PERSEPTOR v2.0 - Retry Handler with Exponential Backoff
Handles rate limits, transient errors, and provider-specific error codes.
"""

import time
import random
import functools
from typing import Callable, Optional, Tuple, Type
from modules.logging_config import get_logger

logger = get_logger("ai.retry")


class AIError(Exception):
    """Base exception for AI provider errors."""
    def __init__(self, message: str, provider: str = "", retryable: bool = False):
        super().__init__(message)
        self.provider = provider
        self.retryable = retryable


class RateLimitError(AIError):
    """Rate limit exceeded."""
    def __init__(self, message: str, provider: str = "", retry_after: float = 0):
        super().__init__(message, provider, retryable=True)
        self.retry_after = retry_after


class AuthenticationError(AIError):
    """Invalid API key or authentication failure."""
    def __init__(self, message: str, provider: str = ""):
        super().__init__(message, provider, retryable=False)


class ModelNotFoundError(AIError):
    """Requested model not available."""
    def __init__(self, message: str, provider: str = ""):
        super().__init__(message, provider, retryable=False)


def classify_error(error: Exception, provider: str = "") -> AIError:
    """Classify provider-specific errors into standard AIError types."""
    err_str = str(error).lower()
    err_type = type(error).__name__.lower()

    # Rate limit detection
    if any(k in err_str for k in ["rate limit", "429", "too many requests", "quota"]):
        retry_after = 0
        if hasattr(error, "retry_after"):
            retry_after = float(error.retry_after)
        return RateLimitError(str(error), provider, retry_after)

    # Authentication errors
    if any(k in err_str for k in ["401", "unauthorized", "invalid api key", "authentication"]):
        return AuthenticationError(str(error), provider)

    # Model not found
    if any(k in err_str for k in ["model not found", "404", "does not exist"]):
        return ModelNotFoundError(str(error), provider)

    # Transient errors (retryable)
    if any(k in err_str for k in ["500", "502", "503", "504", "timeout", "connection"]):
        return AIError(str(error), provider, retryable=True)

    # Default: not retryable
    return AIError(str(error), provider, retryable=False)


def with_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
):
    """
    Decorator for retrying AI calls with exponential backoff and jitter.

    Args:
        max_retries: Maximum retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay cap in seconds
        retryable_exceptions: Tuple of exception types to retry on
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    classified = classify_error(e)

                    # Don't retry non-retryable errors
                    if not classified.retryable:
                        logger.error(
                            f"Non-retryable error in {func.__name__}: {e}",
                            extra={"provider": classified.provider},
                        )
                        raise classified from e

                    last_exception = classified

                    if attempt < max_retries:
                        # Exponential backoff with jitter
                        if isinstance(classified, RateLimitError) and classified.retry_after > 0:
                            delay = classified.retry_after
                        else:
                            delay = min(base_delay * (2 ** attempt), max_delay)
                            delay *= 0.5 + random.random()  # Add jitter

                        logger.warning(
                            f"Retry {attempt + 1}/{max_retries} for {func.__name__} "
                            f"after {delay:.1f}s: {e}",
                            extra={"provider": classified.provider},
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"All {max_retries} retries exhausted for {func.__name__}: {e}",
                            extra={"provider": classified.provider},
                        )

            raise last_exception

        return wrapper
    return decorator
