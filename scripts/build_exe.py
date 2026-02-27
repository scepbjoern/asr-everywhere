#!/usr/bin/env python
"""Build script for creating standalone Windows EXE using PyInstaller.

This script:
1. Cleans previous build artifacts
2. Runs PyInstaller with the spec file
3. Reports success/failure

Usage:
    python scripts/build_exe.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def clean_build_dirs(project_root: Path) -> None:
    """Remove previous build artifacts."""
    dirs_to_clean = ["build", "dist"]
    
    for dir_name in dirs_to_clean:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"Cleaning {dir_path}...")
            shutil.rmtree(dir_path)
    
    # Also remove any .pyc files
    for pyc_file in project_root.rglob("*.pyc"):
        pyc_file.unlink()


def run_pyinstaller(project_root: Path) -> bool:
    """Run PyInstaller with the spec file.
    
    Returns:
        True if build succeeded, False otherwise
    """
    spec_file = project_root / "asr-everywhere.spec"
    
    if not spec_file.exists():
        print(f"ERROR: Spec file not found: {spec_file}")
        return False
    
    print(f"Running PyInstaller with {spec_file}...")
    
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", str(spec_file), "--noconfirm"],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    
    if result.returncode != 0:
        print("PyInstaller failed!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False
    
    print(result.stdout)
    return True


def verify_exe(project_root: Path) -> bool:
    """Verify the EXE was created.
    
    Returns:
        True if EXE exists, False otherwise
    """
    exe_path = project_root / "dist" / "asr-everywhere.exe"
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\n✅ Build successful!")
        print(f"   EXE: {exe_path}")
        print(f"   Size: {size_mb:.1f} MB")
        return True
    else:
        print(f"\n❌ Build failed - EXE not found: {exe_path}")
        return False


def main() -> int:
    """Main build process."""
    project_root = Path(__file__).parent.parent
    
    print("=" * 60)
    print("ASR Everywhere - EXE Builder")
    print("=" * 60)
    
    # Step 1: Clean
    print("\n[1/3] Cleaning previous builds...")
    clean_build_dirs(project_root)
    
    # Step 2: Build
    print("\n[2/3] Building EXE with PyInstaller...")
    if not run_pyinstaller(project_root):
        return 1
    
    # Step 3: Verify
    print("\n[3/3] Verifying build...")
    if not verify_exe(project_root):
        return 1
    
    print("\n" + "=" * 60)
    print("Build complete! You can test the EXE by running:")
    print(f"  {project_root / 'dist' / 'asr-everywhere.exe'}")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
