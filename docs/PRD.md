# ASR Everywhere — Product Requirements Document

## 1. Executive Summary

**ASR Everywhere** is a lightweight Windows desktop application that enables system-wide voice-to-text dictation. Inspired by [Aqua Voice](https://aquavoice.com), it allows users to press a configurable global hotkey (e.g. `WIN+U`) to start recording, press it again to stop, and have the transcribed text automatically inserted at the current cursor position in any application. The transcribed text is optionally copied to the clipboard as well.

The application supports multiple ASR backends — including cloud inference providers (Together.ai, Hugging Face, OpenRouter), the OpenAI API directly (for models like `gpt-4o-transcribe`), and local OpenAI-compatible APIs (e.g. LibreChat, Ollama) — giving users full flexibility over accuracy, cost, privacy, and latency. An optional LLM post-processing step can clean up, reformat, or transform the transcribed text before insertion.

**MVP Goal:** Deliver a fully functional, pip-installable Python application for Windows that supports multiple ASR providers, configurable hotkeys (toggle and push-to-talk), cursor-position text insertion, clipboard integration, optional LLM post-processing, a dictionary for custom terms, microphone selection, language auto-detection (German & English), and a minimal System Tray UI with a settings window.

---

## 2. Mission

**Mission Statement:** Make high-quality speech-to-text dictation universally accessible on Windows — across any application, with any ASR model, under the user's full control.

**Core Principles:**

1. **Provider Agnostic** — Support a broad range of ASR backends from day one; never lock users into a single vendor.
2. **Minimal Friction** — One hotkey press to start, one to stop. Text appears where the cursor is. No extra steps.
3. **User Control** — Every behavior (hotkey, provider, language, post-processing, clipboard handling) is configurable.
4. **Simplicity over Feature Creep** — Keep the UI minimal (System Tray + Settings). No history, no file tagging, no replacements engine.
5. **Extensible Architecture** — Clean provider abstraction so adding new ASR or LLM backends is straightforward.

---

## 3. Target Users

### Primary Persona: Power User / Developer
- Technically proficient (comfortable with pip install, editing JSON config, obtaining API keys)
- Uses multiple applications daily (IDE, browser, email client, chat apps)
- Wants to dictate text quickly without switching context
- May already use ASR services and wants to consolidate into one tool
- Works primarily in German and/or English

### Secondary Persona: Knowledge Worker
- Writes a lot of text (emails, documents, notes)
- Wants to reduce keyboard strain / improve productivity
- Moderate technical comfort (can follow setup instructions)

### Key Needs & Pain Points
- Existing Windows dictation (Win+H) is limited to one model, has poor accuracy for German, and lacks customization
- Aqua Voice is macOS-only
- No single tool lets you easily switch between ASR providers on Windows
- Need for post-processing (punctuation, formatting, filler word removal) on raw transcripts

---

## 4. MVP Scope

### In Scope — Core Functionality
- ✅ Global hotkey: Toggle mode (press to start recording, press again to stop and transcribe)
- ✅ Global hotkey: Push-to-talk mode (hold to record, release to stop and transcribe)
- ✅ Freely configurable hotkey(s) via settings
- ✅ Two separate hotkeys: one that keeps transcription in clipboard, one that restores previous clipboard
- ✅ Audio recording from a user-selected microphone
- ✅ Microphone selection in settings
- ✅ Visual recording indicator (System Tray icon color change / overlay)
- ✅ Text insertion at current cursor position (via clipboard + simulated Ctrl+V)
- ✅ Clipboard behavior configurable (keep transcription in clipboard vs. restore previous clipboard content)
- ✅ Batch transcription (full audio sent after recording stops)

### In Scope — ASR Providers
- ✅ OpenAI Whisper API / gpt-4o-transcribe (direct OpenAI API)
- ✅ Together.ai (OpenAI-compatible API)
- ✅ Hugging Face Inference API (OpenAI-compatible API)
- ✅ OpenRouter (OpenAI-compatible API)
- ✅ Local APIs via OpenAI-compatible endpoints (LibreChat, Ollama, etc.)
- ✅ Provider selection and per-provider API key configuration in settings
- ✅ Model selection per provider

### In Scope — Language
- ✅ German and English support
- ✅ Automatic language detection
- ✅ Manual language override in settings

### In Scope — Post-Processing
- ✅ Optional LLM post-processing of transcribed text (punctuation, formatting, filler word removal, custom instructions)
- ✅ LLM provider: same inference providers as ASR (OpenAI-compatible APIs)
- ✅ Configurable custom instructions (system prompt for LLM)
- ✅ Dictionary / custom terms list (proper nouns, technical terms) injected into LLM context

### In Scope — Technical
- ✅ Python application, pip-installable (`pip install asr-everywhere`)
- ✅ System Tray icon with context menu (Settings, Quit, status indicator)
- ✅ Settings GUI window (minimal, functional)
- ✅ JSON configuration file in `%APPDATA%/asr-everywhere/`
- ✅ API keys stored in JSON config (unencrypted, user responsibility)

### Out of Scope (Future)
- ❌ History / transcription log
- ❌ File tagging
- ❌ Replacements engine (regex-based find/replace)
- ❌ Real-time streaming transcription (optional future enhancement if simple to add)
- ❌ Encrypted API key storage (Windows Credential Manager)
- ❌ MSI installer / standalone .exe packaging
- ❌ Autostart with Windows (user can configure manually)
- ❌ Offline-only mode
- ❌ macOS / Linux support
- ❌ Multi-language beyond DE/EN

---

## 5. User Stories

### Primary User Stories

1. **As a** user, **I want to** press a global hotkey to start and stop voice recording, **so that** I can dictate text from any application without switching windows.
   - *Example:* I'm writing an email in Outlook. I press `WIN+U`, dictate my response, press `WIN+U` again, and the text appears in the email body.

2. **As a** user, **I want to** hold a key to record and release it to stop (push-to-talk), **so that** I have an alternative, more tactile dictation mode.
   - *Example:* I hold `WIN+U`, say a quick sentence, release the key, and it's transcribed and inserted.

3. **As a** user, **I want to** choose between different ASR providers and models in the settings, **so that** I can pick the best provider for my needs (accuracy, speed, cost, privacy).
   - *Example:* I switch from OpenAI gpt-4o-transcribe to a Whisper model on Together.ai to reduce cost.

4. **As a** user, **I want to** have the transcribed text automatically inserted at my cursor position, **so that** dictation works seamlessly in any text field.
   - *Example:* I click into a Slack message input, dictate, and the text appears right there.

5. **As a** user, **I want to** optionally have the transcription cleaned up by an LLM (punctuation, formatting, filler word removal), **so that** the inserted text is polished and ready to use.
   - *Example:* I say "ähm also ich denke wir sollten das meeting auf montag verschieben", and the inserted text is "Ich denke, wir sollten das Meeting auf Montag verschieben."

6. **As a** user, **I want to** define a dictionary of custom terms, **so that** the transcription correctly handles proper nouns, technical terms, and abbreviations.
   - *Example:* I add "Kubernetes", "FastAPI", and my colleague's name "Szczerba" to the dictionary, and they are correctly transcribed.

7. **As a** user, **I want to** use two different hotkeys — one that keeps the transcription in the clipboard and one that restores the previous clipboard content — **so that** I have control over my clipboard state after dictation.
   - *Example:* I press `WIN+U` to dictate-and-restore-clipboard, or `WIN+SHIFT+U` to dictate-and-keep-in-clipboard for pasting elsewhere.

8. **As a** user, **I want to** see a visual indicator when recording is active, **so that** I always know whether the microphone is on.
   - *Example:* The System Tray icon turns red while recording.

### Technical User Stories

9. **As a** developer extending the app, **I want** ASR providers to follow a common interface, **so that** I can add new providers with minimal effort.
   - *Example:* Adding a new provider requires implementing a single `transcribe(audio_data, config) -> str` method.

10. **As a** developer extending the app, **I want** LLM providers to follow the same OpenAI-compatible pattern as ASR providers, **so that** the post-processing pipeline is consistent.

---

## 6. Core Architecture & Patterns

### High-Level Architecture

```
┌─────────────────────────────────────────────────┐
│                  System Tray UI                  │
│          (pystray + tkinter settings)            │
├─────────────────────────────────────────────────┤
│                  Core Engine                     │
│  ┌───────────┐  ┌──────────┐  ┌──────────────┐ │
│  │  Hotkey   │  │  Audio   │  │    Text      │ │
│  │  Manager  │  │ Recorder │  │  Inserter    │ │
│  └─────┬─────┘  └────┬─────┘  └──────┬───────┘ │
│        │              │               │         │
│  ┌─────▼──────────────▼───────────────▼───────┐ │
│  │           Transcription Pipeline            │ │
│  │  Audio → ASR Provider → (LLM Post-Proc) → │ │
│  │  Text Insertion                             │ │
│  └─────────────────────────────────────────────┘ │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │         Provider Abstraction Layer          │ │
│  │  ┌─────────┐ ┌──────────┐ ┌─────────────┐  │ │
│  │  │ OpenAI  │ │Together  │ │  Local API   │  │ │
│  │  │ Direct  │ │HF/OpenR  │ │  (Ollama..)  │  │ │
│  │  └─────────┘ └──────────┘ └─────────────┘  │ │
│  └─────────────────────────────────────────────┘ │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │          Config Manager (JSON)              │ │
│  └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

### Directory Structure

```
asr-everywhere/
├── pyproject.toml
├── README.md
├── docs/
│   └── PRD.md
├── src/
│   └── asr_everywhere/
│       ├── __init__.py
│       ├── __main__.py              # Entry point
│       ├── app.py                   # Application orchestrator
│       ├── config.py                # Config loading/saving (JSON)
│       ├── hotkey_manager.py        # Global hotkey registration
│       ├── audio_recorder.py        # Microphone recording
│       ├── text_inserter.py         # Clipboard + keypress simulation
│       ├── transcription_pipeline.py # Orchestrates ASR → LLM → insert
│       ├── providers/
│       │   ├── __init__.py
│       │   ├── base.py              # Abstract ASR & LLM provider
│       │   ├── openai_provider.py   # OpenAI direct (Whisper, gpt-4o-transcribe)
│       │   ├── openai_compat.py     # Generic OpenAI-compatible (Together, HF, OpenRouter, local)
│       │   └── registry.py          # Provider discovery & instantiation
│       ├── llm/
│       │   ├── __init__.py
│       │   ├── post_processor.py    # LLM post-processing logic
│       │   └── prompts.py           # Default system prompts, dictionary injection
│       └── ui/
│           ├── __init__.py
│           ├── tray.py              # System Tray icon & menu
│           └── settings_window.py   # Settings GUI (tkinter)
├── tests/
│   ├── test_config.py
│   ├── test_providers.py
│   ├── test_pipeline.py
│   └── test_hotkey.py
└── assets/
    ├── icon_idle.ico
    ├── icon_recording.ico
    └── icon_processing.ico
```

### Key Design Patterns

- **Strategy Pattern** — ASR and LLM providers implement a common interface; the pipeline selects the active provider at runtime based on config.
- **Observer / Event-Driven** — Hotkey events trigger recording start/stop; recording completion triggers the transcription pipeline; pipeline completion triggers text insertion.
- **Pipeline Pattern** — Audio → ASR → (optional LLM post-processing) → Text insertion, each step as a composable unit.
- **Singleton Config** — A single `Config` instance loaded at startup, mutated via the Settings UI, persisted to JSON.

---

## 7. Features — Detailed Specifications

### 7.1 Global Hotkey System

| Feature | Details |
|---|---|
| **Toggle Mode** | Press hotkey → start recording. Press again → stop recording, transcribe, insert. |
| **Push-to-Talk Mode** | Hold hotkey → record. Release → stop, transcribe, insert. |
| **Configurable Hotkeys** | User defines hotkey combinations in settings (e.g. `WIN+U`, `CTRL+ALT+R`). |
| **Dual Hotkeys** | Hotkey A: insert + restore clipboard. Hotkey B: insert + keep transcription in clipboard. |
| **Mode Selection** | Toggle or Push-to-Talk, selectable per hotkey in settings. |

**Implementation:** Use `keyboard` library or `pynput` for global hotkey capture on Windows.

### 7.2 Audio Recording

| Feature | Details |
|---|---|
| **Microphone Selection** | User selects input device from a dropdown in settings. Falls back to system default. |
| **Audio Format** | Record as WAV (PCM 16-bit, 16kHz mono) or configurable sample rate per provider needs. |
| **Recording Buffer** | Audio stored in memory during recording; written to temp file or sent as bytes on stop. |

**Implementation:** Use `sounddevice` or `pyaudio` for cross-platform audio capture.

### 7.3 ASR Provider Abstraction

All providers implement:

```python
class ASRProvider(ABC):
    @abstractmethod
    def transcribe(self, audio_data: bytes, config: TranscriptionConfig) -> str:
        """Transcribe audio bytes to text."""
        ...

    @abstractmethod
    def list_models(self) -> list[str]:
        """Return available models for this provider."""
        ...
```

#### Supported Providers

| Provider | API Type | Example Models | Notes |
|---|---|---|---|
| **OpenAI Direct** | OpenAI API | `whisper-1`, `gpt-4o-transcribe` | Native OpenAI endpoint |
| **Together.ai** | OpenAI-compatible | Whisper variants, custom models | `base_url` override |
| **Hugging Face** | OpenAI-compatible | Whisper variants | Inference API |
| **OpenRouter** | OpenAI-compatible | Various ASR models | `base_url` override |
| **Local (Ollama, LibreChat)** | OpenAI-compatible | User-configured | `base_url` = `http://localhost:...` |

The **OpenAI-compatible** providers all share one implementation class (`OpenAICompatProvider`) with configurable `base_url` and `api_key`.

### 7.4 LLM Post-Processing

| Feature | Details |
|---|---|
| **Enable/Disable** | Toggle in settings. Off by default for lowest latency. |
| **Provider** | Same OpenAI-compatible providers as ASR. User selects provider + model. |
| **Custom Instructions** | User-defined system prompt (free text) for the LLM, stored in config. |
| **Dictionary Injection** | Custom terms list appended to the LLM system prompt as context. |
| **Default Behavior** | Fix punctuation, capitalize properly, remove filler words (ähm, also, um, like). |

**Prompt Structure:**

```
System: You are a transcription post-processor. Clean up the following dictated text.
Rules:
- Fix punctuation and capitalization
- Remove filler words
{user_custom_instructions}

Dictionary (use these exact spellings):
{dictionary_terms}

User: {raw_transcription}
```

### 7.5 Text Insertion

| Feature | Details |
|---|---|
| **Method** | Save current clipboard → copy transcription to clipboard → simulate `Ctrl+V` → optionally restore clipboard. |
| **Hotkey A** | Insert text + restore previous clipboard content. |
| **Hotkey B** | Insert text + keep transcription in clipboard. |
| **Fallback** | If `Ctrl+V` simulation fails (some apps), text remains in clipboard for manual paste. |

**Implementation:** Use `pyperclip` or `win32clipboard` for clipboard operations; `pyautogui` or `pynput` for keystroke simulation.

### 7.6 Visual Recording Indicator

| Feature | Details |
|---|---|
| **Tray Icon States** | Idle (default icon), Recording (red icon), Processing (yellow/spinner icon). |
| **Tooltip** | Tray icon tooltip shows current state: "Idle", "Recording...", "Transcribing...". |

### 7.7 Settings UI

A tkinter-based settings window accessible from the System Tray context menu. Sections:

1. **ASR Provider** — Provider dropdown, API key input, model selection, base URL (for local/custom).
2. **LLM Post-Processing** — Enable/disable toggle, provider/model selection, custom instructions text area.
3. **Dictionary** — List of custom terms (add/remove).
4. **Hotkeys** — Hotkey A and B configuration, toggle vs push-to-talk mode per hotkey.
5. **Audio** — Microphone device selection dropdown.
6. **Language** — Language selection (DE, EN, Auto-detect).
7. **Clipboard** — Default clipboard behavior setting.

### 7.8 Dictionary

| Feature | Details |
|---|---|
| **Storage** | List of strings in JSON config under `"dictionary": ["term1", "term2", ...]` |
| **Usage** | Injected into LLM post-processing prompt as context. Also optionally passed to ASR provider `prompt` parameter (where supported, e.g. OpenAI Whisper). |
| **Management** | Add/remove via Settings UI. |

---

## 8. Technology Stack

### Core Dependencies

| Component | Library | Version | Purpose |
|---|---|---|---|
| **Python** | — | ≥ 3.11 | Runtime |
| **Audio Recording** | `sounddevice` | ≥ 0.4 | Microphone capture |
| **Audio Format** | `soundfile` | ≥ 0.12 | WAV encoding |
| **HTTP Client** | `httpx` | ≥ 0.27 | Async HTTP for API calls |
| **OpenAI SDK** | `openai` | ≥ 1.0 | OpenAI & compatible APIs |
| **Global Hotkeys** | `keyboard` | ≥ 0.13 | System-wide hotkey capture |
| **System Tray** | `pystray` | ≥ 0.19 | Tray icon & menu |
| **GUI** | `tkinter` | (stdlib) | Settings window |
| **Clipboard** | `pyperclip` | ≥ 1.8 | Clipboard read/write |
| **Keystroke Sim** | `pynput` | ≥ 1.7 | Simulate Ctrl+V |
| **Image (icons)** | `Pillow` | ≥ 10.0 | Tray icon image handling |

### Optional Dependencies

| Component | Library | Purpose |
|---|---|---|
| **Streaming** | `websockets` | For future real-time streaming support |
| **Packaging** | `PyInstaller` / `Nuitka` | For standalone .exe distribution (future) |

### Third-Party Integrations

| Service | Integration |
|---|---|
| OpenAI API | Direct, for Whisper / gpt-4o-transcribe |
| Together.ai | OpenAI-compatible endpoint |
| Hugging Face Inference | OpenAI-compatible endpoint |
| OpenRouter | OpenAI-compatible endpoint |
| Ollama (local) | OpenAI-compatible endpoint on localhost |
| LibreChat (local) | OpenAI-compatible endpoint on localhost |

---

## 9. Security & Configuration

### Configuration Management

- **Config file:** `%APPDATA%/asr-everywhere/config.json`
- **API keys:** Stored as plaintext in the JSON config file. User is responsible for file system security.
- **Sensitive fields:** API keys are masked in the Settings UI (password field).
- **Default config:** Generated on first run with sensible defaults (no API keys, default hotkeys, system default mic).

### Example Config Structure

```json
{
  "version": 1,
  "hotkeys": {
    "dictate_restore_clipboard": "win+u",
    "dictate_keep_clipboard": "win+shift+u",
    "mode": "toggle"
  },
  "asr": {
    "provider": "openai",
    "model": "gpt-4o-transcribe",
    "language": "auto",
    "providers": {
      "openai": {
        "api_key": "sk-...",
        "base_url": "https://api.openai.com/v1"
      },
      "together": {
        "api_key": "...",
        "base_url": "https://api.together.xyz/v1"
      },
      "huggingface": {
        "api_key": "hf_...",
        "base_url": "https://api-inference.huggingface.co/v1"
      },
      "openrouter": {
        "api_key": "sk-or-...",
        "base_url": "https://openrouter.ai/api/v1"
      },
      "local": {
        "api_key": "",
        "base_url": "http://localhost:11434/v1"
      }
    }
  },
  "llm": {
    "enabled": false,
    "provider": "openai",
    "model": "gpt-4o-mini",
    "custom_instructions": "",
    "providers": {}
  },
  "audio": {
    "device": null,
    "sample_rate": 16000
  },
  "dictionary": [],
  "clipboard": {
    "default_behavior": "restore"
  }
}
```

### Security Scope

**In Scope:**
- ✅ API keys masked in UI
- ✅ Config file permissions guidance in README
- ✅ No API keys logged to console/files

**Out of Scope:**
- ❌ Encrypted key storage (Windows Credential Manager) — future enhancement
- ❌ Authentication/authorization (single-user desktop app)

---

## 10. API Specification

Not applicable — ASR Everywhere is a desktop application, not a service. It *consumes* external APIs but does not expose any.

### External API Usage Pattern

All ASR and LLM calls follow the OpenAI API pattern:

```python
# ASR Transcription
client = openai.OpenAI(api_key=key, base_url=base_url)
transcript = client.audio.transcriptions.create(
    model=model,
    file=audio_file,
    language=language,  # or omit for auto-detect
    prompt=dictionary_terms_joined,  # hint for proper nouns
)

# LLM Post-Processing
response = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": raw_transcription},
    ],
)
```

---

## 11. Success Criteria

### MVP Success Definition
A user can install the application via `pip install`, configure an ASR provider with their API key, press a hotkey, dictate text, and have it appear at their cursor position — in under 5 seconds from pressing stop to text insertion (excluding network latency).

### Functional Requirements
- ✅ Global hotkey works in toggle mode from any application
- ✅ Global hotkey works in push-to-talk mode
- ✅ Audio is recorded from the selected microphone
- ✅ Audio is transcribed via at least 3 different providers (OpenAI, Together.ai, local)
- ✅ Transcribed text is inserted at the current cursor position
- ✅ Two clipboard behaviors work correctly (restore vs. keep)
- ✅ LLM post-processing cleans up text when enabled
- ✅ Dictionary terms are respected in transcription
- ✅ Language auto-detection works for German and English
- ✅ Settings UI allows full configuration without editing JSON
- ✅ Visual recording indicator is visible in System Tray

### Quality Indicators
- No audio data is sent to unintended endpoints
- Application starts in < 3 seconds
- Memory usage stays below 200 MB during recording
- No crashes on standard Windows 10/11 setups

### User Experience Goals
- Zero-learning-curve: press hotkey, talk, done
- Settings are discoverable and self-explanatory
- Visual feedback at every state transition (idle → recording → processing → done)

---

## 12. Implementation Phases

### Phase 1: Core Recording & Transcription (Foundation)
**Goal:** Get the basic record → transcribe → insert pipeline working with one provider.

**Deliverables:**
- ✅ Project scaffolding (`pyproject.toml`, directory structure)
- ✅ Audio recording from default microphone (`sounddevice`)
- ✅ OpenAI Whisper API integration (single provider)
- ✅ Text insertion via clipboard + Ctrl+V simulation
- ✅ Single hardcoded hotkey (toggle mode)
- ✅ Basic System Tray icon (idle/recording states)
- ✅ JSON config file (API key, basic settings)

**Validation:** User can press hotkey, dictate, and see text appear in Notepad.

**Estimated effort:** 1–2 weeks

### Phase 2: Multi-Provider & Settings UI
**Goal:** Add provider abstraction, multiple ASR backends, and a settings GUI.

**Deliverables:**
- ✅ ASR provider abstraction layer (base class + registry)
- ✅ OpenAI-compatible provider (Together.ai, HF, OpenRouter, local)
- ✅ Settings window (tkinter): provider selection, API keys, hotkey config
- ✅ Configurable hotkeys (toggle + push-to-talk)
- ✅ Dual hotkey support (restore clipboard vs. keep)
- ✅ Microphone device selection
- ✅ Language selection + auto-detect

**Validation:** User can switch between providers in Settings and dictate successfully with each.

**Estimated effort:** 1–2 weeks

### Phase 3: LLM Post-Processing & Dictionary
**Goal:** Add optional text cleanup via LLM and custom dictionary support.

**Deliverables:**
- ✅ LLM post-processing pipeline (enable/disable, provider/model selection)
- ✅ Custom instructions UI (text area in settings)
- ✅ Dictionary management (add/remove terms in settings)
- ✅ Dictionary injection into ASR prompt and LLM system prompt
- ✅ Processing state indicator in tray icon

**Validation:** Dictated text with filler words is cleaned up; custom terms are correctly spelled.

**Estimated effort:** 1 week

### Phase 4: Polish & Distribution
**Goal:** Finalize UX, documentation, and distribution.

**Deliverables:**
- ✅ Error handling & user-friendly error messages (API failures, mic issues)
- ✅ README with installation & setup guide
- ✅ PyPI-ready packaging (`pip install asr-everywhere`)
- ✅ Icon design (idle, recording, processing states)
- ✅ Edge case handling (no mic, no API key, network timeout)
- ✅ Basic test suite

**Validation:** Clean install on fresh Windows machine via `pip install asr-everywhere` works end-to-end.

**Estimated effort:** 1 week

---

## 13. Future Considerations

### Post-MVP Enhancements
- **Real-time Streaming Transcription** — Show partial text as user speaks (requires WebSocket-based ASR providers like Deepgram or local streaming Whisper).
- **Transcription History** — Searchable log of past dictations with timestamps.
- **Standalone .exe** — Package via PyInstaller/Nuitka for users who don't want Python installed.
- **Autostart with Windows** — Option to launch at login via registry/startup folder.
- **Encrypted API Key Storage** — Use Windows Credential Manager for secure key storage.

### Integration Opportunities
- **VS Code Extension** — Tighter integration with IDE context (e.g. "dictate into current file").
- **Clipboard Manager Integration** — Work alongside tools like Ditto.
- **Webhook / Custom Actions** — Trigger custom scripts after transcription.

### Advanced Features
- **Multi-language auto-switch** — Seamlessly handle mixed German/English dictation in a single recording.
- **Speaker diarization** — Identify different speakers (for meeting notes use case).
- **Voice commands** — "New paragraph", "delete last sentence", etc.
- **Additional languages** beyond DE/EN.

---

## 14. Risks & Mitigations

| # | Risk | Impact | Mitigation |
|---|---|---|---|
| 1 | **Global hotkey conflicts** — `WIN+U` or other combos may conflict with OS or other apps. | User can't activate recording. | Make hotkeys fully configurable; detect conflicts and warn user. Document known conflicts. |
| 2 | **Clipboard manipulation breaks user workflow** — Overwriting clipboard during dictation may lose important content. | User frustration, data loss. | Implement save/restore clipboard pattern. Dual hotkey system gives user explicit control. |
| 3 | **ASR provider API changes** — Third-party APIs may change endpoints, models, or pricing. | Transcription breaks silently. | Abstract providers behind interface; graceful error handling with clear messages; easy config update. |
| 4 | **Audio capture issues** — Some apps/drivers block exclusive microphone access; UAC may restrict global hotkeys. | Recording fails in certain contexts. | Use shared-mode audio capture; document known limitations; fall back to system default device. |
| 5 | **Latency perceived as too slow** — Batch mode + API call + optional LLM = multiple seconds of wait. | Poor user experience. | Show processing indicator; optimize audio encoding; allow disabling LLM for faster results; consider streaming in future. |

---

## 15. Appendix

### Key Dependencies & Links

| Dependency | Link |
|---|---|
| `sounddevice` | https://python-sounddevice.readthedocs.io |
| `openai` Python SDK | https://github.com/openai/openai-python |
| `keyboard` | https://github.com/boppreh/keyboard |
| `pystray` | https://github.com/moses-palmer/pystray |
| `pynput` | https://github.com/moses-palmer/pynput |
| `pyperclip` | https://github.com/asweigart/pyperclip |
| `Pillow` | https://python-pillow.org |
| OpenAI Audio API | https://platform.openai.com/docs/guides/speech-to-text |
| Together.ai API | https://docs.together.ai |
| Hugging Face Inference | https://huggingface.co/docs/api-inference |
| OpenRouter API | https://openrouter.ai/docs |
| Ollama API | https://github.com/ollama/ollama/blob/main/docs/openai.md |

### Inspiration

- [Aqua Voice](https://aquavoice.com) — macOS dictation app with similar concept (Custom Instructions, Dictionary, multi-language)
- [Whisper Key](https://github.com/PinW/whisper-key-local) — Simple local STT for Windows with global hotkey

### Repository Structure

```
c:\Users\scep\Documents\repos\asr-everywhere_windows\
├── docs/
│   └── PRD.md          ← This document
├── src/
│   └── ...
├── tests/
├── assets/
├── pyproject.toml
└── README.md
```
