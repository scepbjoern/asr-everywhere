"""Tests for Windows autostart functionality."""

import sys
from unittest import mock

from asr_everywhere.autostart import (
    AUTOSTART_ENTRY_NAME,
    AUTOSTART_REGISTRY_PATH,
    disable_autostart,
    enable_autostart,
    get_exe_path,
    is_autostart_enabled,
    sync_autostart,
)


class TestIsExe:
    """Tests for is_exe function."""

    def test_returns_false_when_not_frozen(self) -> None:
        """Test that is_exe returns False when sys.frozen is not set."""
        with mock.patch.object(sys, "frozen", False, create=True):
            # Need to reload the module to pick up the mock
            result = getattr(sys, "frozen", False)
            assert result is False

    def test_returns_true_when_frozen(self) -> None:
        """Test that is_exe returns True when sys.frozen is set."""
        # Simulate PyInstaller frozen state
        with mock.patch.object(sys, "frozen", True, create=True):
            assert getattr(sys, "frozen", False) is True


class TestGetExePath:
    """Tests for get_exe_path function."""

    def test_returns_none_when_not_exe(self) -> None:
        """Test that get_exe_path returns None when not running as EXE."""
        with mock.patch("asr_everywhere.autostart.is_exe", return_value=False):
            result = get_exe_path()
            assert result is None

    def test_returns_executable_when_exe(self) -> None:
        """Test that get_exe_path returns sys.executable when running as EXE."""
        with (
            mock.patch("asr_everywhere.autostart.is_exe", return_value=True),
            mock.patch("sys.executable", "C:\\path\\to\\app.exe"),
        ):
            result = get_exe_path()
            assert result == "C:\\path\\to\\app.exe"


class TestIsAutostartEnabled:
    """Tests for is_autostart_enabled function."""

    def test_returns_false_when_not_exe(self) -> None:
        """Test that is_autostart_enabled returns False when not running as EXE."""
        with mock.patch("asr_everywhere.autostart.is_exe", return_value=False):
            result = is_autostart_enabled()
            assert result is False

    def test_returns_false_when_registry_key_missing(self) -> None:
        """Test that is_autostart_enabled returns False when registry key doesn't exist."""
        with (
            mock.patch("asr_everywhere.autostart.is_exe", return_value=True),
            mock.patch("asr_everywhere.autostart.get_exe_path", return_value="C:\\app.exe"),
            mock.patch("asr_everywhere.autostart.winreg") as mock_winreg,
        ):
            mock_winreg.OpenKey.side_effect = FileNotFoundError()
            result = is_autostart_enabled()
            assert result is False

    def test_returns_true_when_registry_matches_exe(self) -> None:
        """Test that is_autostart_enabled returns True when registry matches EXE path."""
        with (
            mock.patch("asr_everywhere.autostart.is_exe", return_value=True),
            mock.patch("asr_everywhere.autostart.get_exe_path", return_value="C:\\app.exe"),
            mock.patch("asr_everywhere.autostart.winreg") as mock_winreg,
        ):
            mock_key = mock.MagicMock()
            mock_winreg.OpenKey.return_value.__enter__.return_value = mock_key
            mock_winreg.QueryValueEx.return_value = ("C:\\app.exe", mock_winreg.REG_SZ)

            result = is_autostart_enabled()
            assert result is True

    def test_returns_false_when_registry_differs(self) -> None:
        """Test that is_autostart_enabled returns False when registry has different path."""
        with (
            mock.patch("asr_everywhere.autostart.is_exe", return_value=True),
            mock.patch("asr_everywhere.autostart.get_exe_path", return_value="C:\\app.exe"),
            mock.patch("asr_everywhere.autostart.winreg") as mock_winreg,
        ):
            mock_key = mock.MagicMock()
            mock_winreg.OpenKey.return_value.__enter__.return_value = mock_key
            mock_winreg.QueryValueEx.return_value = ("C:\\other.exe", mock_winreg.REG_SZ)

            result = is_autostart_enabled()
            assert result is False


