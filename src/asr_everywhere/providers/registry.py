"""Provider registry for ASR providers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from asr_everywhere.providers.base import ASRProvider
from asr_everywhere.providers.openai_compat import OpenAICompatProvider
from asr_everywhere.providers.openai_provider import OpenAIProvider

if TYPE_CHECKING:
    pass

# Registry mapping provider names to classes
PROVIDERS: dict[str, type[ASRProvider] | callable] = {
    "openai": OpenAIProvider,
    "together": lambda: OpenAICompatProvider("together"),
    "huggingface": lambda: OpenAICompatProvider("huggingface"),
    "local": lambda: OpenAICompatProvider("local"),
}


def get_provider(name: str) -> ASRProvider:
    """Get an instance of the specified provider.

    Args:
        name: Provider name (e.g., "openai")

    Returns:
        Instance of the provider

    Raises:
        ValueError: If provider name is not recognized
    """
    if name not in PROVIDERS:
        available = ", ".join(PROVIDERS.keys())
        raise ValueError(f"Unknown provider '{name}'. Available: {available}")

    provider_class = PROVIDERS[name]
    # Handle lambda factories
    if callable(provider_class) and not isinstance(provider_class, type):
        return provider_class()
    return provider_class()


def list_providers() -> list[str]:
    """Return list of available provider names."""
    return list(PROVIDERS.keys())


def get_provider_models(provider_name: str) -> list[str]:
    """Get available models for a provider.

    Args:
        provider_name: Name of the provider

    Returns:
        List of model names
    """
    provider = get_provider(provider_name)
    return provider.list_models()
