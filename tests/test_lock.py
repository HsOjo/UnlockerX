from __future__ import annotations

from unittest.mock import patch

from app.platform import lock


def test_screen_save_launches_screen_saver_engine():
    with patch('app.platform.lock.run_applescript') as m:
        lock.screen_save()
        script = m.call_args[0][0]
        assert 'com.apple.ScreenSaver.Engine' in script
        assert 'launch' in script.lower()


def test_set_require_password_wake_enables_password():
    with patch('app.platform.lock.run_applescript') as m:
        lock.set_require_password_wake()
        script = m.call_args[0][0]
        assert 'require password to wake' in script
        assert 'true' in script
