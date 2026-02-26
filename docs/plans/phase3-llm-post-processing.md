# Feature: Phase 3 - LLM Post-Processing & Dictionary

The following plan should be complete, but it's important that you validate documentation and codebase patterns and task sanity before you start implementing.

Pay special attention to naming of existing utils, types, and models. Import from the right files etc.

---

## Feature Description

Add optional LLM post-processing of transcribed text and dictionary/custom terms support. This allows users to:
1. Have transcriptions cleaned up (punctuation, formatting, filler word removal)
2. Define custom terms (proper nouns, technical vocabulary) that improve transcription accuracy

## User Stories

**Story 1:**
```
As a user dictating text
I want to optionally have the transcription cleaned up by an LLM
So that the inserted text is polished and ready to use
```

**Story 2:**
```
As a user dictating technical content
I want to define a dictionary of custom terms
So that proper nouns, technical terms, and abbreviations are correctly transcribed
```

## Problem Statement

Raw ASR output often lacks proper punctuation, capitalization, and may contain filler words ("ähm", "um", "like"). Additionally, uncommon proper nouns and technical terms are frequently misspelled. Users need a way to improve transcription quality without manual editing.

## Solution Statement

1. **LLM Post-Processing**: Add an optional pipeline step after ASR that sends the raw transcription to an LLM for cleanup. Support the same providers as ASR (OpenAI, Together.ai, Hugging Face, local).

