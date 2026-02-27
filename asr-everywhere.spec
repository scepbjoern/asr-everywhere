# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for ASR Everywhere.

This file configures the PyInstaller build process to create a standalone
Windows executable with all dependencies and assets bundled.
"""

import sys
from pathlib import Path

# Project root directory
project_root = Path(SPECPATH)

# Hidden imports for platform-specific modules that PyInstaller doesn't detect
hiddenimports = [
    # pystray Windows backend
    "pystray._win32",
    # keyboard library
    "keyboard",
    # pynput Windows backends
    "pynput.keyboard._win32",
    "pynput.mouse._win32",
    # Audio libraries
    "sounddevice",
    "soundfile",
    # OpenAI SDK
    "openai",
    "httpx",
    "httpcore",
    # Pillow
    "PIL",
    # Standard library modules that may be missed
    "tkinter",
    "tkinter.ttk",
    "tkinter.filedialog",
    "tkinter.messagebox",
    # Additional dependencies
    "pyperclip",
    "h11",
    "anyio",
    "distro",
    "sniffio",
    "certifi",
    "charset_normalizer",
    "idna",
    "urllib3",
]

# Data files to bundle (icon assets)
datas = [
    (str(project_root / "assets" / "*.ico"), "assets"),
]

a = Analysis(
    [str(project_root / "src" / "asr_everywhere" / "__main__.py")],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    # Disable UPX compression (can cause issues with some AV)
    upx=False,
    # Optimize bytecode
    optimize=2,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="asr-everywhere",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI application, no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_root / "assets" / "icon_idle.ico"),
)
