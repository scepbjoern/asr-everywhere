"""Windows autostart management via Registry Run Key."""

from __future__ import annotations

import logging
import sys
import winreg

logger = logging.getLogger(__name__)

# Registry path for autostart entries
AUTOSTART_REGISTRY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
AUTOSTART_ENTRY_NAME = "ASR Everywhere"


def is_exe() -> bool:
    """Check if running as compiled EXE (PyInstaller).

    Returns:
        True if running as EXE, False if running as Python script
    """
    return getattr(sys, "frozen", False)


def get_exe_path() -> str | None:
    """Get the path to the current executable.

    Returns:
        Path to EXE if running as EXE, None otherwise
    """
    if is_exe():
        return sys.executable
    return None


def is_autostart_enabled() -> bool:
    """Check if autostart is enabled in Windows Registry.

    Returns:
        True if registry entry exists and points to current EXE
    """
    if not is_exe():
        return False

    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            AUTOSTART_REGISTRY_PATH,
            0,
            winreg.KEY_READ,
        ) as key:
            value, _ = winreg.QueryValueEx(key, AUTOSTART_ENTRY_NAME)
            exe_path = get_exe_path()
            return value == exe_path
    except FileNotFoundError:
        # Registry entry doesn't exist
        return False
    except Exception as e:
        logger.error(f"Failed to check autostart registry: {e}")
        return False


def enable_autostart() -> bool:
    """Enable autostart by creating registry entry.

    Returns:
        True if successful, False on error
    """
    if not is_exe():
        logger.warning("Cannot enable autostart: not running as EXE")
        return False

    exe_path = get_exe_path()
    if not exe_path:
        return False

    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            AUTOSTART_REGISTRY_PATH,
            0,
            winreg.KEY_WRITE,
        ) as key:
            winreg.SetValueEx(
                key,
                AUTOSTART_ENTRY_NAME,
                0,
                winreg.REG_SZ,
                exe_path,
            )
        logger.info(f"Autostart enabled: {exe_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to enable autostart: {e}")
        return False


def disable_autostart() -> bool:
    """Disable autostart by removing registry entry.

    Returns:
        True if successful, False on error
    """
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            AUTOSTART_REGISTRY_PATH,
            0,
            winreg.KEY_WRITE,
        ) as key:
            winreg.DeleteValue(key, AUTOSTART_ENTRY_NAME)
        logger.info("Autostart disabled")
        return True
    except FileNotFoundError:
        # Entry doesn't exist, consider it disabled
        return True
    except Exception as e:
        logger.error(f"Failed to disable autostart: {e}")
        return False


def sync_autostart(enabled: bool) -> bool:
    """Sync registry state with desired autostart setting.

    Args:
        enabled: Desired autostart state

    Returns:
        True if successful, False on error
    """
    if not is_exe():
        return False

    if enabled:
        return enable_autostart()
    else:
        return disable_autostart()
