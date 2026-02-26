"""Configuration management for ASR Everywhere."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CONFIG_VERSION = 1


@dataclass
class HotkeyConfig:
    """Hotkey configuration."""

    dictate: str = "win+ctrl+a"
    mode: str = "toggle"  # toggle or push_to_talk


@dataclass
class ASRConfig:
    """ASR provider configuration."""

    provider: str = "openai"
    model: str = "whisper-1"
    language: str = "auto"  # auto, de, en
    api_key: str = ""
    base_url: str = "https://api.openai.com/v1"


@dataclass
class AudioConfig:
    """Audio recording configuration."""

    device: int | None = None  # None = system default
    sample_rate: int = 16000
    channels: int = 1


@dataclass
class Config:
    """Main configuration container."""

    version: int = CONFIG_VERSION
    hotkey: HotkeyConfig = field(default_factory=HotkeyConfig)
    asr: ASRConfig = field(default_factory=ASRConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    clipboard_restore: bool = True


def get_config_path() -> Path:
    """Return path to config file in %APPDATA%."""
    appdata = os.environ.get("APPDATA", "")
    if not appdata:
        raise RuntimeError("APPDATA environment variable not found")
    config_dir = Path(appdata) / "asr-everywhere"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.json"


def load_config() -> Config:
    """Load configuration from file, creating default if not exists."""
    config_path = get_config_path()

    if not config_path.exists():
        logger.info("Config file not found, creating default")
        config = Config()
        save_config(config)
        return config

    try:
        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)

        # Parse into Config dataclass
        config = Config(
            version=data.get("version", CONFIG_VERSION),
            hotkey=HotkeyConfig(**data.get("hotkey", {})),
            asr=ASRConfig(**data.get("asr", {})),
            audio=AudioConfig(**data.get("audio", {})),
            clipboard_restore=data.get("clipboard_restore", True),
        )
        logger.info(f"Loaded config from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Failed to load config: {e}, using defaults")
        return Config()


def save_config(config: Config) -> None:
    """Save configuration to file."""
    config_path = get_config_path()

    def _asdict_recursive(obj: Any) -> Any:
        if hasattr(obj, "__dataclass_fields__"):
            return {k: _asdict_recursive(v) for k, v in asdict(obj).items()}
        return obj

    data = _asdict_recursive(config)

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved config to {config_path}")
