"""Default system prompts and prompt builder for LLM post-processing."""

DEFAULT_SYSTEM_PROMPT = """You are a transcription post-processor. Clean up the following dictated text.

Rules:
- Fix punctuation and capitalization
- Remove filler words (ähm, um, like, so, also)
- Maintain the original meaning and tone
- Keep the same language (German or English)
- Return ONLY the cleaned text, no explanations"""

VOICE_COMMANDS_PROMPT = """

Voice Commands Processing:
This is dictated text. The speaker may have said punctuation and formatting commands out loud. You MUST detect and transform these spoken commands:

SPOKEN COMMAND → OUTPUT
"Neuer Absatz" or "New paragraph" → Insert two newlines (\\n\\n)
"Neue Zeile" or "New line" → Insert one newline (\\n)
"Punkt" or "Period" → Insert period (.)
"Komma" or "Comma" → Insert comma (,)
"Fragezeichen" or "Question mark" → Insert question mark (?)
"Ausrufezeichen" or "Exclamation mark" → Insert exclamation mark (!)
"Doppelpunkt" or "Colon" → Insert colon (:)
"Semikolon" or "Semicolon" → Insert semicolon (;)
"Anführungszeichen" or "Quote" → Insert opening double quote (")
"Ende Anführungszeichen" or "End quote" → Insert closing double quote (")
"Lösche das" or "Delete that" → Remove the last sentence
"Lösche letztes Wort" or "Delete last word" → Remove the last word
"Lösche letzten Satz" or "Delete last sentence" → Remove the last sentence

EXAMPLES:
Input: "Hallo Punkt Wie geht es dir"
Output: "Hallo. Wie geht es dir?"

Input: "Das ist ein Test Neuer Absatz Und hier geht es weiter"
Output: "Das ist ein Test.

Und hier geht es weiter."

Input: "Erster Satz Neuer Absatz Zweiter Satz"
Output: "Erster Satz.

Zweiter Satz."

IMPORTANT: Only transform these when clearly intended as commands. If ambiguous, keep the literal text."""


def build_system_prompt(
    custom_instructions: str,
    dictionary: list[str],
    voice_commands_enabled: bool = True,
) -> str:
    """Build complete system prompt for LLM post-processing.

    Args:
        custom_instructions: Additional user-provided instructions
        dictionary: List of custom terms that must be spelled correctly
        voice_commands_enabled: Whether to include voice command processing

    Returns:
        Complete system prompt string
    """
    prompt = DEFAULT_SYSTEM_PROMPT
    if custom_instructions:
        prompt += f"\n\nAdditional instructions:\n{custom_instructions}"
    if dictionary:
        prompt += f"\n\nDictionary (use these exact spellings):\n{', '.join(dictionary)}"
    if voice_commands_enabled:
        prompt += VOICE_COMMANDS_PROMPT
    return prompt
