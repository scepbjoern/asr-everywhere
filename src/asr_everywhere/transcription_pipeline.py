"""Transcription pipeline: record → transcribe → insert."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from asr_everywhere.audio_recorder import AudioRecorder
from asr_everywhere.llm.post_processor import PostProcessor
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

            # Transcribe with dictionary terms
            logger.info("Starting transcription")
            result = provider.transcribe(audio_data, self._config.asr, self._config.dictionary)

            if result.text:
                text = result.text
                logger.info(f"Transcription: {text[:100]}...")

                # LLM post-processing (if enabled)
                if self._config.llm.enabled and text.strip():
                    try:
                        processor = PostProcessor(self._config)
                        text = processor.process(text)
                        logger.info("LLM post-processing complete")
                    except Exception as e:
                        logger.error(f"LLM post-processing failed: {e}")
                        # Graceful degradation: use raw transcription
                        self._tray.show_notification(
                            "LLM Error",
                            "Using raw transcription",
                        )

                # Insert text
                success = self._inserter.insert_text(
                    text,
                    restore_clipboard=self._config.clipboard_restore,
                )

                if success:
                    if self._config.show_notification:
                        self._tray.show_notification(
                            "Transcription Complete",
                            f"Inserted: {text[:50]}..." if len(text) > 50 else text,
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
            # Truncate error message to avoid pystray notification limit (256 chars)
            error_msg = str(e)[:200]
            self._tray.show_notification("Error", error_msg)

        finally:
            self._processing = False
            self._tray.set_state(TrayState.IDLE)
