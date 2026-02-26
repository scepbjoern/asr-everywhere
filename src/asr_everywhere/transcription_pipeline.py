"""Transcription pipeline: record → transcribe → insert."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from asr_everywhere.audio_recorder import AudioRecorder
from asr_everywhere.providers.registry import get_provider
from asr_everywhere.text_inserter import TextInserter

if TYPE_CHECKING:
    from asr_everywhere.config import Config
    from asr_everywhere.ui.tray import TrayIcon

logger = logging.getLogger(__name__)


class TranscriptionPipeline:
    """Orchestrates the transcription workflow."""

    def __init__(
        self,
        config: Config,
        recorder: AudioRecorder,
        inserter: TextInserter,
        tray: TrayIcon,
    ) -> None:
        """Initialize pipeline.

        Args:
            config: Application configuration
            recorder: Audio recorder instance
            inserter: Text inserter instance
            tray: Tray icon for status updates
        """
        self._config = config
        self._recorder = recorder
        self._inserter = inserter
        self._tray = tray
        self._processing = False

    def toggle_recording(self) -> None:
        """Toggle recording state (called by hotkey)."""
        if self._processing:
            logger.info("Ignoring toggle during processing")
            return

        if self._recorder.is_recording:
            self.stop_and_transcribe()
        else:
            self.start_recording()

    def start_recording(self) -> None:
        """Start audio recording."""
        from asr_everywhere.ui.tray import TrayState

        if self._processing:
            logger.info("Ignoring start during processing")
            return

        if not self._recorder.is_recording:
            self._tray.set_state(TrayState.RECORDING)
            self._recorder.start_recording()

    def stop_and_transcribe(self) -> None:
        """Stop recording and process audio."""
        from asr_everywhere.ui.tray import TrayState

        if not self._recorder.is_recording:
            return

        # Stop recording
        audio_data = self._recorder.stop_recording()

        if not audio_data:
            logger.warning("No audio recorded")
            self._tray.set_state(TrayState.IDLE)
            return

        # Update state
        self._tray.set_state(TrayState.PROCESSING)
        self._processing = True

        try:
            # Get ASR provider
            provider = get_provider(self._config.asr.provider)

            # Transcribe
            logger.info("Starting transcription")
            result = provider.transcribe(audio_data, self._config.asr)

            if result.text:
                logger.info(f"Transcription: {result.text[:100]}...")

                # Insert text
                success = self._inserter.insert_text(
                    result.text,
                    restore_clipboard=self._config.clipboard_restore,
                )

                if success:
                    if self._config.show_notification:
                        self._tray.show_notification(
                            "Transcription Complete",
                            f"Inserted: {result.text[:50]}..."
                            if len(result.text) > 50
                            else result.text,
                        )
                else:
                    self._tray.show_notification(
                        "Insertion Failed",
                        "Text copied to clipboard",
                    )
            else:
                self._tray.show_notification(
                    "Transcription Failed",
                    "No text returned from ASR",
                )

        except Exception as e:
            logger.error(f"Transcription pipeline error: {e}")
            self._tray.show_notification("Error", str(e))

        finally:
            self._processing = False
            self._tray.set_state(TrayState.IDLE)
