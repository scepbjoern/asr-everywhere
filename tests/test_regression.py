"""Regression tests to ensure core functionality remains stable across phases.

These tests verify the fundamental behavior of Phase 1 components.
Any future changes should not break these tests.
"""

import io
from unittest import mock

import numpy as np
import pytest

from asr_everywhere.audio_recorder import AudioRecorder
from asr_everywhere.config import (
    ASRConfig,
    AudioConfig,
    Config,
    HotkeyConfig,
    load_config,
    save_config,
)
from asr_everywhere.providers.base import TranscriptionResult
from asr_everywhere.providers.openai_provider import OpenAIProvider
from asr_everywhere.providers.registry import get_provider, list_providers
from asr_everywhere.text_inserter import TextInserter
from asr_everywhere.transcription_pipeline import TranscriptionPipeline


# ============================================================================
# Phase 1: Configuration Regression Tests
# ============================================================================


class TestConfigRegression:
    """Regression tests for configuration management."""

    def test_default_hotkey_is_win_ctrl_a(self, default_config):
        """Ensure default hotkey remains win+ctrl+a (changed from win+u)."""
        assert default_config.hotkey.dictate == "win+ctrl+a"

    def test_default_asr_provider_is_openai(self, default_config):
        """Ensure default ASR provider is OpenAI."""
        assert default_config.asr.provider == "openai"

    def test_default_asr_model_is_whisper_1(self, default_config):
        """Ensure default ASR model is whisper-1."""
        assert default_config.asr.model == "whisper-1"

    def test_default_audio_sample_rate_is_16000(self, default_config):
        """Ensure default audio sample rate is 16kHz."""
        assert default_config.audio.sample_rate == 16000

    def test_default_audio_is_mono(self, default_config):
        """Ensure default audio is mono (1 channel)."""
        assert default_config.audio.channels == 1

    def test_config_version_is_1(self, default_config):
        """Ensure config version is 1."""
        assert default_config.version == 1

    def test_clipboard_restore_default_is_true(self, default_config):
        """Ensure clipboard restore is enabled by default."""
        assert default_config.clipboard_restore is True

    def test_config_serialization_roundtrip(self, temp_config_dir, valid_config):
        """Ensure config can be saved and loaded without data loss."""
        with mock.patch("asr_everywhere.config.get_config_path") as mock_path:
            config_path = temp_config_dir / "asr-everywhere" / "config.json"
            mock_path.return_value = config_path

            save_config(valid_config)
            loaded = load_config()

            assert loaded.hotkey.dictate == valid_config.hotkey.dictate
            assert loaded.asr.provider == valid_config.asr.provider
            assert loaded.asr.model == valid_config.asr.model
            assert loaded.audio.sample_rate == valid_config.audio.sample_rate


# ============================================================================
# Phase 1: Audio Recorder Regression Tests
# ============================================================================


class TestAudioRecorderRegression:
    """Regression tests for audio recording functionality."""

    def test_recorder_starts_not_recording(self, mock_audio_config):
        """Recorder should start in not-recording state."""
        recorder = AudioRecorder(mock_audio_config)
        assert not recorder.is_recording

    def test_recorder_state_changes_on_start_stop(self, mock_audio_config):
        """Recorder state should change correctly during start/stop cycle."""
        with mock.patch("asr_everywhere.audio_recorder.sd") as mock_sd:
            mock_stream = mock.MagicMock()
            mock_sd.InputStream.return_value = mock_stream

            recorder = AudioRecorder(mock_audio_config)

            recorder.start_recording()
            assert recorder.is_recording

            # Simulate audio data
            recorder._queue.put(np.zeros((1000, 1), dtype=np.float32))

            audio_bytes = recorder.stop_recording()
            assert not recorder.is_recording
            assert audio_bytes.startswith(b"RIFF")  # WAV header

    def test_recorder_returns_empty_when_not_recording(self, mock_audio_config):
        """Stopping without starting should return empty bytes."""
        recorder = AudioRecorder(mock_audio_config)
        result = recorder.stop_recording()
        assert result == b""


# ============================================================================
# Phase 1: Provider Regression Tests
# ============================================================================


