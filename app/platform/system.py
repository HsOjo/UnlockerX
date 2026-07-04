from __future__ import annotations

import re
from typing import Optional

import Quartz

from app.platform import proc

_LID_RE = re.compile(r'"AppleClamshellState" = (\S+)')
_IDLE_RE = re.compile(r'"HIDIdleTime" = (\d+)')
_DISPLAY_RE = re.compile(r'"dsyp"=\{"min"=(\d+),"max"=(\d+),"value"=(\d+)\}')


def cg_session_info() -> Optional[dict]:
    return Quartz.CGSessionCopyCurrentDictionary()


def is_locked() -> bool:
    info = cg_session_info()
    if not info:
        return False
    return bool(info.get('CGSSessionScreenIsLocked', False))


def check_lid() -> Optional[bool]:
    content = proc.out(['/usr/sbin/ioreg', '-c', 'IOPMrootDomain', '-d', '4'])
    m = _LID_RE.search(content)
    if not m:
        return None
    return m.group(1) == 'Yes'


def idle_time() -> float:
    content = proc.out(['/usr/sbin/ioreg', '-c', 'IOHIDSystem', '-d', '4'])
    m = _IDLE_RE.search(content)
    if not m:
        return 0.0
    return int(m.group(1)) / 1_000_000_000


def display_sleep() -> bool:
    """Return True if the main display is asleep.

    Uses Quartz CGDisplayIsAsleep when available; falls back to the internal
    backlight brightness heuristic for older systems.
    """
    try:
        return bool(Quartz.CGDisplayIsAsleep(Quartz.CGMainDisplayID()))
    except Exception:
        pass

    content = proc.out(['/usr/sbin/ioreg', '-n', 'AppleBacklightDisplay', '-d', '9'])
    m = _DISPLAY_RE.search(content)
    if not m:
        return False
    min_, _max_, value = m.groups()
    return min_ == value


def open_url(url: str, new: bool = False, wait: bool = False) -> None:
    args = ['/usr/bin/open']
    if new:
        args.append('-n')
    if wait:
        args.append('-W')
    args.append(url)
    proc.run(args)


def open_accessibility_settings() -> None:
    open_url('x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility')


def open_bluetooth_settings() -> None:
    open_url('x-apple.systempreferences:com.apple.Bluetooth')
