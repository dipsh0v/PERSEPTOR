"""
PERSEPTOR v2.0 - Data Access Repositories
Clean separation of database operations with parameterized queries.
"""

import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from modules.database.models import get_db_connection
from modules.logging_config import get_logger

logger = get_logger("database.repository")


def _serialize(obj) -> str:
    """Serialize object to JSON string for storage."""
    if obj is None:
        return "{}"
    if isinstance(obj, str):
        return obj
    return json.dumps(obj, ensure_ascii=False, default=str)


def _deserialize(json_str: str) -> Any:
    """Deserialize JSON string from storage."""
    if not json_str:
        return {}
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return json_str


class ReportRepository:
    """Data access for analysis reports."""

    @staticmethod
    def create(report_data: Dict) -> str:
        """Save a new analysis report. Returns the report ID."""
        report_id = report_data.get("id", str(uuid.uuid4()))
        conn = get_db_connection()
        try:
            conn.execute(
                """INSERT INTO analysis_reports
                   (id, url, timestamp, threat_summary, analysis_data, yara_rules,
                    generated_sigma_rules, siem_queries, sigma_matches, provider, model)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    report_id,
                    report_data.get("url", ""),
                    report_data.get("timestamp", datetime.now().isoformat()),
                    report_data.get("threat_summary", ""),
                    _serialize(report_data.get("analysis_data")),
                    _serialize(report_data.get("yara_rules")),
                    report_data.get("generated_sigma_rules", ""),
                    _serialize(report_data.get("siem_queries")),
                    _serialize(report_data.get("sigma_matches")),
                    report_data.get("provider", "openai"),
                    report_data.get("model"),
                ),
            )
            conn.commit()
            logger.info(f"Report saved: {report_id}")
            return report_id
        finally:
            conn.close()

    @staticmethod
    def get_by_id(report_id: str) -> Optional[Dict]:
        """Get a report by ID."""
        conn = get_db_connection()
        try:
            row = conn.execute(
                "SELECT * FROM analysis_reports WHERE id = ?", (report_id,)
            ).fetchone()
            if row:
                return ReportRepository._row_to_dict(row)
            return None
        finally:
            conn.close()

    @staticmethod
    def list_all(limit: int = 100, offset: int = 0) -> List[Dict]:
        """List all reports, newest first."""
        conn = get_db_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM analysis_reports ORDER BY timestamp DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
            return [ReportRepository._row_to_dict(r) for r in rows]
        finally:
            conn.close()

    @staticmethod
    def delete(report_id: str) -> bool:
        """Delete a report. Returns True if deleted."""
        conn = get_db_connection()
        try:
            result = conn.execute(
                "DELETE FROM analysis_reports WHERE id = ?", (report_id,)
            )
            conn.commit()
            deleted = result.rowcount > 0
            if deleted:
                logger.info(f"Report deleted: {report_id}")
            return deleted
        finally:
            conn.close()

    @staticmethod
    def count() -> int:
        """Count total reports."""
        conn = get_db_connection()
        try:
            row = conn.execute("SELECT COUNT(*) as cnt FROM analysis_reports").fetchone()
            return row["cnt"]
        finally:
            conn.close()

    @staticmethod
    def _row_to_dict(row) -> Dict:
        return {
            "id": row["id"],
            "url": row["url"],
            "timestamp": row["timestamp"],
            "threat_summary": row["threat_summary"],
            "analysis_data": _deserialize(row["analysis_data"]),
            "yara_rules": _deserialize(row["yara_rules"]),
            "generated_sigma_rules": row["generated_sigma_rules"],
            "siem_queries": _deserialize(row["siem_queries"]),
            "sigma_matches": _deserialize(row["sigma_matches"]),
            "provider": row["provider"],
            "model": row["model"],
        }


class RuleRepository:
    """Data access for generated rules."""

    @staticmethod
    def create(rule_data: Dict) -> str:
        """Save a new generated rule. Returns the rule ID."""
        rule_id = rule_data.get("id", str(uuid.uuid4()))
        conn = get_db_connection()
        try:
            conn.execute(
                """INSERT INTO generated_rules
                   (id, title, description, author, date, product, confidence_score,
                    rule_content, mitre_techniques, test_cases, recommendations,
                    references_data, explanation, component_scores, provider, model)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    rule_id,
                    rule_data.get("title", "Untitled Rule"),
                    rule_data.get("description", ""),
                    rule_data.get("author", "PERSEPTOR"),
                    rule_data.get("date", datetime.now().strftime("%Y/%m/%d")),
                    rule_data.get("product", "sigma"),
                    rule_data.get("confidence_score", 0.0),
                    _serialize(rule_data.get("rule_content")),
                    _serialize(rule_data.get("mitre_techniques")),
                    _serialize(rule_data.get("test_cases")),
                    _serialize(rule_data.get("recommendations")),
                    _serialize(rule_data.get("references")),
                    rule_data.get("explanation", ""),
                    _serialize(rule_data.get("component_scores")),
                    rule_data.get("provider", "openai"),
                    rule_data.get("model"),
                ),
            )
            conn.commit()
            logger.info(f"Rule saved: {rule_id} - {rule_data.get('title')}")
            return rule_id
        finally:
            conn.close()

    @staticmethod
    def get_by_id(rule_id: str) -> Optional[Dict]:
        """Get a rule by ID."""
        conn = get_db_connection()
        try:
            row = conn.execute(
                "SELECT * FROM generated_rules WHERE id = ?", (rule_id,)
            ).fetchone()
            if row:
                return RuleRepository._row_to_dict(row)
            return None
        finally:
            conn.close()

    @staticmethod
    def list_all(limit: int = 100, offset: int = 0) -> List[Dict]:
        """List all rules, newest first."""
        conn = get_db_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM generated_rules ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
            return [RuleRepository._row_to_dict(r) for r in rows]
        finally:
            conn.close()

    @staticmethod
    def delete(rule_id: str) -> bool:
        """Delete a rule. Returns True if deleted."""
        conn = get_db_connection()
        try:
            result = conn.execute(
                "DELETE FROM generated_rules WHERE id = ?", (rule_id,)
            )
            conn.commit()
            deleted = result.rowcount > 0
            if deleted:
                logger.info(f"Rule deleted: {rule_id}")
            return deleted
        finally:
            conn.close()

    @staticmethod
    def count() -> int:
        conn = get_db_connection()
        try:
            row = conn.execute("SELECT COUNT(*) as cnt FROM generated_rules").fetchone()
            return row["cnt"]
        finally:
            conn.close()

    @staticmethod
    def _row_to_dict(row) -> Dict:
        return {
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "author": row["author"],
            "date": row["date"],
            "product": row["product"],
            "confidence_score": row["confidence_score"],
            "rule_content": _deserialize(row["rule_content"]),
            "mitre_techniques": _deserialize(row["mitre_techniques"]),
            "test_cases": _deserialize(row["test_cases"]),
            "recommendations": _deserialize(row["recommendations"]),
            "references": _deserialize(row["references_data"]),
            "explanation": row["explanation"],
            "component_scores": _deserialize(row["component_scores"]),
            "provider": row["provider"],
            "model": row["model"],
            "created_at": row["created_at"],
        }


