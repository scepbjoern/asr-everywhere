"""Audio recording using sounddevice."""

from __future__ import annotations

import io
import logging
import queue
import threading
from typing import TYPE_CHECKING

import numpy as np
import sounddevice as sd
import soundfile as sf

from asr_everywhere.errors import AudioError

if TYPE_CHECKING:
    from asr_everywhere.config import AudioConfig

logger = logging.getLogger(__name__)


class AudioRecorder:
    """Records audio from microphone using sounddevice."""

    def __init__(self, config: AudioConfig) -> None:
        """Initialize audio recorder.

        Args:
            config: Audio configuration
        """
        self._config = config
        self._queue: queue.Queue[np.ndarray] = queue.Queue()
        self._stream: sd.InputStream | None = None
        self._recording = False
        self._lock = threading.Lock()

    def _callback(
        self,
        indata: np.ndarray,
        frames: int,
        time: dict,
        status: sd.CallbackFlags,
    ) -> None:
        """Callback for audio stream - called from separate thread."""
        if status:
            logger.warning(f"Audio callback status: {status}")
        if self._recording:
            self._queue.put(indata.copy())

    def start_recording(self) -> None:
        """Start recording audio.

        Raises:
            AudioError: If microphone is not available or access is denied
        """
        with self._lock:
            if self._recording:
                logger.warning("Already recording")
                return

            logger.info("Starting audio recording")
            self._recording = True

            # Clear any old data from queue
            while not self._queue.empty():
                try:
                    self._queue.get_nowait()
                except queue.Empty:
                    break

            # Create and start stream
            try:
                self._stream = sd.InputStream(
                    samplerate=self._config.sample_rate,
                    device=self._config.device,
                    channels=self._config.channels,
                    dtype="float32",
                    callback=self._callback,
                )
                self._stream.start()
                logger.info("Audio stream started")
            except sd.PortAudioError as e:
                self._recording = False
                error_msg = str(e).lower()
                if "no device" in error_msg or "device" in error_msg:
                    raise AudioError(
                        str(e),
                        "No microphone found. Connect a microphone and restart.",
                    ) from e
                if "access" in error_msg or "permission" in error_msg:
                    raise AudioError(
                        str(e),
                        "Microphone access denied. Check Windows privacy settings.",
                    ) from e
                raise AudioError(
                    str(e),
                    "Microphone error. Check your audio device settings.",
                ) from e

    def stop_recording(self) -> bytes:
        """Stop recording and return audio as WAV bytes.

        Returns:
            Audio data as WAV-formatted bytes
        """
        with self._lock:
            if not self._recording:
                logger.warning("Not recording")
                return b""

            logger.info("Stopping audio recording")
            self._recording = False

            if self._stream:
                self._stream.stop()
                self._stream.close()
                self._stream = None

            # Collect all recorded chunks
            chunks: list[np.ndarray] = []
            while True:
                try:
                    chunk = self._queue.get_nowait()
                    chunks.append(chunk)
                except queue.Empty:
                    break

            if not chunks:
                logger.warning("No audio data recorded")
                return b""

            # Concatenate chunks
            audio_data = np.concatenate(chunks, axis=0)
            logger.info(
                f"Recorded {len(audio_data)} samples ({len(audio_data) / self._config.sample_rate:.2f}s)"
            )

            # Convert to WAV bytes
            wav_buffer = io.BytesIO()
            sf.write(
                wav_buffer,
                audio_data,
                self._config.sample_rate,
                format="WAV",
                subtype="PCM_16",
            )
            wav_buffer.seek(0)

            return wav_buffer.read()

    @property
    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._recording

    @staticmethod
    def check_microphone_available() -> bool:
        """Check if a microphone is available.

        Returns:
            True if at least one input device is available
        """
        try:
            devices = sd.query_devices()
            return any(dev["max_input_channels"] > 0 for dev in devices)
        except sd.PortAudioError:
            return False

    @staticmethod
    def list_devices() -> list[dict]:
        """List available audio input devices.

        Returns:
            List of device info dicts with 'id', 'name', 'channels'
        """
        devices = []
        for i, dev in enumerate(sd.query_devices()):
            if dev["max_input_channels"] > 0:
                devices.append(
                    {
                        "id": i,
                        "name": dev["name"],
                        "channels": dev["max_input_channels"],
                        "default": dev.get("default_samplerate", 48000),
                    }
                )
        return devices
