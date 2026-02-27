"""OpenAI-compatible API provider (Together.ai, HuggingFace, OpenRouter, local)."""

from __future__ import annotations

import io
import logging
from typing import TYPE_CHECKING

from openai import OpenAI

from asr_everywhere.errors import ConfigError, categorize_openai_error
from asr_everywhere.providers.base import ASRProvider, TranscriptionResult

if TYPE_CHECKING:
    from asr_everywhere.config import ASRConfig

logger = logging.getLogger(__name__)

# Common models available on OpenAI-compatible endpoints
COMPAT_MODELS = ["whisper-1"]  # Most compatible endpoints support whisper-1


class OpenAICompatProvider(ASRProvider):
    """Generic OpenAI-compatible API provider.

    Works with Together.ai, Hugging Face Inference, OpenRouter,
    and local APIs (Ollama, LibreChat).
    """

    def __init__(self, provider_name: str = "compat") -> None:
        """Initialize OpenAI-compatible provider.

        Args:
            provider_name: Name for logging purposes
        """
        self._provider_name = provider_name
        self._client: OpenAI | None = None

    def _get_client(self, config: ASRConfig) -> OpenAI:
        """Get or create OpenAI client with provider-specific base_url.

        Raises:
            ConfigError: If API key is not configured for non-local providers
        """
        if self._client is None:
            api_key = config.get_api_key()
            base_url = config.get_base_url()

            if not api_key and "localhost" not in base_url:
                raise ConfigError(
                    f"{self._provider_name} API key not configured",
                    "No API key configured. Open Settings and add your API key.",
                )

            self._client = OpenAI(
                api_key=api_key or "not-needed",  # Some local APIs don't need key
                base_url=base_url,
            )
        return self._client

    def transcribe(
        self,
        audio_data: bytes,
        config: ASRConfig,
        dictionary: list[str] | None = None,
    ) -> TranscriptionResult:
        """Transcribe audio using OpenAI-compatible API."""
        client = self._get_client(config)

        # Create a file-like object from bytes
        audio_file = io.BytesIO(audio_data)
        audio_file.name = "audio.wav"

        # Build transcription request
        kwargs = {
            "model": config.model,
            "file": audio_file,
        }

        # Add language if specified (not auto)
        if config.language and config.language != "auto":
            kwargs["language"] = config.language

        # Add dictionary terms as prompt for better spelling
        # Note: Some providers don't support prompt parameter well
        if dictionary:
            if self._provider_name == "together":
                logger.warning(
                    f"Dictionary with {len(dictionary)} terms provided, but "
                    f"{self._provider_name} ASR does not reliably support prompt parameter"
                )
            else:
                kwargs["prompt"] = ", ".join(dictionary)
                logger.debug(f"Using dictionary prompt with {len(dictionary)} terms")

        logger.info(
            f"Sending transcription request to {self._provider_name}: "
            f"model={config.model}, base_url={config.get_base_url()}"
        )

        try:
            response = client.audio.transcriptions.create(**kwargs)
            logger.info(f"Transcription complete: {len(response.text)} chars")

            return TranscriptionResult(
                text=response.text,
                language=config.language if config.language != "auto" else None,
            )
        except Exception as e:
            logger.error(f"{self._provider_name} transcription failed: {e}")
            # Categorize the error and re-raise as appropriate type
            raise categorize_openai_error(e) from e

    def list_models(self) -> list[str]:
        """Return available models for this provider."""
        return COMPAT_MODELS.copy()
