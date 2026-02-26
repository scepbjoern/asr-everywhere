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
from asr_everywhere.ui.settings_window import open_settings_in_thread
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
        self._settings_open = False

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
                on_settings=self._open_settings,
                get_model_info=self._get_model_info,
                get_hotkey_mode=lambda: self._config.hotkey.mode,
                on_toggle_hotkey_mode=self._toggle_hotkey_mode,
                get_llm_info=self._get_llm_info,
            )

            # Link tray to pipeline
            self._pipeline._tray = self._tray

            # Register hotkey based on mode
            if self._config.hotkey.mode == "push_to_talk":
                self._hotkey_manager.register_push_to_talk(
                    self._config.hotkey.dictate,
                    self._pipeline.start_recording,
                    self._pipeline.stop_and_transcribe,
                )
            else:
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

        logger.info(
            f"ASR Everywhere started - press {self._config.hotkey.dictate.upper()} to dictate"
        )

        # Keep running until quit
        try:
            # Use keyboard.wait() to keep the app running
            # This is more reliable than a busy loop
            keyboard.wait()
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            self.quit()

    def _get_model_info(self) -> tuple[str, str]:
        """Get current model name and price."""
        if not self._config:
            return ("", "")

        model_name = self._config.asr.model
        model_price = ""

        # Find price from provider config
        provider = self._config.asr.provider
        if provider in self._config.asr.providers:
            provider_config = self._config.asr.providers[provider]
            for model in provider_config.models:
                if model.name == model_name:
                    model_price = model.price_per_1m_tokens
                    break

        return (model_name, model_price)

    def _get_llm_info(self) -> tuple[str, str]:
        """Get current LLM model name and price."""
        if not self._config or not self._config.llm.enabled:
            return ("", "")

        model_name = self._config.llm.model
        model_price = ""

        # Find price from provider config
        provider = self._config.llm.provider
        if provider in self._config.llm.providers:
            provider_config = self._config.llm.providers[provider]
            for model in provider_config.models:
                if model.name == model_name:
                    model_price = model.price_per_1m_tokens
                    break

        return (model_name, model_price)

    def _toggle_hotkey_mode(self) -> None:
        """Toggle between push-to-talk and toggle mode."""
        # Toggle mode
        new_mode = "toggle" if self._config.hotkey.mode == "push_to_talk" else "push_to_talk"
        self._config.hotkey.mode = new_mode

        # Save config
        save_config(self._config)

        # Re-register hotkey with new mode
        self._hotkey_manager.unregister_all()
        if new_mode == "push_to_talk":
            self._hotkey_manager.register_push_to_talk(
                self._config.hotkey.dictate,
                self._pipeline.start_recording,
                self._pipeline.stop_and_transcribe,
            )
        else:
            self._hotkey_manager.register_hotkey(
                self._config.hotkey.dictate,
                self._pipeline.toggle_recording,
            )

        # Refresh tray menu
        self._tray.refresh_menu()

        logger.info(f"Hotkey mode changed to: {new_mode}")

    def _open_settings(self) -> None:
        """Open settings window."""
        if self._settings_open:
            logger.debug("Settings window already open")
            return

        self._settings_open = True

        def on_save():
            # Reload config
            self._config = load_config()

            # Re-register hotkey if changed
            self._hotkey_manager.unregister_all()
            if self._config.hotkey.mode == "push_to_talk":
                self._hotkey_manager.register_push_to_talk(
                    self._config.hotkey.dictate,
                    self._pipeline.start_recording,
                    self._pipeline.stop_and_transcribe,
                )
            else:
                self._hotkey_manager.register_hotkey(
                    self._config.hotkey.dictate,
                    self._pipeline.toggle_recording,
                )

            # Refresh tray menu to show updated model info
            self._tray.refresh_menu()

            logger.info(
                f"Settings updated - hotkey: {self._config.hotkey.dictate}, mode: {self._config.hotkey.mode}"
            )
            self._settings_open = False

        def on_close():
            self._settings_open = False

        open_settings_in_thread(self._config, on_save, on_close)

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
