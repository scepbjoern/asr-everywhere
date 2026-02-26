"""Shared pytest fixtures for regression testing."""

import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from asr_everywhere.config import (
    ASRConfig,
    AudioConfig,
    Config,
    HotkeyConfig,
)


# ============================================================================
# Config Fixtures
# ============================================================================


@pytest.fixture
def default_config():
    """Create a config with all default values for regression testing."""
    return Config()


@pytest.fixture
def valid_config():
    """Create a valid config with test values."""
    return Config(
        version=1,
        hotkey=HotkeyConfig(dictate="win+ctrl+a", mode="toggle"),
        asr=ASRConfig(
            provider="openai",
            model="whisper-1",
            language="auto",
            api_key="test-api-key-12345",
            base_url="https://api.openai.com/v1",
        ),
        audio=AudioConfig(device=None, sample_rate=16000, channels=1),
        clipboard_restore=True,
    )


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary config directory with isolated APPDATA."""
    config_dir = tmp_path / "asr-everywhere"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    with mock.patch.dict(os.environ, {"APPDATA": str(tmp_path)}):
        yield tmp_path


# ============================================================================
# Audio Recorder Fixtures
# ============================================================================


@pytest.fixture
def mock_audio_config():
    """Create mock audio config for testing."""
    return AudioConfig(sample_rate=16000, channels=1, device=None)


@pytest.fixture
def fake_audio_data():
    """Generate fake audio data (WAV header + silence)."""
    import io

    import numpy as np
    import soundfile as sf

    # Generate 1 second of silence at 16kHz mono
    samples = np.zeros(16000, dtype=np.float32)
    buffer = io.BytesIO()
    sf.write(buffer, samples, 16000, format="WAV", subtype="PCM_16")
    buffer.seek(0)
    return buffer.read()


# ============================================================================
# Provider Fixtures
# ============================================================================


@pytest.fixture
def mock_openai_response():
    """Create a mock OpenAI transcription response."""
    response = mock.MagicMock()
    response.text = "This is a test transcription."
    return response


@pytest.fixture
def mock_transcription_result():
    """Create a mock transcription result."""
    from asr_everywhere.providers.base import TranscriptionResult

    return TranscriptionResult(
        text="Test transcription text",
        language="en",
        duration=5.0,
    )


# ============================================================================
# Component Mocks
# ============================================================================


@pytest.fixture
def mock_recorder():
    """Create a fully mocked audio recorder."""
    recorder = mock.MagicMock()
    recorder.is_recording = False
    recorder.start_recording = mock.MagicMock()
    recorder.stop_recording = mock.MagicMock(return_value=b"fake_wav_data")
    return recorder


@pytest.fixture
def mock_inserter():
    """Create a fully mocked text inserter."""
    inserter = mock.MagicMock()
    inserter.insert_text = mock.MagicMock(return_value=True)
    inserter.save_clipboard = mock.MagicMock()
    inserter.restore_clipboard = mock.MagicMock()
    return inserter


@pytest.fixture
def mock_tray():
    """Create a fully mocked tray icon."""
    tray = mock.MagicMock()
    tray.set_state = mock.MagicMock()
    tray.show_notification = mock.MagicMock()
    tray.start = mock.MagicMock()
    tray.stop = mock.MagicMock()
    return tray


@pytest.fixture
def mock_hotkey_manager():
    """Create a fully mocked hotkey manager."""
    manager = mock.MagicMock()
    manager.register_hotkey = mock.MagicMock()
    manager.unregister_hotkey = mock.MagicMock()
    manager.unregister_all = mock.MagicMock()
    return manager


# ============================================================================
# Pipeline Fixtures
# ============================================================================


@pytest.fixture
def pipeline_components(valid_config, mock_recorder, mock_inserter, mock_tray):
    """Create all components needed for pipeline testing."""
    return {
        "config": valid_config,
        "recorder": mock_recorder,
        "inserter": mock_inserter,
        "tray": mock_tray,
    }
