"""Tests for text inserter."""

from unittest import mock

import pytest

from asr_everywhere.text_inserter import TextInserter


@pytest.fixture
def inserter():
    """Create inserter instance."""
    return TextInserter()


def test_insert_text_success(inserter):
    """Test successful text insertion."""
    with (
        mock.patch("asr_everywhere.text_inserter.pyperclip") as mock_clip,
        mock.patch("asr_everywhere.text_inserter.time.sleep"),
    ):
        mock_clip.paste.return_value = "old clipboard"

        result = inserter.insert_text("Hello world", restore_clipboard=True)

        assert result is True
        mock_clip.copy.assert_called()
        # Should have restored clipboard
        assert mock_clip.copy.call_count >= 2


def test_insert_text_no_restore(inserter):
    """Test text insertion without clipboard restore."""
    with (
        mock.patch("asr_everywhere.text_inserter.pyperclip") as mock_clip,
        mock.patch("asr_everywhere.text_inserter.time.sleep"),
    ):
        mock_clip.paste.return_value = "old clipboard"

        result = inserter.insert_text("Hello world", restore_clipboard=False)

        assert result is True
        # Should only copy once (the new text)
        assert mock_clip.copy.call_count == 1


def test_insert_empty_text_fails(inserter):
    """Test inserting empty text returns False."""
    result = inserter.insert_text("")
    assert result is False


def test_save_restore_clipboard(inserter):
    """Test clipboard save and restore."""
    with mock.patch("asr_everywhere.text_inserter.pyperclip") as mock_clip:
        mock_clip.paste.return_value = "saved content"

        inserter.save_clipboard()
        assert inserter._saved_clipboard == "saved content"

        inserter.restore_clipboard()
        mock_clip.copy.assert_called_with("saved content")
