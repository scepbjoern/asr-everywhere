"""Error categories and user-friendly messages for ASR Everywhere."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class ASREverywhereError(Exception):
    """Base exception for ASR Everywhere."""

    def __init__(self, message: str, user_message: str | None = None) -> None:
        """Initialize error.

        Args:
            message: Technical error message for logging
            user_message: User-friendly message for display
        """
        super().__init__(message)
        self.user_message = user_message or message


class ConfigError(ASREverywhereError):
    """Configuration-related errors."""

    pass


class AudioError(ASREverywhereError):
    """Audio/microphone-related errors."""

    pass


class ProviderError(ASREverywhereError):
    """ASR/LLM provider errors."""

    pass


class NetworkError(ASREverywhereError):
    """Network connectivity errors."""

    pass


class ClipboardError(ASREverywhereError):
    """Clipboard operation errors."""

    pass


# Error message mappings for user-friendly display
ERROR_MESSAGES: dict[type[Exception], str] = {
    # Config errors
    ConfigError: "Configuration error. Check your settings.",
    # Audio errors
    AudioError: "Audio error. Check your microphone.",
    # Provider errors
    ProviderError: "Service error. Try again or switch providers.",
    # Network errors
    NetworkError: "Network error. Check your internet connection.",
    # Clipboard errors
    ClipboardError: "Clipboard error. Text may not have been inserted.",
}

# Specific error patterns and their user-friendly messages
SPECIFIC_ERROR_MESSAGES: dict[str, str] = {
    # API key errors
    "api key not configured": "No API key configured. Open Settings and add your API key.",
    "api key not found": "No API key configured. Open Settings and add your API key.",
    "invalid api key": "API key rejected. Please check your key in Settings.",
    "authentication": "API key rejected. Please check your key in Settings.",
    "unauthorized": "API key rejected. Please check your key in Settings.",
    # Microphone errors
    "no microphone": "No microphone found. Connect a microphone and restart.",
    "no audio input": "No microphone found. Connect a microphone and restart.",
    "microphone access denied": "Microphone access denied. Check Windows privacy settings.",
    "portaudio": "Microphone error. Check your audio device settings.",
    # Network errors
    "timeout": "Network timeout. Check your internet connection.",
    "connection": "Network error. Check your internet connection.",
    "network": "Network error. Check your internet connection.",
    # Rate limit
    "rate limit": "Rate limit exceeded. Please wait a moment and try again.",
    # Service errors
    "service unavailable": "Service temporarily unavailable. Try again later.",
    "internal error": "Service error. Try again or switch providers.",
    # LLM errors
    "llm": "LLM post-processing failed. Using raw transcription.",
}


def get_user_message(error: Exception) -> str:
    """Get user-friendly message for an exception.

    Args:
        error: The exception that occurred

    Returns:
        User-friendly error message
    """
    error_str = str(error).lower()

    # Check for specific error patterns first
    for pattern, message in SPECIFIC_ERROR_MESSAGES.items():
        if pattern in error_str:
            return message

    # Check if it's one of our custom errors with a user_message
    if isinstance(error, ASREverywhereError) and error.user_message:
        return error.user_message

    # Check error type for default message
    for error_type, message in ERROR_MESSAGES.items():
        if isinstance(error, error_type):
            return message

    # Fallback to the error string, truncated
    return str(error)[:200]


def categorize_openai_error(error: Exception) -> ASREverywhereError:
    """Categorize an OpenAI API error into appropriate error type.

    Args:
        error: Exception from OpenAI SDK

    Returns:
        Appropriate ASREverywhereError subclass
    """
    error_str = str(error).lower()
    error_type_name = type(error).__name__.lower()

    # Check for authentication errors
    if "auth" in error_type_name or "unauthorized" in error_str or "invalid" in error_str:
        return ProviderError(
            str(error),
            "API key rejected. Please check your key in Settings.",
        )

    # Check for connection/network errors
    if "connection" in error_type_name or "timeout" in error_str or "network" in error_str:
        return NetworkError(
            str(error),
            "Network error. Check your internet connection.",
        )

    # Check for rate limit
    if "rate" in error_str or "limit" in error_type_name:
        return ProviderError(
            str(error),
            "Rate limit exceeded. Please wait a moment and try again.",
        )

    # Check for service errors
    if "status" in error_type_name or "internal" in error_str or "unavailable" in error_str:
        return ProviderError(
            str(error),
            "Service error. Try again or switch providers.",
        )

    # Default to generic provider error
    return ProviderError(str(error), get_user_message(error))
