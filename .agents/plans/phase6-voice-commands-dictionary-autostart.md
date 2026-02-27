# Feature: Phase 6 - Voice Commands, Dictionary Enhancement & Autostart

The following plan should be complete, but its important that you validate documentation and codebase patterns and task sanity before you start implementing.

Pay special attention to naming of existing utils types and models. Import from the right files etc.

## Feature Description

Phase 6 adds three enhancements to ASR Everywhere:

1. **Voice Commands**: Hands-free formatting control during dictation via spoken commands (e.g., "Punkt", "Neuer Absatz", "Delete that"). Commands are processed by the LLM post-processor.

2. **Dictionary Enhancement**: Ensures dictionary terms work correctly with all ASR providers. When using non-OpenAI providers (Together.ai, HuggingFace) without LLM post-processing, the user receives a warning that dictionary terms won't affect transcription accuracy.

3. **Autostart with Windows**: EXE-only feature to launch the app automatically at Windows login via Registry Run Key.

## User Stories

### Voice Commands
As a user, I want to use voice commands during dictation (e.g., "New paragraph", "Punkt", "Delete that") so that I can control formatting and make corrections without touching the keyboard.

### Dictionary Enhancement
As a user, I want to be warned when my dictionary terms won't affect transcription (non-OpenAI provider without LLM post-processing) so that I understand the limitations and can enable LLM post-processing if needed.

### Autostart
As a user (EXE-only), I want ASR Everywhere to start automatically when I log in to Windows so that I don't have to manually launch it every time I restart my computer.

## Problem Statement

- Users cannot control formatting hands-free during dictation
- Dictionary terms don't work with non-OpenAI ASR providers when LLM post-processing is disabled, but users aren't warned
- Users must manually launch the app after every Windows restart

## Solution Statement

1. Extend LLM system prompt with voice command definitions; add toggle in Settings UI
2. Add conditional warning in Settings UI when dictionary has entries, LLM is disabled, and ASR provider doesn't support `prompt` parameter
3. Implement Registry Run Key management with Settings UI toggle (EXE-only)

## Feature Metadata

**Feature Type**: Enhancement
**Estimated Complexity**: Medium
**Primary Systems Affected**: `llm/prompts.py`, `config.py`, `ui/settings_window.py`, `providers/openai_compat.py`
**Dependencies**: `winreg` (stdlib, for autostart)

---

## CONTEXT REFERENCES

### Relevant Codebase Files IMPORTANT: YOU MUST READ THESE FILES BEFORE IMPLEMENTING!

- `src/asr_everywhere/llm/prompts.py` (lines 1-32) - Why: Contains `build_system_prompt()` that must be extended for voice commands
- `src/asr_everywhere/config.py` (lines 76-96) - Why: `LLMConfig` dataclass needs `voice_commands_enabled` field; needs `AutostartConfig` dataclass
- `src/asr_everywhere/ui/settings_window.py` (lines 175-252, 583-594) - Why: LLM tab needs voice commands toggle; `_update_dict_warning()` needs enhancement
- `src/asr_everywhere/providers/openai_compat.py` (lines 86-94) - Why: Shows current dictionary handling for non-OpenAI providers
- `src/asr_everywhere/llm/post_processor.py` (lines 44-50) - Why: Calls `provider.post_process()` with dictionary; may need to pass voice_commands_enabled
- `src/asr_everywhere/transcription_pipeline.py` (lines 108-127) - Why: Shows how LLM post-processing integrates into pipeline

### New Files to Create

- None (all changes to existing files)

### Relevant Documentation YOU SHOULD READ THESE BEFORE IMPLEMENTING!

