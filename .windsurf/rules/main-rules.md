---
trigger: always_on
---

# ASR Everywhere — Global Rules

## Project Overview

**ASR Everywhere** (`asr-everywhere`) is a pip-installable Windows desktop application for system-wide voice-to-text dictation. It runs as a System Tray app, captures audio via configurable global hotkeys (toggle + push-to-talk), transcribes via multiple ASR providers (OpenAI, Together.ai, HF, OpenRouter, local/Ollama), optionally post-processes with an LLM, and inserts the result at the cursor position. See `docs/PRD.md` for full requirements.

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python ≥ 3.11 | Runtime |
| `sounddevice` | Microphone audio capture |
| `soundfile` | WAV encoding |
| `openai` SDK (≥ 1.0) | ASR & LLM API calls (OpenAI + compatible endpoints) |
| `httpx` | Async HTTP client |
| `keyboard` | Global hotkey registration |
| `pystray` | System Tray icon & context menu |
| `tkinter` (stdlib) | Settings GUI window |
| `pyperclip` | Clipboard read/write |
| `pynput` | Keystroke simulation (Ctrl+V) |
| `Pillow` | Tray icon image handling |

---

## Commands

```bash
# Install (editable dev mode)
pip install -e .

# Run
python -m asr_everywhere
# or after install:
asr-everywhere

# Test
pytest tests/

# Lint
ruff check src/ tests/
ruff format --check src/ tests/

# Format
ruff format src/ tests/
```

---

## Project Structure

```
asr-everywhere_windows/
├── docs/
│   └── PRD.md                          # Product Requirements Document
├── src/
│   └── asr_everywhere/
│       ├── __init__.py
│       ├── __main__.py                 # Entry point (python -m asr_everywhere)
│       ├── app.py                      # Application orchestrator
│       ├── config.py                   # JSON config load/save (%APPDATA%)
│       ├── hotkey_manager.py           # Global hotkey registration & events
│       ├── audio_recorder.py           # Microphone recording (sounddevice)
│       ├── text_inserter.py            # Clipboard + Ctrl+V simulation
│       ├── transcription_pipeline.py   # Audio → ASR → LLM → Insert
│       ├── providers/
│       │   ├── base.py                 # Abstract ASRProvider / LLMProvider
│       │   ├── openai_provider.py      # OpenAI direct
│       │   ├── openai_compat.py        # Generic OpenAI-compatible provider
│       │   └── registry.py             # Provider discovery & instantiation
│       ├── llm/
│       │   ├── post_processor.py       # LLM post-processing logic
│       │   └── prompts.py              # System prompts, dictionary injection
│       └── ui/
│           ├── tray.py                 # System Tray icon & menu (pystray)
│           └── settings_window.py      # Settings GUI (tkinter)
├── tests/
├── assets/
│   ├── icon_idle.ico
│   ├── icon_recording.ico
│   └── icon_processing.ico
├── pyproject.toml
└── README.md
```

---

## Architecture

### Data Flow

```
Hotkey Event → Audio Recorder → ASR Provider → (LLM Post-Processor) → Text Inserter
                                                                        ↓
                                                              Clipboard + Ctrl+V
```

### Key Patterns

- **Strategy Pattern** — ASR and LLM providers implement abstract base classes (`ASRProvider`, `LLMProvider`). The pipeline selects the active provider at runtime from config.
- **Event-Driven** — Hotkey events drive the recording lifecycle. State transitions (idle → recording → processing → idle) propagate through the app.
- **Pipeline Pattern** — Transcription flows through composable stages: Audio → ASR → optional LLM → Text Insertion.
- **Singleton Config** — One `Config` instance loaded at startup, mutated via Settings UI, persisted to `%APPDATA%/asr-everywhere/config.json`.

### Provider Abstraction

All ASR providers implement:
```python
class ASRProvider(ABC):
    def transcribe(self, audio_data: bytes, config: TranscriptionConfig) -> str: ...
    def list_models(self) -> list[str]: ...
```

OpenAI-compatible providers (Together.ai, HF, OpenRouter, Ollama, LibreChat) share one implementation (`OpenAICompatProvider`) with configurable `base_url` and `api_key`.

---

## Code Patterns

### Naming Conventions
- **Files**: `snake_case.py`
- **Classes**: `PascalCase` (e.g. `ASRProvider`, `HotkeyManager`, `TranscriptionPipeline`)
- **Functions/methods**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Config keys**: `snake_case` in JSON

### File Organization
- One primary class per module
- Imports at the top, grouped: stdlib → third-party → local
- Type hints on all public function signatures
- Docstrings on all public classes and methods

### Error Handling
- Wrap external API calls in try/except; surface user-friendly error messages via tray notification or settings UI
- Never log or display API keys
- Graceful degradation: if ASR fails, show error; if LLM post-processing fails, insert raw transcription

### Configuration
- All settings in `%APPDATA%/asr-everywhere/config.json`
- API keys stored as plaintext in JSON (user responsibility)
- Default config generated on first run
- Config schema versioned (`"version": 1`)

---

## Testing

- **Run tests**: `pytest tests/`
- **Test location**: `tests/`
- **Pattern**: Unit tests per module (`test_config.py`, `test_providers.py`, `test_pipeline.py`, `test_hotkey.py`)
- **Mocking**: Mock external API calls and audio devices; never make real API calls in tests
- **Framework**: `pytest` with `pytest-mock` for mocking

---

## Validation

Before committing, run:
```bash
ruff check src/ tests/
ruff format --check src/ tests/
pytest tests/
```

---

## Key Files

| File | Purpose |
|------|---------|
| `docs/PRD.md` | Full product requirements, architecture, and implementation phases |
| `src/asr_everywhere/app.py` | Main application orchestrator — wires everything together |
| `src/asr_everywhere/config.py` | Config schema, loading, saving, defaults |
| `src/asr_everywhere/providers/base.py` | Abstract interfaces for ASR and LLM providers |
| `src/asr_everywhere/providers/registry.py` | Maps provider names to implementations |
| `src/asr_everywhere/transcription_pipeline.py` | Core pipeline: record → transcribe → post-process → insert |
| `pyproject.toml` | Package metadata, dependencies, entry points |

---

## On-Demand Context

| Topic | File |
|-------|------|
| Full requirements & scope | `docs/PRD.md` |
| Config JSON schema example | `docs/PRD.md` (Section 9) |
| ASR provider interface | `docs/PRD.md` (Section 7.3) |
| LLM prompt structure | `docs/PRD.md` (Section 7.4) |

---

## Notes

- **Windows only** — All OS-specific code (hotkeys, clipboard, tray) targets Windows 10/11
- **No offline mode** — All ASR/LLM calls go through APIs (local APIs like Ollama still require a running local server)
- **Clipboard safety** — Always save clipboard before overwriting; restore based on hotkey used
- **Languages** — German and English only; auto-detect supported
- **No history, no file tagging, no replacements** — Keep scope minimal per PRD