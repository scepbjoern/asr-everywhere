"""Huggingface Inference API provider for ASR."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import httpx

from asr_everywhere.providers.base import ASRProvider, TranscriptionResult

if TYPE_CHECKING:
    from asr_everywhere.config import ASRConfig

logger = logging.getLogger(__name__)

# Available Whisper models on Huggingface
HF_MODELS = [
    "openai/whisper-large-v3-turbo",
    "openai/whisper-large-v3",
]


class HuggingfaceProvider(ASRProvider):
    """Huggingface Inference API provider for ASR.

    Uses the direct HTTP API at router.huggingface.co/hf-inference/models/<model>
    since Huggingface's ASR endpoint is not OpenAI-compatible.
    """

    def __init__(self) -> None:
        """Initialize Huggingface provider."""
        self._client: httpx.Client | None = None

    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.Client(timeout=120.0)
        return self._client

    def transcribe(
        self,
        audio_data: bytes,
        config: ASRConfig,
        dictionary: list[str] | None = None,
    ) -> TranscriptionResult:
        """Transcribe audio using Huggingface Inference API."""
        api_key = config.get_api_key()
        if not api_key:
            raise ValueError("Huggingface API key not configured")

        # Note: Huggingface Inference API does not support prompt parameter for ASR
        if dictionary:
            logger.warning(
                f"Dictionary with {len(dictionary)} terms provided, but Huggingface ASR does not support prompt parameter"
            )

        # Extract model name (remove hf-inference/ prefix if present)
        model = config.model
        if model.startswith("hf-inference/"):
            model = model[len("hf-inference/") :]

        # Build URL: https://router.huggingface.co/hf-inference/models/<model>
        base_url = config.get_base_url()
        # Use direct model URL format
        if "router.huggingface.co/v1" in base_url:
            # Convert OpenAI-compatible URL to direct URL
            url = f"https://router.huggingface.co/hf-inference/models/{model}"
        else:
            url = f"{base_url.rstrip('/')}/models/{model}"

        logger.info(f"Sending transcription request to Huggingface: model={model}, url={url}")

        client = self._get_client()

        try:
            response = client.post(
                url,
                content=audio_data,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "audio/wav",
                },
            )
            response.raise_for_status()

            result = response.json()

            # Handle different response formats
            if isinstance(result, dict):
                text = result.get("text", "")
            elif isinstance(result, str):
                text = result
            else:
                text = str(result)

            logger.info(f"Transcription complete: {len(text)} chars")

            return TranscriptionResult(
                text=text,
                language=config.language if config.language != "auto" else None,
            )
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Huggingface transcription failed: {e.response.status_code} - {e.response.text}"
            )
            raise
        except Exception as e:
            logger.error(f"Huggingface transcription failed: {e}")
            raise

    def list_models(self) -> list[str]:
        """Return available models for this provider."""
        return HF_MODELS.copy()

    def __del__(self) -> None:
        """Clean up HTTP client."""
        if self._client is not None:
            self._client.close()
