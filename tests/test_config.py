"""Tests for configuration management."""

import os
from pathlib import Path
from unittest import mock

from asr_everywhere.config import (
    ASRConfig,
    Config,
    HotkeyConfig,
    get_config_path,
    load_config,
    save_config,
)


def test_get_config_path():
    """Test config path resolution."""
    with mock.patch.dict(os.environ, {"APPDATA": "/test/appdata"}):
        path = get_config_path()
        assert "asr-everywhere" in str(path)
        assert str(path).endswith("config.json")


def test_default_config():
    """Test default configuration values."""
    config = Config()

    assert config.version == 1
    assert config.hotkey.dictate == "win+ctrl+a"
    assert config.hotkey.mode == "toggle"
    assert config.asr.provider == "openai"
    assert config.asr.model == "whisper-1"
    assert config.audio.sample_rate == 16000
    assert config.clipboard_restore is True


def test_save_and_load_config(tmp_path: Path):
    """Test saving and loading configuration."""
    config_path = tmp_path / "config.json"

    with mock.patch("asr_everywhere.config.get_config_path", return_value=config_path):
        # Create and save config
        config = Config(
            hotkey=HotkeyConfig(dictate="ctrl+alt+r"),
            asr=ASRConfig(api_key="test-key"),
        )
        save_config(config)

        # Verify file exists
        assert config_path.exists()

        # Load and verify
        loaded = load_config()
        assert loaded.hotkey.dictate == "ctrl+alt+r"
        assert loaded.asr.api_key == "test-key"


def test_load_missing_config_creates_default(tmp_path: Path):
    """Test loading missing config creates default."""
    config_path = tmp_path / "config.json"

    with mock.patch("asr_everywhere.config.get_config_path", return_value=config_path):
        config = load_config()

        # Should have default values
        assert config.hotkey.dictate == "win+ctrl+a"

        # Should have created the file
        assert config_path.exists()