class SessionRepository:
    """Data access for user sessions."""

    @staticmethod
    def create(session_data: Dict) -> str:
        """Create a new session. Returns session ID."""
        session_id = str(uuid.uuid4())
        conn = get_db_connection()
        try:
            conn.execute(
                """INSERT INTO user_sessions
                   (id, session_token, provider, encrypted_api_key, model_preference, expires_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    session_id,
                    session_data["session_token"],
                    session_data["provider"],
                    session_data["encrypted_api_key"],
                    session_data.get("model_preference"),
                    session_data["expires_at"],
                ),
            )
            conn.commit()
            logger.info(f"Session created: {session_id}")
            return session_id
        finally:
            conn.close()

    @staticmethod
    def get_by_token(session_token: str) -> Optional[Dict]:
        """Get session by token."""
        conn = get_db_connection()
        try:
            row = conn.execute(
                "SELECT * FROM user_sessions WHERE session_token = ? AND expires_at > datetime('now')",
                (session_token,),
            ).fetchone()
            if row:
                # Update last_used
                conn.execute(
                    "UPDATE user_sessions SET last_used = datetime('now') WHERE id = ?",
                    (row["id"],),
                )
                conn.commit()
                return dict(row)
            return None
        finally:
            conn.close()

    @staticmethod
    def delete(session_id: str) -> bool:
        conn = get_db_connection()
        try:
            result = conn.execute(
                "DELETE FROM user_sessions WHERE id = ?", (session_id,)
            )
            conn.commit()
            return result.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def delete_by_token(session_token: str) -> bool:
        conn = get_db_connection()
        try:
            result = conn.execute(
                "DELETE FROM user_sessions WHERE session_token = ?", (session_token,)
            )
            conn.commit()
            return result.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def cleanup_expired():
        """Remove expired sessions."""
        conn = get_db_connection()
        try:
            result = conn.execute(
                "DELETE FROM user_sessions WHERE expires_at < datetime('now')"
            )
            conn.commit()
            if result.rowcount > 0:
                logger.info(f"Cleaned up {result.rowcount} expired sessions")
        finally:
            conn.close()


class TokenUsageRepository:
    """Data access for token usage tracking."""

    @staticmethod
    def record(usage_data: Dict):
        """Record a token usage entry."""
        conn = get_db_connection()
        try:
            conn.execute(
                """INSERT INTO token_usage
                   (session_id, provider, model, prompt_tokens, completion_tokens,
                    total_tokens, endpoint, latency_ms)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    usage_data.get("session_id"),
                    usage_data.get("provider", "unknown"),
                    usage_data.get("model", "unknown"),
                    usage_data.get("prompt_tokens", 0),
                    usage_data.get("completion_tokens", 0),
                    usage_data.get("total_tokens", 0),
                    usage_data.get("endpoint"),
                    usage_data.get("latency_ms", 0),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def get_usage_summary(session_id: Optional[str] = None) -> Dict:
        """Get aggregated usage statistics."""
        conn = get_db_connection()
        try:
            if session_id:
                row = conn.execute(
                    """SELECT
                        COUNT(*) as total_requests,
                        SUM(prompt_tokens) as total_prompt_tokens,
                        SUM(completion_tokens) as total_completion_tokens,
                        SUM(total_tokens) as total_tokens,
                        AVG(latency_ms) as avg_latency_ms
                       FROM token_usage WHERE session_id = ?""",
                    (session_id,),
                ).fetchone()
            else:
                row = conn.execute(
                    """SELECT
                        COUNT(*) as total_requests,
                        SUM(prompt_tokens) as total_prompt_tokens,
                        SUM(completion_tokens) as total_completion_tokens,
                        SUM(total_tokens) as total_tokens,
                        AVG(latency_ms) as avg_latency_ms
                       FROM token_usage"""
                ).fetchone()

            return {
                "total_requests": row["total_requests"] or 0,
                "total_prompt_tokens": row["total_prompt_tokens"] or 0,
                "total_completion_tokens": row["total_completion_tokens"] or 0,
                "total_tokens": row["total_tokens"] or 0,
                "avg_latency_ms": round(row["avg_latency_ms"] or 0, 1),
            }
        finally:
            conn.close()

    @staticmethod
    def get_usage_by_provider(session_id: Optional[str] = None) -> List[Dict]:
        """Get usage breakdown by provider."""
        conn = get_db_connection()
        try:
            query = """SELECT provider, model,
                        COUNT(*) as requests,
                        SUM(total_tokens) as total_tokens,
                        AVG(latency_ms) as avg_latency
                       FROM token_usage"""
            params = ()
            if session_id:
                query += " WHERE session_id = ?"
                params = (session_id,)
            query += " GROUP BY provider, model ORDER BY requests DESC"

            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()
