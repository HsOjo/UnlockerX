from __future__ import annotations

from app.platform.applescript import run_applescript


def screen_save() -> None:
    run_applescript('tell application id "com.apple.ScreenSaver.Engine" to launch')


def set_require_password_wake() -> None:
    run_applescript(
        'tell application "System Events" to set require password to wake '
        'of security preferences to true')
