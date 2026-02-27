# ASR Everywhere

A lightweight Windows desktop application for system-wide voice-to-text dictation.

## Features

- **Global Hotkeys**: Toggle mode (press to start/stop) and push-to-talk mode
- **Multiple ASR Providers**: OpenAI, Together.ai, Hugging Face, OpenRouter, local APIs
- **LLM Post-Processing**: Optional text cleanup and formatting
- **Dictionary Support**: Custom terms for proper nouns and technical vocabulary
- **System Tray UI**: Minimal interface with settings window
- **Multi-language**: German and English with auto-detection

## Requirements

- **Operating System**: Windows 10 or Windows 11
- **Microphone**: Any audio input device
- **Internet Connection**: Required for ASR/LLM API calls

## Installation

### Download Installer (Recommended for Non-Developers)

Download the latest installer from the [Releases page](https://github.com/scepbjoern/asr-everywhere/releases):

1. Download `asr-everywhere-setup.exe`
2. Run the installer and follow the wizard
3. Launch from Start Menu or Desktop shortcut

**Note**: The standalone EXE does not require Python to be installed.

### From PyPI (For Python Users)

```powershell
pip install asr-everywhere
```

### From Source (Development)

```powershell
# Clone the repository
git clone https://github.com/your-repo/asr-everywhere.git
cd asr-everywhere

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

## Quick Start

1. **Launch the application**:
   ```powershell
   asr-everywhere
   ```
   Or using Python:
   ```powershell
   python -m asr_everywhere
   ```

2. **Configure your API key**:
   - Right-click the system tray icon (green microphone)
   - Select "Settings"
   - Choose your ASR provider and enter your API key
   - Click "Save"

3. **Start dictating**:
   - Press `WIN+CTRL+A` (default hotkey) to start recording
   - Speak into your microphone
   - Press `WIN+CTRL+A` again to stop and transcribe
   - The transcribed text appears at your cursor position

## Configuration

Configuration is stored in: `%APPDATA%\asr-everywhere\config.json`

### Hotkey Modes

- **Toggle Mode**: Press once to start recording, press again to stop
- **Push-to-Talk Mode**: Hold the hotkey while speaking, release to stop

Change modes via the tray menu or settings window.

### Supported ASR Providers

| Provider | API Key Required | Models |
|----------|-----------------|--------|
| OpenAI | Yes | whisper-1, gpt-4o-transcribe, gpt-4o-mini-transcribe |
| Together.ai | Yes | openai/whisper-large-v3 |
| Hugging Face | Yes | openai/whisper-large-v3-turbo, openai/whisper-large-v3 |
| Local (Ollama) | No | User-configured |

### LLM Post-Processing

Enable LLM post-processing in Settings to:
- Fix grammar and punctuation
- Apply custom formatting instructions
- Use dictionary terms for consistent spelling

## Troubleshooting

### "No microphone found"

- Connect a microphone and restart the application
- Check Windows Settings → Privacy → Microphone
- Ensure microphone access is enabled for desktop apps

### "API key not configured"

- Open Settings from the tray icon
- Select your ASR provider
- Enter your API key in the designated field
- Click Save

### "API key rejected"

- Verify your API key is correct
- Check if your API key has expired
- Ensure your account has available credits
- For OpenAI: Check at [platform.openai.com](https://platform.openai.com/api-keys)

### "Network error"

- Check your internet connection
- Verify your firewall isn't blocking the application
- Try a different network if on corporate VPN

### Hotkey not working

- Check if another application is using the same hotkey
- Change the hotkey in Settings to a different combination
- Run the application as administrator if needed

### Transcription quality issues

- Speak clearly and at a moderate pace
- Use a quality microphone in a quiet environment
- Add technical terms to the Dictionary in Settings
- Try a different ASR model or provider

## Development

### Running Tests

```powershell
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/asr_everywhere --cov-report=term-missing

# Run regression tests
pytest tests/test_regression.py -v
```

### Code Quality

```powershell
# Lint
ruff check src/ tests/

# Format
ruff format src/ tests/

# Format check
ruff format --check src/ tests/
```

### Building

```powershell
# Install build tools
pip install build

# Build package
python -m build

# Verify wheel contents
python -m zipfile -l dist/asr_everywhere-0.1.0-py3-none-any.whl
```

### Building Standalone EXE

```powershell
# Install dev dependencies (includes PyInstaller)
pip install -e ".[dev]"

# Build EXE
python scripts/build_exe.py

# Test EXE
.\dist\asr-everywhere.exe
```

### Building Windows Installer

Prerequisites:
- [Inno Setup 6](https://jrsoftware.org/isinfo.php) installed

```powershell
# Build EXE first
python scripts/build_exe.py

# Build installer
iscc installer/setup.iss

# Output: dist/installer/asr-everywhere-setup.exe
```

## Project Structure

```
asr-everywhere/
├── src/asr_everywhere/
│   ├── app.py                 # Main application
│   ├── config.py              # Configuration management
│   ├── audio_recorder.py      # Microphone recording
│   ├── transcription_pipeline.py  # ASR workflow
│   ├── text_inserter.py       # Clipboard + Ctrl+V
│   ├── hotkey_manager.py      # Global hotkeys
│   ├── errors.py              # Error handling
│   ├── providers/             # ASR providers
│   ├── llm/                   # LLM post-processing
│   └── ui/                    # Tray icon, settings
├── assets/                    # Icons
├── tests/                     # Test suite
└── docs/                      # Documentation
```

## License

MIT License - See [LICENSE](LICENSE) for details.
