"""
PERSEPTOR v2.0 - OpenAI Provider
Supports GPT-4.1, GPT-4o, O-series reasoning models.
"""

import time
from typing import List, Optional
from modules.ai.base_provider import AIProvider, AIResponse, Message, ModelInfo, TokenUsage
from modules.logging_config import get_logger

logger = get_logger("ai.openai")

# O-series models don't accept temperature parameter
O_SERIES_MODELS = frozenset({
    "o1", "o1-mini", "o1-preview", "o1-preview-2024-09-12",
    "o3", "o3-mini", "o3-mini-2024-09-12",
    "o4", "o4-mini", "o4-mini-2025-04-16",
})

OPENAI_MODELS = [
    ModelInfo(
        provider="openai", model_id="gpt-4.1-2025-04-14",
        display_name="GPT-4.1", tier="flagship",
        max_tokens=128000, supports_streaming=True, supports_temperature=True,
        cost_per_1k_input=0.002, cost_per_1k_output=0.008,
    ),
    ModelInfo(
        provider="openai", model_id="gpt-4.1-mini-2025-04-14",
        display_name="GPT-4.1 Mini", tier="efficient",
        max_tokens=128000, supports_streaming=True, supports_temperature=True,
        cost_per_1k_input=0.0004, cost_per_1k_output=0.0016,
    ),
    ModelInfo(
        provider="openai", model_id="gpt-4o",
        display_name="GPT-4o", tier="flagship",
        max_tokens=128000, supports_streaming=True, supports_temperature=True,
        cost_per_1k_input=0.0025, cost_per_1k_output=0.01,
    ),
    ModelInfo(
        provider="openai", model_id="gpt-4o-mini",
        display_name="GPT-4o Mini", tier="efficient",
        max_tokens=128000, supports_streaming=True, supports_temperature=True,
        cost_per_1k_input=0.00015, cost_per_1k_output=0.0006,
    ),
    ModelInfo(
        provider="openai", model_id="o4-mini-2025-04-16",
        display_name="O4 Mini (Reasoning)", tier="reasoning",
        max_tokens=128000, supports_streaming=True, supports_temperature=False,
        cost_per_1k_input=0.0011, cost_per_1k_output=0.0044,
    ),
    ModelInfo(
        provider="openai", model_id="o3-mini",
        display_name="O3 Mini (Reasoning)", tier="reasoning",
        max_tokens=128000, supports_streaming=True, supports_temperature=False,
        cost_per_1k_input=0.0011, cost_per_1k_output=0.0044,
    ),
]

_MODEL_MAP = {m.model_id: m for m in OPENAI_MODELS}


class OpenAIProvider(AIProvider):
    """OpenAI API provider using the official SDK."""

    def __init__(self, api_key: str, default_model: str = "gpt-4.1-2025-04-14", **kwargs):
        super().__init__(api_key, default_model, **kwargs)
        try:
            from openai import OpenAI
            self._client = OpenAI(api_key=api_key)
        except ImportError:
            # Fallback to langchain
            self._client = None
        logger.info(f"OpenAI provider initialized with model: {default_model}")

    @property
    def provider_name(self) -> str:
        return "openai"

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

        if self._client:
            return self._generate_native(messages, model_id, temperature, max_tokens, start_time, **kwargs)
        return self._generate_langchain(messages, model_id, temperature, max_tokens, start_time, **kwargs)

    def _generate_native(self, messages, model_id, temperature, max_tokens, start_time, **kwargs):
        """Generate using OpenAI native SDK."""
        is_o_series = model_id in O_SERIES_MODELS

        # O-series models: "system" → "developer", drop "assistant" few-shot messages
        formatted = []
        for m in messages:
            role = m.role
            if is_o_series:
                if role == "system":
                    role = "developer"
                elif role == "assistant":
                    # O-series doesn't support assistant prefill; skip few-shot examples
                    continue
            formatted.append({"role": role, "content": m.content})

        params = {
            "model": model_id,
            "messages": formatted,
        }

        # O-series reasoning models require max_completion_tokens instead of max_tokens
        # and don't accept the temperature parameter
        if is_o_series:
            params["max_completion_tokens"] = max_tokens
        else:
            params["max_tokens"] = max_tokens
            params["temperature"] = temperature

        response = self._client.chat.completions.create(**params)
        latency = (time.perf_counter() - start_time) * 1000

        choice = response.choices[0]

        # O-series may return content in message.content or as empty with reasoning
        content = choice.message.content or ""
        if not content and hasattr(choice.message, 'refusal') and choice.message.refusal:
            content = choice.message.refusal
            logger.warning(f"Model refusal: {content[:200]}")

        # Log first 300 chars for debugging
        logger.debug(f"Raw response content (first 300): {content[:300]}")

        usage = TokenUsage(
            prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
            completion_tokens=response.usage.completion_tokens if response.usage else 0,
            total_tokens=response.usage.total_tokens if response.usage else 0,
        )

        logger.info(
            f"OpenAI generation complete",
            extra={
                "model": model_id,
                "tokens": usage.total_tokens,
                "duration_ms": latency,
                "content_length": len(content),
            },
        )

        return AIResponse(
            content=content,
            model=model_id,
            provider="openai",
            usage=usage,
            latency_ms=latency,
            finish_reason=choice.finish_reason or "",
            raw_response=response,
        )

    def _generate_langchain(self, messages, model_id, temperature, max_tokens, start_time, **kwargs):
        """Fallback: generate using LangChain."""
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage

        params = {"model": model_id, "openai_api_key": self.api_key}
        if model_id not in O_SERIES_MODELS:
            params["temperature"] = temperature

        llm = ChatOpenAI(**params)

        lc_messages = []
        for m in messages:
            if m.role == "system":
                lc_messages.append(SystemMessage(content=m.content))
            else:
                lc_messages.append(HumanMessage(content=m.content))

        response = llm.invoke(lc_messages)
        latency = (time.perf_counter() - start_time) * 1000

        usage_meta = getattr(response, "response_metadata", {}).get("token_usage", {})
        usage = TokenUsage(
            prompt_tokens=usage_meta.get("prompt_tokens", 0),
            completion_tokens=usage_meta.get("completion_tokens", 0),
            total_tokens=usage_meta.get("total_tokens", 0),
        )

        logger.info(
            f"OpenAI (LangChain) generation complete",
            extra={"model": model_id, "tokens": usage.total_tokens, "duration_ms": latency},
        )

        return AIResponse(
            content=response.content or "",
            model=model_id,
            provider="openai",
            usage=usage,
            latency_ms=latency,
        )

    def generate_stream(self, messages, model=None, temperature=0.1, max_tokens=4096, **kwargs):
        """Stream response chunks."""
        model_id = self._resolve_model(model)

        if self._client:
            formatted = [{"role": m.role, "content": m.content} for m in messages]
            params = {"model": model_id, "messages": formatted, "stream": True}
            if model_id in O_SERIES_MODELS:
                params["max_completion_tokens"] = max_tokens
            else:
                params["max_tokens"] = max_tokens
                params["temperature"] = temperature

            stream = self._client.chat.completions.create(**params)
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        else:
            # Fallback: no streaming, return full response
            response = self.generate(messages, model_id, temperature, max_tokens, **kwargs)
            yield response.content

    def get_model_info(self, model=None):
        model_id = self._resolve_model(model)
        return _MODEL_MAP.get(model_id, OPENAI_MODELS[0])

    def list_models(self):
        return OPENAI_MODELS.copy()
