# Feature: Phase 5 - EXE Packaging & Windows Integration

The following plan should be complete, but its important that you validate documentation and codebase patterns and task sanity before you start implementing.

Pay special attention to naming of existing utils types and models. Import from the right files etc.

## Feature Description

Transform ASR Everywhere into a standalone Windows application that can be installed and run without Python. Create a professional Windows installer with Start Menu integration and optional desktop shortcut. This enables non-technical users to install and use the application.

## User Story

```
As a non-technical Windows user
I want to download and install ASR Everywhere like any other Windows application
So that I can use voice dictation without installing Python or understanding pip
```

## Problem Statement

Currently, users must:
1. Install Python 3.11+
2. Understand pip and virtual environments
3. Run command-line commands
4. Manually create shortcuts

This creates a significant barrier for non-developers who just want to use the application.

## Solution Statement

Use PyInstaller to bundle the application into a single executable file, then create a Windows installer using Inno Setup that:
- Installs the EXE to Program Files
- Creates Start Menu shortcut
- Offers optional Desktop shortcut
- Provides clean uninstall

## Feature Metadata

**Feature Type**: Enhancement
**Estimated Complexity**: Medium
**Primary Systems Affected**: Build system, Distribution
**Dependencies**: PyInstaller>=6.0, Inno Setup (external tool)

---

## CONTEXT REFERENCES

### Relevant Codebase Files IMPORTANT: YOU MUST READ THESE FILES BEFORE IMPLEMENTING!

- `pyproject.toml` (lines 1-109) - Build configuration, dependencies, entry points
- `src/asr_everywhere/__main__.py` (lines 1-9) - Entry point that calls `main()`
- `src/asr_everywhere/app.py` (lines 271-275) - `main()` function definition
- `src/asr_everywhere/ui/tray.py` (lines 71-125) - Asset loading logic, needs to work with PyInstaller's bundled assets
- `.github/workflows/test.yml` (lines 1-41) - Existing CI workflow pattern to extend
- `assets/icon_idle.ico`, `assets/icon_recording.ico`, `assets/icon_processing.ico` - Icon files to bundle

### New Files to Create

- `asr-everywhere.spec` - PyInstaller spec file (project root)
- `scripts/build_exe.py` - Build script for EXE generation
- `installer/setup.iss` - Inno Setup installer script
- `.github/workflows/release.yml` - GitHub Actions release workflow

### Relevant Documentation

