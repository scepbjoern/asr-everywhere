"""Abstract base class for ASR providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from asr_everywhere.config import ASRConfig


@dataclass
class TranscriptionResult:
    """Result of a transcription."""

    text: str
    language: str | None = None
    duration: float | None = None


class ASRProvider(ABC):
    """Abstract base class for ASR providers."""

    @abstractmethod
    def transcribe(
        self,
        audio_data: bytes,
        config: ASRConfig,
        dictionary: list[str] | None = None,
    ) -> TranscriptionResult:
        """Transcribe audio bytes to text.

        Args:
            audio_data: Audio data as bytes (WAV format)
            config: ASR configuration
            dictionary: Optional list of custom terms for proper spelling

        Returns:
            TranscriptionResult with transcribed text
        """
        ...

    @abstractmethod
    def list_models(self) -> list[str]:
        """Return list of available models for this provider."""
        ...
