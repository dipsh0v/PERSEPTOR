"""
PERSEPTOR v2.0 - Session Manager
Handles API key encryption, session token generation, and session lifecycle.
"""

import os
import uuid
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict
from cryptography.fernet import Fernet
from modules.config import config
from modules.database.repository import SessionRepository
from modules.logging_config import get_logger

logger = get_logger("session")


class SessionManager:
    """Manages encrypted sessions for API key storage."""

    def __init__(self):
        # Derive Fernet key from secret_key
        secret = config.security.secret_key
        if not secret:
            secret = os.urandom(32).hex()
        # Fernet requires 32 url-safe base64-encoded bytes
        key_bytes = secret.encode()[:32].ljust(32, b'\0')
        self._fernet = Fernet(base64.urlsafe_b64encode(key_bytes))
        self._expiry_hours = config.security.session_expiry_hours

    def create_session(
        self,
        api_key: str,
        provider: str = "openai",
        model_preference: Optional[str] = None,
    ) -> Dict:
        """
        Create a new session with encrypted API key.

        Args:
            api_key: The raw API key to encrypt
            provider: AI provider name
            model_preference: Preferred model ID

        Returns:
            Dict with session_token, expires_at
        """
        session_token = str(uuid.uuid4())
        encrypted_key = self._fernet.encrypt(api_key.encode()).decode()
        expires_at = datetime.now() + timedelta(hours=self._expiry_hours)

        session_data = {
            "session_token": session_token,
            "provider": provider,
            "encrypted_api_key": encrypted_key,
            "model_preference": model_preference,
            "expires_at": expires_at.isoformat(),
        }

        session_id = SessionRepository.create(session_data)
        logger.info(f"Session created for provider: {provider}")

        return {
            "session_token": session_token,
            "session_id": session_id,
            "provider": provider,
            "model_preference": model_preference,
            "expires_at": expires_at.isoformat(),
        }

    def validate_session(self, session_token: str) -> Optional[Dict]:
        """
        Validate a session token and return decrypted API key.

        Returns:
            Dict with api_key, provider, model_preference or None if invalid
        """
        session = SessionRepository.get_by_token(session_token)
        if not session:
            return None

        try:
            api_key = self._fernet.decrypt(
                session["encrypted_api_key"].encode()
            ).decode()

            return {
                "session_id": session["id"],
                "api_key": api_key,
                "provider": session["provider"],
                "model_preference": session["model_preference"],
            }
        except Exception as e:
            logger.error(f"Session decryption failed: {e}")
            return None

    def destroy_session(self, session_token: str) -> bool:
        """Destroy a session."""
        result = SessionRepository.delete_by_token(session_token)
        if result:
            logger.info("Session destroyed")
        return result

    def cleanup_expired(self):
        """Remove all expired sessions."""
        SessionRepository.cleanup_expired()


# Global session manager instance
session_manager = SessionManager()
