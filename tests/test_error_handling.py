"""Tests for error handling functionality."""

from __future__ import annotations

from unittest import mock

import pytest
import sounddevice as sd

from asr_everywhere.audio_recorder import AudioRecorder
from asr_everywhere.errors import (
    ASREverywhereError,
    AudioError,
    ConfigError,
    NetworkError,
    ProviderError,
    categorize_openai_error,
    get_user_message,
)
from asr_everywhere.providers.openai_provider import OpenAIProvider
from asr_everywhere.transcription_pipeline import TranscriptionPipeline

# ============================================================================
# Error Message Tests
# ============================================================================


class TestErrorMessages:
    """Tests for error message generation."""

    def test_get_user_message_for_api_key_error(self):
        """API key errors should return friendly message."""
        error = ValueError("API key not configured")
        message = get_user_message(error)
        assert "API key" in message
        assert "Settings" in message

    def test_get_user_message_for_authentication_error(self):
        """Authentication errors should return friendly message."""
        error = Exception("Authentication failed")
        message = get_user_message(error)
        assert "API key rejected" in message

    def test_get_user_message_for_network_timeout(self):
        """Network timeout errors should return friendly message."""
        error = Exception("Connection timeout")
        message = get_user_message(error)
        assert "Network" in message

    def test_get_user_message_for_no_microphone(self):
        """No microphone errors should return friendly message."""
        error = Exception("No microphone found")
        message = get_user_message(error)
        assert "microphone" in message.lower()

    def test_get_user_message_for_rate_limit(self):
        """Rate limit errors should return friendly message."""
        error = Exception("Rate limit exceeded")
        message = get_user_message(error)
        assert "Rate limit" in message

    def test_get_user_message_for_custom_error(self):
        """Custom errors with user_message should use it."""
        error = AudioError(
            "Technical message",
            "User-friendly message",
        )
        message = get_user_message(error)
        assert message == "User-friendly message"

    def test_get_user_message_truncates_long_errors(self):
        """Long error messages should be truncated."""
        error = Exception("x" * 500)
        message = get_user_message(error)
        assert len(message) <= 200


# ============================================================================
# Error Categorization Tests
# ============================================================================


class TestErrorCategorization:
    """Tests for OpenAI error categorization."""

    def test_categorize_authentication_error(self):
        """Authentication errors should become ProviderError."""
        error = Exception("Authentication failed: invalid api key")
        categorized = categorize_openai_error(error)
        assert isinstance(categorized, ProviderError)
        assert "API key rejected" in categorized.user_message

    def test_categorize_connection_error(self):
        """Connection errors should become NetworkError."""
        error = Exception("Connection error: timeout")
        categorized = categorize_openai_error(error)
        assert isinstance(categorized, NetworkError)
        assert "Network" in categorized.user_message

    def test_categorize_rate_limit_error(self):
        """Rate limit errors should become ProviderError."""
        error = Exception("Rate limit exceeded")
        categorized = categorize_openai_error(error)
        assert isinstance(categorized, ProviderError)
        assert "Rate limit" in categorized.user_message

    def test_categorize_generic_error(self):
        """Generic errors should become ProviderError with friendly message."""
        error = Exception("Unknown error")
        categorized = categorize_openai_error(error)
        assert isinstance(categorized, ProviderError)


# ============================================================================
# Audio Recorder Error Handling Tests
# ============================================================================


class TestAudioRecorderErrors:
    """Tests for audio recorder error handling."""

    def test_start_recording_raises_audio_error_no_device(self, mock_audio_config):
        """Should raise AudioError when no device available."""
        with mock.patch("asr_everywhere.audio_recorder.sd") as mock_sd:
            mock_sd.InputStream.side_effect = sd.PortAudioError("No device found")
            mock_sd.PortAudioError = sd.PortAudioError

            recorder = AudioRecorder(mock_audio_config)

            with pytest.raises(AudioError) as exc_info:
                recorder.start_recording()

            assert "No microphone" in exc_info.value.user_message

    def test_start_recording_raises_audio_error_access_denied(self, mock_audio_config):
        """Should raise AudioError when access denied."""
        with mock.patch("asr_everywhere.audio_recorder.sd") as mock_sd:
            mock_sd.InputStream.side_effect = sd.PortAudioError("Access denied")
            mock_sd.PortAudioError = sd.PortAudioError

            recorder = AudioRecorder(mock_audio_config)

            with pytest.raises(AudioError) as exc_info:
                recorder.start_recording()

            assert "access denied" in exc_info.value.user_message.lower()

    def test_check_microphone_available_returns_true(self):
        """Should return True when microphone is available."""
        with mock.patch("asr_everywhere.audio_recorder.sd") as mock_sd:
            mock_sd.query_devices.return_value = [
                {"max_input_channels": 1, "name": "Mic"},
            ]

            result = AudioRecorder.check_microphone_available()
            assert result is True

    def test_check_microphone_available_returns_false_no_devices(self):
        """Should return False when no input devices."""
        with mock.patch("asr_everywhere.audio_recorder.sd") as mock_sd:
            mock_sd.query_devices.return_value = [
                {"max_input_channels": 0, "name": "Speaker"},
            ]

            result = AudioRecorder.check_microphone_available()
            assert result is False

    def test_check_microphone_available_returns_false_on_error(self):
        """Should return False on PortAudioError."""
        with mock.patch("asr_everywhere.audio_recorder.sd") as mock_sd:
            mock_sd.query_devices.side_effect = sd.PortAudioError("Error")
            mock_sd.PortAudioError = sd.PortAudioError

            result = AudioRecorder.check_microphone_available()
            assert result is False


