# ASR Everywhere

A lightweight Windows desktop application for system-wide voice-to-text dictation.

## Features

- **Global Hotkeys**: Toggle mode (press to start/stop) and push-to-talk mode
- **Multiple ASR Providers**: OpenAI, Together.ai, Hugging Face, OpenRouter, local APIs
- **LLM Post-Processing**: Optional text cleanup and formatting
- **Dictionary Support**: Custom terms for proper nouns and technical vocabulary
- **System Tray UI**: Minimal interface with settings window
- **Multi-language**: German and English with auto-detection

## Installation

```powershell
pip install asr-everywhere
```

## Usage

1. Launch: `asr-everywhere` or `python -m asr_everywhere`
2. Configure API keys via System Tray → Settings
3. Press hotkey (default: `WIN+U`) to start/stop recording
4. Transcribed text appears at cursor position

## Development

```powershell
# Clone and setup
git clone https://github.com/your-repo/asr-everywhere.git
cd asr-everywhere
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"

# Run tests
pytest tests/

# Lint
ruff check src/ tests/
```

## Configuration

Config file: `%APPDATA%\asr-everywhere\config.json`

## Requirements

- Windows 10/11
- Python ≥ 3.11
- Microphone

## License

MIT
