# Phase 5 - EXE Packaging & Windows Integration

## Overview

Transform ASR Everywhere into a standalone Windows application with:
- Single executable file (.exe)
- Windows Start Menu integration
- Optional desktop shortcut
- No Python installation required for end users

## Why PyInstaller?

PyInstaller is the standard tool for packaging Python applications as standalone executables:
- Bundles Python interpreter and all dependencies
- Creates single-file or directory-based distribution
- Supports Windows, macOS, Linux
- Active community and well-documented
- Works well with GUI applications (System Tray)

## Implementation Order

### 1. Create PyInstaller Spec File

**File:** `asr-everywhere.spec` (project root)

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/asr_everywhere/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/*.ico', 'assets'),  # Include icon files
    ],
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
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='asr-everywhere',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI application, no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon_idle.ico',  # Application icon
)
```

### 2. Update pyproject.toml

Add PyInstaller as dev dependency and build script:

```toml
[project.optional-dependencies]
dev = [
    # ... existing deps ...
    "pyinstaller>=6.0",
]

[project.scripts]
# Keep existing scripts for pip install

[tool.setuptools]
# Existing config
```

### 3. Create Build Script

**File:** `scripts/build_exe.py`

```python
"""Build standalone executable using PyInstaller."""

import subprocess
import sys
from pathlib import Path

def build():
    """Build the executable."""
    project_root = Path(__file__).parent.parent
    
    # Clean previous builds
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"
    
    if dist_dir.exists():
        import shutil
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        import shutil
        shutil.rmtree(build_dir)
    
    # Run PyInstaller
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--clean",
            "--noconfirm",
            str(project_root / "asr-everywhere.spec"),
        ],
        cwd=project_root,
    )
    
    if result.returncode != 0:
        print("Build failed!")
        sys.exit(1)
    
    exe_path = dist_dir / "asr-everywhere.exe"
    if exe_path.exists():
        print(f"Build successful: {exe_path}")
        print(f"Size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
    else:
        print("Build failed: EXE not found")
        sys.exit(1)

if __name__ == "__main__":
    build()
```

### 4. Create Installer Script (Inno Setup)

**File:** `installer/setup.iss`

```ini
; Inno Setup Script for ASR Everywhere
; Requires Inno Setup (https://jrsoftware.org/isinfo.php)

#define MyAppName "ASR Everywhere"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "ASR Everywhere Contributors"
#define MyAppURL "https://github.com/scepbjoern/asr-everywhere"
#define MyAppExeName "asr-everywhere.exe"

[Setup]
AppId={{ASR-Everywhere-2024}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=..\LICENSE
InfoBeforeFile=..\README.md
OutputDir=..\dist\installer
OutputBaseFilename=asr-everywhere-setup
SetupIconFile=..\assets\icon_idle.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\assets\*.ico"; DestDir: "{app}\assets"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\icon_idle.ico"
Name: "{group}\{cm:ProgramOnTheWeb,{#MyAppName}}"; Filename: "{#MyAppURL}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\icon_idle.ico"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
```

### 5. Update README.md

Add installation section for EXE:

```markdown
## Installation

### Option A: Standalone EXE (Recommended for Non-Developers)

1. Download `asr-everywhere-setup.exe` from [Releases](https://github.com/scepbjoern/asr-everywhere/releases)
2. Run the installer
3. Launch from Start Menu → ASR Everywhere

**Requirements:** Windows 10/11 (no Python needed)

### Option B: From PyPI (For Developers)

```powershell
pip install asr-everywhere
```

### Option C: From Source (For Development)

```powershell
git clone https://github.com/scepbjoern/asr-everywhere.git
cd asr-everywhere
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```
```

### 6. Create GitHub Actions Workflow for Releases

**File:** `.github/workflows/release.yml`

```yaml
name: Build and Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
        pip install pyinstaller
    
    - name: Build EXE
      run: python scripts/build_exe.py
    
    - name: Build Installer
      run: |
        # Install Inno Setup
        choco install innosetup -y
        iscc installer/setup.iss
    
    - name: Create Release
      uses: softprops/action-gh-release@v1
      with:
        files: |
          dist/asr-everywhere.exe
          dist/installer/asr-everywhere-setup.exe
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Testing Checklist

### Build Verification
- [ ] `python scripts/build_exe.py` completes without errors
- [ ] `dist/asr-everywhere.exe` exists
- [ ] EXE size is reasonable (< 100 MB)
- [ ] EXE runs without Python installed

### Functionality Tests
- [ ] EXE launches and shows tray icon
- [ ] Settings window opens
- [ ] Microphone detection works
- [ ] Hotkey registration works
- [ ] Transcription works
- [ ] Icons display correctly

### Installer Tests
- [ ] Installer runs successfully
- [ ] Start Menu shortcut created
- [ ] Desktop shortcut option works
- [ ] Uninstaller removes all files
- [ ] App runs from installed location

### Clean Machine Tests
- [ ] Run on Windows 10 VM without Python
- [ ] Run on Windows 11 VM without Python
- [ ] All features work without Python runtime

## Known Issues & Solutions

### Issue: Large EXE Size
**Solution:** Use `--exclude-module` to remove unused modules, enable UPX compression

### Issue: Antivirus False Positives
**Solution:** Code signing (requires certificate), or document as known issue

### Issue: Missing DLLs
**Solution:** Ensure all hiddenimports are listed in spec file

### Issue: Console Window Appears
**Solution:** Set `console=False` in EXE() spec

## File Structure After Phase 5

```
asr-everywhere/
├── asr-everywhere.spec      # PyInstaller spec file
├── scripts/
│   └── build_exe.py         # Build script
├── installer/
│   └── setup.iss            # Inno Setup script
├── dist/
│   ├── asr-everywhere.exe   # Standalone EXE
│   └── installer/
│       └── asr-everywhere-setup.exe  # Installer
└── .github/workflows/
    └── release.yml          # Release automation
```

## Commands

```powershell
# Build EXE locally
python scripts/build_exe.py

# Build installer (requires Inno Setup)
iscc installer/setup.iss

# Test EXE
.\dist\asr-everywhere.exe

# Test installer
.\dist\installer\asr-everywhere-setup.exe
```

## Dependencies to Add

```toml
[project.optional-dependencies]
dev = [
    # ... existing ...
    "pyinstaller>=6.0",
]
```

## Estimated Effort

| Task | Time |
|------|------|
| Create spec file & build script | 1 hour |
| Debug hidden imports | 1-2 hours |
| Create installer script | 1 hour |
| Test on clean machines | 1-2 hours |
| GitHub Actions setup | 1 hour |
| Documentation update | 30 min |

**Total:** ~6-8 hours

## Success Criteria

1. ✅ Single EXE file runs without Python
2. ✅ All features work (tray, settings, transcription)
3. ✅ Start Menu shortcut created by installer
4. ✅ Desktop shortcut optional
5. ✅ Clean uninstall
6. ✅ GitHub release automation works
