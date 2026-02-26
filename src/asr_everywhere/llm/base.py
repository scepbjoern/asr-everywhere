"""Abstract base class for LLM providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from asr_everywhere.config import LLMConfig


@dataclass
class PostProcessResult:
    """Result of LLM post-processing."""

    text: str
    original_text: str


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def post_process(
        self,
        text: str,
        config: LLMConfig,
        dictionary: list[str],
    ) -> PostProcessResult:
        """Post-process transcribed text.

        Args:
            text: The transcribed text to process
            config: LLM configuration
            dictionary: List of custom terms for proper spelling

        Returns:
            PostProcessResult with processed text and original text
        """
        ...

    @abstractmethod
    def list_models(self) -> list[str]:
        """Return list of available models for this provider."""
        ...
