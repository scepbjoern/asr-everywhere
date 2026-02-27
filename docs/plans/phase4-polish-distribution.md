# Feature: Phase 4 - Polish & Distribution

The following plan should be complete, but it's important that you validate documentation and codebase patterns and task sanity before you start implementing.

Pay special attention to naming of existing utils types and models. Import from the right files etc.

## Feature Description

Phase 4 is the final polish phase that transforms ASR Everywhere from a functional prototype into a production-ready, PyPI-distributable package. This phase focuses on four key areas: robust error handling with user-friendly messages, comprehensive documentation, proper icon assets, and PyPI packaging readiness.

## User Story

**As a** new user wanting to try ASR Everywhere  
**I want to** install it via `pip install asr-everywhere` and have it work reliably with clear error messages when something goes wrong  
**So that** I can quickly get started with voice dictation without troubleshooting cryptic errors

## Problem Statement

The current implementation has:
- Basic error handling that surfaces raw exception messages to users
- Dynamically generated tray icons (colored circles) instead of professional assets
- A minimal README without detailed setup instructions
- Untested PyPI packaging configuration

Users encountering issues (no mic, no API key, network timeout) receive unhelpful error messages, and the application lacks a professional appearance.

## Solution Statement

Implement comprehensive error handling with categorized error types and user-friendly messages, create professional tray icons for all three states (idle, recording, processing), enhance the README with detailed setup instructions, and verify PyPI packaging is complete and functional.

## Feature Metadata

**Feature Type**: Enhancement/Polish
**Estimated Complexity**: Medium
**Primary Systems Affected**: 
- `transcription_pipeline.py` (error handling)
- `audio_recorder.py` (error handling)
- `providers/*.py` (error handling)
- `ui/tray.py` (icon loading)
- `README.md` (documentation)
- `pyproject.toml` (packaging verification)
- `assets/` (icon files)

**Dependencies**: Pillow for icon handling (already installed)

---

## CONTEXT REFERENCES

### Relevant Codebase Files - IMPORTANT: YOU MUST READ THESE FILES BEFORE IMPLEMENTING!

- `src/asr_everywhere/transcription_pipeline.py` (lines 67-144) - Why: Contains main error handling logic, needs enhancement for categorized errors
- `src/asr_everywhere/audio_recorder.py` (lines 49-76) - Why: Audio recording error handling, needs mic detection validation
- `src/asr_everywhere/providers/openai_provider.py` (lines 70-80) - Why: API error handling pattern to enhance
- `src/asr_everywhere/providers/openai_compat.py` (lines 93-103) - Why: Provider error handling pattern
- `src/asr_everywhere/ui/tray.py` (lines 60-87) - Why: Icon creation logic, needs to load from files instead of generating
- `src/asr_everywhere/app.py` (lines 47-102) - Why: Initialization error handling
- `src/asr_everywhere/config.py` (lines 199-278) - Why: Config loading error handling
- `pyproject.toml` - Why: Packaging configuration to verify
- `README.md` - Why: Documentation to enhance
- `tests/test_regression.py` - Why: Existing test patterns to follow

### New Files to Create

- `assets/icon_idle.ico` - System tray icon for idle state
- `assets/icon_recording.ico` - System tray icon for recording state  
- `assets/icon_processing.ico` - System tray icon for processing state
- `tests/test_error_handling.py` - Unit tests for error handling scenarios

### Relevant Documentation - YOU SHOULD READ THESE BEFORE IMPLEMENTING!