class TestProviderRegression:
    """Regression tests for ASR provider functionality."""

    def test_openai_provider_has_whisper_model(self):
        """OpenAI provider must support whisper-1 model."""
        provider = OpenAIProvider()
        models = provider.list_models()
        assert "whisper-1" in models

    def test_openai_provider_has_gpt4o_transcribe_model(self):
        """OpenAI provider must support gpt-4o-transcribe model."""
        provider = OpenAIProvider()
        models = provider.list_models()
        assert "gpt-4o-transcribe" in models

    def test_registry_contains_openai(self):
        """Registry must contain openai provider."""
        providers = list_providers()
        assert "openai" in providers

    def test_registry_returns_openai_provider(self):
        """Registry must return OpenAIProvider for 'openai' name."""
        provider = get_provider("openai")
        assert isinstance(provider, OpenAIProvider)

    def test_registry_raises_for_unknown_provider(self):
        """Registry must raise ValueError for unknown provider."""
        with pytest.raises(ValueError, match="Unknown provider"):
            get_provider("nonexistent_provider")

    def test_openai_transcribe_returns_result(self, valid_config):
        """OpenAI provider must return TranscriptionResult."""
        provider = OpenAIProvider()

        with mock.patch("asr_everywhere.providers.openai_provider.OpenAI") as mock_openai:
            mock_client = mock.MagicMock()
            mock_openai.return_value = mock_client

            mock_response = mock.MagicMock()
            mock_response.text = "Test transcription"
            mock_client.audio.transcriptions.create.return_value = mock_response

            result = provider.transcribe(b"fake audio", valid_config.asr)

            assert isinstance(result, TranscriptionResult)
            assert result.text == "Test transcription"


# ============================================================================
# Phase 1: Text Inserter Regression Tests
# ============================================================================


class TestTextInserterRegression:
    """Regression tests for text insertion functionality."""

    def test_inserter_saves_clipboard(self):
        """Inserter must save clipboard before insertion."""
        inserter = TextInserter()

        with mock.patch("asr_everywhere.text_inserter.pyperclip") as mock_clip:
            mock_clip.paste.return_value = "old content"

            inserter.save_clipboard()
            assert inserter._saved_clipboard == "old content"

    def test_inserter_restores_clipboard(self):
        """Inserter must restore clipboard after insertion."""
        inserter = TextInserter()

        with mock.patch("asr_everywhere.text_inserter.pyperclip") as mock_clip, \
             mock.patch("asr_everywhere.text_inserter.time.sleep"):
            mock_clip.paste.return_value = "saved content"

            inserter.save_clipboard()
            inserter.restore_clipboard()

            mock_clip.copy.assert_called_with("saved content")

    def test_inserter_returns_false_for_empty_text(self):
        """Inserter must return False for empty text."""
        inserter = TextInserter()
        result = inserter.insert_text("")
        assert result is False

    def test_inserter_returns_true_for_valid_text(self):
        """Inserter must return True for valid text insertion."""
        inserter = TextInserter()

        with mock.patch("asr_everywhere.text_inserter.pyperclip") as mock_clip, \
             mock.patch("asr_everywhere.text_inserter.time.sleep"):
            mock_clip.paste.return_value = "old"

            result = inserter.insert_text("test text", restore_clipboard=False)
            assert result is True


# ============================================================================
# Phase 1: Pipeline Regression Tests
# ============================================================================


