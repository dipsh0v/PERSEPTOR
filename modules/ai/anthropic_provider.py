"""
PERSEPTOR v2.0 - Anthropic Claude Provider
Supports Claude Sonnet 4, Opus 4.6, Haiku 4.5.
"""

import time
from typing import List, Optional
from modules.ai.base_provider import AIProvider, AIResponse, Message, ModelInfo, TokenUsage
from modules.logging_config import get_logger

logger = get_logger("ai.anthropic")

ANTHROPIC_MODELS = [
    ModelInfo(
        provider="anthropic", model_id="claude-sonnet-4-20250514",
        display_name="Claude Sonnet 4", tier="flagship",
        max_tokens=200000, supports_streaming=True, supports_temperature=True,
        cost_per_1k_input=0.003, cost_per_1k_output=0.015,
    ),
    ModelInfo(
        provider="anthropic", model_id="claude-opus-4-6",
        display_name="Claude Opus 4.6", tier="flagship",
        max_tokens=200000, supports_streaming=True, supports_temperature=True,
        cost_per_1k_input=0.015, cost_per_1k_output=0.075,
    ),
    ModelInfo(
        provider="anthropic", model_id="claude-haiku-4-5-20251001",
        display_name="Claude Haiku 4.5", tier="efficient",
        max_tokens=200000, supports_streaming=True, supports_temperature=True,
        cost_per_1k_input=0.0008, cost_per_1k_output=0.004,
    ),
]

_MODEL_MAP = {m.model_id: m for m in ANTHROPIC_MODELS}


class AnthropicProvider(AIProvider):
    """Anthropic Claude API provider."""

    def __init__(self, api_key: str, default_model: str = "claude-sonnet-4-20250514", **kwargs):
        super().__init__(api_key, default_model, **kwargs)
        try:
            import anthropic
            self._client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError(
                "anthropic package is required. Install with: pip install anthropic>=0.30.0"
            )
        logger.info(f"Anthropic provider initialized with model: {default_model}")

    @property
    def provider_name(self) -> str:
        return "anthropic"

    def generate(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        **kwargs,
    ) -> AIResponse:
        model_id = self._resolve_model(model)
        start_time = time.perf_counter()

        # Anthropic separates system prompt from messages
        system_prompt = ""
        user_messages = []
        for m in messages:
            if m.role == "system":
                system_prompt += m.content + "\n"
            else:
                user_messages.append({"role": m.role, "content": m.content})

        # Ensure at least one user message
        if not user_messages:
            user_messages = [{"role": "user", "content": system_prompt.strip()}]
            system_prompt = ""

        params = {
            "model": model_id,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": user_messages,
        }
        if system_prompt.strip():
            params["system"] = system_prompt.strip()

        response = self._client.messages.create(**params)
        latency = (time.perf_counter() - start_time) * 1000

        content = ""
        for block in response.content:
            if hasattr(block, "text"):
                content += block.text

        usage = TokenUsage(
            prompt_tokens=response.usage.input_tokens if response.usage else 0,
            completion_tokens=response.usage.output_tokens if response.usage else 0,
            total_tokens=(
                (response.usage.input_tokens + response.usage.output_tokens)
                if response.usage else 0
            ),
        )

        logger.info(
            f"Anthropic generation complete",
            extra={"model": model_id, "tokens": usage.total_tokens, "duration_ms": latency},
        )

        return AIResponse(
            content=content,
            model=model_id,
            provider="anthropic",
            usage=usage,
            latency_ms=latency,
            finish_reason=response.stop_reason or "",
            raw_response=response,
        )

    def generate_stream(self, messages, model=None, temperature=0.1, max_tokens=4096, **kwargs):
        """Stream response chunks using Anthropic streaming API."""
        model_id = self._resolve_model(model)

        system_prompt = ""
        user_messages = []
        for m in messages:
            if m.role == "system":
                system_prompt += m.content + "\n"
            else:
                user_messages.append({"role": m.role, "content": m.content})

        if not user_messages:
            user_messages = [{"role": "user", "content": system_prompt.strip()}]
            system_prompt = ""

        params = {
            "model": model_id,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": user_messages,
        }
        if system_prompt.strip():
            params["system"] = system_prompt.strip()

        with self._client.messages.stream(**params) as stream:
            for text in stream.text_stream:
                yield text

    def get_model_info(self, model=None):
        model_id = self._resolve_model(model)
        return _MODEL_MAP.get(model_id, ANTHROPIC_MODELS[0])

    def list_models(self):
        return ANTHROPIC_MODELS.copy()
