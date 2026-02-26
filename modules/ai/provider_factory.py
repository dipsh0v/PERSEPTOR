"""
PERSEPTOR v2.0 - AI Provider Factory
Creates and caches provider instances based on configuration.
"""

from typing import Optional, Dict, List
from modules.ai.base_provider import AIProvider, ModelInfo
from modules.logging_config import get_logger

logger = get_logger("ai.factory")

# Provider instance cache: (provider_name, api_key_hash) -> AIProvider
_provider_cache: Dict[str, AIProvider] = {}


def _hash_key(api_key: str) -> str:
    """Create a short hash of the API key for caching (not for security)."""
    import hashlib
    return hashlib.sha256(api_key.encode()).hexdigest()[:16]


def get_provider(
    provider_name: str,
    api_key: str,
    model: Optional[str] = None,
    **kwargs,
) -> AIProvider:
    """
    Get an AI provider instance. Cached per (provider, api_key) pair.

    Args:
        provider_name: "openai", "anthropic", or "google"
        api_key: API key for the provider
        model: Default model override
        **kwargs: Additional provider-specific arguments

    Returns:
        AIProvider instance

    Raises:
        ValueError: If provider_name is not supported
        ImportError: If required SDK is not installed
    """
    if not api_key:
        raise ValueError(f"API key is required for provider '{provider_name}'")

    cache_key = f"{provider_name}:{_hash_key(api_key)}"

    if cache_key in _provider_cache:
        provider = _provider_cache[cache_key]
        # Update default model if specified
        if model:
            provider.default_model = model
        return provider

    provider_name = provider_name.lower().strip()

    if provider_name == "openai":
        from modules.ai.openai_provider import OpenAIProvider
        provider = OpenAIProvider(
            api_key=api_key,
            default_model=model or "gpt-4.1-2025-04-14",
            **kwargs,
        )

    elif provider_name == "anthropic":
        from modules.ai.anthropic_provider import AnthropicProvider
        provider = AnthropicProvider(
            api_key=api_key,
            default_model=model or "claude-sonnet-4-20250514",
            **kwargs,
        )

    elif provider_name == "google":
        from modules.ai.google_provider import GoogleProvider
        provider = GoogleProvider(
            api_key=api_key,
            default_model=model or "gemini-2.5-flash",
            **kwargs,
        )

    else:
        raise ValueError(
            f"Unsupported provider: '{provider_name}'. "
            f"Supported: openai, anthropic, google"
        )

    _provider_cache[cache_key] = provider
    logger.info(f"Created new {provider_name} provider (cached)")
    return provider


def _serialize_model(m) -> Dict:
    """Serialize a ModelInfo to dict matching frontend ModelInfo interface."""
    return {
        "model_id": m.model_id,
        "display_name": m.display_name,
        "tier": m.tier,
        "max_tokens": m.max_tokens,
        "supports_streaming": m.supports_streaming,
        "cost_per_1k_input": getattr(m, 'cost_per_1k_input', 0.0),
        "cost_per_1k_output": getattr(m, 'cost_per_1k_output', 0.0),
    }


def get_available_providers() -> List[Dict]:
    """Get list of available providers with their models.
    Returns format matching frontend ProviderInfo interface:
      { provider, display_name, models: ModelInfo[], key_prefix }
    """
    providers = []

    # OpenAI
    try:
        from modules.ai.openai_provider import OPENAI_MODELS
        providers.append({
            "provider": "openai",
            "display_name": "OpenAI",
            "models": [_serialize_model(m) for m in OPENAI_MODELS],
            "key_prefix": "sk-",
        })
    except ImportError:
        pass

    # Anthropic
    try:
        from modules.ai.anthropic_provider import ANTHROPIC_MODELS
        providers.append({
            "provider": "anthropic",
            "display_name": "Anthropic",
            "models": [_serialize_model(m) for m in ANTHROPIC_MODELS],
            "key_prefix": "sk-ant-",
        })
    except ImportError:
        pass

    # Google
    try:
        from modules.ai.google_provider import GOOGLE_MODELS
        providers.append({
            "provider": "google",
            "display_name": "Google Gemini",
            "models": [_serialize_model(m) for m in GOOGLE_MODELS],
            "key_prefix": "AIza",
        })
    except ImportError:
        pass

    return providers


def clear_cache():
    """Clear the provider cache."""
    global _provider_cache
    _provider_cache.clear()
    logger.info("Provider cache cleared")