2. **Dictionary**: Store custom terms in config, inject them into:
   - ASR prompt parameter (Whisper's `prompt` accepts custom vocabulary)
   - LLM system prompt (as "Dictionary:" section)

## Feature Metadata

**Feature Type**: New Capability
**Estimated Complexity**: Medium
**Primary Systems Affected**:
- `config.py` - Add LLMConfig, dictionary list
- `transcription_pipeline.py` - Add LLM post-processing step
- `providers/` - Add LLMProvider abstract class
- `ui/settings_window.py` - Add LLM and Dictionary tabs
- `providers/openai_provider.py` - Add dictionary prompt support
- `providers/openai_compat.py` - Add dictionary prompt support

**Dependencies**: Existing `openai` SDK (already installed)

---

## CONTEXT REFERENCES

### Relevant Codebase Files - READ THESE BEFORE IMPLEMENTING

**Config Schema Pattern:**
- `src/asr_everywhere/config.py` (lines 1-202) - Config dataclass patterns, `ASRConfig`, `ProviderConfig`, `load_config`, `save_config`
  - Why: Shows how to structure new config sections (LLMConfig), provider configs pattern

**Provider Pattern:**
- `src/asr_everywhere/providers/base.py` (lines 1-46) - `ASRProvider` abstract base class, `TranscriptionResult`
  - Why: Pattern for creating `LLMProvider` abstract base class
- `src/asr_everywhere/providers/openai_provider.py` (lines 40-75) - `transcribe()` method, OpenAI client usage
  - Why: Shows how to use OpenAI SDK, pattern for adding `prompt` parameter
- `src/asr_everywhere/providers/openai_compat.py` (lines 38-91) - OpenAI-compatible provider pattern
  - Why: Pattern for LLM provider that uses same API structure
- `src/asr_everywhere/providers/registry.py` (lines 1-63) - Provider registry pattern
  - Why: Pattern for LLM provider registry

**Pipeline Pattern:**
- `src/asr_everywhere/transcription_pipeline.py` (lines 66-128) - `stop_and_transcribe()` method
  - Why: Where to inject LLM post-processing step, error handling pattern

**UI Pattern:**
- `src/asr_everywhere/ui/settings_window.py` (lines 92-169, 246-307) - Tab creation pattern, form fields
  - Why: Pattern for adding LLM and Dictionary tabs

**PRD Reference:**
- `docs/PRD.md` (lines 282-305) - LLM post-processing spec, prompt structure
- `docs/PRD.md` (lines 338-344) - Dictionary spec
- `docs/PRD.md` (lines 395-442) - Example config JSON with LLM section

### New Files to Create

1. `src/asr_everywhere/llm/__init__.py` - Package init
2. `src/asr_everywhere/llm/base.py` - `LLMProvider` abstract base class
3. `src/asr_everywhere/llm/openai_llm.py` - OpenAI LLM provider implementation
4. `src/asr_everywhere/llm/openai_compat_llm.py` - OpenAI-compatible LLM provider
5. `src/asr_everywhere/llm/registry.py` - LLM provider registry
6. `src/asr_everywhere/llm/prompts.py` - Default system prompts, prompt builder
7. `src/asr_everywhere/llm/post_processor.py` - Post-processing orchestrator
8. `tests/test_llm_provider.py` - Unit tests for LLM providers
9. `tests/test_post_processor.py` - Unit tests for post-processing

### Files to Modify

1. `src/asr_everywhere/config.py` - Add `LLMConfig`, `dictionary` field
2. `src/asr_everywhere/transcription_pipeline.py` - Add LLM step after ASR
3. `src/asr_everywhere/providers/openai_provider.py` - Add `prompt` parameter support
4. `src/asr_everywhere/providers/openai_compat.py` - Add `prompt` parameter support
5. `src/asr_everywhere/providers/huggingface_provider.py` - Add `prompt` parameter support (if HF supports it)
6. `src/asr_everywhere/ui/settings_window.py` - Add LLM and Dictionary tabs
7. `config.example.json` - Add LLM and dictionary example

### Relevant Documentation

- [OpenAI Whisper Prompting Guide](https://developers.openai.com/cookbook/examples/whisper_prompting_guide/)
  - Section: "Pass names in the prompt to prevent misspellings"
  - Why: Shows how to use `prompt` parameter for custom vocabulary (comma-separated terms)
- [OpenAI Chat Completions API](https://platform.openai.com/docs/api-reference/chat)
  - Section: chat.completions.create
  - Why: LLM API call pattern

---

## PATTERNS TO FOLLOW

### Naming Conventions

From existing codebase:
- Files: `snake_case.py`
- Classes: `PascalCase` (e.g., `ASRProvider`, `TranscriptionPipeline`)
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Config keys: `snake_case` in JSON

### Dataclass Pattern (from config.py)

```python
@dataclass
class ProviderConfig:
    """Configuration for a specific ASR provider."""
    api_key: str = ""
    base_url: str = ""
    models: list[ModelConfig] = field(default_factory=list)
```

### Provider Abstract Base Class Pattern (from providers/base.py)

```python
class ASRProvider(ABC):
    """Abstract base class for ASR providers."""

    @abstractmethod
    def transcribe(
        self,
        audio_data: bytes,
        config: ASRConfig,
    ) -> TranscriptionResult:
        """Transcribe audio bytes to text."""
        ...

    @abstractmethod
    def list_models(self) -> list[str]:
        """Return list of available models for this provider."""
        ...
```

### Error Handling Pattern (from providers/openai_provider.py)

```python
try:
    response = client.audio.transcriptions.create(**kwargs)
    logger.info(f"Transcription complete: {len(response.text)} chars")
    return TranscriptionResult(text=response.text, ...)
except Exception as e:
    logger.error(f"OpenAI transcription failed: {e}")
    raise
```

### Logging Pattern

```python
logger = logging.getLogger(__name__)
logger.info(f"Starting transcription")
logger.error(f"Failed: {e}")
```

### Test Pattern (from tests/test_providers.py)

```python
@pytest.fixture
def asr_config():
    """Create test ASR config."""
    return ASRConfig(provider="openai", model="whisper-1", api_key="test-key")

def test_transcribe_success(asr_config):
    """Test successful transcription."""
    provider = OpenAIProvider()
    with mock.patch("asr_everywhere.providers.openai_provider.OpenAI") as mock_openai:
        mock_client = mock.MagicMock()
        mock_openai.return_value = mock_client
        # ... assertions
```

---

## IMPLEMENTATION PLAN

### Phase 1: Config Schema Updates

**Goal**: Add LLM configuration and dictionary to config schema.

**Tasks:**

1. Add `LLMConfig` dataclass to `config.py`:
   ```python
   @dataclass
   class LLMConfig:
       enabled: bool = False
       provider: str = "openai"
       model: str = "gpt-4o-mini"
       custom_instructions: str = ""
       providers: dict[str, ProviderConfig] = field(default_factory=dict)
       
       def get_api_key(self) -> str: ...
       def get_base_url(self) -> str: ...
   ```

2. Add `dictionary: list[str] = field(default_factory=list)` to `Config` dataclass

3. Add `llm: LLMConfig = field(default_factory=LLMConfig)` to `Config` dataclass

4. Update `_get_default_providers()` to include LLM default providers

5. Update `load_config()` to parse LLM section and dictionary

6. Update `config.example.json` with LLM and dictionary examples

**Validation**: Run `pytest tests/test_config.py` - existing tests should pass

### Phase 2: LLM Provider Abstraction

**Goal**: Create LLM provider infrastructure following ASR provider pattern.

**Tasks:**

1. Create `src/asr_everywhere/llm/__init__.py` (empty or exports)

2. Create `src/asr_everywhere/llm/base.py`:
   ```python
   @dataclass
   class PostProcessResult:
       text: str
       original_text: str
       
   class LLMProvider(ABC):
       @abstractmethod
       def post_process(
           self,
           text: str,
           config: LLMConfig,
           dictionary: list[str],
       ) -> PostProcessResult:
           """Post-process transcribed text."""
           ...
       
       @abstractmethod
       def list_models(self) -> list[str]:
           """Return available models."""
           ...
   ```

3. Create `src/asr_everywhere/llm/openai_llm.py`:
   - Implement `LLMProvider` for OpenAI
   - Use `client.chat.completions.create()`
   - Build system prompt with dictionary injection

4. Create `src/asr_everywhere/llm/openai_compat_llm.py`:
   - Generic OpenAI-compatible provider (Together, HF, local)

5. Create `src/asr_everywhere/llm/registry.py`:
   - `LLM_PROVIDERS` dict
   - `get_llm_provider(name: str) -> LLMProvider`
   - `list_llm_providers() -> list[str]`

**Validation**: Create basic unit tests in `tests/test_llm_provider.py`

### Phase 3: Prompts Module

**Goal**: Create prompt builder for LLM post-processing.

**Tasks:**

1. Create `src/asr_everywhere/llm/prompts.py`:
   ```python
   DEFAULT_SYSTEM_PROMPT = """You are a transcription post-processor. Clean up the following dictated text.

Rules:
- Fix punctuation and capitalization
- Remove filler words (ähm, um, like, so, also)
- Maintain the original meaning and tone
- Keep the same language (German or English)"""

   def build_system_prompt(
       custom_instructions: str,
       dictionary: list[str],
   ) -> str:
       """Build complete system prompt."""
       prompt = DEFAULT_SYSTEM_PROMPT
       if custom_instructions:
           prompt += f"\n\nAdditional instructions:\n{custom_instructions}"
       if dictionary:
           prompt += f"\n\nDictionary (use these exact spellings):\n{', '.join(dictionary)}"
       return prompt
   ```

**Validation**: Unit test for prompt builder

### Phase 4: Post-Processor Orchestrator

**Goal**: Create the post-processing logic that ties everything together.

**Tasks:**

1. Create `src/asr_everywhere/llm/post_processor.py`:
   ```python
   class PostProcessor:
       def __init__(self, config: Config) -> None:
           self._config = config
       
       def process(self, text: str) -> str:
           """Post-process text if LLM enabled, else return original."""
           if not self._config.llm.enabled:
               return text
           
           provider = get_llm_provider(self._config.llm.provider)
           result = provider.post_process(
               text,
               self._config.llm,
               self._config.dictionary,
           )
           return result.text
   ```

**Validation**: Unit tests with mocked provider

### Phase 5: Dictionary Injection into ASR

**Goal**: Pass dictionary terms to ASR providers via `prompt` parameter.

**Tasks:**

1. Update `src/asr_everywhere/providers/base.py`:
   - Add `dictionary: list[str] | None = None` parameter to `transcribe()` signature

2. Update `src/asr_everywhere/providers/openai_provider.py`:
   - Add `prompt` kwarg if dictionary provided:
   ```python
   if dictionary:
       kwargs["prompt"] = ", ".join(dictionary)
   ```

3. Update `src/asr_everywhere/providers/openai_compat.py`:
   - Same pattern as OpenAI provider

4. Update `src/asr_everywhere/providers/huggingface_provider.py`:
   - Check if HF API supports prompt; if not, log warning and skip

5. Update `transcription_pipeline.py` to pass dictionary to `provider.transcribe()`

**Validation**: Unit tests verify prompt parameter is passed

### Phase 6: Pipeline Integration

**Goal**: Integrate LLM post-processing into transcription pipeline.

**Tasks:**

1. Update `src/asr_everywhere/transcription_pipeline.py`:
   ```python
   def stop_and_transcribe(self) -> None:
       # ... existing ASR code ...
       result = provider.transcribe(audio_data, self._config.asr, self._config.dictionary)
       
       text = result.text
       
       # LLM post-processing
       if self._config.llm.enabled and text:
           try:
               processor = PostProcessor(self._config)
               text = processor.process(text)
               logger.info(f"LLM post-processing complete")
           except Exception as e:
               logger.error(f"LLM post-processing failed: {e}")
               # Graceful degradation: use raw transcription
               self._tray.show_notification("LLM Error", "Using raw transcription")
       
       # Insert text
       self._inserter.insert_text(text, ...)
   ```

**Validation**: Integration test with mocked ASR and LLM

### Phase 7: Settings UI - LLM Tab

**Goal**: Add LLM configuration tab to settings window.

**Tasks:**

1. Add `_create_llm_tab()` method to `settings_window.py`:
   - Enable/disable checkbox
   - Provider dropdown (reuse `list_llm_providers()`)
   - Model dropdown
   - API Key entry (password field)
   - Base URL entry (for local)
   - Custom instructions text area (multi-line)

2. Add LLM tab to notebook: `self._notebook.add(tab, text="LLM")`

3. Update `_on_save_click()` to save LLM config

4. Update `_cleanup_vars()` to include LLM variables

**Validation**: Manual UI test, verify config saves correctly

### Phase 8: Settings UI - Dictionary Tab

**Goal**: Add dictionary management tab to settings window.

**Tasks:**

1. Add `_create_dictionary_tab()` method:
   - Listbox showing current terms
   - Add button + entry field for new term
   - Remove button for selected term
   - Clear all button

2. Add Dictionary tab to notebook

3. Update `_on_save_click()` to save dictionary

4. Update `_cleanup_vars()` to include dictionary variables

**Validation**: Manual UI test, verify terms persist in config

### Phase 9: Testing & Validation

**Goal**: Comprehensive test coverage for new functionality.

**Tasks:**

1. Create `tests/test_llm_provider.py`:
   - Test `LLMProvider` abstract class
   - Test `OpenAILLMProvider` with mocked OpenAI client
   - Test `OpenAICompatLLMProvider`
   - Test registry functions

2. Create `tests/test_post_processor.py`:
   - Test with LLM disabled (returns original)
   - Test with LLM enabled (calls provider)
   - Test error handling (graceful degradation)

3. Create `tests/test_prompts.py`:
   - Test default prompt
   - Test with custom instructions
   - Test with dictionary

4. Update `tests/test_pipeline.py`:
   - Add test for LLM post-processing step
   - Add test for dictionary passed to ASR

5. Update `tests/test_providers.py`:
   - Add test for dictionary/prompt parameter

**Validation**: Run `pytest tests/ -v` - all tests pass

---

## VALIDATION COMMANDS

```bash
# Run all tests
pytest tests/ -v

# Run specific test files
pytest tests/test_llm_provider.py -v
pytest tests/test_post_processor.py -v
pytest tests/test_pipeline.py -v

# Lint check
ruff check src/ tests/

# Format check
ruff format --check src/ tests/

# Full validation
ruff check src/ tests/ && ruff format --check src/ tests/ && pytest tests/
```

---

## EDGE CASES TO HANDLE

1. **LLM API failure**: Return raw transcription, show notification
2. **Empty dictionary**: Don't add prompt parameter
3. **Very long dictionary**: Whisper prompt has limits (~224 tokens) - truncate or warn
4. **LLM timeout**: Use reasonable timeout (30s), fall back to raw on timeout
5. **No API key for LLM**: Show error in settings, disable LLM
6. **Mixed language text**: LLM should preserve original language

---

## CONFIG EXAMPLE (Final State)

```json
{
  "version": 1,
  "hotkey": { "dictate": "win+ctrl+a", "mode": "toggle" },
  "asr": {
    "provider": "openai",
    "model": "gpt-4o-transcribe",
    "language": "auto",
    "providers": { ... }
  },
  "llm": {
    "enabled": true,
    "provider": "openai",
    "model": "gpt-4o-mini",
    "custom_instructions": "Always use formal German 'Sie' form",
    "providers": {
      "openai": {
        "api_key": "",
        "base_url": "https://api.openai.com/v1",
        "models": [
          {"name": "gpt-4o-mini", "price_per_hour": "included"}
        ]
      },
      "together": {
        "api_key": "",
        "base_url": "https://api.together.xyz/v1",
        "models": []
      },
      "local": {
        "api_key": "",
        "base_url": "http://localhost:11434/v1",
        "models": []
      }
    }
  },
  "dictionary": ["Kubernetes", "FastAPI", "Szczerba", "ASR Everywhere"],
  "audio": { "device": null, "sample_rate": 16000 },
  "clipboard_restore": true,
  "show_notification": true
}
```

---

## IMPLEMENTATION ORDER

1. **Config schema** (Phase 1) - Foundation for everything
2. **LLM base + prompts** (Phase 2-3) - Core infrastructure
3. **Post-processor** (Phase 4) - Orchestrator
4. **ASR dictionary injection** (Phase 5) - Enhances ASR
5. **Pipeline integration** (Phase 6) - Wires it all together
6. **Settings UI** (Phase 7-8) - User configuration
7. **Testing** (Phase 9) - Validation

---

## NOTES

- LLM provider can share API key with ASR provider if same provider selected
- Consider adding "Test LLM" button in settings (similar to "Test Connection" for ASR)
- Default LLM model: `gpt-4o-mini` (fast, cheap, good for text cleanup)
- Processing state already implemented in tray (orange icon)
