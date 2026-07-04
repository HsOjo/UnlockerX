"""Application lifecycle helpers: restart, login startup, accessibility check."""
from __future__ import annotations

import ctypes
import logging
import os
import subprocess
import sys
from typing import Optional

from Foundation import NSDictionary, NSArray, NSNumber

from app.platform import proc, system
from app.res.const import Const


log = logging.getLogger(__name__)


def _app_path() -> Optional[str]:
    """Return the path to the current .app bundle or executable."""
    # Running from a PyInstaller bundle.
    meipass = getattr(sys, '_MEIPASS', None)
    if meipass:
        # In onefile mode the binary is next to the _MEIPASS dir.
        exe = sys.executable
        if exe.endswith(f'.app/Contents/MacOS/{Const.app_name}'):
            return exe[:exe.index('.app/') + 4]
        return exe

    # Source run: __main__.py lives at repo root; return it.
    root = os.path.dirname(sys.argv[0]) or os.getcwd()
    return root


def _app_executable() -> str:
    """Return the executable to launch at login.

    In a frozen PyInstaller app this is the bundle binary; when running from
    source it falls back to the current Python interpreter.
    """
    return sys.executable


def restart(args: tuple[str, ...] = ()) -> None:
    path = _app_path()
    if path and path.endswith('.app'):
        system.open_url(path, new=True, wait=False)
    elif path:
        proc.run([sys.executable, os.path.join(path, '__main__.py'), *args])
    sys.exit(0)


def has_login_startup() -> bool:
    """Return True if the LaunchAgent plist exists."""
    return os.path.exists(Const.launch_agent_plist)


def _write_launch_agent_plist() -> bool:
    plist = NSDictionary.dictionaryWithDictionary_({
        'Label': Const.agent_label,
        'ProgramArguments': NSArray.arrayWithArray_([_app_executable()]),
        'RunAtLoad': NSNumber.numberWithBool_(True),
        'KeepAlive': NSDictionary.dictionaryWithDictionary_({
            'SuccessfulExit': NSNumber.numberWithBool_(False),
        }),
        'ProcessType': 'Interactive',
    })
    os.makedirs(os.path.dirname(Const.launch_agent_plist), exist_ok=True)
    ok = plist.writeToFile_atomically_(Const.launch_agent_plist, True)
    if not ok:
        log.error(f'failed to write LaunchAgent plist: {Const.launch_agent_plist}')
    return bool(ok)


def set_login_startup(enable: bool) -> bool:
    """Enable or disable login startup via a user LaunchAgent plist."""
    domain = f'gui/{os.getuid()}'
    if enable:
        if not _write_launch_agent_plist():
            return False
        result = subprocess.run(
            ['/bin/launchctl', 'bootstrap', domain, Const.launch_agent_plist],
            capture_output=True, text=True, check=False)
        if result.returncode != 0:
            log.error(f'launchctl bootstrap failed: {result.stderr.strip()}')
            return False
        return True

    result = subprocess.run(
        ['/bin/launchctl', 'bootout', domain, Const.launch_agent_plist],
        capture_output=True, text=True, check=False)
    if result.returncode != 0 and 'No such process' not in result.stderr:
        log.warning(f'launchctl bootout: {result.stderr.strip()}')
    try:
        if os.path.exists(Const.launch_agent_plist):
            os.remove(Const.launch_agent_plist)
    except OSError:
        log.exception('failed to remove LaunchAgent plist')
        return False
    return True


def accessibility_granted() -> bool:
    """Return True if this process has Accessibility permission.

    Uses AXIsProcessTrustedWithOptions (ApplicationServices) to avoid the
    false positives and System Events prompts of the osascript probe.
    """
    try:
        lib = ctypes.CDLL(
            '/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices')
        lib.AXIsProcessTrustedWithOptions.restype = ctypes.c_bool
        lib.AXIsProcessTrustedWithOptions.argtypes = [ctypes.c_void_p]
        return bool(lib.AXIsProcessTrustedWithOptions(None))
    except Exception:
        log.exception('AXIsProcessTrustedWithOptions failed, falling back to osascript')

    # Fallback probe using System Events. -1743 = not allowed.
    stat, _, err = proc.run(['/usr/bin/osascript', '-e',
        'tell application "System Events" to key code 63'])
    if stat == -1743:
        return False
    # -1743 = not allowed. 0 = allowed. Other errors do not mean lack of permission.
    return '1002' not in err or stat == 0
