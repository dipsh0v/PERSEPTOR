"""
PERSEPTOR v2.0 - Abstract Base AI Provider
Defines the interface that all AI providers must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, AsyncIterator, Dict, Any


@dataclass
class Message:
    """Universal message format across all providers."""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class TokenUsage:
    """Token usage tracking."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class AIResponse:
    """Standardized response from any AI provider."""
    content: str
    model: str
    provider: str
    usage: TokenUsage = field(default_factory=TokenUsage)
    latency_ms: float = 0.0
    finish_reason: str = ""
    raw_response: Any = None


@dataclass
class ModelInfo:
    """Information about a specific model."""
    provider: str
    model_id: str
    display_name: str
    tier: str  # "flagship", "efficient", "reasoning"
    max_tokens: int = 128000
    supports_streaming: bool = True
    supports_temperature: bool = True
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0


class AIProvider(ABC):
    """
    Abstract base class for AI providers.
    All providers (OpenAI, Anthropic, Google) must implement this interface.
    """

    def __init__(self, api_key: str, default_model: str = "", **kwargs):
        self.api_key = api_key
        self.default_model = default_model
        self._kwargs = kwargs

    @abstractmethod
    def generate(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        **kwargs,
    ) -> AIResponse:
        """
        Generate a response from the AI model (synchronous).

        Args:
            messages: List of Message objects (system, user, assistant)
            model: Model ID to use (overrides default)
            temperature: Sampling temperature (0.0 - 1.0)
            max_tokens: Maximum tokens in response
        """
        ...

    @abstractmethod
    def generate_stream(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        **kwargs,
    ):
        """
        Generate a streaming response (yields string chunks).

        Yields:
            str: Content chunks as they are generated
        """
        ...

    @abstractmethod
    def get_model_info(self, model: Optional[str] = None) -> ModelInfo:
        """Get information about a specific model or the default model."""
        ...

    @abstractmethod
    def list_models(self) -> List[ModelInfo]:
        """List all available models for this provider."""
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name (e.g., 'openai', 'anthropic', 'google')."""
        ...

    def _resolve_model(self, model: Optional[str]) -> str:
        """Resolve model ID, using default if not specified."""
        return model or self.default_model
