"""Tests for ASR providers."""

from unittest import mock

import pytest

from asr_everywhere.config import ASRConfig
from asr_everywhere.providers.openai_provider import OpenAIProvider
from asr_everywhere.providers.registry import get_provider, list_providers


@pytest.fixture
def asr_config():
    """Create test ASR config."""
    return ASRConfig(
        provider="openai",
        model="whisper-1",
        api_key="test-key",
    )


def test_list_models():
    """Test listing available models."""
    provider = OpenAIProvider()
    models = provider.list_models()

    assert "whisper-1" in models
    assert "gpt-4o-transcribe" in models


def test_transcribe_success(asr_config):
    """Test successful transcription."""
    provider = OpenAIProvider()

    with mock.patch("asr_everywhere.providers.openai_provider.OpenAI") as mock_openai:
        mock_client = mock.MagicMock()
        mock_openai.return_value = mock_client

        mock_response = mock.MagicMock()
        mock_response.text = "Hello world"
        mock_client.audio.transcriptions.create.return_value = mock_response

        result = provider.transcribe(b"fake audio data", asr_config)

        assert result.text == "Hello world"
        mock_client.audio.transcriptions.create.assert_called_once()


def test_transcribe_missing_api_key():
    """Test transcription fails without API key."""
    from asr_everywhere.errors import ConfigError

    provider = OpenAIProvider()
    config = ASRConfig(api_key="")

    with pytest.raises(ConfigError, match="API key"):
        provider.transcribe(b"audio", config)


def test_get_provider():
    """Test provider registry."""
    provider = get_provider("openai")
    assert isinstance(provider, OpenAIProvider)


def test_get_provider_unknown():
    """Test getting unknown provider raises error."""
    with pytest.raises(ValueError, match="Unknown provider"):
        get_provider("unknown_provider")


def test_list_providers():
    """Test listing available providers."""
    providers = list_providers()
    assert "openai" in providers
