"""
PERSEPTOR v2.0 - Central Configuration Management
All application settings, AI provider configs, and environment defaults.
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, List
from dotenv import load_dotenv

# Load .env file from project root
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_project_root, '.env'))


@dataclass
class AIProviderConfig:
    """Configuration for a single AI provider."""
    provider: str  # "openai", "anthropic", "google"
    api_key: str = ""
    default_model: str = ""
    temperature: float = 0.1
    max_tokens: int = 4096
    reasoning_effort: str = "high"

    # Provider-specific model catalogs
    PROVIDER_MODELS: Dict[str, List[Dict[str, str]]] = field(default_factory=lambda: {
        "openai": [
            {"id": "gpt-4.1-2025-04-14", "name": "GPT-4.1", "tier": "flagship"},
            {"id": "gpt-4.1-mini-2025-04-14", "name": "GPT-4.1 Mini", "tier": "efficient"},
            {"id": "gpt-4o", "name": "GPT-4o", "tier": "flagship"},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "tier": "efficient"},
            {"id": "o4-mini-2025-04-16", "name": "O4 Mini (Reasoning)", "tier": "reasoning"},
            {"id": "o3-mini", "name": "O3 Mini (Reasoning)", "tier": "reasoning"},
        ],
        "anthropic": [
            {"id": "claude-sonnet-4-20250514", "name": "Claude Sonnet 4", "tier": "flagship"},
            {"id": "claude-opus-4-6", "name": "Claude Opus 4.6", "tier": "flagship"},
            {"id": "claude-haiku-4-5-20251001", "name": "Claude Haiku 4.5", "tier": "efficient"},
        ],
        "google": [
            {"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro", "tier": "flagship"},
            {"id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash", "tier": "efficient"},
            {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash", "tier": "efficient"},
        ],
    })

    # O-series models that don't accept temperature
    O_SERIES_MODELS = frozenset({
        "o1", "o1-mini", "o1-preview", "o3", "o3-mini", "o4", "o4-mini",
        "o1-preview-2024-09-12", "o3-mini-2024-09-12", "o4-mini-2025-04-16"
    })


@dataclass
class DatabaseConfig:
    """Database configuration."""
    path: str = ""
    journal_mode: str = "WAL"
    busy_timeout: int = 5000

    def __post_init__(self):
        if not self.path:
            self.path = os.path.join(_project_root, "data", "perseptor.db")


@dataclass
class CacheConfig:
    """Cache configuration."""
    enabled: bool = True
    max_size: int = 100
    default_ttl: int = 3600  # seconds
    redis_url: str = ""


@dataclass
class SecurityConfig:
    """Security configuration."""
    cors_origins: List[str] = field(default_factory=lambda: ["http://localhost:3000"])
    rate_limit_per_minute: int = 60
    max_upload_size_mb: int = 10
    session_expiry_hours: int = 24
    secret_key: str = ""

    def __post_init__(self):
        if not self.secret_key:
            self.secret_key = os.environ.get("SECRET_KEY", os.urandom(32).hex())


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "json"  # "json" or "text"
    file_path: str = ""
    max_file_size_mb: int = 10
    backup_count: int = 5

    def __post_init__(self):
        if not self.file_path:
            self.file_path = os.path.join(_project_root, "logs", "perseptor.log")


class AppConfig:
    """
    Central application configuration. Singleton pattern.
    Reads from environment variables with sensible defaults.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._load_config()

    def _load_config(self):
        """Load all configuration from environment variables."""

        # Application
        self.app_name = "PERSEPTOR"
        self.version = "2.0.0"
        self.debug = os.environ.get("FLASK_ENV", "development") == "development"
        self.host = os.environ.get("BACKEND_HOST", "0.0.0.0")
        self.port = int(os.environ.get("BACKEND_PORT", "5000"))

        # AI Providers
        self.default_provider = os.environ.get("DEFAULT_AI_PROVIDER", "openai")
        self.default_model = os.environ.get("DEFAULT_MODEL", "gpt-4.1-2025-04-14")

        self.ai_providers = {
            "openai": AIProviderConfig(
                provider="openai",
                api_key=os.environ.get("OPENAI_API_KEY", ""),
                default_model="gpt-4.1-2025-04-14",
                temperature=float(os.environ.get("OPENAI_TEMPERATURE", "0.1")),
            ),
            "anthropic": AIProviderConfig(
                provider="anthropic",
                api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
                default_model="claude-sonnet-4-20250514",
                temperature=float(os.environ.get("ANTHROPIC_TEMPERATURE", "0.1")),
            ),
            "google": AIProviderConfig(
                provider="google",
                api_key=os.environ.get("GOOGLE_API_KEY", ""),
                default_model="gemini-2.5-flash",
                temperature=float(os.environ.get("GOOGLE_TEMPERATURE", "0.1")),
            ),
        }

        # Database
        self.database = DatabaseConfig(
            path=os.environ.get("DATABASE_PATH", ""),
            journal_mode=os.environ.get("DB_JOURNAL_MODE", "WAL"),
        )

        # Cache
        self.cache = CacheConfig(
            enabled=os.environ.get("CACHE_ENABLED", "true").lower() == "true",
            max_size=int(os.environ.get("CACHE_MAX_SIZE", "100")),
            default_ttl=int(os.environ.get("CACHE_TTL", "3600")),
            redis_url=os.environ.get("REDIS_URL", ""),
        )

        # Security
        cors_raw = os.environ.get("CORS_ORIGINS", "http://localhost:3000")
        self.security = SecurityConfig(
            cors_origins=[o.strip() for o in cors_raw.split(",")],
            rate_limit_per_minute=int(os.environ.get("RATE_LIMIT_PER_MINUTE", "60")),
            max_upload_size_mb=int(os.environ.get("MAX_UPLOAD_SIZE_MB", "10")),
            session_expiry_hours=int(os.environ.get("SESSION_EXPIRY_HOURS", "24")),
            secret_key=os.environ.get("SECRET_KEY", ""),
        )

        # Logging
        self.logging = LoggingConfig(
            level=os.environ.get("LOG_LEVEL", "INFO"),
            format=os.environ.get("LOG_FORMAT", "json"),
            file_path=os.environ.get("LOG_FILE_PATH", ""),
        )

        # OCR
        self.tesseract_cmd = os.environ.get("TESSERACT_CMD", "/usr/bin/tesseract")
        self.ocr_engine = os.environ.get("OCR_ENGINE", "tesseract")  # "tesseract" or "easyocr"

        # Sigma Rules
        self.sigma_rules_dir = os.environ.get(
            "SIGMA_RULES_DIR",
            os.path.join(_project_root, "Global_Sigma_Rules")
        )
        self.sigma_rule_author = os.environ.get("SIGMA_RULE_AUTHOR", "PERSEPTOR")

    def get_provider_config(self, provider: str) -> AIProviderConfig:
        """Get configuration for a specific AI provider."""
        return self.ai_providers.get(provider, self.ai_providers[self.default_provider])

    def get_available_models(self) -> Dict[str, List[Dict[str, str]]]:
        """Get all available models organized by provider."""
        return AIProviderConfig.PROVIDER_MODELS

    def get_models_for_provider(self, provider: str) -> List[Dict[str, str]]:
        """Get available models for a specific provider."""
        return AIProviderConfig.PROVIDER_MODELS.get(provider, [])

    def to_dict(self) -> dict:
        """Return safe (no secrets) config summary."""
        return {
            "app_name": self.app_name,
            "version": self.version,
            "debug": self.debug,
            "default_provider": self.default_provider,
            "default_model": self.default_model,
            "available_providers": list(self.ai_providers.keys()),
            "database_path": self.database.path,
            "cache_enabled": self.cache.enabled,
            "log_level": self.logging.level,
            "sigma_rules_dir": self.sigma_rules_dir,
        }


# Global config instance
config = AppConfig()
