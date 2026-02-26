"""Tests for LLM prompts module."""

from asr_everywhere.llm.prompts import DEFAULT_SYSTEM_PROMPT, build_system_prompt


class TestBuildSystemPrompt:
    """Tests for build_system_prompt function."""

    def test_default_prompt_only(self) -> None:
        """Test building prompt with no custom instructions or dictionary."""
        prompt = build_system_prompt("", [])
        assert prompt == DEFAULT_SYSTEM_PROMPT

    def test_prompt_with_custom_instructions(self) -> None:
        """Test building prompt with custom instructions."""
        prompt = build_system_prompt("Always use formal German 'Sie' form.", [])
        assert DEFAULT_SYSTEM_PROMPT in prompt
        assert "Additional instructions:" in prompt
        assert "Always use formal German 'Sie' form." in prompt

    def test_prompt_with_dictionary(self) -> None:
        """Test building prompt with dictionary terms."""
        prompt = build_system_prompt("", ["Kubernetes", "FastAPI", "Szczerba"])
        assert DEFAULT_SYSTEM_PROMPT in prompt
        assert "Dictionary (use these exact spellings):" in prompt
        assert "Kubernetes, FastAPI, Szczerba" in prompt

    def test_prompt_with_both(self) -> None:
        """Test building prompt with both custom instructions and dictionary."""
        prompt = build_system_prompt(
            "Use formal language.",
            ["Kubernetes", "FastAPI"],
        )
        assert DEFAULT_SYSTEM_PROMPT in prompt
        assert "Additional instructions:" in prompt
        assert "Use formal language." in prompt
        assert "Dictionary (use these exact spellings):" in prompt
        assert "Kubernetes, FastAPI" in prompt

    def test_default_prompt_content(self) -> None:
        """Test that default prompt contains expected rules."""
        assert "transcription post-processor" in DEFAULT_SYSTEM_PROMPT.lower()
        assert "punctuation" in DEFAULT_SYSTEM_PROMPT.lower()
        assert "filler words" in DEFAULT_SYSTEM_PROMPT.lower()
        assert "German or English" in DEFAULT_SYSTEM_PROMPT
