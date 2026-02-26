"""Main application orchestrator."""

from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING

import keyboard

from asr_everywhere.audio_recorder import AudioRecorder
from asr_everywhere.config import Config, load_config
from asr_everywhere.hotkey_manager import HotkeyManager
from asr_everywhere.text_inserter import TextInserter
from asr_everywhere.transcription_pipeline import TranscriptionPipeline
from asr_everywhere.ui.tray import TrayIcon

if TYPE_CHECKING:
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class ASREverywhereApp:
    """Main application class."""

    def __init__(self) -> None:
        """Initialize application."""
        self._config: Config | None = None
        self._tray: TrayIcon | None = None
        self._recorder: AudioRecorder | None = None
        self._inserter: TextInserter | None = None
        self._hotkey_manager: HotkeyManager | None = None
        self._pipeline: TranscriptionPipeline | None = None
        self._running = False

    def initialize(self) -> bool:
        """Initialize all components.

        Returns:
            True if initialization succeeded
        """
        try:
            # Load config
            self._config = load_config()

            # Create components (pipeline before tray so we can pass callback)
            self._recorder = AudioRecorder(self._config.audio)
            self._inserter = TextInserter()
            self._hotkey_manager = HotkeyManager()

            # Create pipeline first
            self._pipeline = TranscriptionPipeline(
                config=self._config,
                recorder=self._recorder,
                inserter=self._inserter,
                tray=None,  # Will be set after tray creation
            )

            # Create tray with toggle callback
            self._tray = TrayIcon(
                on_quit=self.quit,
                on_toggle_recording=self._pipeline.toggle_recording,
            )

            # Link tray to pipeline
            self._pipeline._tray = self._tray

            # Register hotkey
            self._hotkey_manager.register_hotkey(
                self._config.hotkey.dictate,
                self._pipeline.toggle_recording,
            )

            logger.info("Application initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            return False

    def run(self) -> None:
        """Run the application."""
        if not self.initialize():
            sys.exit(1)

        self._running = True

        # Start tray icon
        self._tray.start()

        logger.info(f"ASR Everywhere started - press {self._config.hotkey.dictate.upper()} to dictate")

        # Keep running until quit
        try:
            # Use keyboard.wait() to keep the app running
            # This is more reliable than a busy loop
            keyboard.wait()
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            self.quit()

    def quit(self) -> None:
        """Quit the application."""
        if not self._running:
            return

        logger.info("Shutting down...")

        # Stop recording if active
        if self._recorder and self._recorder.is_recording:
            self._recorder.stop_recording()

        # Unregister hotkeys
        if self._hotkey_manager:
            self._hotkey_manager.unregister_all()

        # Stop tray
        if self._tray:
            self._tray.stop()

        self._running = False
        logger.info("Application stopped")


def main() -> int:
    """Main entry point."""
    app = ASREverywhereApp()
    app.run()
    return 0
