"""OpenAI Whisper API provider."""

from __future__ import annotations

import io
import logging
from typing import TYPE_CHECKING

from openai import OpenAI

from asr_everywhere.providers.base import ASRProvider, TranscriptionResult

if TYPE_CHECKING:
    from asr_everywhere.config import ASRConfig

logger = logging.getLogger(__name__)

# Models supported by OpenAI for transcription
OPENAI_MODELS = ["whisper-1", "gpt-4o-transcribe", "gpt-4o-mini-transcribe"]


class OpenAIProvider(ASRProvider):
    """OpenAI Whisper API provider."""

    def __init__(self) -> None:
        """Initialize OpenAI provider."""
        self._client: OpenAI | None = None

    def _get_client(self, config: ASRConfig) -> OpenAI:
        """Get or create OpenAI client."""
        if self._client is None:
            if not config.api_key:
                raise ValueError("OpenAI API key not configured")
            self._client = OpenAI(
                api_key=config.api_key,
                base_url=config.base_url,
            )
        return self._client

    def transcribe(
        self,
        audio_data: bytes,
        config: ASRConfig,
        dictionary: list[str] | None = None,
    ) -> TranscriptionResult:
        """Transcribe audio using OpenAI Whisper API."""
        client = self._get_client(config)

        # Create a file-like object from bytes
        audio_file = io.BytesIO(audio_data)
        audio_file.name = "audio.wav"  # OpenAI needs filename for format detection

        # Build transcription request
        kwargs = {
            "model": config.model,
            "file": audio_file,
        }

        # Add language if specified (not auto)
        if config.language and config.language != "auto":
            kwargs["language"] = config.language

        # Add dictionary terms as prompt for better spelling
        if dictionary:
            kwargs["prompt"] = ", ".join(dictionary)
            logger.debug(f"Using dictionary prompt with {len(dictionary)} terms")

        logger.info(f"Sending transcription request to OpenAI: model={config.model}")

        try:
            response = client.audio.transcriptions.create(**kwargs)
            logger.info(f"Transcription complete: {len(response.text)} chars")

            return TranscriptionResult(
                text=response.text,
                language=config.language if config.language != "auto" else None,
            )
        except Exception as e:
            logger.error(f"OpenAI transcription failed: {e}")
            raise

    def list_models(self) -> list[str]:
        """Return available OpenAI transcription models."""
        return OPENAI_MODELS.copy()
