"""Default system prompts and prompt builder for LLM post-processing."""

DEFAULT_SYSTEM_PROMPT = """You are a transcription post-processor. Clean up the following dictated text.

Rules:
- Fix punctuation and capitalization
- Remove filler words (ähm, um, like, so, also)
- Maintain the original meaning and tone
- Keep the same language (German or English)
- Return ONLY the cleaned text, no explanations"""


def build_system_prompt(
    custom_instructions: str,
    dictionary: list[str],
) -> str:
    """Build complete system prompt for LLM post-processing.

    Args:
        custom_instructions: Additional user-provided instructions
        dictionary: List of custom terms that must be spelled correctly

    Returns:
        Complete system prompt string
    """
    prompt = DEFAULT_SYSTEM_PROMPT
    if custom_instructions:
        prompt += f"\n\nAdditional instructions:\n{custom_instructions}"
    if dictionary:
        prompt += f"\n\nDictionary (use these exact spellings):\n{', '.join(dictionary)}"
    return prompt
