"""
PERSEPTOR v2.0 - Database Models and Schema
SQLite database initialization with WAL mode for concurrent access.
"""

import sqlite3
import os
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
    """Initialize database schema. Safe to call multiple times."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Schema version tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Analysis Reports
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_reports (
                id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                threat_summary TEXT,
                analysis_data TEXT,
                yara_rules TEXT,
                generated_sigma_rules TEXT,
                siem_queries TEXT,
                sigma_matches TEXT,
                provider TEXT DEFAULT 'openai',
                model TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Generated Rules
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generated_rules (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                author TEXT DEFAULT 'PERSEPTOR',
                date TEXT,
                product TEXT DEFAULT 'sigma',
                confidence_score REAL DEFAULT 0.0,
                rule_content TEXT,
                mitre_techniques TEXT,
                test_cases TEXT,
                recommendations TEXT,
                references_data TEXT,
                explanation TEXT,
                component_scores TEXT,
                provider TEXT DEFAULT 'openai',
                model TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # User Sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id TEXT PRIMARY KEY,
                session_token TEXT UNIQUE NOT NULL,
                provider TEXT NOT NULL,
                encrypted_api_key TEXT NOT NULL,
                model_preference TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Token Usage Tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS token_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                provider TEXT NOT NULL,
                model TEXT NOT NULL,
                prompt_tokens INTEGER DEFAULT 0,
                completion_tokens INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                endpoint TEXT,
                latency_ms REAL DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES user_sessions(id) ON DELETE SET NULL
            )
        """)

        # Indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_reports_timestamp ON analysis_reports(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_reports_url ON analysis_reports(url)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rules_product ON generated_rules(product)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rules_created ON generated_rules(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(session_token)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_expires ON user_sessions(expires_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_usage_session ON token_usage(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_usage_timestamp ON token_usage(timestamp)")

        # Record schema version
        cursor.execute("INSERT OR IGNORE INTO schema_version (version) VALUES (1)")

        conn.commit()
        logger.info(f"Database initialized at: {_get_db_path()}")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        raise
    finally:
        conn.close()
