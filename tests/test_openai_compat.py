"""Tests for OpenAI-compatible provider."""

from unittest import mock

import pytest

from asr_everywhere.config import ASRConfig, ProviderConfig
from asr_everywhere.providers.openai_compat import OpenAICompatProvider


@pytest.fixture
def compat_config():
    """Create test config for compatible provider."""
    return ASRConfig(
        provider="together",
        model="whisper-1",
        providers={
            "together": ProviderConfig(
                api_key="test-key",
                base_url="https://api.together.xyz/v1",
            )
        },
    )


def test_compat_provider_transcribe(compat_config):
    """Test transcription with compatible provider."""
    provider = OpenAICompatProvider("together")

    with mock.patch("asr_everywhere.providers.openai_compat.OpenAI") as mock_openai:
        mock_client = mock.MagicMock()
        mock_openai.return_value = mock_client

        mock_response = mock.MagicMock()
        mock_response.text = "Hello from Together"
        mock_client.audio.transcriptions.create.return_value = mock_response

        result = provider.transcribe(b"fake audio", compat_config)

        assert result.text == "Hello from Together"
        mock_client.audio.transcriptions.create.assert_called_once()


def test_compat_provider_uses_base_url(compat_config):
    """Test that provider uses configured base_url."""
    provider = OpenAICompatProvider("together")

    with mock.patch("asr_everywhere.providers.openai_compat.OpenAI") as mock_openai:
        mock_client = mock.MagicMock()
        mock_openai.return_value = mock_client

        mock_response = mock.MagicMock()
        mock_response.text = "test"
        mock_client.audio.transcriptions.create.return_value = mock_response

        provider.transcribe(b"audio", compat_config)

        # Verify OpenAI was called with correct base_url
        mock_openai.assert_called_once()
        call_kwargs = mock_openai.call_args.kwargs
        assert call_kwargs["base_url"] == "https://api.together.xyz/v1"


def test_compat_provider_local_no_key():
    """Test local provider works without API key."""
    config = ASRConfig(
        provider="local",
        model="whisper-1",
        providers={
            "local": ProviderConfig(
                api_key="",
                base_url="http://localhost:11434/v1",
            )
        },
    )

    provider = OpenAICompatProvider("local")

    with mock.patch("asr_everywhere.providers.openai_compat.OpenAI") as mock_openai:
        mock_client = mock.MagicMock()
        mock_openai.return_value = mock_client

        mock_response = mock.MagicMock()
        mock_response.text = "Local transcription"
        mock_client.audio.transcriptions.create.return_value = mock_response

        result = provider.transcribe(b"audio", config)

        assert result.text == "Local transcription"


def test_compat_provider_missing_key_raises():
    """Test that missing API key raises error for non-local providers."""
    config = ASRConfig(
        provider="together",
        model="whisper-1",
        providers={
            "together": ProviderConfig(
                api_key="",
                base_url="https://api.together.xyz/v1",
            )
        },
    )

    provider = OpenAICompatProvider("together")

    with pytest.raises(ValueError, match="together API key not configured"):
        provider.transcribe(b"audio", config)


def test_compat_provider_list_models():
    """Test list_models returns expected models."""
    provider = OpenAICompatProvider("test")
    models = provider.list_models()

    assert "whisper-1" in models
    assert isinstance(models, list)


def test_compat_provider_with_language():
    """Test transcription with language parameter."""
    config = ASRConfig(
        provider="together",
        model="whisper-1",
        language="de",
        providers={
            "together": ProviderConfig(
                api_key="test-key",
                base_url="https://api.together.xyz/v1",
            )
        },
    )

    provider = OpenAICompatProvider("together")

    with mock.patch("asr_everywhere.providers.openai_compat.OpenAI") as mock_openai:
        mock_client = mock.MagicMock()
        mock_openai.return_value = mock_client

        mock_response = mock.MagicMock()
        mock_response.text = "German text"
        mock_client.audio.transcriptions.create.return_value = mock_response

        result = provider.transcribe(b"audio", config)

        # Verify language was passed
        call_kwargs = mock_client.audio.transcriptions.create.call_args.kwargs
        assert call_kwargs["language"] == "de"
        assert result.language == "de"
