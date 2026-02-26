"""OpenAI-compatible LLM provider implementation (Together, local, etc.)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from openai import OpenAI

from asr_everywhere.llm.base import LLMProvider, PostProcessResult
from asr_everywhere.llm.prompts import build_system_prompt

if TYPE_CHECKING:
    from asr_everywhere.config import LLMConfig

logger = logging.getLogger(__name__)


class OpenAICompatLLMProvider(LLMProvider):
    """OpenAI-compatible LLM provider for post-processing (Together, local, etc.)."""

    def __init__(self) -> None:
        """Initialize OpenAI-compatible LLM provider."""
        self._client: OpenAI | None = None

    def _get_client(self, api_key: str, base_url: str) -> OpenAI:
        """Get or create OpenAI client with custom base URL."""
        if self._client is None:
            self._client = OpenAI(api_key=api_key, base_url=base_url)
        return self._client

    def post_process(
        self,
        text: str,
        config: LLMConfig,
        dictionary: list[str],
    ) -> PostProcessResult:
        """Post-process text using OpenAI-compatible LLM.

        Args:
            text: The transcribed text to process
            config: LLM configuration
            dictionary: List of custom terms for proper spelling

        Returns:
            PostProcessResult with processed text
        """
        api_key = config.get_api_key()
        base_url = config.get_base_url()

        if not base_url:
            logger.error("No base URL configured for LLM provider")
            raise ValueError("No base URL configured for LLM provider")

        # Use placeholder API key for local servers that don't require one
        effective_api_key = api_key or "sk-dummy"

        client = self._get_client(effective_api_key, base_url)
        system_prompt = build_system_prompt(config.custom_instructions, dictionary)

        logger.info(f"Post-processing text with LLM: {config.model} at {base_url}")

        try:
            response = client.chat.completions.create(
                model=config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                max_tokens=4096,
                temperature=0.3,
            )

            processed_text = response.choices[0].message.content or text
            logger.info(f"LLM post-processing complete: {len(processed_text)} chars")

            return PostProcessResult(text=processed_text, original_text=text)

        except Exception as e:
            logger.error(f"LLM post-processing failed: {e}")
            raise

    def list_models(self) -> list[str]:
        """Return list of available models (empty - user configured)."""
        return []