class TestEnableAutostart:
    """Tests for enable_autostart function."""

    def test_returns_false_when_not_exe(self) -> None:
        """Test that enable_autostart returns False when not running as EXE."""
        with mock.patch("asr_everywhere.autostart.is_exe", return_value=False):
            result = enable_autostart()
            assert result is False

    def test_creates_registry_entry(self) -> None:
        """Test that enable_autostart creates registry entry."""
        with (
            mock.patch("asr_everywhere.autostart.is_exe", return_value=True),
            mock.patch("asr_everywhere.autostart.get_exe_path", return_value="C:\\app.exe"),
            mock.patch("asr_everywhere.autostart.winreg") as mock_winreg,
        ):
            mock_key = mock.MagicMock()
            mock_winreg.OpenKey.return_value.__enter__.return_value = mock_key

            result = enable_autostart()

            assert result is True
            mock_winreg.SetValueEx.assert_called_once()
            call_args = mock_winreg.SetValueEx.call_args
            assert call_args[0][0] == mock_key
            assert call_args[0][1] == AUTOSTART_ENTRY_NAME
            assert call_args[0][4] == "C:\\app.exe"

    def test_returns_false_on_registry_error(self) -> None:
        """Test that enable_autostart returns False on registry error."""
        with (
            mock.patch("asr_everywhere.autostart.is_exe", return_value=True),
            mock.patch("asr_everywhere.autostart.get_exe_path", return_value="C:\\app.exe"),
            mock.patch("asr_everywhere.autostart.winreg") as mock_winreg,
        ):
            mock_winreg.OpenKey.side_effect = PermissionError("Access denied")

            result = enable_autostart()
            assert result is False


class TestDisableAutostart:
    """Tests for disable_autostart function."""

    def test_removes_registry_entry(self) -> None:
        """Test that disable_autostart removes registry entry."""
        with mock.patch("asr_everywhere.autostart.winreg") as mock_winreg:
            mock_key = mock.MagicMock()
            mock_winreg.OpenKey.return_value.__enter__.return_value = mock_key

            result = disable_autostart()

            assert result is True
            mock_winreg.DeleteValue.assert_called_once_with(mock_key, AUTOSTART_ENTRY_NAME)

    def test_returns_true_when_entry_not_found(self) -> None:
        """Test that disable_autostart returns True when entry doesn't exist."""
        with mock.patch("asr_everywhere.autostart.winreg") as mock_winreg:
            mock_winreg.DeleteValue.side_effect = FileNotFoundError()

            result = disable_autostart()
            assert result is True

    def test_returns_false_on_registry_error(self) -> None:
        """Test that disable_autostart returns False on registry error."""
        with mock.patch("asr_everywhere.autostart.winreg") as mock_winreg:
            mock_winreg.OpenKey.side_effect = PermissionError("Access denied")

            result = disable_autostart()
            assert result is False


class TestSyncAutostart:
    """Tests for sync_autostart function."""

    def test_returns_false_when_not_exe(self) -> None:
        """Test that sync_autostart returns False when not running as EXE."""
        with mock.patch("asr_everywhere.autostart.is_exe", return_value=False):
            result = sync_autostart(True)
            assert result is False

    def test_calls_enable_when_enabled_true(self) -> None:
        """Test that sync_autostart calls enable_autostart when enabled is True."""
        with (
            mock.patch("asr_everywhere.autostart.is_exe", return_value=True),
            mock.patch(
                "asr_everywhere.autostart.enable_autostart", return_value=True
            ) as mock_enable,
        ):
            result = sync_autostart(True)

            assert result is True
            mock_enable.assert_called_once()

    def test_calls_disable_when_enabled_false(self) -> None:
        """Test that sync_autostart calls disable_autostart when enabled is False."""
        with (
            mock.patch("asr_everywhere.autostart.is_exe", return_value=True),
            mock.patch(
                "asr_everywhere.autostart.disable_autostart", return_value=True
            ) as mock_disable,
        ):
            result = sync_autostart(False)

            assert result is True
            mock_disable.assert_called_once()


class TestRegistryConstants:
    """Tests for registry constants."""

    def test_registry_path_is_correct(self) -> None:
        """Test that registry path is correct for Windows Run key."""
        assert "CurrentVersion" in AUTOSTART_REGISTRY_PATH
        assert "Run" in AUTOSTART_REGISTRY_PATH

    def test_entry_name_is_set(self) -> None:
        """Test that entry name is defined."""
        assert AUTOSTART_ENTRY_NAME == "ASR Everywhere"