# ============================================================================
# Provider Error Handling Tests
# ============================================================================


class TestProviderErrors:
    """Tests for provider error handling."""

    def test_openai_provider_raises_config_error_no_key(self, valid_config):
        """Should raise ConfigError when API key not configured."""
        provider = OpenAIProvider()
        valid_config.asr.api_key = ""

        with pytest.raises(ConfigError) as exc_info:
            provider._get_client(valid_config.asr)

        assert "API key" in exc_info.value.user_message

    def test_openai_provider_categorizes_transcription_error(self, valid_config):
        """Should categorize transcription errors."""
        provider = OpenAIProvider()
        valid_config.asr.api_key = "test-key"

        with (
            mock.patch("asr_everywhere.providers.openai_provider.OpenAI") as mock_openai,
        ):
            mock_client = mock.MagicMock()
            mock_openai.return_value = mock_client
            mock_client.audio.transcriptions.create.side_effect = Exception("Authentication failed")

            with pytest.raises(ProviderError) as exc_info:
                provider.transcribe(b"audio", valid_config.asr)

            assert "API key rejected" in exc_info.value.user_message


# ============================================================================
# Pipeline Error Handling Tests
# ============================================================================


class TestPipelineErrorHandling:
    """Tests for pipeline error handling."""

    def test_pipeline_handles_audio_error_gracefully(self, pipeline_components):
        """Pipeline should handle AudioError and show notification."""
        from asr_everywhere.errors import AudioError

        pipeline = TranscriptionPipeline(
            config=pipeline_components["config"],
            recorder=pipeline_components["recorder"],
            inserter=pipeline_components["inserter"],
            tray=pipeline_components["tray"],
        )

        # Make recorder raise AudioError
        pipeline_components["recorder"].start_recording.side_effect = AudioError(
            "No device",
            "No microphone found",
        )

        # Should not raise
        pipeline.start_recording()

        # Should show notification
        pipeline_components["tray"].show_notification.assert_called()
        call_args = pipeline_components["tray"].show_notification.call_args
        assert "Recording Error" in str(call_args)

    def test_pipeline_handles_provider_error_gracefully(self, pipeline_components):
        """Pipeline should handle ProviderError and show user-friendly message."""
        from asr_everywhere.errors import ProviderError

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
            mock_get.side_effect = ProviderError(
                "API error",
                "API key rejected. Check your key in Settings.",
            )

            # Should not raise
            pipeline.toggle_recording()

            # Should show user-friendly message
            pipeline_components["tray"].show_notification.assert_called()
            call_args = pipeline_components["tray"].show_notification.call_args
            assert "API key rejected" in str(call_args)

    def test_pipeline_graceful_degradation_llm_error(self, pipeline_components):
        """Pipeline should use raw transcription when LLM fails."""
        recorder = pipeline_components["recorder"]
        recorder.is_recording = True
        recorder.stop_recording.return_value = b"audio"

        # Enable LLM
        pipeline_components["config"].llm.enabled = True

        pipeline = TranscriptionPipeline(
            config=pipeline_components["config"],
            recorder=recorder,
            inserter=pipeline_components["inserter"],
            tray=pipeline_components["tray"],
        )

        with (
            mock.patch("asr_everywhere.transcription_pipeline.get_provider") as mock_get,
            mock.patch("asr_everywhere.transcription_pipeline.PostProcessor") as mock_pp,
        ):
            mock_provider = mock.MagicMock()
            mock_provider.transcribe.return_value.text = "Raw transcription"
            mock_get.return_value = mock_provider

            # Make LLM post-processor fail
            mock_pp.return_value.process.side_effect = Exception("LLM error")

            pipeline.toggle_recording()

            # Should still insert text
            pipeline_components["inserter"].insert_text.assert_called_with(
                "Raw transcription",
                restore_clipboard=True,
            )


# ============================================================================
# Regression Tests for Error Handling
# ============================================================================


class TestErrorHandlingRegression:
    """Regression tests for error handling."""

    def test_audio_error_has_user_message(self):
        """AudioError must have user_message attribute."""
        error = AudioError("Technical", "User friendly")
        assert hasattr(error, "user_message")
        assert error.user_message == "User friendly"

    def test_config_error_has_user_message(self):
        """ConfigError must have user_message attribute."""
        error = ConfigError("Technical", "User friendly")
        assert hasattr(error, "user_message")
        assert error.user_message == "User friendly"

    def test_provider_error_has_user_message(self):
        """ProviderError must have user_message attribute."""
        error = ProviderError("Technical", "User friendly")
        assert hasattr(error, "user_message")
        assert error.user_message == "User friendly"

    def test_network_error_has_user_message(self):
        """NetworkError must have user_message attribute."""
        error = NetworkError("Technical", "User friendly")
        assert hasattr(error, "user_message")
        assert error.user_message == "User friendly"

    def test_all_errors_inherit_from_base(self):
        """All custom errors must inherit from ASREverywhereError."""
        errors = [AudioError, ConfigError, ProviderError, NetworkError]
        for error_class in errors:
            assert issubclass(error_class, ASREverywhereError)

    def test_error_message_not_too_long_for_notification(self):
        """Error messages must fit in tray notification (256 char limit)."""
        # Create a very long error
        error = Exception("x" * 1000)
        message = get_user_message(error)

        # pystray has a limit around 256 chars
        assert len(message) <= 200
