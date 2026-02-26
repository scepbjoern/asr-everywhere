"""Tests for audio recorder."""

from unittest import mock

import numpy as np
import pytest

from asr_everywhere.audio_recorder import AudioRecorder
from asr_everywhere.config import AudioConfig


@pytest.fixture
def audio_config():
    """Create test audio config."""
    return AudioConfig(sample_rate=16000, channels=1)


@pytest.fixture
def recorder(audio_config):
    """Create recorder instance."""
    return AudioRecorder(audio_config)


def test_recorder_initial_state(recorder):
    """Test recorder starts in not-recording state."""
    assert not recorder.is_recording


def test_list_devices():
    """Test device listing."""
    with mock.patch("asr_everywhere.audio_recorder.sd") as mock_sd:
        mock_sd.query_devices.return_value = [
            {"name": "Mic 1", "max_input_channels": 1, "default_samplerate": 48000},
            {"name": "Speaker", "max_input_channels": 0},
            {"name": "Mic 2", "max_input_channels": 2, "default_samplerate": 44100},
        ]

        devices = AudioRecorder.list_devices()

        # Should only include input devices
        assert len(devices) == 2
        assert devices[0]["name"] == "Mic 1"
        assert devices[1]["name"] == "Mic 2"


def test_start_stop_recording(recorder):
    """Test starting and stopping recording."""
    with mock.patch("asr_everywhere.audio_recorder.sd") as mock_sd:
        mock_stream = mock.MagicMock()
        mock_sd.InputStream.return_value = mock_stream

        # Start recording
        recorder.start_recording()
        assert recorder.is_recording
        mock_stream.start.assert_called_once()

        # Simulate some audio data
        test_data = np.random.rand(1000, 1).astype(np.float32)
        recorder._queue.put(test_data)

        # Stop recording
        audio_bytes = recorder.stop_recording()
        assert not recorder.is_recording
        mock_stream.stop.assert_called_once()
        mock_stream.close.assert_called_once()

        # Should return WAV bytes
        assert audio_bytes.startswith(b"RIFF")  # WAV header


def test_stop_without_start_returns_empty(recorder):
    """Test stopping without starting returns empty bytes."""
    audio_bytes = recorder.stop_recording()
    assert audio_bytes == b""
