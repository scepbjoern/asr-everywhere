"""LLM post-processing orchestrator."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from asr_everywhere.llm.registry import get_llm_provider

if TYPE_CHECKING:
    from asr_everywhere.config import Config

logger = logging.getLogger(__name__)


class PostProcessor:
    """Orchestrates LLM post-processing of transcribed text."""

    def __init__(self, config: Config) -> None:
        """Initialize post-processor.

        Args:
            config: Application configuration
        """
        self._config = config

    def process(self, text: str) -> str:
        """Post-process text if LLM is enabled.

        Args:
            text: The transcribed text to process

        Returns:
            Processed text if LLM enabled, otherwise original text
        """
        if not self._config.llm.enabled:
            logger.debug("LLM post-processing disabled, returning original text")
            return text

        if not text.strip():
            logger.debug("Empty text, skipping LLM post-processing")
            return text

        try:
            provider = get_llm_provider(self._config.llm.provider)
            result = provider.post_process(
                text,
                self._config.llm,
                self._config.dictionary,
            )
            logger.info("LLM post-processing successful")
            return result.text

        except Exception as e:
            logger.error(f"LLM post-processing failed: {e}")
            # Graceful degradation: return original text
            raise
