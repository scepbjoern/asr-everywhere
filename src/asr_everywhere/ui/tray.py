"""System Tray icon using pystray."""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from enum import Enum

import pystray
from PIL import Image, ImageDraw
from pystray import Menu, MenuItem

logger = logging.getLogger(__name__)


class TrayState(Enum):
    """Tray icon states."""

    IDLE = "idle"
    RECORDING = "recording"
    PROCESSING = "processing"


class TrayIcon:
    """System Tray icon with state indicators."""

    def __init__(
        self,
        on_quit: Callable[[], None],
        on_toggle_recording: Callable[[], None] | None = None,
        on_settings: Callable[[], None] | None = None,
        get_model_info: Callable[[], tuple[str, str]] | None = None,
        get_hotkey_mode: Callable[[], str] | None = None,
        on_toggle_hotkey_mode: Callable[[], None] | None = None,
    ) -> None:
        """Initialize tray icon.

        Args:
            on_quit: Callback for quit action
            on_toggle_recording: Callback to start/stop recording (optional)
            on_settings: Callback for settings action (optional for Phase 1)
            get_model_info: Callback returning (model_name, price) tuple (optional)
            get_hotkey_mode: Callback returning current hotkey mode (optional)
            on_toggle_hotkey_mode: Callback to toggle hotkey mode (optional)
        """
        self._on_quit = on_quit
        self._on_toggle_recording = on_toggle_recording
        self._on_settings = on_settings
        self._get_model_info = get_model_info
        self._get_hotkey_mode = get_hotkey_mode
        self._on_toggle_hotkey_mode = on_toggle_hotkey_mode
        self._state = TrayState.IDLE
        self._icon: pystray.Icon | None = None
        self._thread: threading.Thread | None = None

        # Create icons for each state
        self._icons = {
            TrayState.IDLE: self._create_icon("#4CAF50"),  # Green
            TrayState.RECORDING: self._create_icon("#F44336"),  # Red
            TrayState.PROCESSING: self._create_icon("#FF9800"),  # Orange
        }

    def _create_icon(self, color: str) -> Image.Image:
        """Create a simple colored circle icon.

        Args:
            color: Hex color string

        Returns:
            PIL Image
        """
        size = 64
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Draw filled circle
        margin = 8
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=color,
        )

        return image

    def _create_menu(self) -> Menu:
        """Create tray context menu."""
        items = [
            MenuItem(
                lambda item: f"Status: {self._state.value}",
                lambda item: None,
                enabled=False,
            ),
        ]

        # Add model info if available
        if self._get_model_info:
            items.append(
                MenuItem(
                    lambda item: self._get_model_text(),
                    lambda item: None,
                    enabled=False,
                )
            )

        items.append(Menu.SEPARATOR)

        if self._on_toggle_recording:
            items.append(
                MenuItem(
                    lambda item: (
                        "Stop Recording"
                        if self._state == TrayState.RECORDING
                        else "Start Recording"
                    ),
                    lambda item: self._on_toggle_recording(),
                )
            )

        if self._on_settings:
            items.append(MenuItem("Settings", lambda item: self._on_settings()))

        # Add hotkey mode toggle if available
        if self._get_hotkey_mode and self._on_toggle_hotkey_mode:
            items.append(
                MenuItem(
                    lambda item: f"Mode: {'Push-to-Talk' if self._get_hotkey_mode() == 'push_to_talk' else 'Toggle'}",
                    lambda item: self._on_toggle_hotkey_mode(),
                )
            )

        items.extend(
            [
                Menu.SEPARATOR,
                MenuItem("Quit", lambda item: self._on_quit()),
            ]
        )

        return Menu(*items)

    def _get_model_text(self) -> str:
        """Get formatted model info text for menu."""
        if not self._get_model_info:
            return ""
        model_name, model_price = self._get_model_info()
        if not model_name:
            return ""
        price_text = f" ({model_price})" if model_price else ""
        return f"Model: {model_name}{price_text}"

    def set_state(self, state: TrayState) -> None:
        """Update tray icon state.

        Args:
            state: New state to display
        """
        self._state = state
        if self._icon:
            self._icon.icon = self._icons[state]
            self._icon.title = f"ASR Everywhere - {state.value.title()}"
            # Update menu to show current status
            self._icon.update_menu()
        logger.debug(f"Tray state changed to: {state.value}")

    def refresh_menu(self) -> None:
        """Refresh the tray menu to show updated model info."""
        if self._icon:
            self._icon.update_menu()

    def show_notification(self, title: str, message: str) -> None:
        """Show a notification balloon.

        Args:
            title: Notification title
            message: Notification message
        """
        if self._icon:
            self._icon.notify(message, title)

    def _run_icon(self) -> None:
        """Run the tray icon (called in thread)."""
        self._icon = pystray.Icon(
            "asr_everywhere",
            icon=self._icons[TrayState.IDLE],
            title="ASR Everywhere",
            menu=self._create_menu(),
        )
        self._icon.run()

    def start(self) -> None:
        """Start the tray icon in a background thread."""
        if self._thread and self._thread.is_alive():
            logger.warning("Tray icon already running")
            return

        self._thread = threading.Thread(target=self._run_icon, daemon=True)
        self._thread.start()
        logger.info("Tray icon started")

    def stop(self) -> None:
        """Stop the tray icon."""
        if self._icon:
            self._icon.stop()
        # Don't join if we're being called from the tray thread itself
        if self._thread and self._thread is not threading.current_thread():
            self._thread.join(timeout=2.0)
        logger.info("Tray icon stopped")
