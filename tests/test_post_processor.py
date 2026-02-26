"""Tests for LLM post-processor."""

from __future__ import annotations

from unittest import mock

import pytest

from asr_everywhere.config import Config, LLMConfig, ProviderConfig
from asr_everywhere.llm.post_processor import PostProcessor


@pytest.fixture
def config_with_llm_disabled() -> Config:
    """Create config with LLM disabled."""
    config = Config()
    config.llm.enabled = False
    return config


@pytest.fixture
def config_with_llm_enabled() -> Config:
    """Create config with LLM enabled."""
    config = Config()
    config.llm = LLMConfig(
        enabled=True,
        provider="openai",
        model="gpt-4o-mini",
        custom_instructions="Use formal German",
        providers={
            "openai": ProviderConfig(
                api_key="test-key",
                base_url="https://api.openai.com/v1",
            ),
        },
    )
    config.dictionary = ["Kubernetes", "FastAPI"]
    return config


class TestPostProcessor:
    """Tests for PostProcessor class."""

    def test_process_disabled_returns_original(self, config_with_llm_disabled: Config) -> None:
        """Test that disabled LLM returns original text."""
        processor = PostProcessor(config_with_llm_disabled)
        result = processor.process("Test text")
        assert result == "Test text"

    def test_process_empty_text_returns_empty(self, config_with_llm_enabled: Config) -> None:
        """Test that empty text returns empty."""
        processor = PostProcessor(config_with_llm_enabled)
        result = processor.process("")
        assert result == ""

    def test_process_whitespace_only_returns_whitespace(
        self, config_with_llm_enabled: Config
    ) -> None:
        """Test that whitespace-only text returns as-is."""
        processor = PostProcessor(config_with_llm_enabled)
        result = processor.process("   ")
        assert result == "   "

    def test_process_enabled_calls_provider(self, config_with_llm_enabled: Config) -> None:
        """Test that enabled LLM calls the provider."""
        processor = PostProcessor(config_with_llm_enabled)

        with mock.patch("asr_everywhere.llm.post_processor.get_llm_provider") as mock_get_provider:
            mock_provider = mock.MagicMock()
            mock_get_provider.return_value = mock_provider
            mock_provider.post_process.return_value = mock.MagicMock(
                text="Processed text",
                original_text="Original text",
            )

            result = processor.process("Original text")

            assert result == "Processed text"
            mock_get_provider.assert_called_once_with("openai")
            mock_provider.post_process.assert_called_once_with(
                "Original text",
                config_with_llm_enabled.llm,
                config_with_llm_enabled.dictionary,
            )

    def test_process_provider_error_raises(self, config_with_llm_enabled: Config) -> None:
        """Test that provider errors are raised for caller to handle."""
        processor = PostProcessor(config_with_llm_enabled)

        with mock.patch("asr_everywhere.llm.post_processor.get_llm_provider") as mock_get_provider:
            mock_provider = mock.MagicMock()
            mock_get_provider.return_value = mock_provider
            mock_provider.post_process.side_effect = Exception("API Error")

            with pytest.raises(Exception, match="API Error"):
                processor.process("Test text")