class TestPipelineRegression:
    """Regression tests for transcription pipeline."""

    def test_pipeline_starts_recording_on_toggle(self, pipeline_components):
        """Pipeline must start recording when toggle called while idle."""
        pipeline = TranscriptionPipeline(
            config=pipeline_components["config"],
            recorder=pipeline_components["recorder"],
            inserter=pipeline_components["inserter"],
            tray=pipeline_components["tray"],
        )

        pipeline.toggle_recording()

        pipeline_components["recorder"].start_recording.assert_called_once()
        pipeline_components["tray"].set_state.assert_called()

    def test_pipeline_stops_and_transcribes_on_toggle(self, pipeline_components):
        """Pipeline must stop recording and transcribe when toggle called while recording."""
        recorder = pipeline_components["recorder"]
        recorder.is_recording = True
        recorder.stop_recording.return_value = b"audio data"

        pipeline = TranscriptionPipeline(
            config=pipeline_components["config"],
            recorder=recorder,
            inserter=pipeline_components["inserter"],
            tray=pipeline_components["tray"],
        )

        with mock.patch("asr_everywhere.transcription_pipeline.get_provider") as mock_get:
            mock_provider = mock.MagicMock()
            mock_provider.transcribe.return_value.text = "Transcribed"
            mock_get.return_value = mock_provider

            pipeline.toggle_recording()

            recorder.stop_recording.assert_called_once()
            mock_provider.transcribe.assert_called_once()
            pipeline_components["inserter"].insert_text.assert_called()

    def test_pipeline_ignores_toggle_during_processing(self, pipeline_components):
        """Pipeline must ignore toggle during processing."""
        pipeline = TranscriptionPipeline(
            config=pipeline_components["config"],
            recorder=pipeline_components["recorder"],
            inserter=pipeline_components["inserter"],
            tray=pipeline_components["tray"],
        )

        pipeline._processing = True
        pipeline.toggle_recording()

        pipeline_components["recorder"].start_recording.assert_not_called()
        pipeline_components["recorder"].stop_recording.assert_not_called()

    def test_pipeline_shows_notification_on_success(self, pipeline_components):
        """Pipeline must show notification on successful transcription."""
        recorder = pipeline_components["recorder"]
        recorder.is_recording = True
        recorder.stop_recording.return_value = b"audio"

        pipeline = TranscriptionPipeline(
            config=pipeline_components["config"],
            recorder=recorder,
            inserter=pipeline_components["inserter"],
            tray=pipeline_components["tray"],
        )

        with mock.patch("asr_everywhere.transcription_pipeline.get_provider") as mock_get:
            mock_provider = mock.MagicMock()
            mock_provider.transcribe.return_value.text = "Success text"
            mock_get.return_value = mock_provider

            pipeline.toggle_recording()

            pipeline_components["tray"].show_notification.assert_called()

    def test_pipeline_handles_transcription_error(self, pipeline_components):
        """Pipeline must handle transcription errors gracefully."""
        recorder = pipeline_components["recorder"]
        recorder.is_recording = True
        recorder.stop_recording.return_value = b"audio"

        pipeline = TranscriptionPipeline(
            config=pipeline_components["config"],
            recorder=recorder,
            inserter=pipeline_components["inserter"],
            tray=pipeline_components["tray"],
        )

        with mock.patch("asr_everywhere.transcription_pipeline.get_provider") as mock_get:
            mock_get.side_effect = Exception("API Error")

            # Should not raise
            pipeline.toggle_recording()

            # Should still update tray state
            pipeline_components["tray"].set_state.assert_called()


# ============================================================================
# Phase 1: Integration Regression Tests
# ============================================================================


class TestIntegrationRegression:
    """Integration tests for complete workflows."""

    def test_full_recording_transcription_workflow(self, valid_config, fake_audio_data):
        """Test complete workflow from recording to text insertion."""
        # Create real components with mocked external dependencies
        recorder = AudioRecorder(valid_config.audio)
        inserter = TextInserter()
        tray = mock.MagicMock()

        pipeline = TranscriptionPipeline(
            config=valid_config,
            recorder=recorder,
            inserter=inserter,
            tray=tray,
        )

        # Mock the audio stream
        with mock.patch("asr_everywhere.audio_recorder.sd") as mock_sd, \
             mock.patch("asr_everywhere.transcription_pipeline.get_provider") as mock_get, \
             mock.patch("asr_everywhere.text_inserter.pyperclip") as mock_clip, \
             mock.patch("asr_everywhere.text_inserter.time.sleep"):

            # Setup audio stream mock
            mock_stream = mock.MagicMock()
            mock_sd.InputStream.return_value = mock_stream

            # Setup transcription mock
            mock_provider = mock.MagicMock()
            mock_provider.transcribe.return_value.text = "Integration test text"
            mock_get.return_value = mock_provider

            # Setup clipboard mock
            mock_clip.paste.return_value = "old clipboard"

            # Simulate recording
            pipeline.toggle_recording()
            assert recorder.is_recording

            # Simulate audio data
            test_samples = np.zeros((16000, 1), dtype=np.float32)
            recorder._queue.put(test_samples)

            # Stop and transcribe
            pipeline.toggle_recording()
            assert not recorder.is_recording

            # Verify workflow completed
            mock_provider.transcribe.assert_called_once()
            mock_clip.copy.assert_called()
