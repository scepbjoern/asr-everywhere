# Feature: Phase 2 - Settings UI & Multi-Provider Support

The following plan should be complete, but it's important that you validate documentation and codebase patterns and task sanity before you start implementing.

Pay special attention to naming of existing utils types and models. Import from the right files etc.

## Feature Description

Implement a tkinter-based Settings GUI window accessible from the System Tray, enabling users to configure ASR providers, API keys, hotkeys, audio devices, and language settings without manually editing JSON. This phase also extends the provider system to support OpenAI-compatible endpoints (Together.ai, Hugging Face, local APIs).

**New Features Added:**
- **Model Configuration:** Models are now configurable per provider in `config.json` with price per audio hour
- **Notification Toggle:** Optional notification after successful transcription (configurable in settings)
- **Tray Model Display:** Current model and price shown in tray icon right-click menu
- **OpenRouter Removed:** OpenRouter provider removed (no ASR models available)

## User Story

As a Windows user
I want to configure ASR providers, hotkeys, and audio settings through a graphical interface
So that I can customize the application without editing JSON files manually

## Problem Statement

Phase 1 delivered a functional dictation pipeline but requires users to edit JSON configuration manually. Users cannot:
- Switch between ASR providers without editing config files
- Configure API keys through a secure UI (masked input)
- Select microphone devices from available options
- Customize hotkeys through a user-friendly interface
- Choose language settings (German/English/Auto)

This creates friction for non-technical users and increases setup errors.

## Solution Statement

Build a tkinter Settings window with tabbed interface containing:
1. **ASR Provider tab** - Provider dropdown, API key (masked), model selection, base URL
2. **Hotkeys tab** - Hotkey configuration with capture functionality, mode selection (toggle/push-to-talk)
3. **Audio tab** - Microphone device dropdown, sample rate display
4. **Language tab** - Language selection (DE/EN/Auto), clipboard behavior

Additionally, extend the provider system to support OpenAI-compatible endpoints through a configurable `base_url`.

## Feature Metadata

**Feature Type**: Enhancement
**Estimated Complexity**: Medium
**Primary Systems Affected**:
- UI subsystem (new `settings_window.py`)
- Provider system (new `OpenAICompatProvider`)
- Configuration management (schema extension)
- System Tray (add Settings menu callback)
- Hotkey manager (support reconfiguration)

**Dependencies**:
- `tkinter` (stdlib) - GUI framework
- `keyboard` (existing) - Hotkey capture for settings
- `sounddevice` (existing) - Device enumeration

---

## CONTEXT REFERENCES

### Relevant Codebase Files IMPORTANT: YOU MUST READ THESE FILES BEFORE IMPLEMENTING!

- `docs/PRD.md` (lines 324-343) - Settings UI sections and requirements
- `docs/PRD.md` (lines 393-446) - Full config schema with multi-provider structure
- `docs/PRD.md` (lines 269-279) - Supported providers table
- `docs/PRD.md` (lines 230-239) - Hotkey system specifications
- `.windsurf/rules/main-rules.md` (lines 1-203) - Project conventions, naming, architecture
- `src/asr_everywhere/config.py` (lines 1-110) - Current config implementation to extend
- `src/asr_everywhere/providers/base.py` (lines 22-46) - ASRProvider interface
- `src/asr_everywhere/providers/openai_provider.py` (lines 22-79) - Pattern for provider implementation
- `src/asr_everywhere/providers/registry.py` (lines 1-41) - Provider registry to extend
- `src/asr_everywhere/ui/tray.py` (lines 28-43, 96-97) - TrayIcon constructor and settings callback
- `src/asr_everywhere/hotkey_manager.py` (lines 20-37) - Hotkey registration pattern
- `src/asr_everywhere/audio_recorder.py` (lines 133-151) - `list_devices()` static method
- `tests/conftest.py` (lines 1-169) - Test fixtures pattern

### New Files to Create

```
src/asr_everywhere/
├── ui/
│   └── settings_window.py      # SettingsWindow class (tkinter Toplevel)
├── providers/
│   └── openai_compat.py        # OpenAICompatProvider for Together/HF/OpenRouter/local
└── llm/                        # Placeholder for Phase 3 (empty __init__.py)

tests/
├── test_settings_window.py     # UI component tests
└── test_openai_compat.py       # OpenAI-compatible provider tests
```

### Files to Modify

- `src/asr_everywhere/config.py` - Extend config schema for multi-provider support
- `src/asr_everywhere/providers/registry.py` - Register new providers
- `src/asr_everywhere/ui/tray.py` - Wire up settings callback
- `src/asr_everywhere/ui/__init__.py` - Export SettingsWindow
- `src/asr_everywhere/app.py` - Pass settings callback to tray, handle config reload
- `config.example.json` - Update to show multi-provider structure

### Relevant Documentation YOU SHOULD READ BEFORE IMPLEMENTING!

