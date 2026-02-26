"""
PERSEPTOR v2.0 - Structured Logging Configuration
JSON-formatted logging with rotating file handler, performance timers, and request tracking.
"""

import logging
import logging.handlers
import json
import os
import time
import uuid
import functools
from datetime import datetime, timezone
from typing import Optional


class JSONFormatter(logging.Formatter):
    """Structured JSON log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }

        # Add extra fields if present
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if hasattr(record, "duration_ms"):
            log_entry["duration_ms"] = record.duration_ms
        if hasattr(record, "provider"):
            log_entry["provider"] = record.provider
        if hasattr(record, "model"):
            log_entry["model"] = record.model
        if hasattr(record, "tokens"):
            log_entry["tokens"] = record.tokens
        if hasattr(record, "endpoint"):
            log_entry["endpoint"] = record.endpoint
        if hasattr(record, "status_code"):
            log_entry["status_code"] = record.status_code

        # Add exception info
        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }

        return json.dumps(log_entry, ensure_ascii=False)


class TextFormatter(logging.Formatter):
    """Readable text log formatter for development."""

    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, "")
        reset = self.RESET

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prefix = f"{color}[{timestamp}] [{record.levelname:8s}]{reset}"
        module_info = f"[{record.module}.{record.funcName}:{record.lineno}]"

        parts = [prefix, module_info, record.getMessage()]

        if hasattr(record, "duration_ms"):
            parts.append(f"({record.duration_ms:.1f}ms)")
        if hasattr(record, "request_id"):
            parts.append(f"[req:{record.request_id[:8]}]")

        msg = " ".join(parts)

        if record.exc_info and record.exc_info[1]:
            msg += "\n" + self.formatException(record.exc_info)

        return msg


def setup_logging(
    level: str = "INFO",
    log_format: str = "json",
    file_path: Optional[str] = None,
    max_file_size_mb: int = 10,
    backup_count: int = 5,
) -> logging.Logger:
    """
    Configure structured logging for PERSEPTOR.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: "json" for structured logs, "text" for readable dev logs
        file_path: Path to log file (None for console only)
        max_file_size_mb: Max log file size before rotation
        backup_count: Number of backup log files to keep
    """
    root_logger = logging.getLogger("perseptor")
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Choose formatter
    if log_format == "json":
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (if path provided)
    if file_path:
        log_dir = os.path.dirname(file_path)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            file_path,
            maxBytes=max_file_size_mb * 1024 * 1024,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(JSONFormatter())  # Always JSON for files
        root_logger.addHandler(file_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a child logger under the perseptor namespace."""
    return logging.getLogger(f"perseptor.{name}")


def performance_timer(func):
    """Decorator to measure and log function execution time."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__ or "timer")
        start = time.perf_counter()

        try:
            result = func(*args, **kwargs)
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.info(
                f"{func.__name__} completed",
                extra={"duration_ms": elapsed_ms},
            )
            return result
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.error(
                f"{func.__name__} failed: {e}",
                extra={"duration_ms": elapsed_ms},
                exc_info=True,
            )
            raise

    return wrapper


async def async_performance_timer_wrapper(func, *args, **kwargs):
    """Async version of performance timer."""
    logger = get_logger(func.__module__ or "timer")
    start = time.perf_counter()

    try:
        result = await func(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info(
            f"{func.__name__} completed",
            extra={"duration_ms": elapsed_ms},
        )
        return result
    except Exception as e:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.error(
            f"{func.__name__} failed: {e}",
            extra={"duration_ms": elapsed_ms},
            exc_info=True,
        )
        raise


def generate_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid.uuid4())


def create_flask_request_logger(app):
    """
    Flask middleware for request/response logging.
    Attach to Flask app with: create_flask_request_logger(app)
    """
    logger = get_logger("http")

    @app.before_request
    def log_request():
        from flask import request, g
        g.request_id = generate_request_id()
        g.request_start = time.perf_counter()
        logger.info(
            f"{request.method} {request.path}",
            extra={
                "request_id": g.request_id,
                "endpoint": request.path,
            },
        )

    @app.after_request
    def log_response(response):
        from flask import request, g
        duration_ms = (time.perf_counter() - g.get("request_start", time.perf_counter())) * 1000
        logger.info(
            f"{request.method} {request.path} -> {response.status_code}",
            extra={
                "request_id": g.get("request_id", "unknown"),
                "endpoint": request.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        # Add request ID to response headers
        response.headers["X-Request-ID"] = g.get("request_id", "unknown")
        return response
