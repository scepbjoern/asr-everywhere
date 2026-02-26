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
        self._ptt_hooks: dict[str, tuple[Callable[[], None], Callable[[], None]]] = {}

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

    def register_push_to_talk(
        self,
        hotkey: str,
        on_press: Callable[[], None],
        on_release: Callable[[], None],
    ) -> None:
        """Register a push-to-talk hotkey.

        Args:
            hotkey: Hotkey string (e.g., "win+u")
            on_press: Function to call when hotkey is pressed down
            on_release: Function to call when hotkey is released
        """
        if hotkey in self._ptt_hooks:
            logger.warning(f"Push-to-talk '{hotkey}' already registered, replacing")
            self.unregister_push_to_talk(hotkey)

        # Store callbacks
        self._ptt_hooks[hotkey] = (on_press, on_release)

        # Register press callback (triggered when key goes down)
        keyboard.add_hotkey(hotkey, on_press, trigger_on_release=False)

        # Register release callback using keyboard.hook for key release detection
        def on_key_release(event):
            if event.event_type == keyboard.KEY_UP:
                # Check if the hotkey combo is now released
                if not keyboard.is_pressed(hotkey):
                    on_release()

        hook = keyboard.hook(on_key_release, suppress=False)
        self._ptt_hooks[hotkey] = (on_press, on_release, hook)
        logger.info(f"Registered push-to-talk: {hotkey}")

    def unregister_push_to_talk(self, hotkey: str) -> None:
        """Unregister a push-to-talk hotkey.

        Args:
            hotkey: Hotkey string to unregister
        """
        if hotkey in self._ptt_hooks:
            try:
                keyboard.remove_hotkey(hotkey)
                # Unhook the release listener
                if len(self._ptt_hooks[hotkey]) > 2:
                    keyboard.unhook(self._ptt_hooks[hotkey][2])
                logger.info(f"Unregistered push-to-talk: {hotkey}")
            except (ValueError, KeyError):
                logger.debug(f"Push-to-talk '{hotkey}' was already removed")
            del self._ptt_hooks[hotkey]

    def unregister_hotkey(self, hotkey: str) -> None:
        """Unregister a hotkey.

        Args:
            hotkey: Hotkey string to unregister
        """
        if hotkey in self._registered:
            try:
                keyboard.remove_hotkey(hotkey)
                logger.info(f"Unregistered hotkey: {hotkey}")
            except (ValueError, KeyError):
                # Hotkey may have been removed by unhook_all or similar
                logger.debug(f"Hotkey '{hotkey}' was already removed from keyboard library")
            del self._registered[hotkey]

    def unregister_all(self) -> None:
        """Unregister all hotkeys."""
        for hotkey in list(self._registered.keys()):
            self.unregister_hotkey(hotkey)
        for hotkey in list(self._ptt_hooks.keys()):
            self.unregister_push_to_talk(hotkey)
        logger.info("Unregistered all hotkeys")

    def is_pressed(self, hotkey: str) -> bool:
        """Check if a hotkey is currently pressed.

        Args:
            hotkey: Hotkey string to check

        Returns:
            True if the hotkey combination is pressed
        """
        return keyboard.is_pressed(hotkey)