- [Python Packaging User Guide - pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
  - Section: A full example
  - Why: Reference for complete pyproject.toml structure

### Patterns to Follow

**Error Handling Pattern (from `transcription_pipeline.py`):**
```python
try:
    # Operation
except Exception as e:
    logger.error(f"Operation failed: {e}")
    self._tray.show_notification("Error", str(e)[:200])
```

**Tray Icon Pattern (from `tray.py`):**
```python
def _create_icon(self, color: str) -> Image.Image:
    size = 64
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse([margin, margin, size - margin, size - margin], fill=color)
    return image
```

**Logging Pattern:**
```python
logger = logging.getLogger(__name__)
logger.info(f"Operation description: {details}")
logger.error(f"Failed to X: {e}")
```

**Test Pattern (from `test_regression.py`):**
```python
def test_error_case(self, mock_components):
    """Test description."""
    with mock.patch("module.function") as mock_func:
        mock_func.side_effect = Exception("Error")
        # Should not raise
        result = some_operation()
        # Verify graceful handling
```

---

## IMPLEMENTATION PLAN

### Phase 1: Error Categories and User-Friendly Messages

**Goal**: Define error categories and create user-friendly error messages for all failure scenarios.

**Tasks:**

1. **Create error handling module** (`src/asr_everywhere/errors.py`)
   - Define error categories: `ConfigError`, `AudioError`, `ProviderError`, `NetworkError`
   - Create `get_user_message(exception)` function that maps exceptions to friendly messages
   - Include actionable guidance in each message (e.g., "Check your API key in Settings")

2. **Define error message mappings**:
   | Error Type | User Message |
   |------------|--------------|
   | No API key | "No API key configured. Open Settings and add your API key." |
   | Invalid API key | "API key rejected. Please check your key in Settings." |
   | Network timeout | "Network error. Check your internet connection." |
   | No microphone | "No microphone found. Connect a microphone and restart." |
   | Mic access denied | "Microphone access denied. Check Windows privacy settings." |
   | ASR API error | "Transcription service error. Try again or switch providers." |
   | LLM API error | "LLM post-processing failed. Using raw transcription." |
   | Clipboard error | "Clipboard error. Text may not have been inserted." |

### Phase 2: Enhance Error Handling in Components

**Goal**: Update all components to use categorized error handling with user-friendly messages.

**Tasks:**

1. **Update `audio_recorder.py`**:
   - Add validation in `start_recording()` for microphone availability
   - Catch `sounddevice.PortAudioError` and raise `AudioError` with friendly message
   - Add method `check_microphone_available()` for proactive validation

2. **Update `providers/openai_provider.py` and `openai_compat.py`**:
   - Wrap API calls with specific exception handling
   - Map `openai.AuthenticationError` → `ProviderError` with "Invalid API key" message
   - Map `openai.APIConnectionError` → `NetworkError` with "Network error" message
   - Map `openai.RateLimitError` → `ProviderError` with "Rate limit exceeded" message
   - Map `openai.APIStatusError` → `ProviderError` with "Service error" message

3. **Update `transcription_pipeline.py`**:
   - Import `get_user_message` from errors module
   - Replace generic error messages with categorized ones
   - Add specific handling for `AudioError`, `ProviderError`, `NetworkError`
   - Ensure graceful degradation (LLM fails → use raw transcription)

4. **Update `app.py`**:
   - Add startup validation for microphone availability
   - Show warning notification if no microphone detected
   - Handle config loading errors gracefully

5. **Update `config.py`**:
   - Add validation for required config fields
   - Provide clear messages for config errors

### Phase 3: Professional Tray Icons

**Goal**: Replace dynamically generated icons with professional .ico files.

**Tasks:**

1. **Create icon assets**:
   - Design three icons: idle (green microphone), recording (red circle/pulse), processing (orange spinner/dots)
   - Required sizes: 16x16, 32x32, 48x48, 64x64, 256x256 (for high-DPI)
   - Export as .ico format with all sizes embedded

2. **Update `tray.py`**:
   - Add `_load_icon_from_file(filename: str) -> Image.Image` method
   - Fallback to generated icon if file not found (for dev mode)
   - Update `__init__` to load icons from `assets/` directory
   - Use `importlib.resources` or `pkgutil.get_data` for packaged resource loading

3. **Update `pyproject.toml`**:
   - Ensure assets are included in package via `tool.setuptools.package-data`

### Phase 4: README Enhancement

**Goal**: Create comprehensive installation and setup guide.

**Tasks:**

1. **Enhance README.md sections**:
   - **Features**: Keep existing, ensure complete
   - **Requirements**: Add Windows version specifics, Python version
   - **Installation**: Add detailed pip install instructions
   - **Quick Start**: Step-by-step first-use guide
   - **Configuration**: Explain config file location and structure
   - **Providers**: List supported providers with setup instructions
   - **Troubleshooting**: Common issues and solutions
   - **Development**: Keep existing, add test/lint commands

2. **Add troubleshooting section**:
   ```markdown
   ## Troubleshooting
   
   ### "No microphone found"
   - Connect a microphone and restart the app
   - Check Windows Settings → Privacy → Microphone
   
   ### "API key not configured"
   - Open Settings from the tray icon
   - Select your provider and enter the API key
   
   ### Hotkey not working
   - Check if another app is using the same hotkey
   - Change the hotkey in Settings
   ```

### Phase 5: PyPI Packaging Verification

**Goal**: Ensure package is ready for PyPI distribution.

**Tasks:**

1. **Verify `pyproject.toml` completeness**:
   - Check all required fields: name, version, description, readme, license
   - Verify classifiers are appropriate
   - Ensure all dependencies are listed with version constraints
   - Add `project.urls` for Homepage, Repository, Bug Tracker

2. **Add package data configuration**:
   ```toml
   [tool.setuptools.package-data]
   asr_everywhere = ["../../assets/*.ico"]
   ```

3. **Test build and install locally**:
   ```bash
   pip install build
   python -m build
   pip install dist/asr_everywhere-0.1.0-py3-none-any.whl
   ```

4. **Verify entry points work**:
   - Test `asr-everywhere` command
   - Test `python -m asr_everywhere`

### Phase 6: Test Coverage for Error Handling

**Goal**: Add comprehensive tests for error handling scenarios.

**Tasks:**

1. **Create `tests/test_error_handling.py`**:
   - Test microphone not available scenario
   - Test API key missing/invalid scenarios
   - Test network timeout scenarios
   - Test graceful degradation when LLM fails
   - Test error message truncation for tray notifications

2. **Update existing tests** if needed to accommodate error handling changes

---

## EDGE CASES TO HANDLE

1. **No microphone on startup**: Show notification, allow app to run (user may connect mic later)
2. **API key removed after startup**: Handle on next transcription attempt
3. **Network goes down during transcription**: Clear error message, suggest retry
4. **Clipboard contains large data**: Handle gracefully, don't crash
5. **Config file corrupted**: Regenerate defaults, notify user
6. **Icon files missing**: Fallback to generated icons (dev mode)
7. **Very long transcription**: Truncate notification message (already handled at 200 chars)
8. **Hotkey conflicts**: Detect and warn (future enhancement, document in README for now)

---

## VALIDATION

### Manual Testing Checklist

- [ ] Fresh `pip install` works without errors
- [ ] `asr-everywhere` command launches app
- [ ] App shows clear error when no API key configured
- [ ] App shows clear error when no microphone available
- [ ] App shows clear error when network is unavailable
- [ ] App shows clear error when API key is invalid
- [ ] Tray icons display correctly (not blurry)
- [ ] README instructions are accurate and complete
- [ ] Settings can be opened and saved
- [ ] Transcription works end-to-end

### Automated Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/asr_everywhere --cov-report=term-missing

# Run linting
ruff check src/ tests/
ruff format --check src/ tests/
```

### Build Verification

```bash
# Build package
python -m build

# Verify wheel contents
python -m zipfile -l dist/asr_everywhere-0.1.0-py3-none-any.whl

# Install and test
pip install dist/asr_everywhere-0.1.0-py3-none-any.whl
asr-everywhere
```

---

## FILES MODIFIED/CREATED SUMMARY

| File | Action | Purpose |
|------|--------|---------|
| `src/asr_everywhere/errors.py` | Create | Error categories and user messages |
| `src/asr_everywhere/audio_recorder.py` | Modify | Enhanced error handling |
| `src/asr_everywhere/providers/openai_provider.py` | Modify | API error mapping |
| `src/asr_everywhere/providers/openai_compat.py` | Modify | API error mapping |
| `src/asr_everywhere/transcription_pipeline.py` | Modify | Use categorized errors |
| `src/asr_everywhere/app.py` | Modify | Startup validation |
| `src/asr_everywhere/ui/tray.py` | Modify | Load icons from files |
| `assets/icon_idle.ico` | Create | Idle state icon |
| `assets/icon_recording.ico` | Create | Recording state icon |
| `assets/icon_processing.ico` | Create | Processing state icon |
| `README.md` | Modify | Enhanced documentation |
| `pyproject.toml` | Modify | Package data config, URLs |
| `tests/test_error_handling.py` | Create | Error handling tests |

---

## IMPLEMENTATION ORDER

1. **errors.py** - Foundation for all error handling
2. **audio_recorder.py** - Microphone validation
3. **providers/*.py** - API error mapping
4. **transcription_pipeline.py** - Integrate error handling
5. **app.py** - Startup validation
6. **tray.py** - Icon loading
7. **assets/*.ico** - Create icon files
8. **README.md** - Documentation
9. **pyproject.toml** - Packaging verification
10. **tests/test_error_handling.py** - Test coverage

---

## NOTES

- Icon design can be simple but professional - consider using a microphone symbol
- Error messages should be actionable (tell user what to do)
- Keep error handling consistent across all components
- Test with actual API calls (mocked) to ensure error mapping works
- Consider adding a "Check for updates" feature in future (out of scope for Phase 4)
