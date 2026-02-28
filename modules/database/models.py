"""
PERSEPTOR v2.0 - Database Models and Schema
SQLite database initialization with WAL mode for concurrent access.
Now managed via Alembic migrations.
"""

import sqlite3
import os
import subprocess
from modules.config import config
from modules.logging_config import get_logger

logger = get_logger("database")

_DB_PATH = None


def _get_db_path() -> str:
    global _DB_PATH
    if _DB_PATH is None:
        _DB_PATH = config.database.path
    return _DB_PATH


def get_db_connection() -> sqlite3.Connection:
    """Get a new database connection with optimal settings."""
    db_path = _get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path, timeout=config.database.busy_timeout / 1000)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def init_db():
    """Initialize database schema by running Alembic migrations."""
    db_path = _get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    try:
        # Run Alembic upgrade head automatically
        subprocess.run(
            ["python", "-m", "alembic", "upgrade", "head"],
            check=True,
            capture_output=True,
            text=True,
            cwd="/app"
        )
        logger.info(f"Database initialized/migrated successfully at: {db_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Database migration failed. Stdout: {e.stdout}. Stderr: {e.stderr}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {e}", exc_info=True)
        raise
