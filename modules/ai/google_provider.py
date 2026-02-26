"""
PERSEPTOR v2.0 - Google Gemini Provider
Supports Gemini 2.5 Pro, 2.5 Flash, 2.0 Flash.
"""

import time
from typing import List, Optional
from modules.ai.base_provider import AIProvider, AIResponse, Message, ModelInfo, TokenUsage
from modules.logging_config import get_logger

logger = get_logger("ai.google")

GOOGLE_MODELS = [
    ModelInfo(
        provider="google", model_id="gemini-2.5-pro",
        display_name="Gemini 2.5 Pro", tier="flagship",
        max_tokens=1000000, supports_streaming=True, supports_temperature=True,
        cost_per_1k_input=0.00125, cost_per_1k_output=0.005,
    ),
    ModelInfo(
        provider="google", model_id="gemini-2.5-flash",
        display_name="Gemini 2.5 Flash", tier="efficient",
        max_tokens=1000000, supports_streaming=True, supports_temperature=True,
        cost_per_1k_input=0.00015, cost_per_1k_output=0.0006,
    ),
    ModelInfo(
        provider="google", model_id="gemini-2.0-flash",
        display_name="Gemini 2.0 Flash", tier="efficient",
        max_tokens=1000000, supports_streaming=True, supports_temperature=True,
        cost_per_1k_input=0.0001, cost_per_1k_output=0.0004,
    ),
]

_MODEL_MAP = {m.model_id: m for m in GOOGLE_MODELS}


class GoogleProvider(AIProvider):
    """Google Gemini API provider."""

    def __init__(self, api_key: str, default_model: str = "gemini-2.5-flash", **kwargs):
        super().__init__(api_key, default_model, **kwargs)
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self._genai = genai
        except ImportError:
            raise ImportError(
                "google-generativeai package is required. Install with: pip install google-generativeai>=0.5.0"
            )
        logger.info(f"Google provider initialized with model: {default_model}")

    @property
    def provider_name(self) -> str:
        return "google"

    def _build_contents(self, messages: List[Message]):
        """Convert Message list to Gemini content format."""
        # Gemini uses a different format: system instruction separate, then user/model turns
        system_parts = []
        contents = []

        for m in messages:
            if m.role == "system":
                system_parts.append(m.content)
            elif m.role == "user":
                contents.append({"role": "user", "parts": [{"text": m.content}]})
            elif m.role == "assistant":
                contents.append({"role": "model", "parts": [{"text": m.content}]})

        return system_parts, contents

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

        system_parts, contents = self._build_contents(messages)

        # Create model with system instruction
        gen_config = self._genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        model_kwargs = {"model_name": model_id, "generation_config": gen_config}
        if system_parts:
            model_kwargs["system_instruction"] = "\n".join(system_parts)

        gemini_model = self._genai.GenerativeModel(**model_kwargs)

        # If no user contents, create from system
        if not contents:
            contents = [{"role": "user", "parts": [{"text": "\n".join(system_parts)}]}]
            model_kwargs.pop("system_instruction", None)
            gemini_model = self._genai.GenerativeModel(
                model_name=model_id, generation_config=gen_config
            )

        response = gemini_model.generate_content(contents)
        latency = (time.perf_counter() - start_time) * 1000

        content = response.text if response.text else ""

        # Extract token usage from response metadata
        usage_meta = getattr(response, "usage_metadata", None)
        usage = TokenUsage(
            prompt_tokens=getattr(usage_meta, "prompt_token_count", 0) if usage_meta else 0,
            completion_tokens=getattr(usage_meta, "candidates_token_count", 0) if usage_meta else 0,
            total_tokens=getattr(usage_meta, "total_token_count", 0) if usage_meta else 0,
        )

        logger.info(
            f"Google generation complete",
            extra={"model": model_id, "tokens": usage.total_tokens, "duration_ms": latency},
        )

        return AIResponse(
            content=content,
            model=model_id,
            provider="google",
            usage=usage,
            latency_ms=latency,
            finish_reason=str(getattr(response.candidates[0], "finish_reason", "")) if response.candidates else "",
            raw_response=response,
        )

    def generate_stream(self, messages, model=None, temperature=0.1, max_tokens=4096, **kwargs):
        """Stream response chunks."""
        model_id = self._resolve_model(model)
        system_parts, contents = self._build_contents(messages)

        gen_config = self._genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        model_kwargs = {"model_name": model_id, "generation_config": gen_config}
        if system_parts:
            model_kwargs["system_instruction"] = "\n".join(system_parts)

        gemini_model = self._genai.GenerativeModel(**model_kwargs)

        if not contents:
            contents = [{"role": "user", "parts": [{"text": "\n".join(system_parts)}]}]

        response = gemini_model.generate_content(contents, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text

    def get_model_info(self, model=None):
        model_id = self._resolve_model(model)
        return _MODEL_MAP.get(model_id, GOOGLE_MODELS[0])

    def list_models(self):
        return GOOGLE_MODELS.copy()
