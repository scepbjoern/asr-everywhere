---
description: Initialize ASR Everywhere development environment
---
# Initialize Project

Run the following steps to set up the ASR Everywhere development environment on Windows.

## Prerequisites

- **Python ≥ 3.11** — See `docs/python-setup.md` for installation instructions
- **Git** — For version control

## 1. Initialize Git Repository
```powershell
git init
git add .
git commit -m "Initial commit: project scaffolding"
```
Initializes version control and creates the first commit.

## 2. Create Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
Creates and activates a Python virtual environment.

## 3. Install Dependencies
```powershell
pip install -e ".[dev]"
```
Installs the package in editable mode with development dependencies (pytest, ruff).

## 4. Validate Installation
```powershell
# Check package is installed
pip show asr-everywhere

# Run tests
pytest tests/

# Run linter
ruff check src/ tests/
```

## 5. Run Application
```powershell
# Run as module
python -m asr_everywhere

# Or after install:
asr-everywhere
```

## Configuration

On first run, the app creates a default config at:
```
%APPDATA%\asr-everywhere\config.json
```

Edit via Settings UI (System Tray → Settings) or directly in JSON.

## Development Workflow

```powershell
# Format code
ruff format src/ tests/

# Run tests
pytest tests/

# Run with verbose output
pytest -v tests/
```

## Notes

- **Windows only** — Hotkeys, clipboard, and tray functionality are Windows-specific
- **API Keys** — Configure in Settings UI or directly in `config.json`
- **Microphone** — Select input device in Settings; defaults to system default
