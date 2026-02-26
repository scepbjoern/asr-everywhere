"""Text insertion via clipboard and keyboard simulation."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

import pyperclip
from pynput.keyboard import Controller, Key

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class TextInserter:
    """Inserts text at cursor position via clipboard + Ctrl+V."""

    def __init__(self) -> None:
        """Initialize text inserter."""
        self._keyboard = Controller()
        self._saved_clipboard: str | None = None

    def save_clipboard(self) -> None:
        """Save current clipboard content."""
        try:
            self._saved_clipboard = pyperclip.paste()
            logger.debug("Saved clipboard content")
        except Exception as e:
            logger.warning(f"Failed to save clipboard: {e}")
            self._saved_clipboard = None

    def restore_clipboard(self) -> None:
        """Restore previously saved clipboard content."""
        if self._saved_clipboard is not None:
            try:
                pyperclip.copy(self._saved_clipboard)
                logger.debug("Restored clipboard content")
            except Exception as e:
                logger.warning(f"Failed to restore clipboard: {e}")
        self._saved_clipboard = None

    def insert_text(self, text: str, restore_clipboard: bool = True) -> bool:
        """Insert text at cursor position.

        Args:
            text: Text to insert
            restore_clipboard: Whether to restore clipboard after insertion

        Returns:
            True if insertion succeeded
        """
        if not text:
            logger.warning("No text to insert")
            return False

        # Save clipboard before overwriting
        self.save_clipboard()

        try:
            # Copy text to clipboard
            pyperclip.copy(text)
            logger.debug(f"Copied {len(text)} chars to clipboard")

            # Small delay to ensure clipboard is updated
            time.sleep(0.05)

            # Simulate Ctrl+V
            with self._keyboard.pressed(Key.ctrl):
                self._keyboard.press("v")
                self._keyboard.release("v")

            logger.info(f"Inserted text via Ctrl+V: {len(text)} chars")

            # Restore clipboard if requested
            if restore_clipboard:
                # Small delay before restoring
                time.sleep(0.1)
                self.restore_clipboard()

            return True

        except Exception as e:
            logger.error(f"Failed to insert text: {e}")
            # Try to restore clipboard on error
            self.restore_clipboard()
            return False
