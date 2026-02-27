"""Tests for LLM providers."""

from __future__ import annotations

from unittest import mock

import pytest

from asr_everywhere.config import LLMConfig, ProviderConfig
from asr_everywhere.llm.base import PostProcessResult
from asr_everywhere.llm.openai_compat_llm import OpenAICompatLLMProvider
from asr_everywhere.llm.openai_llm import OpenAILLMProvider
from asr_everywhere.llm.registry import get_llm_provider, list_llm_providers


@pytest.fixture
def llm_config() -> LLMConfig:
    """Create test LLM config."""
    return LLMConfig(
        enabled=True,
        provider="openai",
        model="gpt-4o-mini",
        custom_instructions="Test instructions",
        providers={
            "openai": ProviderConfig(
                api_key="test-api-key",
                base_url="https://api.openai.com/v1",
            ),
        },
    )


@pytest.fixture
def llm_config_local() -> LLMConfig:
    """Create test LLM config for local provider."""
    return LLMConfig(
        enabled=True,
        provider="local",
        model="llama3",
        custom_instructions="",
        providers={
            "local": ProviderConfig(
                api_key="",
                base_url="http://localhost:11434/v1",
            ),
        },
    )


class TestPostProcessResult:
    """Tests for PostProcessResult dataclass."""

    def test_result_creation(self) -> None:
        """Test creating a PostProcessResult."""
        result = PostProcessResult(
            text="Processed text",
            original_text="Original text",
        )
        assert result.text == "Processed text"
        assert result.original_text == "Original text"


class TestOpenAILLMProvider:
    """Tests for OpenAI LLM provider."""

    def test_list_models(self) -> None:
        """Test listing available models."""
        provider = OpenAILLMProvider()
        models = provider.list_models()
        assert "gpt-4o-mini" in models
        assert "gpt-4o" in models

    def test_post_process_success(self, llm_config: LLMConfig) -> None:
        """Test successful post-processing."""
        provider = OpenAILLMProvider()

        with mock.patch("asr_everywhere.llm.openai_llm.OpenAI") as mock_openai:
            mock_client = mock.MagicMock()
            mock_openai.return_value = mock_client

            # Mock response
            mock_response = mock.MagicMock()
            mock_response.choices = [mock.MagicMock()]
            mock_response.choices[0].message.content = "Cleaned up text."
            mock_client.chat.completions.create.return_value = mock_response

            result = provider.post_process(
                "um, some text ähm",
                llm_config,
                ["Kubernetes", "FastAPI"],
            )

            assert result.text == "Cleaned up text."
            assert result.original_text == "um, some text ähm"

            # Verify API call
            mock_client.chat.completions.create.assert_called_once()
            call_kwargs = mock_client.chat.completions.create.call_args[1]
            assert call_kwargs["model"] == "gpt-4o-mini"
            assert len(call_kwargs["messages"]) == 2
            assert call_kwargs["messages"][0]["role"] == "system"
            assert call_kwargs["messages"][1]["role"] == "user"

    def test_post_process_no_api_key(self, llm_config: LLMConfig) -> None:
        """Test post-processing fails without API key."""
        llm_config.providers["openai"].api_key = ""
        provider = OpenAILLMProvider()

        with pytest.raises(ValueError, match="No API key"):
            provider.post_process("test text", llm_config, [])

    def test_post_process_api_error(self, llm_config: LLMConfig) -> None:
        """Test post-processing handles API errors."""
        provider = OpenAILLMProvider()

        with mock.patch("asr_everywhere.llm.openai_llm.OpenAI") as mock_openai:
            mock_client = mock.MagicMock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.side_effect = Exception("API Error")

            with pytest.raises(Exception, match="API Error"):
                provider.post_process("test text", llm_config, [])


class TestOpenAICompatLLMProvider:
    """Tests for OpenAI-compatible LLM provider."""

    def test_post_process_success(self, llm_config_local: LLMConfig) -> None:
        """Test successful post-processing with local provider."""
        provider = OpenAICompatLLMProvider()

        with mock.patch("asr_everywhere.llm.openai_compat_llm.OpenAI") as mock_openai:
            mock_client = mock.MagicMock()
            mock_openai.return_value = mock_client

            # Mock response
            mock_response = mock.MagicMock()
            mock_response.choices = [mock.MagicMock()]
            mock_response.choices[0].message.content = "Processed text"
            mock_client.chat.completions.create.return_value = mock_response

            result = provider.post_process(
                "test text",
                llm_config_local,
                [],
            )

            assert result.text == "Processed text"
            assert result.original_text == "test text"

    def test_list_models_empty(self) -> None:
        """Test listing models returns empty list for compat provider."""
        provider = OpenAICompatLLMProvider()
        assert provider.list_models() == []


class TestLLMRegistry:
    """Tests for LLM provider registry."""

    def test_list_llm_providers(self) -> None:
        """Test listing LLM providers."""
        providers = list_llm_providers()
        assert "openai" in providers
        assert "together" in providers
        assert "local" in providers

    def test_get_llm_provider_openai(self) -> None:
        """Test getting OpenAI provider."""
        provider = get_llm_provider("openai")
        assert isinstance(provider, OpenAILLMProvider)

    def test_get_llm_provider_local(self) -> None:
        """Test getting local provider."""
        provider = get_llm_provider("local")
        assert isinstance(provider, OpenAICompatLLMProvider)

    def test_get_llm_provider_invalid(self) -> None:
        """Test getting invalid provider raises error."""
        with pytest.raises(ValueError, match="Unknown LLM provider"):
            get_llm_provider("invalid_provider")
