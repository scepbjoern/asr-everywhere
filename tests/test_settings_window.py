"""Tests for Settings window."""

from unittest import mock

import pytest

# Skip all tests in this module if tkinter is not available or broken
tkinter_available = True
try:
    import tkinter as tk

    _root = tk.Tk()
    _root.destroy()
except Exception:
    tkinter_available = False

pytestmark = pytest.mark.skipif(
    not tkinter_available,
    reason="tkinter not available or Tcl not properly installed",
)


@pytest.fixture
def tk_root():
    """Create a tkinter root window for testing."""
    import tkinter as tk

    if not tkinter_available:
        pytest.skip("tkinter not available or Tcl not properly installed")
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window
        yield root
        root.destroy()
    except Exception:
        pytest.skip("tkinter not available or Tcl not properly installed")


@pytest.fixture
def mock_external_deps():
    """Mock external dependencies (audio devices, providers)."""
    with (
        mock.patch("asr_everywhere.ui.settings_window.list_providers") as mock_list,
        mock.patch("asr_everywhere.audio_recorder.AudioRecorder.list_devices") as mock_devices,
    ):
        mock_list.return_value = ["openai", "together", "local"]
        mock_devices.return_value = []
        yield


def test_settings_window_creation(tk_root, mock_external_deps):
    """Test settings window can be created."""
    from asr_everywhere.config import Config
    from asr_everywhere.ui.settings_window import SettingsWindow

    config = Config()
    on_save_called = []

    def on_save():
        on_save_called.append(True)

    window = SettingsWindow(tk_root, config, on_save)
    assert window is not None


def test_settings_window_provider_list(tk_root, mock_external_deps):
    """Test that providers are loaded correctly."""
    from asr_everywhere.config import Config
    from asr_everywhere.ui.settings_window import SettingsWindow

    with mock.patch("asr_everywhere.ui.settings_window.list_providers") as mock_list:
        mock_list.return_value = ["openai", "together", "local"]

        config = Config()
        SettingsWindow(tk_root, config, lambda: None)

        # Verify list_providers was called
        mock_list.assert_called()


def test_settings_window_device_list(tk_root, mock_external_deps):
    """Test that audio devices are loaded."""
    from asr_everywhere.config import Config
    from asr_everywhere.ui.settings_window import SettingsWindow

    with mock.patch("asr_everywhere.audio_recorder.AudioRecorder.list_devices") as mock_devices:
        mock_devices.return_value = [
            {"id": 0, "name": "Mic 1", "channels": 2},
            {"id": 1, "name": "Mic 2", "channels": 1},
        ]

        config = Config()
        SettingsWindow(tk_root, config, lambda: None)

        # Verify devices were queried
        mock_devices.assert_called()


def test_settings_window_uses_config_values(tk_root, mock_external_deps):
    """Test that settings window uses values from config."""
    from asr_everywhere.config import Config
    from asr_everywhere.ui.settings_window import SettingsWindow

    config = Config()
    config.asr.provider = "together"
    config.asr.language = "de"
    config.hotkey.dictate = "ctrl+shift+d"
    config.hotkey.mode = "push_to_talk"

    window = SettingsWindow(tk_root, config, lambda: None)

    # Verify the config values are used
    assert window._provider_var.get() == "together"
    assert window._language_var.get() == "de"
    assert window._hotkey_var.get() == "ctrl+shift+d"
    assert window._mode_var.get() == "push_to_talk"


def test_settings_window_on_provider_change(tk_root, mock_external_deps):
    """Test provider change updates model list."""
    from asr_everywhere.config import Config
    from asr_everywhere.ui.settings_window import SettingsWindow

    config = Config()

    with mock.patch("asr_everywhere.ui.settings_window.get_provider_models") as mock_models:
        mock_models.return_value = ["whisper-1"]

        window = SettingsWindow(tk_root, config, lambda: None)

        # Simulate provider change
        window._provider_var.set("together")
        window._on_provider_change(mock.MagicMock())

        # Verify models were fetched
        mock_models.assert_called_with("together")


def test_settings_window_save_updates_config(tk_root, mock_external_deps):
    """Test that saving updates the config."""
    from asr_everywhere.config import Config
    from asr_everywhere.ui.settings_window import SettingsWindow

    config = Config()

    with mock.patch("asr_everywhere.ui.settings_window.save_config") as mock_save:
        on_save_called = []

        def on_save():
            on_save_called.append(True)

        window = SettingsWindow(tk_root, config, on_save)

        # Set some values
        window._provider_var.set("together")
        window._model_var.set("whisper-1")
        window._language_var.set("de")
        window._hotkey_var.set("ctrl+shift+d")
        window._mode_var.set("push_to_talk")
        window._clipboard_var.set("keep")

        # Mock the window.destroy to avoid actual destruction
        window._window.destroy = mock.MagicMock()

        # Trigger save
        window._on_save_click()

        # Verify config was updated
        assert config.asr.provider == "together"
        assert config.asr.model == "whisper-1"
        assert config.asr.language == "de"
        assert config.hotkey.dictate == "ctrl+shift+d"
        assert config.hotkey.mode == "push_to_talk"
        assert config.clipboard_restore is False

        # Verify save was called
        mock_save.assert_called_once_with(config)
        assert on_save_called == [True]


def test_settings_window_test_provider_shows_warning_no_key(tk_root, mock_external_deps):
    """Test that testing provider without API key shows warning."""
    from asr_everywhere.config import Config
    from asr_everywhere.ui.settings_window import SettingsWindow

    config = Config()

    with mock.patch("tkinter.messagebox.showwarning") as mock_warning:
        window = SettingsWindow(tk_root, config, lambda: None)

        # Set provider without API key
        window._provider_var.set("together")
        window._api_key_var.set("")

        # Trigger test
        window._test_provider()

        # Verify warning was shown
        mock_warning.assert_called_once()


def test_settings_window_refresh_devices(tk_root, mock_external_deps):
    """Test that device refresh updates the list."""
    from asr_everywhere.config import Config
    from asr_everywhere.ui.settings_window import SettingsWindow

    config = Config()

    with (
        mock.patch("asr_everywhere.audio_recorder.AudioRecorder.list_devices") as mock_devices,
        mock.patch("tkinter.messagebox.showinfo") as mock_info,
    ):
        mock_devices.return_value = [
            {"id": 0, "name": "New Mic", "channels": 2},
        ]

        window = SettingsWindow(tk_root, config, lambda: None)

        # Trigger refresh
        window._refresh_devices()

        # Verify devices were updated
        assert len(window._devices) == 1
        mock_info.assert_called_once()
