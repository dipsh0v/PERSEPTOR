"""Initial schema

Revision ID: 2ca3cdc4d32d
Revises: 
Create Date: 2026-02-26 23:38:53.679079

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2ca3cdc4d32d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
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
            atomic_tests TEXT,
            mitre_mapping TEXT,
            provider TEXT DEFAULT 'openai',
            model TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    op.execute("""
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
    op.execute("""
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
    op.execute("""
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
    op.execute("CREATE INDEX IF NOT EXISTS idx_reports_timestamp ON analysis_reports(timestamp)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_reports_url ON analysis_reports(url)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_rules_product ON generated_rules(product)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_rules_created ON generated_rules(created_at)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(session_token)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_sessions_expires ON user_sessions(expires_at)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_usage_session ON token_usage(session_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_usage_timestamp ON token_usage(timestamp)")



def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS token_usage")
    op.execute("DROP TABLE IF EXISTS user_sessions")
    op.execute("DROP TABLE IF EXISTS generated_rules")
    op.execute("DROP TABLE IF EXISTS analysis_reports")