- [Tkinter Validation Tutorial](https://www.pythontutorial.net/tkinter/tkinter-validation/)
  - Section: validatecommand for entry validation
  - Why: API key format validation, hotkey format validation

- [Python GUIs - Input Validation](https://www.pythonguis.com/tutorials/input-validation-tkinter/)
  - Section: Common validation strategies
  - Why: Best practices for form validation in dialogs

- [tkinter.ttk Documentation](https://docs.python.org/3/library/tkinter.ttk.html)
  - Section: Notebook, Combobox, Entry widgets
  - Why: Tabbed interface and dropdown widgets

- [Stack Overflow - Scrollbar in Notebook](https://stackoverflow.com/questions/58045626/scrollbar-in-tkinter-notebook-frames)
  - Section: Scrollable frame implementation
  - Why: Settings may need scrolling for smaller screens

- [OpenAI API - Audio Transcriptions](https://platform.openai.com/docs/guides/speech-to-text)
  - Section: API parameters
  - Why: Understanding Whisper API parameters for provider config

### Patterns to Follow

**Naming Conventions:**
- Files: `snake_case.py` (e.g., `settings_window.py`, `openai_compat.py`)
- Classes: `PascalCase` (e.g., `SettingsWindow`, `OpenAICompatProvider`)
- Functions/methods: `snake_case`
- Tkinter variables: `_var` suffix (e.g., `self._provider_var`)

**Error Handling:**
```python
# Wrap external API calls in try/except
# Show user-friendly error via messagebox
try:
    result = provider.transcribe(audio_data, config)
except Exception as e:
    logger.error(f"Transcription failed: {e}")
    messagebox.showerror("Error", f"Failed to test provider: {e}")
```

**Logging Pattern:**
```python
import logging
logger = logging.getLogger(__name__)

# No API keys in logs - mask sensitive data
logger.info(f"Provider changed to: {provider_name}")
# NOT: logger.info(f"API key: {api_key}")  # NEVER do this
```

**Config Pattern:**
```python
from asr_everywhere.config import Config, save_config

# Load config once at window init
self._config = load_config()

# Save immediately on user action
def _on_save(self):
    save_config(self._config)
    logger.info("Configuration saved")
```

**Tkinter Window Pattern:**
```python
import tkinter as tk
from tkinter import ttk, messagebox

class SettingsWindow:
    def __init__(self, parent: tk.Tk | None, config: Config, on_save: Callable[[], None]):
        self._window = tk.Toplevel(parent)
        self._window.title("ASR Everywhere - Settings")
        self._window.geometry("500x400")
        self._config = config
        self._on_save = on_save
        
        self._create_widgets()
    
    def show(self) -> None:
        """Show the settings window."""
        self._window.deiconify()
        self._window.wait_window()
```

---

## IMPLEMENTATION PLAN

### Phase 1: Extend Configuration Schema

**Goal:** Update config dataclasses to support multi-provider structure per PRD.

**Tasks:**
1. Add `ProviderConfig` dataclass with `api_key` and `base_url` fields
2. Add `providers: dict[str, ProviderConfig]` to `ASRConfig`
3. Update `load_config()` to handle nested provider configs
4. Update `save_config()` to persist provider configs
5. Update `config.example.json` with multi-provider example

### Phase 2: Create OpenAI-Compatible Provider

**Goal:** Implement generic provider for Together.ai, HF, OpenRouter, local APIs.

**Tasks:**
1. Create `providers/openai_compat.py` with `OpenAICompatProvider` class
2. Inherit from `ASRProvider` abstract base class
3. Implement `transcribe()` using configurable `base_url`
4. Implement `list_models()` returning common Whisper variants
5. Register provider in `registry.py` for: together, huggingface, openrouter, local

### Phase 3: Create Settings Window Foundation

**Goal:** Build basic tkinter window structure with tabbed interface.

**Tasks:**
1. Create `ui/settings_window.py` with `SettingsWindow` class
2. Use `ttk.Notebook` for tabbed interface
3. Create placeholder tabs: ASR, Hotkeys, Audio, Language
4. Add Save/Cancel buttons with proper layout
5. Wire up window close behavior

### Phase 4: Implement ASR Provider Tab

**Goal:** Build UI for provider selection and API key configuration.

**Tasks:**
1. Create provider dropdown (`ttk.Combobox`) populated from `list_providers()`
2. Create API key entry with `show="*"` for masking
3. Create model dropdown populated dynamically based on provider
4. Create base URL entry (visible only for "local" provider)
5. Add "Test Connection" button with validation
6. Bind provider change to update model list and visibility

### Phase 5: Implement Hotkeys Tab

**Goal:** Build UI for hotkey configuration with capture functionality.

**Tasks:**
1. Create hotkey entry field with "Capture" button
2. Implement hotkey capture using `keyboard` library (listen for next key combo)
3. Create mode radio buttons: Toggle / Push-to-Talk
4. Add validation for hotkey format
5. Show warning if hotkey conflicts with existing registration

### Phase 6: Implement Audio Tab

**Goal:** Build UI for microphone device selection.

**Tasks:**
1. Create device dropdown populated from `AudioRecorder.list_devices()`
2. Show device name and channels in dropdown
3. Add "Refresh Devices" button
4. Handle case when no devices available

### Phase 7: Implement Language Tab

**Goal:** Build UI for language and clipboard settings.

**Tasks:**
1. Create language dropdown: Auto-detect, German, English
2. Create clipboard behavior radio buttons: Restore / Keep
3. Simple layout, no complex logic needed

### Phase 8: Wire Settings to Application

**Goal:** Connect Settings window to System Tray and handle config reload.

**Tasks:**
1. Update `TrayIcon` to accept `on_settings` callback
2. Create settings callback in `ASREverywhereApp` that opens SettingsWindow
3. Handle config reload after save (re-register hotkeys, update provider)
4. Pass `on_save` callback to SettingsWindow for hotkey re-registration

### Phase 9: Testing & Validation

**Goal:** Ensure all components work correctly with mocked dependencies.

**Tasks:**
1. Create `tests/test_openai_compat.py` - mock OpenAI client, test transcription
2. Create `tests/test_settings_window.py` - test UI creation, validation
3. Add integration test for config save/load with new schema
4. Run `pytest tests/` and ensure all pass
5. Run `ruff check src/ tests/` and fix linting issues
6. Manual validation: open settings, change provider, save, verify dictation works

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

### 1. UPDATE `src/asr_everywhere/config.py` - Extend Configuration Schema

Add multi-provider support to configuration.

```python
# Add new dataclass after ASRConfig:

@dataclass
class ProviderConfig:
    """Configuration for a specific ASR provider."""
    
    api_key: str = ""
    base_url: str = ""

# Update ASRConfig to include providers dict:

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
```

Update `load_config()` to parse nested provider configs:

```python
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
        
        # Parse provider configs
        providers_data = data.get("asr", {}).get("providers", {})
        providers = {
            name: ProviderConfig(**pcfg) 
            for name, pcfg in providers_data.items()
        }
        
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
        )
        logger.info(f"Loaded config from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Failed to load config: {e}, using defaults")
        config = Config()
        config.asr.providers = _get_default_providers()
        return config


def _get_default_providers() -> dict[str, ProviderConfig]:
    """Get default provider configurations."""
    return {
        "openai": ProviderConfig(
            api_key="",
            base_url="https://api.openai.com/v1",
        ),
        "together": ProviderConfig(
            api_key="",
            base_url="https://api.together.xyz/v1",
        ),
        "huggingface": ProviderConfig(
            api_key="",
            base_url="https://api-inference.huggingface.co/v1",
        ),
        "openrouter": ProviderConfig(
            api_key="",
            base_url="https://openrouter.ai/api/v1",
        ),
        "local": ProviderConfig(
            api_key="",
            base_url="http://localhost:11434/v1",
        ),
    }
```

**Validation:** Run `python -c "from asr_everywhere.config import load_config; c = load_config(); print(c.asr.providers)"`

---

### 2. CREATE `src/asr_everywhere/providers/openai_compat.py`

Implement OpenAI-compatible provider for Together.ai, HF, OpenRouter, local APIs.

```python
"""OpenAI-compatible API provider (Together.ai, HuggingFace, OpenRouter, local)."""

from __future__ import annotations

import io
import logging
from typing import TYPE_CHECKING

from openai import OpenAI

from asr_everywhere.providers.base import ASRProvider, TranscriptionResult

if TYPE_CHECKING:
    from asr_everywhere.config import ASRConfig

logger = logging.getLogger(__name__)

# Common models available on OpenAI-compatible endpoints
COMPAT_MODELS = ["whisper-1"]  # Most compatible endpoints support whisper-1


class OpenAICompatProvider(ASRProvider):
    """Generic OpenAI-compatible API provider.
    
    Works with Together.ai, Hugging Face Inference, OpenRouter, 
    and local APIs (Ollama, LibreChat).
    """

    def __init__(self, provider_name: str = "compat") -> None:
        """Initialize OpenAI-compatible provider.
        
        Args:
            provider_name: Name for logging purposes
        """
        self._provider_name = provider_name
        self._client: OpenAI | None = None

    def _get_client(self, config: ASRConfig) -> OpenAI:
        """Get or create OpenAI client with provider-specific base_url."""
        if self._client is None:
            api_key = config.get_api_key()
            base_url = config.get_base_url()
            
            if not api_key and "localhost" not in base_url:
                raise ValueError(f"{self._provider_name} API key not configured")
            
            self._client = OpenAI(
                api_key=api_key or "not-needed",  # Some local APIs don't need key
                base_url=base_url,
            )
        return self._client

    def transcribe(
        self,
        audio_data: bytes,
        config: ASRConfig,
    ) -> TranscriptionResult:
        """Transcribe audio using OpenAI-compatible API."""
        client = self._get_client(config)

        # Create a file-like object from bytes
        audio_file = io.BytesIO(audio_data)
        audio_file.name = "audio.wav"

        # Build transcription request
        kwargs = {
            "model": config.model,
            "file": audio_file,
        }

        # Add language if specified (not auto)
        if config.language and config.language != "auto":
            kwargs["language"] = config.language

        logger.info(
            f"Sending transcription request to {self._provider_name}: "
            f"model={config.model}, base_url={config.get_base_url()}"
        )

        try:
            response = client.audio.transcriptions.create(**kwargs)
            logger.info(f"Transcription complete: {len(response.text)} chars")

            return TranscriptionResult(
                text=response.text,
                language=config.language if config.language != "auto" else None,
            )
        except Exception as e:
            logger.error(f"{self._provider_name} transcription failed: {e}")
            raise

    def list_models(self) -> list[str]:
        """Return available models for this provider."""
        return COMPAT_MODELS.copy()
```

**Validation:** Run `python -c "from asr_everywhere.providers.openai_compat import OpenAICompatProvider; p = OpenAICompatProvider('test'); print(p.list_models())"`

---

### 3. UPDATE `src/asr_everywhere/providers/registry.py`

Register all OpenAI-compatible providers.

```python
"""Provider registry for ASR providers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from asr_everywhere.providers.base import ASRProvider
from asr_everywhere.providers.openai_provider import OpenAIProvider
from asr_everywhere.providers.openai_compat import OpenAICompatProvider

if TYPE_CHECKING:
    pass

# Registry mapping provider names to classes
PROVIDERS: dict[str, type[ASRProvider]] = {
    "openai": OpenAIProvider,
    "together": lambda: OpenAICompatProvider("together"),
    "huggingface": lambda: OpenAICompatProvider("huggingface"),
    "openrouter": lambda: OpenAICompatProvider("openrouter"),
    "local": lambda: OpenAICompatProvider("local"),
}


def get_provider(name: str) -> ASRProvider:
    """Get an instance of the specified provider.
    
    Args:
        name: Provider name (e.g., "openai", "together", "local")
        
    Returns:
        Instance of the provider
        
    Raises:
        ValueError: If provider name is not recognized
    """
    if name not in PROVIDERS:
        available = ", ".join(PROVIDERS.keys())
        raise ValueError(f"Unknown provider '{name}'. Available: {available}")

    provider_class = PROVIDERS[name]
    # Handle lambda factories
    if callable(provider_class) and not isinstance(provider_class, type):
        return provider_class()
    return provider_class()


def list_providers() -> list[str]:
    """Return list of available provider names."""
    return list(PROVIDERS.keys())


def get_provider_models(provider_name: str) -> list[str]:
    """Get available models for a provider.
    
    Args:
        provider_name: Name of the provider
        
    Returns:
        List of model names
    """
    provider = get_provider(provider_name)
    return provider.list_models()
```

**Validation:** Run `python -c "from asr_everywhere.providers.registry import list_providers; print(list_providers())"`

---

### 4. CREATE `src/asr_everywhere/ui/settings_window.py`

Implement the Settings window with tabbed interface.

```python
"""Settings window using tkinter."""

from __future__ import annotations

import logging
import tkinter as tk
from tkinter import messagebox, ttk
from collections.abc import Callable
from typing import TYPE_CHECKING

from asr_everywhere.audio_recorder import AudioRecorder
from asr_everywhere.config import Config, save_config
from asr_everywhere.providers.registry import get_provider_models, list_providers

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class SettingsWindow:
    """Settings window for configuring ASR Everywhere."""

    def __init__(
        self,
        parent: tk.Tk | None,
        config: Config,
        on_save: Callable[[], None],
    ) -> None:
        """Initialize settings window.
        
        Args:
            parent: Parent window (or None for standalone)
            config: Current configuration
            on_save: Callback to invoke after saving config
        """
        self._config = config
        self._on_save = on_save
        self._hotkey_capturing = False
        
        # Create window
        self._window = tk.Toplevel(parent)
        self._window.title("ASR Everywhere - Settings")
        self._window.geometry("550x450")
        self._window.resizable(True, True)
        
        # Create main container
        self._main_frame = ttk.Frame(self._window, padding="10")
        self._main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook (tabs)
        self._notebook = ttk.Notebook(self._main_frame)
        self._notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create tabs
        self._create_asr_tab()
        self._create_hotkeys_tab()
        self._create_audio_tab()
        self._create_language_tab()
        
        # Create buttons
        self._create_buttons()
        
        # Center window on parent
        self._center_window()
        
        # Bind close event
        self._window.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _center_window(self) -> None:
        """Center window on screen."""
        self._window.update_idletasks()
        width = self._window.winfo_width()
        height = self._window.winfo_height()
        x = (self._window.winfo_screenwidth() // 2) - (width // 2)
        y = (self._window.winfo_screenheight() // 2) - (height // 2)
        self._window.geometry(f"{width}x{height}+{x}+{y}")

    def _create_asr_tab(self) -> None:
        """Create ASR Provider configuration tab."""
        tab = ttk.Frame(self._notebook, padding="10")
        self._notebook.add(tab, text="ASR Provider")
        
        # Provider selection
        ttk.Label(tab, text="Provider:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self._provider_var = tk.StringVar(value=self._config.asr.provider)
        provider_combo = ttk.Combobox(
            tab,
            textvariable=self._provider_var,
            values=list_providers(),
            state="readonly",
            width=30,
        )
        provider_combo.grid(row=0, column=1, sticky=tk.W, pady=5)
        provider_combo.bind("<<ComboboxSelected>>", self._on_provider_change)
        
        # API Key
        ttk.Label(tab, text="API Key:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self._api_key_var = tk.StringVar(value=self._config.asr.get_api_key())
        self._api_key_entry = ttk.Entry(
            tab,
            textvariable=self._api_key_var,
            show="*",
            width=35,
        )
        self._api_key_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Model selection
        ttk.Label(tab, text="Model:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self._model_var = tk.StringVar(value=self._config.asr.model)
        self._model_combo = ttk.Combobox(
            tab,
            textvariable=self._model_var,
            values=get_provider_models(self._config.asr.provider),
            state="readonly",
            width=30,
        )
        self._model_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Base URL (for local/custom)
        ttk.Label(tab, text="Base URL:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self._base_url_var = tk.StringVar(value=self._config.asr.get_base_url())
        self._base_url_entry = ttk.Entry(tab, textvariable=self._base_url_var, width=35)
        self._base_url_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Update visibility based on provider
        self._update_base_url_visibility()
        
        # Test button
        test_btn = ttk.Button(tab, text="Test Connection", command=self._test_provider)
        test_btn.grid(row=4, column=1, sticky=tk.W, pady=15)

    def _create_hotkeys_tab(self) -> None:
        """Create Hotkeys configuration tab."""
        tab = ttk.Frame(self._notebook, padding="10")
        self._notebook.add(tab, text="Hotkeys")
        
        # Dictation hotkey
        ttk.Label(tab, text="Dictation Hotkey:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self._hotkey_var = tk.StringVar(value=self._config.hotkey.dictate)
        hotkey_entry = ttk.Entry(tab, textvariable=self._hotkey_var, width=25)
        hotkey_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        hotkey_entry.config(state="readonly")
        
        capture_btn = ttk.Button(
            tab, text="Capture", command=self._capture_hotkey
        )
        capture_btn.grid(row=0, column=2, sticky=tk.W, padx=5)
        
        # Mode selection
        ttk.Label(tab, text="Mode:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self._mode_var = tk.StringVar(value=self._config.hotkey.mode)
        mode_frame = ttk.Frame(tab)
        mode_frame.grid(row=1, column=1, sticky=tk.W)
        ttk.Radiobutton(
            mode_frame, text="Toggle", variable=self._mode_var, value="toggle"
        ).pack(side=tk.LEFT)
        ttk.Radiobutton(
            mode_frame, text="Push-to-Talk", variable=self._mode_var, value="push_to_talk"
        ).pack(side=tk.LEFT, padx=10)
        
        # Help text
        help_text = "Toggle: Press to start/stop. Push-to-Talk: Hold to record."
        ttk.Label(tab, text=help_text, foreground="gray").grid(
            row=2, column=0, columnspan=3, sticky=tk.W, pady=10
        )

    def _create_audio_tab(self) -> None:
        """Create Audio configuration tab."""
        tab = ttk.Frame(self._notebook, padding="10")
        self._notebook.add(tab, text="Audio")
        
        # Microphone selection
        ttk.Label(tab, text="Microphone:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        devices = AudioRecorder.list_devices()
        device_names = [f"{d['name']} ({d['channels']}ch)" for d in devices]
        
        # Find current device name
        current_device = self._config.audio.device
        current_name = "System Default"
        if current_device is not None:
            for d in devices:
                if d["id"] == current_device:
                    current_name = f"{d['name']} ({d['channels']}ch)"
                    break
        
        self._device_var = tk.StringVar(value=current_name)
        self._device_combo = ttk.Combobox(
            tab,
            textvariable=self._device_var,
            values=["System Default"] + device_names,
            state="readonly",
            width=40,
        )
        self._device_combo.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Store devices for later lookup
        self._devices = devices
        
        # Refresh button
        refresh_btn = ttk.Button(
            tab, text="Refresh", command=self._refresh_devices
        )
        refresh_btn.grid(row=0, column=2, sticky=tk.W, padx=5)
        
        # Sample rate (info only)
        ttk.Label(tab, text="Sample Rate:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(tab, text=f"{self._config.audio.sample_rate} Hz").grid(
            row=1, column=1, sticky=tk.W
        )

    def _create_language_tab(self) -> None:
        """Create Language configuration tab."""
        tab = ttk.Frame(self._notebook, padding="10")
        self._notebook.add(tab, text="Language")
        
        # Language selection
        ttk.Label(tab, text="Language:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self._language_var = tk.StringVar(value=self._config.asr.language)
        language_combo = ttk.Combobox(
            tab,
            textvariable=self._language_var,
            values=["auto", "de", "en"],
            state="readonly",
            width=20,
        )
        language_combo.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Language labels
        lang_labels = {"auto": "Auto-detect", "de": "German", "en": "English"}
        ttk.Label(tab, text="(Auto-detect, German, or English)").grid(
            row=0, column=2, sticky=tk.W, padx=10
        )
        
        # Clipboard behavior
        ttk.Label(tab, text="Clipboard:").grid(row=1, column=0, sticky=tk.W, pady=15)
        self._clipboard_var = tk.StringVar(
            value="restore" if self._config.clipboard_restore else "keep"
        )
        clipboard_frame = ttk.Frame(tab)
        clipboard_frame.grid(row=1, column=1, sticky=tk.W)
        ttk.Radiobutton(
            clipboard_frame,
            text="Restore after insert",
            variable=self._clipboard_var,
            value="restore",
        ).pack(side=tk.LEFT)
        ttk.Radiobutton(
            clipboard_frame,
            text="Keep transcription",
            variable=self._clipboard_var,
            value="keep",
        ).pack(side=tk.LEFT, padx=10)

    def _create_buttons(self) -> None:
        """Create Save and Cancel buttons."""
        button_frame = ttk.Frame(self._main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Save", command=self._on_save_click).pack(
            side=tk.RIGHT, padx=5
        )
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).pack(
            side=tk.RIGHT
        )

    def _on_provider_change(self, event: tk.Event) -> None:
        """Handle provider selection change."""
        provider = self._provider_var.get()
        
        # Update model list
        models = get_provider_models(provider)
        self._model_combo["values"] = models
        if models:
            self._model_var.set(models[0])
        
        # Update API key and base URL from config
        if provider in self._config.asr.providers:
            self._api_key_var.set(self._config.asr.providers[provider].api_key)
            self._base_url_var.set(self._config.asr.providers[provider].base_url)
        else:
            self._api_key_var.set("")
            self._base_url_var.set("")
        
        # Update visibility
        self._update_base_url_visibility()
        
        logger.debug(f"Provider changed to: {provider}")

    def _update_base_url_visibility(self) -> None:
        """Update base URL field visibility and editability."""
        provider = self._provider_var.get()
        # Allow editing for local provider, show but readonly for others
        if provider == "local":
            self._base_url_entry.config(state="normal")
        else:
            # Still show the URL but make it readonly
            self._base_url_entry.config(state="readonly")

    def _capture_hotkey(self) -> None:
        """Capture hotkey combination from keyboard."""
        import keyboard
        
        if self._hotkey_capturing:
            return
        
        self._hotkey_capturing = True
        self._hotkey_var.set("Press keys...")
        
        def on_capture(event):
            # Build hotkey string
            modifiers = []
            if event.name:
                key = event.name.lower()
            else:
                key = ""
            
            # Check modifier keys
            if keyboard.is_pressed("ctrl"):
                modifiers.append("ctrl")
            if keyboard.is_pressed("alt"):
                modifiers.append("alt")
            if keyboard.is_pressed("shift"):
                modifiers.append("shift")
            if keyboard.is_pressed("windows"):
                modifiers.append("win")
            
            # Build final hotkey string
            if modifiers and key:
                hotkey = "+".join(modifiers + [key])
            elif key:
                hotkey = key
            else:
                hotkey = ""
            
            if hotkey:
                self._hotkey_var.set(hotkey)
                keyboard.unhook_all()
                self._hotkey_capturing = False
        
        # Hook next key press
        keyboard.on_press(on_capture, suppress=True)
        
        # Timeout after 5 seconds
        self._window.after(5000, self._cancel_hotkey_capture)

    def _cancel_hotkey_capture(self) -> None:
        """Cancel hotkey capture if still active."""
        if self._hotkey_capturing:
            import keyboard
            keyboard.unhook_all()
            self._hotkey_var.set(self._config.hotkey.dictate)
            self._hotkey_capturing = False

    def _refresh_devices(self) -> None:
        """Refresh audio device list."""
        devices = AudioRecorder.list_devices()
        device_names = [f"{d['name']} ({d['channels']}ch)" for d in devices]
        self._device_combo["values"] = ["System Default"] + device_names
        self._devices = devices
        messagebox.showinfo("Refresh", "Device list refreshed")

    def _test_provider(self) -> None:
        """Test provider connection with current settings."""
        provider_name = self._provider_var.get()
        api_key = self._api_key_var.get()
        base_url = self._base_url_var.get()
        
        if not api_key and provider_name != "local":
            messagebox.showwarning(
                "Missing API Key",
                f"Please enter an API key for {provider_name}",
            )
            return
        
        # Simple validation - check if we can create a client
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key or "test", base_url=base_url)
            # Just verify client creation works
            messagebox.showinfo(
                "Success",
                f"Connection settings valid for {provider_name}",
            )
        except Exception as e:
            messagebox.showerror(
                "Connection Error",
                f"Failed to connect to {provider_name}:\n{e}",
            )

    def _on_save_click(self) -> None:
        """Handle Save button click."""
        # Update config from UI values
        self._config.asr.provider = self._provider_var.get()
        self._config.asr.model = self._model_var.get()
        self._config.asr.language = self._language_var.get()
        
        # Update provider-specific config
        provider = self._config.asr.provider
        if provider in self._config.asr.providers:
            self._config.asr.providers[provider].api_key = self._api_key_var.get()
            self._config.asr.providers[provider].base_url = self._base_url_var.get()
        
        # Update hotkey config
        self._config.hotkey.dictate = self._hotkey_var.get()
        self._config.hotkey.mode = self._mode_var.get()
        
        # Update audio config
        device_name = self._device_var.get()
        if device_name == "System Default":
            self._config.audio.device = None
        else:
            for d in self._devices:
                if f"{d['name']} ({d['channels']}ch)" == device_name:
                    self._config.audio.device = d["id"]
                    break
        
        # Update clipboard config
        self._config.clipboard_restore = self._clipboard_var.get() == "restore"
        
        # Save config
        save_config(self._config)
        
        # Notify parent
        self._on_save()
        
        # Close window
        self._window.destroy()
        
        logger.info("Settings saved")

    def _on_cancel(self) -> None:
        """Handle Cancel button or window close."""
        self._window.destroy()

    def show(self) -> None:
        """Show the settings window (modal)."""
        self._window.wait_window()
```

**Validation:** Run `python -c "from asr_everywhere.ui.settings_window import SettingsWindow; print('SettingsWindow imported successfully')"`

---

### 5. UPDATE `src/asr_everywhere/ui/__init__.py`

Export SettingsWindow.

```python
"""UI components for ASR Everywhere."""

from asr_everywhere.ui.tray import TrayIcon
from asr_everywhere.ui.settings_window import SettingsWindow

__all__ = ["TrayIcon", "SettingsWindow"]
```

---

### 6. UPDATE `src/asr_everywhere/app.py`

Wire Settings window to System Tray and handle config reload.

```python
# Add to imports:
from asr_everywhere.ui.settings_window import SettingsWindow

# Add method to ASREverywhereApp class:

def _open_settings(self) -> None:
    """Open settings window."""
    def on_save():
        # Reload config
        self._config = load_config()
        
        # Re-register hotkey if changed
        self._hotkey_manager.unregister_all()
        self._hotkey_manager.register_hotkey(
            self._config.hotkey.dictate,
            self._pipeline.toggle_recording,
        )
        
        logger.info(f"Settings updated - hotkey: {self._config.hotkey.dictate}")
    
    SettingsWindow(None, self._config, on_save).show()

# Update TrayIcon creation to pass settings callback:
self._tray = TrayIcon(
    on_quit=self.quit,
    on_toggle_recording=self._pipeline.toggle_recording,
    on_settings=self._open_settings,  # Add this
)
```

---

### 7. UPDATE `config.example.json`

Update example config with multi-provider structure.

```json
{
  "version": 1,
  "hotkey": {
    "dictate": "win+ctrl+a",
    "mode": "toggle"
  },
  "asr": {
    "provider": "openai",
    "model": "whisper-1",
    "language": "auto",
    "api_key": "",
    "base_url": "https://api.openai.com/v1",
    "providers": {
      "openai": {
        "api_key": "",
        "base_url": "https://api.openai.com/v1"
      },
      "together": {
        "api_key": "",
        "base_url": "https://api.together.xyz/v1"
      },
      "huggingface": {
        "api_key": "",
        "base_url": "https://api-inference.huggingface.co/v1"
      },
      "openrouter": {
        "api_key": "",
        "base_url": "https://openrouter.ai/api/v1"
      },
      "local": {
        "api_key": "",
        "base_url": "http://localhost:11434/v1"
      }
    }
  },
  "audio": {
    "device": null,
    "sample_rate": 16000,
    "channels": 1
  },
  "clipboard_restore": true
}
```

---

### 8. CREATE `tests/test_openai_compat.py`

Test OpenAI-compatible provider.

```python
"""Tests for OpenAI-compatible provider."""

from unittest import mock

import pytest

from asr_everywhere.config import ASRConfig, ProviderConfig
from asr_everywhere.providers.openai_compat import OpenAICompatProvider


@pytest.fixture
def compat_config():
    """Create test config for compatible provider."""
    return ASRConfig(
        provider="together",
        model="whisper-1",
        providers={
            "together": ProviderConfig(
                api_key="test-key",
                base_url="https://api.together.xyz/v1",
            )
        },
    )


def test_compat_provider_transcribe(compat_config):
    """Test transcription with compatible provider."""
    provider = OpenAICompatProvider("together")

    with mock.patch("asr_everywhere.providers.openai_compat.OpenAI") as mock_openai:
        mock_client = mock.MagicMock()
        mock_openai.return_value = mock_client

        mock_response = mock.MagicMock()
        mock_response.text = "Hello from Together"
        mock_client.audio.transcriptions.create.return_value = mock_response

        result = provider.transcribe(b"fake audio", compat_config)

        assert result.text == "Hello from Together"
        mock_client.audio.transcriptions.create.assert_called_once()


def test_compat_provider_uses_base_url(compat_config):
    """Test that provider uses configured base_url."""
    provider = OpenAICompatProvider("together")

    with mock.patch("asr_everywhere.providers.openai_compat.OpenAI") as mock_openai:
        mock_client = mock.MagicMock()
        mock_openai.return_value = mock_client

        mock_response = mock.MagicMock()
        mock_response.text = "test"
        mock_client.audio.transcriptions.create.return_value = mock_response

        provider.transcribe(b"audio", compat_config)

        # Verify OpenAI was called with correct base_url
        mock_openai.assert_called_once()
        call_kwargs = mock_openai.call_args.kwargs
        assert call_kwargs["base_url"] == "https://api.together.xyz/v1"


def test_compat_provider_local_no_key():
    """Test local provider works without API key."""
    config = ASRConfig(
        provider="local",
        model="whisper-1",
        providers={
            "local": ProviderConfig(
                api_key="",
                base_url="http://localhost:11434/v1",
            )
        },
    )

    provider = OpenAICompatProvider("local")

    with mock.patch("asr_everywhere.providers.openai_compat.OpenAI") as mock_openai:
        mock_client = mock.MagicMock()
        mock_openai.return_value = mock_client

        mock_response = mock.MagicMock()
        mock_response.text = "Local transcription"
        mock_client.audio.transcriptions.create.return_value = mock_response

        result = provider.transcribe(b"audio", config)

        assert result.text == "Local transcription"
```

---

### 9. CREATE `tests/test_settings_window.py`

Test Settings window components.

```python
"""Tests for Settings window."""

from unittest import mock

import pytest

from asr_everywhere.config import Config
from asr_everywhere.ui.settings_window import SettingsWindow


@pytest.fixture
def mock_tkinter():
    """Mock tkinter components."""
    with mock.patch("tkinter.Toplevel"), \
         mock.patch("tkinter.ttk.Frame"), \
         mock.patch("tkinter.ttk.Notebook"), \
         mock.patch("tkinter.ttk.Label"), \
         mock.patch("tkinter.ttk.Entry"), \
         mock.patch("tkinter.ttk.Combobox"), \
         mock.patch("tkinter.ttk.Button"), \
         mock.patch("tkinter.ttk.Radiobutton"):
        yield


def test_settings_window_creation(mock_tkinter):
    """Test settings window can be created."""
    config = Config()
    on_save_called = []

    def on_save():
        on_save_called.append(True)

    window = SettingsWindow(None, config, on_save)
    assert window is not None


def test_settings_window_provider_list(mock_tkinter):
    """Test that providers are loaded correctly."""
    with mock.patch(
        "asr_everywhere.ui.settings_window.list_providers"
    ) as mock_list:
        mock_list.return_value = ["openai", "together", "local"]

        config = Config()
        window = SettingsWindow(None, config, lambda: None)

        # Verify list_providers was called
        mock_list.assert_called()


def test_settings_window_device_list(mock_tkinter):
    """Test that audio devices are loaded."""
    with mock.patch(
        "asr_everywhere.audio_recorder.AudioRecorder.list_devices"
    ) as mock_devices:
        mock_devices.return_value = [
            {"id": 0, "name": "Mic 1", "channels": 2},
            {"id": 1, "name": "Mic 2", "channels": 1},
        ]

        config = Config()
        window = SettingsWindow(None, config, lambda: None)

        # Verify devices were queried
        mock_devices.assert_called()
```

---

### 10. VALIDATE Implementation

Run all tests and linting:

```bash
# Run tests
pytest tests/ -v

# Run linting
ruff check src/ tests/

# Run formatting check
ruff format --check src/ tests/

# Manual validation
python -m asr_everywhere
# Right-click tray icon → Settings
# Change provider, enter API key, save
# Verify dictation still works
```

---

## Edge Cases to Handle

1. **No API key entered** - Show warning when testing/saving without API key (except local)
2. **Invalid hotkey combination** - Validate hotkey format, show error if invalid
3. **Hotkey conflict** - Warn if hotkey already registered by another app
4. **No microphone devices** - Show "No devices found" message, disable dropdown
5. **Config file locked** - Handle permission errors gracefully, show error message
6. **Network timeout during test** - Show user-friendly error, suggest checking connection
7. **Provider API changes** - Error handling in provider should surface to UI
8. **Window already open** - Prevent multiple settings windows (focus existing)

---

## Security Considerations

- **API keys masked in UI** - Use `show="*"` for Entry widgets
- **No API keys in logs** - Never log sensitive configuration values
- **Config file permissions** - Document that user is responsible for file security
- **Clipboard handling** - No sensitive data exposed through clipboard settings

---

## Performance Considerations

- **Device enumeration** - Cache device list, only refresh on button click
- **Model list loading** - Fetch models lazily when provider changes
- **Config save** - Immediate save on button click (no background thread needed)
- **Window creation** - Create window on demand, destroy on close

---

## Future Enhancements (Out of Scope for Phase 2)

- LLM post-processing tab (Phase 3)
- Dictionary management tab (Phase 3)
- Dual hotkey support (separate restore/keep clipboard hotkeys)
- Push-to-talk mode implementation
- Hotkey conflict detection with system shortcuts
- Export/import configuration
- Reset to defaults button
