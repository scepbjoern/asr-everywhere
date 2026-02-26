"""Provider registry for ASR providers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from asr_everywhere.providers.base import ASRProvider
from asr_everywhere.providers.openai_provider import OpenAIProvider

if TYPE_CHECKING:
    pass

# Registry mapping provider names to classes
PROVIDERS: dict[str, type[ASRProvider]] = {
    "openai": OpenAIProvider,
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

    return PROVIDERS[name]()


def list_providers() -> list[str]:
    """Return list of available provider names."""
    return list(PROVIDERS.keys())
