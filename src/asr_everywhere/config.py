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
class ModelConfig:
    """Configuration for a specific model."""

    name: str
    price_per_hour: str = ""  # e.g. "0.36 USD" or "in Plus-Plan enthalten"


@dataclass
class ProviderConfig:
    """Configuration for a specific ASR provider."""

    api_key: str = ""
    base_url: str = ""
    models: list[ModelConfig] = field(default_factory=list)


@dataclass
class ASRConfig:
    """ASR provider configuration."""

    provider: str = "openai"
    model: str = "whisper-1"
    language: str = "auto"  # auto, de, en
    api_key: str = ""  # Kept for backward compatibility
    base_url: str = "https://api.openai.com/v1"  # Kept for backward compatibility
    providers: dict[str, ProviderConfig] = field(default_factory=dict)

    def get_api_key(self) -> str:
        """Get API key for current provider."""
        if self.provider in self.providers:
            return self.providers[self.provider].api_key
        return self.api_key

    def get_base_url(self) -> str:
        """Get base URL for current provider."""
        if self.provider in self.providers:
            return self.providers[self.provider].base_url
        return self.base_url


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
    show_notification: bool = True  # Show notification after successful transcription


def get_config_path() -> Path:
    """Return path to config file in %APPDATA%."""
    appdata = os.environ.get("APPDATA", "")
    if not appdata:
        raise RuntimeError("APPDATA environment variable not found")
    config_dir = Path(appdata) / "asr-everywhere"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.json"


def _get_default_providers() -> dict[str, ProviderConfig]:
    """Get default provider configurations."""
    return {
        "openai": ProviderConfig(
            api_key="",
            base_url="https://api.openai.com/v1",
            models=[
                ModelConfig(name="gpt-4o-transcribe", price_per_hour="0.36 USD"),
                ModelConfig(name="gpt-4o-mini-transcribe", price_per_hour="0.18 USD"),
            ],
        ),
        "together": ProviderConfig(
            api_key="",
            base_url="https://api.together.xyz/v1",
            models=[
                ModelConfig(name="Whisper Large v3", price_per_hour="0.09 USD"),
            ],
        ),
        "huggingface": ProviderConfig(
            api_key="",
            base_url="https://router.huggingface.co/v1",
            models=[
                ModelConfig(name="hf-inference/openai/whisper-large-v3-turbo", price_per_hour="in Plus-Plan enthalten"),
                ModelConfig(name="hf-inference/openai/whisper-large-v3", price_per_hour="in Plus-Plan enthalten"),
            ],
        ),
        "local": ProviderConfig(
            api_key="",
            base_url="http://localhost:11434/v1",
            models=[],  # User-configured
        ),
    }


def load_config() -> Config:
    """Load configuration from file, creating default if not exists."""
    config_path = get_config_path()

    if not config_path.exists():
        logger.info("Config file not found, creating default")
        config = Config()
        # Initialize default provider configs
        config.asr.providers = _get_default_providers()
        save_config(config)
        return config

    try:
        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)

        # Parse provider configs including models
        providers_data = data.get("asr", {}).get("providers", {})
        providers = {}
        for name, pcfg in providers_data.items():
            models_data = pcfg.get("models", [])
            models = [ModelConfig(**m) for m in models_data] if models_data else []
            providers[name] = ProviderConfig(
                api_key=pcfg.get("api_key", ""),
                base_url=pcfg.get("base_url", ""),
                models=models,
            )

        # If no providers in config, use defaults
        if not providers:
            providers = _get_default_providers()

        config = Config(
            version=data.get("version", CONFIG_VERSION),
            hotkey=HotkeyConfig(**data.get("hotkey", {})),
            asr=ASRConfig(
                provider=data.get("asr", {}).get("provider", "openai"),
                model=data.get("asr", {}).get("model", "whisper-1"),
                language=data.get("asr", {}).get("language", "auto"),
                api_key=data.get("asr", {}).get("api_key", ""),
                base_url=data.get("asr", {}).get("base_url", "https://api.openai.com/v1"),
                providers=providers,
            ),
            audio=AudioConfig(**data.get("audio", {})),
            clipboard_restore=data.get("clipboard_restore", True),
            show_notification=data.get("show_notification", True),
        )
        logger.info(f"Loaded config from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Failed to load config: {e}, using defaults")
        config = Config()
        config.asr.providers = _get_default_providers()
        return config


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