- [PyInstaller Manual - Spec Files](https://pyinstaller.org/en/stable/spec-files.html)
  - How to configure hiddenimports, datas, EXE options
  - Why: Required for proper bundling of pystray, pynput, keyboard
- [PyInstaller - Hidden Imports](https://pyinstaller.org/en/stable/when-things-go-wrong.html#hidden-imports)
  - Troubleshooting missing modules
  - Why: pynput and pystray require platform-specific hidden imports
- [Inno Setup Documentation](https://jrsoftware.org/ishelp/)
  - Script syntax, [Files], [Icons], [Tasks] sections
  - Why: Required for creating professional Windows installer

### Patterns to Follow

**Naming Conventions:**
- Script files: `snake_case.py`
- Spec file: `asr-everywhere.spec` (matches package name)
- Installer script: `setup.iss` (standard Inno Setup naming)

**Build Pattern:**
- Use `python -m build` for wheel/sdist (existing)
- Use `python scripts/build_exe.py` for EXE (new)
- Use `iscc installer/setup.iss` for installer (new)

**Asset Handling Pattern (from `tray.py`):**
```python
# When running from source
if "site-packages" not in __file__:
    dev_assets = Path(__file__).parent.parent.parent.parent / "assets"

# When installed via pip or PyInstaller
# PyInstaller sets sys._MEIPASS for temp extraction folder
if getattr(sys, 'frozen', False):
    # Running as PyInstaller bundle
    assets_dir = Path(sys._MEIPASS) / "assets"
```

**GitHub Actions Pattern (from `test.yml`):**
```yaml
runs-on: windows-latest
steps:
  - uses: actions/checkout@v4
  - uses: actions/setup-python@v5
    with:
      python-version: "3.11"
```

---

## IMPLEMENTATION PLAN

### Phase 1: PyInstaller Configuration

**Goal:** Create spec file and build script for EXE generation.

**Tasks:**

1. **Update `tray.py` for PyInstaller compatibility**
   - Add `sys._MEIPASS` detection for bundled assets
   - Modify `_get_assets_dir()` to handle frozen state

2. **Create `asr-everywhere.spec`**
   - Configure Analysis with entry point
   - Add hiddenimports for platform-specific modules:
     ```python
     hiddenimports=[
         'pystray._win32',
         'keyboard',
         'pynput.keyboard._win32',
         'pynput.mouse._win32',
         'sounddevice',
         'soundfile',
         'openai',
         'httpx',
         'PIL',
     ]
     ```
   - Add datas for icon files:
     ```python
     datas=[('assets/*.ico', 'assets')]
     ```
   - Configure EXE with `console=False`, icon

3. **Create `scripts/build_exe.py`**
   - Clean previous builds
   - Run PyInstaller with spec file
   - Report success/failure

4. **Add PyInstaller to dev dependencies**
   - Update `pyproject.toml` optional-dependencies

### Phase 2: Inno Setup Installer

**Goal:** Create professional Windows installer.

**Tasks:**

1. **Create `installer/setup.iss`**
   - Define app metadata (name, version, publisher)
   - Configure installation directory
   - Add Files section for EXE and assets
   - Add Icons section for Start Menu and optional Desktop
   - Add Languages (English, German)
   - Add Run section for post-install launch option

2. **Document Inno Setup requirement**
   - Add to README.md prerequisites for building installer

### Phase 3: GitHub Actions Release Workflow

**Goal:** Automate EXE and installer builds on release tags.

**Tasks:**

1. **Create `.github/workflows/release.yml`**
   - Trigger on `v*` tags
   - Build EXE using PyInstaller
   - Install Inno Setup via chocolatey
   - Build installer
   - Create GitHub Release with artifacts

2. **Update README.md**
   - Add installation section for EXE download
   - Link to Releases page

### Phase 4: Testing & Validation

**Goal:** Verify EXE works on clean Windows machines.

**Tasks:**

1. **Local Testing**
   - Build EXE: `python scripts/build_exe.py`
   - Test EXE runs without Python
   - Test all features (tray, settings, transcription)
   - Test icon loading

2. **Installer Testing**
   - Build installer: `iscc installer/setup.iss`
   - Test installation on clean Windows 10/11 VM
   - Verify Start Menu shortcut
   - Verify Desktop shortcut option
   - Test uninstall removes all files

3. **CI Testing**
   - Create a test release tag
   - Verify GitHub Actions workflow succeeds
   - Download artifacts and test

---

## VALIDATION COMMANDS

```powershell
# Build EXE locally
python scripts/build_exe.py

# Test EXE
.\dist\asr-everywhere.exe

# Build installer (requires Inno Setup installed)
iscc installer/setup.iss

# Test installer
.\dist\installer\asr-everywhere-setup.exe

# Lint and format
ruff check src/ tests/
ruff format src/ tests/

# Run tests (should still pass)
pytest tests/ -v
```

---

## EDGE CASES & KNOWN ISSUES

### Issue 1: pynput Hidden Imports
**Problem:** pynput uses conditional imports for platform backends that PyInstaller doesn't detect.
**Solution:** Add explicit hiddenimports:
```python
'pynput.keyboard._win32',
'pynput.mouse._win32',
```

### Issue 2: pystray Backend
**Problem:** pystray uses conditional imports for platform backends.
**Solution:** Add `'pystray._win32'` to hiddenimports.

### Issue 3: Asset Loading in Frozen State
**Problem:** PyInstaller extracts files to a temp directory (`sys._MEIPASS`), not the original path.
**Solution:** Update `_get_assets_dir()` in `tray.py`:
```python
if getattr(sys, 'frozen', False):
    # Running as PyInstaller bundle
    return Path(sys._MEIPASS) / "assets"
```

### Issue 4: Large EXE Size
**Problem:** Single-file EXE may be 50-100 MB due to Python runtime and dependencies.
**Solution:** Accept this as normal. Can use UPX compression in spec file if needed.

### Issue 5: Antivirus False Positives
**Problem:** Unsigned executables may trigger antivirus warnings.
**Solution:** Document this as expected behavior. Code signing requires a certificate (not in scope).

---

## SUCCESS CRITERIA

1. ✅ `python scripts/build_exe.py` produces `dist/asr-everywhere.exe`
2. ✅ EXE runs on Windows 10/11 without Python installed
3. ✅ All features work: tray icon, settings, hotkeys, transcription
4. ✅ Icons display correctly (loaded from bundled assets)
5. ✅ `iscc installer/setup.iss` produces `dist/installer/asr-everywhere-setup.exe`
6. ✅ Installer creates Start Menu shortcut
7. ✅ Installer offers Desktop shortcut option
8. ✅ Uninstaller removes all installed files
9. ✅ GitHub Actions release workflow builds and uploads artifacts
10. ✅ All existing tests still pass

---

## FILE STRUCTURE AFTER IMPLEMENTATION

```
asr-everywhere/
├── asr-everywhere.spec      # PyInstaller spec file
├── scripts/
│   └── build_exe.py         # Build script
├── installer/
│   └── setup.iss            # Inno Setup script
├── dist/
│   ├── asr-everywhere.exe   # Standalone EXE (after build)
│   └── installer/
│       └── asr-everywhere-setup.exe  # Installer (after build)
├── .github/workflows/
│   ├── test.yml             # Existing test workflow
│   └── release.yml          # New release workflow
└── README.md                # Updated with EXE installation
```

---

## ESTIMATED EFFORT

| Task | Time |
|------|------|
| Update tray.py for PyInstaller | 30 min |
| Create spec file | 30 min |
| Debug hidden imports | 1-2 hours |
| Create build script | 30 min |
| Create Inno Setup script | 1 hour |
| Create GitHub Actions workflow | 1 hour |
| Testing on clean machines | 1-2 hours |
| Documentation updates | 30 min |

**Total:** ~6-8 hours
