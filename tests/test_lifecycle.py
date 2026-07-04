from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.platform import lifecycle


def _cdll_mock(trusted: bool):
    lib = MagicMock()
    lib.AXIsProcessTrustedWithOptions.return_value = trusted
    return lib


@patch('ctypes.CDLL', return_value=_cdll_mock(True))
def test_accessibility_granted_uses_ax_api(_mock_cdll):
    assert lifecycle.accessibility_granted() is True
    _mock_cdll.assert_called_once()


@patch('ctypes.CDLL', return_value=_cdll_mock(False))
def test_accessibility_granted_false_from_ax_api(_mock_cdll):
    assert lifecycle.accessibility_granted() is False


@patch('ctypes.CDLL', side_effect=OSError('missing'))
def test_accessibility_granted_falls_back_to_osascript(_mock_cdll):
    with patch('app.platform.lifecycle.proc.run', return_value=(-1743, '', '')):
        assert lifecycle.accessibility_granted() is False


@patch('ctypes.CDLL', side_effect=OSError('missing'))
def test_accessibility_granted_other_error_treated_as_allowed(_mock_cdll):
    # Non -1743 errors from the osascript probe are treated as "allowed".
    with patch('app.platform.lifecycle.proc.run', return_value=(1, '', 'some error')):
        assert lifecycle.accessibility_granted() is True


def test_has_login_startup_checks_plist_existence():
    with patch('app.platform.lifecycle.os.path.exists', return_value=True):
        assert lifecycle.has_login_startup() is True
    with patch('app.platform.lifecycle.os.path.exists', return_value=False):
        assert lifecycle.has_login_startup() is False
