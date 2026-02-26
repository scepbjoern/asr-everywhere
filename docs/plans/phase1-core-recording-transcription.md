# Feature: Phase 1 - Core Recording & Transcription

The following plan should be complete, but it's important that you validate documentation and codebase patterns and task sanity before you start implementing.

Pay special attention to naming of existing utils types and models. Import from the right files etc.

## Feature Description

Implement the foundational pipeline for system-wide voice-to-text dictation on Windows. This phase delivers a working MVP where a user can press a global hotkey to record audio, have it transcribed via OpenAI Whisper API, and have the text automatically inserted at the cursor position.

## User Story

As a Windows user
I want to press a hotkey to record my voice and have the transcribed text appear at my cursor
So that I can dictate text into any application without switching windows

## Problem Statement

Windows lacks a flexible, provider-agnostic dictation solution. Built-in Win+H dictation is limited to one model with poor German support. macOS has Aqua Voice, but Windows users have no equivalent. Users need a simple, pip-installable tool that works system-wide with their choice of ASR provider.

## Solution Statement

Build a Python desktop application that:
1. Registers a global hotkey (WIN+U) using the `keyboard` library
2. Records audio from the default microphone using `sounddevice` with callback-based streaming
3. Sends audio to OpenAI Whisper API for transcription
4. Inserts text at cursor via clipboard (pyperclip) + Ctrl+V simulation (pynput)
5. Provides visual feedback via System Tray icon (pystray) with idle/recording/processing states
6. Stores configuration in JSON at `%APPDATA%/asr-everywhere/config.json`

## Feature Metadata

**Feature Type**: New Capability
**Estimated Complexity**: Medium
**Primary Systems Affected**: 
- Audio recording subsystem
- Hotkey management
- ASR provider integration
- Text insertion mechanism
- System Tray UI
- Configuration management

**Dependencies**: 
- `sounddevice>=0.4` - Audio capture
- `soundfile>=0.12` - WAV encoding
- `openai>=1.0` - Whisper API
- `keyboard>=0.13` - Global hotkeys
- `pystray>=0.19` - System Tray
- `pyperclip>=1.8` - Clipboard operations
- `pynput>=1.7` - Keystroke simulation
- `Pillow>=10.0` - Icon image handling

---

## CONTEXT REFERENCES

### Relevant Codebase Files IMPORTANT: YOU MUST READ THESE FILES BEFORE IMPLEMENTING!

- `docs/PRD.md` (lines 522-538) - Phase 1 deliverables and validation criteria
- `docs/PRD.md` (lines 229-348) - Feature specifications: hotkeys, audio, ASR, text insertion, tray
- `docs/PRD.md` (lines 385-446) - Configuration schema and example JSON
- `docs/PRD.md` (lines 469-487) - OpenAI API usage pattern for transcription
- `.windsurf/rules/main-rules.md` (lines 1-203) - Project conventions, naming, architecture patterns
- `pyproject.toml` (lines 1-68) - Dependencies, entry points, ruff config
- `src/asr_everywhere/__init__.py` - Package initialization, version
- `src/asr_everywhere/__main__.py` - Entry point stub to replace

### New Files to Create

```
src/asr_everywhere/
├── app.py                      # Application orchestrator - wires all components
├── config.py                   # Config class: load, save, defaults, %APPDATA% path
├── hotkey_manager.py           # HotkeyManager: register WIN+U, toggle callback
├── audio_recorder.py           # AudioRecorder: sounddevice InputStream, callback
├── text_inserter.py            # TextInserter: clipboard save/restore, Ctrl+V
├── transcription_pipeline.py   # TranscriptionPipeline: record → transcribe → insert
├── providers/
│   ├── __init__.py
│   ├── base.py                 # ASRProvider ABC (transcribe, list_models)
│   ├── openai_provider.py      # OpenAIProvider implementation
│   └── registry.py             # Provider discovery (simple dict for Phase 1)
└── ui/
    ├── __init__.py
    └── tray.py                 # TrayIcon: pystray icon, menu, state changes

assets/
├── icon_idle.ico               # Default tray icon (create simple colored circle)
├── icon_recording.ico          # Red circle for recording state
└── icon_processing.ico         # Yellow/orange circle for processing state

tests/
├── test_config.py              # Config load/save tests
├── test_audio_recorder.py      # AudioRecorder tests (mock sounddevice)
├── test_text_inserter.py       # TextInserter tests (mock clipboard)
├── test_providers.py           # OpenAIProvider tests (mock API)
└── test_pipeline.py            # Integration tests (mock all components)
```

### Relevant Documentation YOU SHOULD READ BEFORE IMPLEMENTING!

