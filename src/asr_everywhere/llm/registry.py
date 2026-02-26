"""LLM provider registry."""

from __future__ import annotations

from asr_everywhere.llm.base import LLMProvider
from asr_everywhere.llm.openai_compat_llm import OpenAICompatLLMProvider
from asr_everywhere.llm.openai_llm import OpenAILLMProvider

# Registry of LLM providers
LLM_PROVIDERS: dict[str, type[LLMProvider]] = {
    "openai": OpenAILLMProvider,
    "together": OpenAICompatLLMProvider,
    "huggingface": OpenAICompatLLMProvider,
    "local": OpenAICompatLLMProvider,
}


def get_llm_provider(name: str) -> LLMProvider:
    """Get LLM provider instance by name.

    Args:
        name: Provider name (e.g., "openai", "together", "local")

    Returns:
        LLMProvider instance

    Raises:
        ValueError: If provider name is not recognized
    """
    if name not in LLM_PROVIDERS:
        raise ValueError(f"Unknown LLM provider: {name}. Available: {list_llm_providers()}")
    return LLM_PROVIDERS[name]()


def list_llm_providers() -> list[str]:
    """Return list of available LLM provider names."""
    return list(LLM_PROVIDERS.keys())
