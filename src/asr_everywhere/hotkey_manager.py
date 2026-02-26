"""Global hotkey management using keyboard library."""

from __future__ import annotations

import logging
from collections.abc import Callable

import keyboard

logger = logging.getLogger(__name__)


class HotkeyManager:
    """Manages global hotkey registration."""

    def __init__(self) -> None:
        """Initialize hotkey manager."""
        self._registered: dict[str, Callable[[], None]] = {}

    def register_hotkey(
        self,
        hotkey: str,
        callback: Callable[[], None],
    ) -> None:
        """Register a global hotkey.

        Args:
            hotkey: Hotkey string (e.g., "win+u", "ctrl+alt+r")
            callback: Function to call when hotkey is pressed
        """
        if hotkey in self._registered:
            logger.warning(f"Hotkey '{hotkey}' already registered, replacing")
            self.unregister_hotkey(hotkey)

        keyboard.add_hotkey(hotkey, callback)
        self._registered[hotkey] = callback
        logger.info(f"Registered hotkey: {hotkey}")

    def unregister_hotkey(self, hotkey: str) -> None:
        """Unregister a hotkey.

        Args:
            hotkey: Hotkey string to unregister
        """
        if hotkey in self._registered:
            keyboard.remove_hotkey(hotkey)
            del self._registered[hotkey]
            logger.info(f"Unregistered hotkey: {hotkey}")

    def unregister_all(self) -> None:
        """Unregister all hotkeys."""
        for hotkey in list(self._registered.keys()):
            self.unregister_hotkey(hotkey)
        logger.info("Unregistered all hotkeys")

    def is_pressed(self, hotkey: str) -> bool:
        """Check if a hotkey is currently pressed.

        Args:
            hotkey: Hotkey string to check

        Returns:
            True if the hotkey combination is pressed
        """
        return keyboard.is_pressed(hotkey)