- [sounddevice Usage - Recording](https://python-sounddevice.readthedocs.io/en/0.3.12/usage.html)
  - Section: Recording with rec() and InputStream callback
  - Why: Shows how to record arbitrary duration audio with callback streams

- [sounddevice Example - Recording with Arbitrary Duration](https://python-sounddevice.readthedocs.io/en/0.3.12/examples.html)
  - Section: rec_unlimited.py example
  - Why: Reference implementation for callback-based recording to queue

- [keyboard library GitHub](https://github.com/boppreh/keyboard)
  - Section: add_hotkey(), wait(), hook documentation
  - Why: Global hotkey registration with toggle support

- [pynput Keyboard Documentation](https://pynput.readthedocs.io/en/latest/keyboard.html)
  - Section: Controlling the keyboard (Controller, press, release)
  - Why: Simulating Ctrl+V for text insertion

- [pystray Usage Documentation](https://pystray.readthedocs.io/en/latest/usage.html)
  - Section: Creating a system tray icon, menus
  - Why: System Tray implementation with icon state changes

- [OpenAI Python SDK](https://github.com/openai/openai-python)
  - Section: audio.transcriptions.create()
  - Why: Whisper API transcription

- [pyperclip PyPI](https://pypi.org/project/pyperclip/)
  - Section: copy(), paste() functions
  - Why: Clipboard save/restore functionality

### Patterns to Follow

**Naming Conventions:**
- Files: `snake_case.py`
- Classes: `PascalCase` (e.g., `AudioRecorder`, `HotkeyManager`, `TranscriptionPipeline`)
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Config keys: `snake_case` in JSON

**Error Handling:**
```python
# Wrap external API calls in try/except
# Surface user-friendly error messages via tray notification
# Graceful degradation: if ASR fails, show error; never crash
try:
    transcript = self.provider.transcribe(audio_data, config)
except Exception as e:
    self._show_error(f"Transcription failed: {e}")
    return None
```

**Logging Pattern:**
- No API keys in logs
- Use `logging` module with INFO level for state transitions
- DEBUG level for detailed audio/hotkey events

**Config Pattern:**
```python
from pathlib import Path
import os

def get_config_path() -> Path:
    """Return path to config file in %APPDATA%."""
    appdata = os.environ.get("APPDATA", "")
    config_dir = Path(appdata) / "asr-everywhere"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.json"
```

**Singleton-like Config:**
- Load config once at app startup
- Pass config instance to components that need it
- Save immediately on settings changes

---

## IMPLEMENTATION PLAN

### Phase 1: Foundation - Configuration & Entry Point

**Goal:** Establish config management and update entry point to run the app.

**Tasks:**
1. Create `config.py` with `Config` dataclass/dict wrapper
2. Implement `get_config_path()`, `load_config()`, `save_config()`, `get_default_config()`
3. Update `__main__.py` to initialize config and launch app
4. Create `assets/` directory structure

### Phase 2: Audio Recording Subsystem

**Goal:** Implement callback-based audio recording with arbitrary duration.

**Tasks:**
1. Create `audio_recorder.py` with `AudioRecorder` class
2. Implement `start_recording()`, `stop_recording()`, `get_audio_bytes()`
3. Use `sounddevice.InputStream` with callback to queue
4. Convert recorded numpy array to WAV bytes using `soundfile`
5. Support device selection (default to system default)

### Phase 3: ASR Provider Implementation

**Goal:** Create OpenAI Whisper integration with provider abstraction.

**Tasks:**
1. Create `providers/base.py` with `ASRProvider` ABC
2. Create `providers/openai_provider.py` implementing `OpenAIProvider`
3. Implement `transcribe(audio_bytes, config) -> str`
4. Implement `list_models() -> list[str]` returning `["whisper-1", "gpt-4o-transcribe"]`
5. Create `providers/registry.py` with simple provider lookup

### Phase 4: Text Insertion

**Goal:** Implement clipboard-based text insertion at cursor position.

**Tasks:**
1. Create `text_inserter.py` with `TextInserter` class
2. Implement `save_clipboard()`, `restore_clipboard()`
3. Implement `insert_text(text, restore=True)` using pyperclip + pynput
4. Handle clipboard save/restore errors gracefully

### Phase 5: Hotkey Management

**Goal:** Register global WIN+U hotkey with toggle mode.

**Tasks:**
1. Create `hotkey_manager.py` with `HotkeyManager` class
2. Implement `register_hotkey(key, callback)` using `keyboard.add_hotkey()`
3. Implement toggle state tracking (idle ↔ recording)
4. Support hotkey removal on app exit

### Phase 6: System Tray UI

**Goal:** Create tray icon with state indicators and basic menu.

**Tasks:**
1. Create `ui/tray.py` with `TrayIcon` class
2. Implement icon creation using Pillow (colored circles)
3. Implement `set_state(state)` for idle/recording/processing icons
4. Create menu with: Status (disabled), Settings (disabled for Phase 1), Quit
5. Implement `run()` to start tray in separate thread

### Phase 7: Application Orchestrator

**Goal:** Wire all components together in the main app.

**Tasks:**
1. Create `app.py` with `ASREverywhereApp` class
2. Initialize all components in correct order
3. Implement state machine: idle → recording → processing → idle
4. Wire hotkey callback to recording toggle
5. Wire recording completion to transcription pipeline
6. Wire transcription completion to text insertion
7. Handle errors at each stage with tray notifications

### Phase 8: Testing & Validation

**Goal:** Ensure all components work correctly with mocked dependencies.

**Tasks:**
1. Create `tests/test_config.py` - config load/save/default
2. Create `tests/test_audio_recorder.py` - mock sounddevice
3. Create `tests/test_text_inserter.py` - mock pyperclip/pynput
4. Create `tests/test_providers.py` - mock OpenAI API
5. Create `tests/test_pipeline.py` - integration test with all mocks
6. Run `pytest tests/` and ensure all pass
7. Run `ruff check src/ tests/` and fix linting issues
8. Manual validation: run app, press WIN+U, dictate, verify text insertion

---

## STEP-BY-STEP TASKS

IMPORTANT: Execute every task in order, top to bottom. Each task is atomic and independently testable.

### Task Format Guidelines

Use information-dense keywords for clarity:
- **CREATE**: Make a new file
- **IMPLEMENT**: Add code to an existing file
- **UPDATE**: Modify existing code
- **ADD**: Append to existing structure
- **VALIDATE**: Test the implementation

---

### 1. CREATE `src/asr_everywhere/config.py`

Implement configuration management with JSON persistence in %APPDATA%.

```python
"""Configuration management for ASR Everywhere."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
import os
from typing import Any

logger = logging.getLogger(__name__)

CONFIG_VERSION = 1

@dataclass
class HotkeyConfig:
    """Hotkey configuration."""
    dictate: str = "win+u"
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
        with open(config_path, "r", encoding="utf-8") as f:
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
```

**Validation:** Run `python -c "from asr_everywhere.config import load_config; c = load_config(); print(c)"`

---

### 2. CREATE `src/asr_everywhere/providers/__init__.py`

```python
"""ASR providers for transcription."""

from asr_everywhere.providers.base import ASRProvider
from asr_everywhere.providers.openai_provider import OpenAIProvider

__all__ = ["ASRProvider", "OpenAIProvider"]
```

---

### 3. CREATE `src/asr_everywhere/providers/base.py`

Define abstract base class for ASR providers.

```python
"""Abstract base class for ASR providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from asr_everywhere.config import ASRConfig


@dataclass
class TranscriptionResult:
    """Result of a transcription."""
    text: str
    language: str | None = None
    duration: float | None = None


class ASRProvider(ABC):
    """Abstract base class for ASR providers."""
    
    @abstractmethod
    def transcribe(
        self, 
        audio_data: bytes, 
        config: ASRConfig,
    ) -> TranscriptionResult:
        """Transcribe audio bytes to text.
        
        Args:
            audio_data: Audio data as bytes (WAV format)
            config: ASR configuration
            
        Returns:
            TranscriptionResult with transcribed text
        """
        ...
    
    @abstractmethod
    def list_models(self) -> list[str]:
        """Return list of available models for this provider."""
        ...
```

---

### 4. CREATE `src/asr_everywhere/providers/openai_provider.py`

Implement OpenAI Whisper API integration.

```python
"""OpenAI Whisper API provider."""

from __future__ import annotations

import io
import logging
from typing import TYPE_CHECKING

from openai import OpenAI

from asr_everywhere.providers.base import ASRProvider, TranscriptionResult

if TYPE_CHECKING:
    from asr_everywhere.config import ASRConfig

logger = logging.getLogger(__name__)

# Models supported by OpenAI for transcription
OPENAI_MODELS = ["whisper-1", "gpt-4o-transcribe", "gpt-4o-mini-transcribe"]


class OpenAIProvider(ASRProvider):
    """OpenAI Whisper API provider."""
    
    def __init__(self) -> None:
        """Initialize OpenAI provider."""
        self._client: OpenAI | None = None
    
    def _get_client(self, config: ASRConfig) -> OpenAI:
        """Get or create OpenAI client."""
        if self._client is None:
            if not config.api_key:
                raise ValueError("OpenAI API key not configured")
            self._client = OpenAI(
                api_key=config.api_key,
                base_url=config.base_url,
            )
        return self._client
    
    def transcribe(
        self, 
        audio_data: bytes, 
        config: ASRConfig,
    ) -> TranscriptionResult:
        """Transcribe audio using OpenAI Whisper API."""
        client = self._get_client(config)
        
        # Create a file-like object from bytes
        audio_file = io.BytesIO(audio_data)
        audio_file.name = "audio.wav"  # OpenAI needs filename for format detection
        
        # Build transcription request
        kwargs = {
            "model": config.model,
            "file": audio_file,
        }
        
        # Add language if specified (not auto)
        if config.language and config.language != "auto":
            kwargs["language"] = config.language
        
        logger.info(f"Sending transcription request to OpenAI: model={config.model}")
        
        try:
            response = client.audio.transcriptions.create(**kwargs)
            logger.info(f"Transcription complete: {len(response.text)} chars")
            
            return TranscriptionResult(
                text=response.text,
                language=config.language if config.language != "auto" else None,
            )
        except Exception as e:
            logger.error(f"OpenAI transcription failed: {e}")
            raise
    
    def list_models(self) -> list[str]:
        """Return available OpenAI transcription models."""
        return OPENAI_MODELS.copy()
```

---

### 5. CREATE `src/asr_everywhere/providers/registry.py`

Simple provider registry for Phase 1.

```python
"""Provider registry for ASR providers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from asr_everywhere.providers.base import ASRProvider
from asr_everywhere.providers.openai_provider import OpenAIProvider

if TYPE_CHECKING:
    pass

# Registry mapping provider names to classes
PROVIDERS: dict[str, type[ASRProvider]] = {
    "openai": OpenAIProvider,
}


def get_provider(name: str) -> ASRProvider:
    """Get an instance of the specified provider.
    
    Args:
        name: Provider name (e.g., "openai")
        
    Returns:
        Instance of the provider
        
    Raises:
        ValueError: If provider name is not recognized
    """
    if name not in PROVIDERS:
        available = ", ".join(PROVIDERS.keys())
        raise ValueError(f"Unknown provider '{name}'. Available: {available}")
    
    return PROVIDERS[name]()


def list_providers() -> list[str]:
    """Return list of available provider names."""
    return list(PROVIDERS.keys())
```

---

### 6. CREATE `src/asr_everywhere/audio_recorder.py`

Implement callback-based audio recording.

```python
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
        """Start recording audio."""
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
            self._stream = sd.InputStream(
                samplerate=self._config.sample_rate,
                device=self._config.device,
                channels=self._config.channels,
                dtype="float32",
                callback=self._callback,
            )
            self._stream.start()
            logger.info("Audio stream started")
    
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
            logger.info(f"Recorded {len(audio_data)} samples ({len(audio_data) / self._config.sample_rate:.2f}s)")
            
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
    def list_devices() -> list[dict]:
        """List available audio input devices.
        
        Returns:
            List of device info dicts with 'id', 'name', 'channels'
        """
        devices = []
        for i, dev in enumerate(sd.query_devices()):
            if dev["max_input_channels"] > 0:
                devices.append({
                    "id": i,
                    "name": dev["name"],
                    "channels": dev["max_input_channels"],
                    "default": dev.get("default_samplerate", 48000),
                })
        return devices
```

---

### 7. CREATE `src/asr_everywhere/text_inserter.py`

Implement clipboard-based text insertion.

```python
"""Text insertion via clipboard and keyboard simulation."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

import pyperclip
from pynput.keyboard import Controller, Key

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class TextInserter:
    """Inserts text at cursor position via clipboard + Ctrl+V."""
    
    def __init__(self) -> None:
        """Initialize text inserter."""
        self._keyboard = Controller()
        self._saved_clipboard: str | None = None
    
    def save_clipboard(self) -> None:
        """Save current clipboard content."""
        try:
            self._saved_clipboard = pyperclip.paste()
            logger.debug("Saved clipboard content")
        except Exception as e:
            logger.warning(f"Failed to save clipboard: {e}")
            self._saved_clipboard = None
    
    def restore_clipboard(self) -> None:
        """Restore previously saved clipboard content."""
        if self._saved_clipboard is not None:
            try:
                pyperclip.copy(self._saved_clipboard)
                logger.debug("Restored clipboard content")
            except Exception as e:
                logger.warning(f"Failed to restore clipboard: {e}")
        self._saved_clipboard = None
    
    def insert_text(self, text: str, restore_clipboard: bool = True) -> bool:
        """Insert text at cursor position.
        
        Args:
            text: Text to insert
            restore_clipboard: Whether to restore clipboard after insertion
            
        Returns:
            True if insertion succeeded
        """
        if not text:
            logger.warning("No text to insert")
            return False
        
        # Save clipboard before overwriting
        self.save_clipboard()
        
        try:
            # Copy text to clipboard
            pyperclip.copy(text)
            logger.debug(f"Copied {len(text)} chars to clipboard")
            
            # Small delay to ensure clipboard is updated
            time.sleep(0.05)
            
            # Simulate Ctrl+V
            with self._keyboard.pressed(Key.ctrl):
                self._keyboard.press("v")
                self._keyboard.release("v")
            
            logger.info(f"Inserted text via Ctrl+V: {len(text)} chars")
            
            # Restore clipboard if requested
            if restore_clipboard:
                # Small delay before restoring
                time.sleep(0.1)
                self.restore_clipboard()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to insert text: {e}")
            # Try to restore clipboard on error
            self.restore_clipboard()
            return False
```

---

### 8. CREATE `src/asr_everywhere/hotkey_manager.py`

Implement global hotkey registration.

```python
"""Global hotkey management using keyboard library."""

from __future__ import annotations

import logging
from typing import Callable

import keyboard

logger = logging.getLogger(__name__)


class HotkeyManager:
    """Manages global hotkey registration."""
    
    def __init__(self) -> None:
        """Initialize hotkey manager."""
        self._registered: dict[str, Callable[[], None]] = {}
    
    def register_hotkey(
        self, 
        hotkey: str, 
        callback: Callable[[], None],
    ) -> None:
        """Register a global hotkey.
        
        Args:
            hotkey: Hotkey string (e.g., "win+u", "ctrl+alt+r")
            callback: Function to call when hotkey is pressed
        """
        if hotkey in self._registered:
            logger.warning(f"Hotkey '{hotkey}' already registered, replacing")
            self.unregister_hotkey(hotkey)
        
        keyboard.add_hotkey(hotkey, callback)
        self._registered[hotkey] = callback
        logger.info(f"Registered hotkey: {hotkey}")
    
    def unregister_hotkey(self, hotkey: str) -> None:
        """Unregister a hotkey.
        
        Args:
            hotkey: Hotkey string to unregister
        """
        if hotkey in self._registered:
            keyboard.remove_hotkey(hotkey)
            del self._registered[hotkey]
            logger.info(f"Unregistered hotkey: {hotkey}")
    
    def unregister_all(self) -> None:
        """Unregister all hotkeys."""
        for hotkey in list(self._registered.keys()):
            self.unregister_hotkey(hotkey)
        logger.info("Unregistered all hotkeys")
    
    def is_pressed(self, hotkey: str) -> bool:
        """Check if a hotkey is currently pressed.
        
        Args:
            hotkey: Hotkey string to check
            
        Returns:
            True if the hotkey combination is pressed
        """
        return keyboard.is_pressed(hotkey)
```

---

### 9. CREATE `src/asr_everywhere/ui/__init__.py`

```python
"""UI components for ASR Everywhere."""

from asr_everywhere.ui.tray import TrayIcon

__all__ = ["TrayIcon"]
```

---

### 10. CREATE `src/asr_everywhere/ui/tray.py`

Implement System Tray icon with state management.

```python
"""System Tray icon using pystray."""

from __future__ import annotations

import logging
import threading
from enum import Enum
from pathlib import Path
from typing import Callable

from PIL import Image, ImageDraw
import pystray
from pystray import Menu, MenuItem

logger = logging.getLogger(__name__)


class TrayState(Enum):
    """Tray icon states."""
    IDLE = "idle"
    RECORDING = "recording"
    PROCESSING = "processing"


class TrayIcon:
    """System Tray icon with state indicators."""
    
    def __init__(
        self, 
        on_quit: Callable[[], None],
        on_settings: Callable[[], None] | None = None,
    ) -> None:
        """Initialize tray icon.
        
        Args:
            on_quit: Callback for quit action
            on_settings: Callback for settings action (optional for Phase 1)
        """
        self._on_quit = on_quit
        self._on_settings = on_settings
        self._state = TrayState.IDLE
        self._icon: pystray.Icon | None = None
        self._thread: threading.Thread | None = None
        
        # Create icons for each state
        self._icons = {
            TrayState.IDLE: self._create_icon("#4CAF50"),      # Green
            TrayState.RECORDING: self._create_icon("#F44336"), # Red
            TrayState.PROCESSING: self._create_icon("#FF9800"), # Orange
        }
    
    def _create_icon(self, color: str) -> Image.Image:
        """Create a simple colored circle icon.
        
        Args:
            color: Hex color string
            
        Returns:
            PIL Image
        """
        size = 64
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw filled circle
        margin = 8
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=color,
        )
        
        return image
    
    def _create_menu(self) -> Menu:
        """Create tray context menu."""
        items = [
            MenuItem(
                lambda: f"Status: {self._state.value}",
                lambda: None,
                enabled=False,
            ),
            Menu.SEPARATOR,
        ]
        
        if self._on_settings:
            items.append(MenuItem("Settings", self._on_settings))
        
        items.extend([
            Menu.SEPARATOR,
            MenuItem("Quit", self._on_quit),
        ])
        
        return Menu(*items)
    
    def set_state(self, state: TrayState) -> None:
        """Update tray icon state.
        
        Args:
            state: New state to display
        """
        self._state = state
        if self._icon:
            self._icon.icon = self._icons[state]
            self._icon.title = f"ASR Everywhere - {state.value.title()}"
            # Update menu to show current status
            self._icon.update_menu()
        logger.debug(f"Tray state changed to: {state.value}")
    
    def show_notification(self, title: str, message: str) -> None:
        """Show a notification balloon.
        
        Args:
            title: Notification title
            message: Notification message
        """
        if self._icon:
            self._icon.notify(message, title)
    
    def _run_icon(self) -> None:
        """Run the tray icon (called in thread)."""
        self._icon = pystray.Icon(
            "asr_everywhere",
            icon=self._icons[TrayState.IDLE],
            title="ASR Everywhere",
            menu=self._create_menu(),
        )
        self._icon.run()
    
    def start(self) -> None:
        """Start the tray icon in a background thread."""
        if self._thread and self._thread.is_alive():
            logger.warning("Tray icon already running")
            return
        
        self._thread = threading.Thread(target=self._run_icon, daemon=True)
        self._thread.start()
        logger.info("Tray icon started")
    
    def stop(self) -> None:
        """Stop the tray icon."""
        if self._icon:
            self._icon.stop()
        if self._thread:
            self._thread.join(timeout=2.0)
        logger.info("Tray icon stopped")
```

---

### 11. CREATE `src/asr_everywhere/transcription_pipeline.py`

Implement the core pipeline orchestrating all components.

```python
"""Transcription pipeline: record → transcribe → insert."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from asr_everywhere.audio_recorder import AudioRecorder
from asr_everywhere.providers.registry import get_provider
from asr_everywhere.text_inserter import TextInserter

if TYPE_CHECKING:
    from asr_everywhere.config import Config
    from asr_everywhere.ui.tray import TrayIcon, TrayState

logger = logging.getLogger(__name__)


class TranscriptionPipeline:
    """Orchestrates the transcription workflow."""
    
    def __init__(
        self,
        config: Config,
        recorder: AudioRecorder,
        inserter: TextInserter,
        tray: TrayIcon,
    ) -> None:
        """Initialize pipeline.
        
        Args:
            config: Application configuration
            recorder: Audio recorder instance
            inserter: Text inserter instance
            tray: Tray icon for status updates
        """
        self._config = config
        self._recorder = recorder
        self._inserter = inserter
        self._tray = tray
        self._processing = False
    
    def toggle_recording(self) -> None:
        """Toggle recording state (called by hotkey)."""
        if self._processing:
            logger.info("Ignoring toggle during processing")
            return
        
        if self._recorder.is_recording:
            self._stop_and_transcribe()
        else:
            self._start_recording()
    
    def _start_recording(self) -> None:
        """Start audio recording."""
        from asr_everywhere.ui.tray import TrayState
        self._tray.set_state(TrayState.RECORDING)
        self._recorder.start_recording()
    
    def _stop_and_transcribe(self) -> None:
        """Stop recording and process audio."""
        from asr_everywhere.ui.tray import TrayState
        
        # Stop recording
        audio_data = self._recorder.stop_recording()
        
        if not audio_data:
            logger.warning("No audio recorded")
            self._tray.set_state(TrayState.IDLE)
            return
        
        # Update state
        self._tray.set_state(TrayState.PROCESSING)
        self._processing = True
        
        try:
            # Get ASR provider
            provider = get_provider(self._config.asr.provider)
            
            # Transcribe
            logger.info("Starting transcription")
            result = provider.transcribe(audio_data, self._config.asr)
            
            if result.text:
                logger.info(f"Transcription: {result.text[:100]}...")
                
                # Insert text
                success = self._inserter.insert_text(
                    result.text,
                    restore_clipboard=self._config.clipboard_restore,
                )
                
                if success:
                    self._tray.show_notification(
                        "Transcription Complete",
                        f"Inserted: {result.text[:50]}..." if len(result.text) > 50 else result.text,
                    )
                else:
                    self._tray.show_notification(
                        "Insertion Failed",
                        "Text copied to clipboard",
                    )
            else:
                self._tray.show_notification(
                    "Transcription Failed",
                    "No text returned from ASR",
                )
                
        except Exception as e:
            logger.error(f"Transcription pipeline error: {e}")
            self._tray.show_notification("Error", str(e))
        
        finally:
            self._processing = False
            self._tray.set_state(TrayState.IDLE)
```

---

### 12. CREATE `src/asr_everywhere/app.py`

Main application orchestrator.

```python
"""Main application orchestrator."""

from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING

from asr_everywhere.audio_recorder import AudioRecorder
from asr_everywhere.config import Config, load_config
from asr_everywhere.hotkey_manager import HotkeyManager
from asr_everywhere.text_inserter import TextInserter
from asr_everywhere.transcription_pipeline import TranscriptionPipeline
from asr_everywhere.ui.tray import TrayIcon

if TYPE_CHECKING:
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class ASREverywhereApp:
    """Main application class."""
    
    def __init__(self) -> None:
        """Initialize application."""
        self._config: Config | None = None
        self._tray: TrayIcon | None = None
        self._recorder: AudioRecorder | None = None
        self._inserter: TextInserter | None = None
        self._hotkey_manager: HotkeyManager | None = None
        self._pipeline: TranscriptionPipeline | None = None
        self._running = False
    
    def initialize(self) -> bool:
        """Initialize all components.
        
        Returns:
            True if initialization succeeded
        """
        try:
            # Load config
            self._config = load_config()
            
            # Create components
            self._tray = TrayIcon(on_quit=self.quit)
            self._recorder = AudioRecorder(self._config.audio)
            self._inserter = TextInserter()
            self._hotkey_manager = HotkeyManager()
            
            # Create pipeline
            self._pipeline = TranscriptionPipeline(
                config=self._config,
                recorder=self._recorder,
                inserter=self._inserter,
                tray=self._tray,
            )
            
            # Register hotkey
            self._hotkey_manager.register_hotkey(
                self._config.hotkey.dictate,
                self._pipeline.toggle_recording,
            )
            
            logger.info("Application initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            return False
    
    def run(self) -> None:
        """Run the application."""
        if not self.initialize():
            sys.exit(1)
        
        self._running = True
        
        # Start tray icon
        self._tray.start()
        
        logger.info("ASR Everywhere started - press WIN+U to dictate")
        
        # Keep running until quit
        try:
            # Use keyboard.wait() to keep the app running
            # This is more reliable than a busy loop
            keyboard.wait()
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            self.quit()
    
    def quit(self) -> None:
        """Quit the application."""
        if not self._running:
            return
        
        logger.info("Shutting down...")
        
        # Stop recording if active
        if self._recorder and self._recorder.is_recording:
            self._recorder.stop_recording()
        
        # Unregister hotkeys
        if self._hotkey_manager:
            self._hotkey_manager.unregister_all()
        
        # Stop tray
        if self._tray:
            self._tray.stop()
        
        self._running = False
        logger.info("Application stopped")


def main() -> int:
    """Main entry point."""
    import keyboard  # For keyboard.wait()
    
    app = ASREverywhereApp()
    app.run()
    return 0
```

---

### 13. UPDATE `src/asr_everywhere/__main__.py`

Replace stub with actual app launch.

```python
"""Entry point for asr-everywhere."""

from asr_everywhere.app import main

if __name__ == "__main__":
    import sys
    sys.exit(main())
```

---

### 14. CREATE `assets/` directory and placeholder icons

Create simple colored circle icons using Python/Pillow (can be generated at runtime or saved as actual .ico files).

For Phase 1, we'll generate icons dynamically in the `TrayIcon` class, so no static files needed initially. Create the directory for future use:

```
assets/
├── .gitkeep
```

---

### 15. CREATE `tests/test_config.py`

```python
"""Tests for configuration management."""

import json
import os
from pathlib import Path
from unittest import mock

import pytest

from asr_everywhere.config import (
    Config,
    HotkeyConfig,
    ASRConfig,
    AudioConfig,
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
    assert config.hotkey.dictate == "win+u"
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
        assert config.hotkey.dictate == "win+u"
        
        # Should have created the file
        assert config_path.exists()
```

---

### 16. CREATE `tests/test_audio_recorder.py`

```python
"""Tests for audio recorder."""

import numpy as np
import pytest
from unittest import mock

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
```

---

### 17. CREATE `tests/test_text_inserter.py`

```python
"""Tests for text inserter."""

import pytest
from unittest import mock

from asr_everywhere.text_inserter import TextInserter


@pytest.fixture
def inserter():
    """Create inserter instance."""
    return TextInserter()


def test_insert_text_success(inserter):
    """Test successful text insertion."""
    with mock.patch("asr_everywhere.text_inserter.pyperclip") as mock_clip, \
         mock.patch("asr_everywhere.text_inserter.time.sleep"):
        
        mock_clip.paste.return_value = "old clipboard"
        
        result = inserter.insert_text("Hello world", restore_clipboard=True)
        
        assert result is True
        mock_clip.copy.assert_called()
        # Should have restored clipboard
        assert mock_clip.copy.call_count >= 2


def test_insert_text_no_restore(inserter):
    """Test text insertion without clipboard restore."""
    with mock.patch("asr_everywhere.text_inserter.pyperclip") as mock_clip, \
         mock.patch("asr_everywhere.text_inserter.time.sleep"):
        
        mock_clip.paste.return_value = "old clipboard"
        
        result = inserter.insert_text("Hello world", restore_clipboard=False)
        
        assert result is True
        # Should only copy once (the new text)
        assert mock_clip.copy.call_count == 1


def test_insert_empty_text_fails(inserter):
    """Test inserting empty text returns False."""
    result = inserter.insert_text("")
    assert result is False


def test_save_restore_clipboard(inserter):
    """Test clipboard save and restore."""
    with mock.patch("asr_everywhere.text_inserter.pyperclip") as mock_clip:
        
        mock_clip.paste.return_value = "saved content"
        
        inserter.save_clipboard()
        assert inserter._saved_clipboard == "saved content"
        
        inserter.restore_clipboard()
        mock_clip.copy.assert_called_with("saved content")
```

---

### 18. CREATE `tests/test_providers.py`

```python
"""Tests for ASR providers."""

import pytest
from unittest import mock

from asr_everywhere.config import ASRConfig
from asr_everywhere.providers.openai_provider import OpenAIProvider
from asr_everywhere.providers.registry import get_provider, list_providers


@pytest.fixture
def asr_config():
    """Create test ASR config."""
    return ASRConfig(
        provider="openai",
        model="whisper-1",
        api_key="test-key",
    )


def test_list_models():
    """Test listing available models."""
    provider = OpenAIProvider()
    models = provider.list_models()
    
    assert "whisper-1" in models
    assert "gpt-4o-transcribe" in models


def test_transcribe_success(asr_config):
    """Test successful transcription."""
    provider = OpenAIProvider()
    
    with mock.patch("asr_everywhere.providers.openai_provider.OpenAI") as mock_openai:
        mock_client = mock.MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = mock.MagicMock()
        mock_response.text = "Hello world"
        mock_client.audio.transcriptions.create.return_value = mock_response
        
        result = provider.transcribe(b"fake audio data", asr_config)
        
        assert result.text == "Hello world"
        mock_client.audio.transcriptions.create.assert_called_once()


def test_transcribe_missing_api_key():
    """Test transcription fails without API key."""
    provider = OpenAIProvider()
    config = ASRConfig(api_key="")
    
    with pytest.raises(ValueError, match="API key"):
        provider.transcribe(b"audio", config)


def test_get_provider():
    """Test provider registry."""
    provider = get_provider("openai")
    assert isinstance(provider, OpenAIProvider)


def test_get_provider_unknown():
    """Test getting unknown provider raises error."""
    with pytest.raises(ValueError, match="Unknown provider"):
        get_provider("unknown_provider")


def test_list_providers():
    """Test listing available providers."""
    providers = list_providers()
    assert "openai" in providers
```

---

### 19. CREATE `tests/test_pipeline.py`

```python
"""Tests for transcription pipeline."""

import pytest
from unittest import mock

from asr_everywhere.config import Config
from asr_everywhere.transcription_pipeline import TranscriptionPipeline


@pytest.fixture
def mock_config():
    """Create mock config."""
    config = mock.MagicMock(spec=Config)
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
```

---

### 20. VALIDATE: Run tests and linting

```bash
# Run tests
pytest tests/ -v

# Run linting
ruff check src/ tests/

# Run formatting check
ruff format --check src/ tests/
```

---

### 21. MANUAL VALIDATION: End-to-end test

1. Install app: `pip install -e .`
2. Run: `python -m asr_everywhere`
3. Verify tray icon appears in system tray
4. Press WIN+U - verify tray icon turns red (recording)
5. Speak into microphone
6. Press WIN+U again - verify tray icon turns orange (processing)
7. Verify transcribed text appears at cursor position
8. Verify tray icon returns to green (idle)

---

## VALIDATION CHECKLIST

Before marking Phase 1 complete, verify:

- [ ] `pip install -e .` succeeds without errors
- [ ] `python -m asr_everywhere` launches without crashing
- [ ] Tray icon appears in Windows system tray
- [ ] WIN+U hotkey toggles recording state
- [ ] Tray icon changes color during recording (red)
- [ ] Tray icon changes color during processing (orange)
- [ ] Transcribed text appears at cursor position in Notepad
- [ ] Clipboard is restored after insertion (if configured)
- [ ] `pytest tests/` passes all tests
- [ ] `ruff check src/ tests/` shows no errors
- [ ] `ruff format --check src/ tests/` shows no issues
- [ ] Config file created at `%APPDATA%/asr-everywhere/config.json`
- [ ] API key can be set in config and is used for transcription
- [ ] Error messages shown via tray notification on failures

---

## KNOWN LIMITATIONS (Phase 1)

- Only OpenAI provider supported (multi-provider in Phase 2)
- Single hardcoded hotkey WIN+U (configurable in Phase 2)
- No settings UI (Phase 2)
- No LLM post-processing (Phase 3)
- No dictionary support (Phase 3)
- No microphone selection (Phase 2)
- No language selection (Phase 2)

---

## FUTURE ENHANCEMENTS (Post-Phase 1)

- Phase 2: Multi-provider support, settings UI, configurable hotkeys
- Phase 3: LLM post-processing, dictionary
- Phase 4: Polish, error handling, documentation, PyPI packaging
