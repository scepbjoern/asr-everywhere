"""Tests for transcription pipeline."""

from unittest import mock

import pytest

from asr_everywhere.transcription_pipeline import TranscriptionPipeline


@pytest.fixture
def mock_config():
    """Create mock config."""
    config = mock.MagicMock()
    config.asr.provider = "openai"
    config.asr.model = "whisper-1"
    config.clipboard_restore = True
    return config


@pytest.fixture
def mock_components():
    """Create mock components."""
    recorder = mock.MagicMock()
    recorder.is_recording = False

    inserter = mock.MagicMock()
    inserter.insert_text.return_value = True

    tray = mock.MagicMock()

    return recorder, inserter, tray


def test_toggle_starts_recording(mock_config, mock_components):
    """Test toggle starts recording when idle."""
    recorder, inserter, tray = mock_components

    pipeline = TranscriptionPipeline(
        config=mock_config,
        recorder=recorder,
        inserter=inserter,
        tray=tray,
    )

    pipeline.toggle_recording()

    recorder.start_recording.assert_called_once()
    tray.set_state.assert_called()


def test_toggle_stops_and_transcribes(mock_config, mock_components):
    """Test toggle stops and transcribes when recording."""
    recorder, inserter, tray = mock_components
    recorder.is_recording = True
    recorder.stop_recording.return_value = b"audio data"

    pipeline = TranscriptionPipeline(
        config=mock_config,
        recorder=recorder,
        inserter=inserter,
        tray=tray,
    )

    with mock.patch("asr_everywhere.transcription_pipeline.get_provider") as mock_get_provider:
        mock_provider = mock.MagicMock()
        mock_provider.transcribe.return_value.text = "Transcribed text"
        mock_get_provider.return_value = mock_provider

        pipeline.toggle_recording()

        recorder.stop_recording.assert_called_once()
        mock_provider.transcribe.assert_called_once()
        inserter.insert_text.assert_called_with("Transcribed text", restore_clipboard=True)


def test_ignores_toggle_during_processing(mock_config, mock_components):
    """Test toggle is ignored during processing."""
    recorder, inserter, tray = mock_components

    pipeline = TranscriptionPipeline(
        config=mock_config,
        recorder=recorder,
        inserter=inserter,
        tray=tray,
    )

    pipeline._processing = True

    pipeline.toggle_recording()

    recorder.start_recording.assert_not_called()
    recorder.stop_recording.assert_not_called()