- [Python winreg documentation](https://docs.python.org/3/library/winreg.html)
  - Section: `HKEY_CURRENT_USER` and `OpenKey`/`SetValueEx`
  - Why: Required for autostart registry implementation
- [Windows Registry Run Keys](https://learn.microsoft.com/en-us/windows/win32/setupapi/run-and-runonce-registry-keys)
  - Section: HKCU\Software\Microsoft\Windows\CurrentVersion\Run
  - Why: Standard location for per-user autostart entries

### Patterns to Follow

**Naming Conventions:**
- Config fields: `snake_case` (e.g., `voice_commands_enabled`)
- Dataclass fields: `snake_case`
- Methods: `snake_case` (e.g., `_update_dict_warning()`)

**Error Handling:**
- Wrap external calls (registry) in try/except
- Log errors with `logger.error()`
- Graceful degradation (autostart toggle fails silently, shows error in UI)

**Logging Pattern:**
```python
logger = logging.getLogger(__name__)
logger.debug(f"Voice commands enabled: {enabled}")
logger.info("LLM post-processing complete")
logger.warning(f"Dictionary with {len(dictionary)} terms provided, but provider does not support prompt")
```

**Config Pattern:**
- Add new fields to dataclass with default values
- Update `load_config()` to read new fields with `.get()` fallback
- Update `save_config()` - automatically handles new fields via `asdict()`

---

## IMPLEMENTATION PLAN

### Phase 1: Config Schema Extension

Add new configuration fields to support voice commands and autostart.

**Tasks:**

1. UPDATE `src/asr_everywhere/config.py`
   - ADD `voice_commands_enabled: bool = True` to `LLMConfig` dataclass (after `custom_instructions`)
   - ADD `AutostartConfig` dataclass with `enabled: bool = True`
   - ADD `autostart: AutostartConfig = field(default_factory=AutostartConfig)` to `Config` dataclass
   - UPDATE `load_config()` to read `llm.voice_commands_enabled` with default `True`
   - UPDATE `load_config()` to read `autostart.enabled` with default `True`
   - PATTERN: See `LLMConfig` at lines 76-96 for dataclass pattern
   - VALIDATE: `python -c "from asr_everywhere.config import Config; c = Config(); print(c.llm.voice_commands_enabled, c.autostart.enabled)"`

### Phase 2: Voice Commands Implementation

Extend LLM prompt system to support voice commands.

**Tasks:**

2. UPDATE `src/asr_everywhere/llm/prompts.py`
   - ADD `VOICE_COMMANDS_PROMPT` constant with command definitions (bilingual DE/EN)
   - UPDATE `build_system_prompt()` signature to accept `voice_commands_enabled: bool = True`
   - UPDATE `build_system_prompt()` to append voice commands section when enabled
   - PATTERN: See `build_system_prompt()` at lines 13-31
   - VALIDATE: `python -m pytest tests/test_prompts.py -v`

3. UPDATE `src/asr_everywhere/llm/post_processor.py`
   - UPDATE `process()` method to pass `voice_commands_enabled` to prompt builder
   - Need to access `self._config.llm.voice_commands_enabled`
   - PATTERN: See `provider.post_process()` call at lines 46-50
   - VALIDATE: `python -m pytest tests/test_post_processor.py -v`

4. UPDATE `src/asr_everywhere/llm/base.py` (if needed)
   - Check if `post_process()` signature needs `voice_commands_enabled` parameter
   - If yes, update abstract method and all implementations

### Phase 3: Dictionary Warning Enhancement

Improve user feedback when dictionary won't work with current configuration.

**Tasks:**

5. UPDATE `src/asr_everywhere/ui/settings_window.py`
   - UPDATE `_update_dict_warning()` method (lines 583-594)
   - New logic: Show warning if:
     - `dictionary` has entries AND
     - `llm.enabled == False` AND
     - ASR provider in `{"together", "huggingface"}`
   - Warning text: "⚠️ Dictionary terms require LLM post-processing for this provider. Enable LLM post-processing to use dictionary terms."
   - Call `_update_dict_warning()` after LLM enabled checkbox changes
   - PATTERN: See existing `_update_dict_warning()` at lines 583-594
   - VALIDATE: Manual testing in Settings UI

### Phase 4: Voice Commands UI

Add toggle for voice commands in Settings UI.

**Tasks:**

6. UPDATE `src/asr_everywhere/ui/settings_window.py`
   - ADD `_voice_commands_var: tk.BooleanVar` in `_create_llm_tab()` (after LLM enabled checkbox)
   - ADD checkbox "Enable voice commands" below LLM enabled checkbox
   - Checkbox only enabled when LLM is enabled (grayed out otherwise)
   - UPDATE `_on_llm_enabled_change()` to also enable/disable voice commands checkbox
   - UPDATE `_on_save_click()` to save `voice_commands_enabled` to config
   - ADD to `_cleanup_vars()` list
   - PATTERN: See `_llm_enabled_var` handling at lines 181-188, 332-342
   - VALIDATE: Manual testing in Settings UI

### Phase 5: Autostart Implementation

Implement Windows autostart via Registry Run Key.

**Tasks:**

7. CREATE `src/asr_everywhere/autostart.py`
   - IMPLEMENT `is_exe() -> bool` - Check if running as compiled EXE (`getattr(sys, 'frozen', False)`)
   - IMPLEMENT `is_autostart_enabled() -> bool` - Check registry key exists
   - IMPLEMENT `enable_autostart() -> bool` - Create registry entry
   - IMPLEMENT `disable_autostart() -> bool` - Remove registry entry
   - Registry path: `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
   - Entry name: `"ASR Everywhere"`
   - Entry value: Full path to EXE
   - Use `winreg` module (stdlib)
   - Wrap all registry operations in try/except, return False on error
   - VALIDATE: `python -c "from asr_everywhere.autostart import is_exe; print(is_exe())"`

8. UPDATE `src/asr_everywhere/ui/settings_window.py`
   - ADD new tab "System" or add autostart section to "Language" tab
   - ADD `_autostart_var: tk.BooleanVar` (only visible if `is_exe()` is True)
   - ADD checkbox "Start with Windows" 
   - Load current state from `is_autostart_enabled()` and `config.autostart.enabled`
   - UPDATE `_on_save_click()` to save autostart preference and update registry
   - ADD to `_cleanup_vars()` list
   - PATTERN: See checkbox pattern in `_create_llm_tab()` at lines 181-188
   - VALIDATE: Manual testing in Settings UI (EXE mode only)

9. UPDATE `src/asr_everywhere/app.py` (optional)
   - On startup, sync registry state with config (if EXE mode)
   - If `config.autostart.enabled` differs from registry, update registry
   - This handles case where user manually deleted registry entry

### Phase 6: Testing

Add comprehensive tests for new functionality.

**Tasks:**

10. UPDATE `tests/test_prompts.py`
    - ADD test for `build_system_prompt()` with `voice_commands_enabled=True`
    - ADD test for `build_system_prompt()` with `voice_commands_enabled=False`
    - Verify voice commands section is present/absent
    - PATTERN: See existing tests at lines 6-45
    - VALIDATE: `python -m pytest tests/test_prompts.py -v`

11. CREATE `tests/test_autostart.py`
    - Mock `sys.frozen` to test `is_exe()`
    - Mock `winreg` to test registry operations
    - Test `enable_autostart()`, `disable_autostart()`, `is_autostart_enabled()`
    - VALIDATE: `python -m pytest tests/test_autostart.py -v`

12. UPDATE `tests/test_regression.py`
    - ADD regression tests for voice commands config default
    - ADD regression tests for autostart config default
    - PATTERN: See existing regression tests
    - VALIDATE: `python -m pytest tests/test_regression.py -v`

---

## TESTING STRATEGY

### Unit Tests

- `tests/test_prompts.py`: Voice commands prompt generation
- `tests/test_autostart.py`: Registry operations (mocked)
- `tests/test_config.py`: Config loading/saving with new fields

### Integration Tests

- Settings UI: Voice commands toggle affects LLM prompt
- Settings UI: Dictionary warning shows when appropriate
- Settings UI: Autostart toggle updates registry (requires EXE build)

### Regression Tests (MANDATORY)

**Every new feature MUST extend the regression test suite:**

```python
class TestPhase6Regression:
    """Regression tests for Phase 6 functionality."""
    
    def test_voice_commands_default_enabled(self, default_config):
        """Ensure voice commands are enabled by default."""
        assert default_config.llm.voice_commands_enabled == True
    
    def test_autostart_default_enabled(self, default_config):
        """Ensure autostart is enabled by default."""
        assert default_config.autostart.enabled == True
    
    def test_voice_commands_in_prompt_when_enabled(self):
        """Ensure voice commands appear in prompt when enabled."""
        from asr_everywhere.llm.prompts import build_system_prompt
        prompt = build_system_prompt("", [], voice_commands_enabled=True)
        assert "Voice Commands" in prompt or "voice command" in prompt.lower()
    
    def test_voice_commands_not_in_prompt_when_disabled(self):
        """Ensure voice commands don't appear in prompt when disabled."""
        from asr_everywhere.llm.prompts import build_system_prompt
        prompt = build_system_prompt("", [], voice_commands_enabled=False)
        assert "Voice Commands" not in prompt and "voice command" not in prompt.lower()
```

### Edge Cases

- Voice commands disabled but LLM enabled: Should work, just no command processing
- LLM disabled but voice commands enabled: Voice commands ignored (graceful degradation)
- Autostart toggle in pip mode: Should be hidden or disabled
- Registry access denied: Should fail gracefully, show error in UI
- Dictionary with non-OpenAI provider and LLM enabled: Should work (via LLM post-processing)

---

## VALIDATION COMMANDS

Execute every command to ensure zero regressions and 100% feature correctness.

### Level 1: Syntax & Style

```bash
ruff check src/ tests/
ruff format --check src/ tests/
```

### Level 2: Unit Tests

```bash
python -m pytest tests/test_prompts.py tests/test_config.py tests/test_autostart.py -v
```

### Level 3: Integration Tests

```bash
python -m pytest tests/test_post_processor.py tests/test_settings_window.py -v
```

### Level 4: Regression Tests (MANDATORY)

```bash
python -m pytest tests/test_regression.py -v
```

**All regression tests must pass before proceeding.**

### Level 5: Manual Validation

1. Run `python -m asr_everywhere` and open Settings
2. Verify "Enable voice commands" checkbox appears in LLM tab
3. Verify checkbox is enabled only when LLM is enabled
4. Set ASR provider to "together", disable LLM, add dictionary term
5. Verify warning appears in Dictionary tab
6. Enable LLM, verify warning disappears
7. (EXE only) Verify "Start with Windows" checkbox in Settings
8. (EXE only) Toggle autostart, verify registry entry created/removed

---

## ACCEPTANCE CRITERIA

- [ ] Voice commands toggle in Settings UI (requires LLM enabled)
- [ ] Voice commands section injected into LLM prompt when enabled
- [ ] Bilingual commands (DE + EN) supported
- [ ] Dictionary warning shows when LLM disabled + non-OpenAI provider + dictionary has entries
- [ ] Autostart toggle in Settings UI (EXE-only, hidden in pip mode)
- [ ] Autostart creates/removes registry entry correctly
- [ ] Config schema includes `llm.voice_commands_enabled` and `autostart.enabled`
- [ ] All validation commands pass with zero errors
- [ ] Unit test coverage for new functionality
- [ ] No regressions in existing functionality

---

## COMPLETION CHECKLIST

- [ ] All tasks completed in order
- [ ] Each task validation passed immediately
- [ ] All validation commands executed successfully
- [ ] Full test suite passes (unit + integration + regression)
- [ ] No linting or type checking errors
- [ ] Manual testing confirms feature works
- [ ] Acceptance criteria all met
- [ ] Code reviewed for quality and maintainability

---

## NOTES

### Voice Commands Design Decision

Voice commands are processed by the LLM during post-processing, not by the ASR. This means:
- **Pro**: Works with all ASR providers; flexible; easy to extend
- **Con**: Requires LLM post-processing enabled; adds latency

Alternative approaches considered:
1. ASR prompt-based (OpenAI only, rejected for limited provider support)
2. Regex-based (rejected for inflexibility and language-specific complexity)

### Dictionary Enhancement

The current implementation already passes dictionary to LLM post-processing. The enhancement is purely UI feedback to warn users when dictionary won't work (non-OpenAI ASR + LLM disabled).

### Autostart Scope

Autostart is EXE-only because:
- Registry entry needs path to EXE (not Python script)
- pip-installed users can use OS-level autostart mechanisms
- Keeps implementation simple

### Future Considerations

- Custom voice commands (user-defined)
- Voice command for "undo last dictation"
- Autostart delay option
