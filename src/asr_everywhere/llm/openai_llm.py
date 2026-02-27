"""OpenAI LLM provider implementation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from openai import OpenAI

from asr_everywhere.llm.base import LLMProvider, PostProcessResult
from asr_everywhere.llm.prompts import build_system_prompt

if TYPE_CHECKING:
    from asr_everywhere.config import LLMConfig

logger = logging.getLogger(__name__)


class OpenAILLMProvider(LLMProvider):
    """OpenAI LLM provider for post-processing transcriptions."""

    def __init__(self) -> None:
        """Initialize OpenAI LLM provider."""
        self._client: OpenAI | None = None

    def _get_client(self, api_key: str, base_url: str) -> OpenAI:
        """Get or create OpenAI client."""
        if self._client is None:
            self._client = OpenAI(api_key=api_key, base_url=base_url)
        return self._client

    def post_process(
        self,
        text: str,
        config: LLMConfig,
        dictionary: list[str],
    ) -> PostProcessResult:
        """Post-process text using OpenAI LLM.

        Args:
            text: The transcribed text to process
            config: LLM configuration
            dictionary: List of custom terms for proper spelling

        Returns:
            PostProcessResult with processed text
        """
        api_key = config.get_api_key()
        base_url = config.get_base_url()

        if not api_key:
            logger.error("No API key configured for OpenAI LLM")
            raise ValueError("No API key configured for OpenAI LLM")

        client = self._get_client(api_key, base_url)
        system_prompt = build_system_prompt(
            config.custom_instructions, dictionary, config.voice_commands_enabled
        )

        logger.info(f"Post-processing text with OpenAI LLM: {config.model}")
        logger.info(f"System prompt ({len(system_prompt)} chars): {system_prompt[:500]}...")

        try:
            if config.model.startswith("gpt-5"):
                # GPT-5 models don't support temperature (only default 1)
                response = client.chat.completions.create(
                    model=config.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text},
                    ],
                    max_completion_tokens=4096,
                )
            else:
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
            logger.error(f"OpenAI LLM post-processing failed: {e}")
            raise

    def list_models(self) -> list[str]:
        """Return list of available models."""
        return ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
