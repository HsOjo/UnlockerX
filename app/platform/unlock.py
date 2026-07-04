from __future__ import annotations

import subprocess
import time

import Quartz

from app.platform import keychain, system

_TAP = Quartz.kCGHIDEventTap
_SHIFT = Quartz.kCGEventFlagMaskShift
_KEY_SHIFT = 56
_KEY_BACKSPACE = 51
_KEY_RETURN = 36

_HID_SOURCE = None


def _hid_source():
    """Lazily create the HID event source used for simulated keystrokes."""
    global _HID_SOURCE
    if _HID_SOURCE is None:
        _HID_SOURCE = Quartz.CGEventSourceCreate(Quartz.kCGEventSourceStateHIDSystemState)
    return _HID_SOURCE

# US QWERTY virtual keycode mapping. This is used instead of keycode 0 + Unicode
# string because macOS secure input on the lock screen blocks the latter.
_LETTER_CODES = {
    'a': 0x00, 'b': 0x0b, 'c': 0x08, 'd': 0x02, 'e': 0x0e, 'f': 0x03,
    'g': 0x05, 'h': 0x04, 'i': 0x22, 'j': 0x26, 'k': 0x28, 'l': 0x25,
    'm': 0x2e, 'n': 0x2d, 'o': 0x1f, 'p': 0x23, 'q': 0x0c, 'r': 0x0f,
    's': 0x01, 't': 0x11, 'u': 0x20, 'v': 0x09, 'w': 0x0d, 'x': 0x07,
    'y': 0x10, 'z': 0x06,
}
_SYMBOL_CODES = {
    '`': 0x32, '-': 0x1b, '=': 0x18, '[': 0x21, ']': 0x1e, '\\': 0x2a,
    ';': 0x29, "'": 0x27, ',': 0x2b, '.': 0x2f, '/': 0x2c, ' ': 0x31,
}
_DIGIT_CODES = {'1': 0x12, '2': 0x13, '3': 0x14, '4': 0x15, '5': 0x17,
                '6': 0x16, '7': 0x1a, '8': 0x1c, '9': 0x19, '0': 0x1d}

_KEYCODE_MAP: dict[str, tuple[int, int]] = {}
for ch, code in _LETTER_CODES.items():
    _KEYCODE_MAP[ch] = (code, 0)
    _KEYCODE_MAP[ch.upper()] = (code, _SHIFT)
for ch, code in _DIGIT_CODES.items():
    _KEYCODE_MAP[ch] = (code, 0)
for ch, code in _SYMBOL_CODES.items():
    _KEYCODE_MAP[ch] = (code, 0)
# shifted symbols on US QWERTY
for unshifted, shifted in [
    ('`', '~'), ('-', '_'), ('=', '+'), ('[', '{'), (']', '}'),
    ('\\', '|'), (';', ':'), ("'", '"'), (',', '<'), ('.', '>'),
    ('/', '?'),
]:
    code, _ = _KEYCODE_MAP[unshifted]
    _KEYCODE_MAP[shifted] = (code, _SHIFT)
for digit, shifted in zip('1234567890', '!@#$%^&*()'):
    code, _ = _KEYCODE_MAP[digit]
    _KEYCODE_MAP[shifted] = (code, _SHIFT)


def _tap_key(keycode: int, flags: int = 0) -> None:
    source = _hid_source()
    for down in (True, False):
        ev = Quartz.CGEventCreateKeyboardEvent(source, keycode, down)
        if flags:
            Quartz.CGEventSetFlags(ev, flags)
        Quartz.CGEventPost(_TAP, ev)


def _type_string(text: str) -> None:
    source = _hid_source()
    for ch in text:
        for down in (True, False):
            ev = Quartz.CGEventCreateKeyboardEvent(source, 0, down)
            Quartz.CGEventKeyboardSetUnicodeString(ev, len(ch), ch)
            Quartz.CGEventPost(_TAP, ev)
        time.sleep(0.01)


def _type_string_keycodes(text: str) -> None:
    """Type text using real keycodes. Falls back to Unicode for unmapped chars."""
    source = _hid_source()
    for ch in text:
        mapping = _KEYCODE_MAP.get(ch)
        if mapping is None:
            _type_string(ch)
            continue
        keycode, flags = mapping
        needs_shift = bool(flags & _SHIFT)
        if needs_shift:
            Quartz.CGEventPost(_TAP, Quartz.CGEventCreateKeyboardEvent(source, _KEY_SHIFT, True))
        for down in (True, False):
            ev = Quartz.CGEventCreateKeyboardEvent(source, keycode, down)
            if flags:
                Quartz.CGEventSetFlags(ev, flags)
            Quartz.CGEventPost(_TAP, ev)
        if needs_shift:
            Quartz.CGEventPost(_TAP, Quartz.CGEventCreateKeyboardEvent(source, _KEY_SHIFT, False))
        time.sleep(0.02)


def _unlock_cgevent(password: str) -> None:
    """CGEvent-based typing sequence: Backspace, password, Return.

    A Backspace press is sent first to activate or clear the lock-screen
    password field without moving the cursor or changing focus.
    """
    _tap_key(_KEY_BACKSPACE)
    time.sleep(0.1)
    _type_string_keycodes(password)
    time.sleep(0.1)
    _tap_key(_KEY_RETURN)


def _escape_applescript_string(text: str) -> str:
    """Escape a string for use inside an AppleScript double-quoted string."""
    return text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')


def _unlock_applescript(password: str) -> None:
    """AppleScript/System Events-based typing sequence.

    This is the primary method because System Events handles keyboard layout,
    Shift/Option modifiers, and focus on the login window more reliably than
    raw CGEvent keycode 0 events. The sequence is Cmd+A → password → Return;
    it never uses Tab so focus is not moved away from the password field.
    """
    escaped = _escape_applescript_string(password)
    script = f'''
tell application "System Events"
    keystroke "a" using command down
    delay 0.05
    keystroke "{escaped}"
    delay 0.05
    keystroke return
end tell
'''
    subprocess.run(['/usr/bin/osascript', '-e', script], capture_output=True, text=True, timeout=10)


def _unlock_applescript_ui(password: str) -> None:
    """AppleScript/System Events UI-element-based password injection.

    Some macOS versions block "keystroke" text from reaching the lock-screen
    secure password field (only Return/Tab get through). This fallback writes
    the password directly into the loginwindow password field via accessibility
    and then presses Return.
    """
    escaped = _escape_applescript_string(password)
    script = f'''
tell application "System Events"
    tell process "loginwindow"
        try
            click text field 1 of window 1
            set value of text field 1 of window 1 to "{escaped}"
        end try
        try
            click secure text field 1 of window 1
            set value of secure text field 1 of window 1 to "{escaped}"
        end try
    end tell
    delay 0.05
    keystroke return
end tell
'''
    subprocess.run(['/usr/bin/osascript', '-e', script], capture_output=True, text=True, timeout=10)


def _wait_unlock(timeout: float = 3.0, interval: float = 0.5) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(interval)
        if not system.is_locked():
            return True
    return not system.is_locked()


def unlock() -> bool:
    """Type the stored password into the lock screen and verify it unlocked."""
    if not system.is_locked():
        return True
    password = keychain.get_password()
    if password is None:
        return False

    # Primary: CGEvent with real keycodes. macOS secure input on the lock
    # screen blocks Unicode-string events, but low-level keycode events posted
    # from a HID system source usually reach the password field once it has
    # focus.
    _unlock_cgevent(password)
    if _wait_unlock():
        return True

    # Retry once after a short pause; the lock screen may need more time.
    if system.is_locked():
        time.sleep(1.0)
        _unlock_cgevent(password)
        if _wait_unlock():
            return True

    # Fallback 1: AppleScript/System Events (handles keyboard layout/modifiers).
    if system.is_locked():
        _unlock_applescript(password)
        if _wait_unlock():
            return True

    # Fallback 2: write directly into the loginwindow password field via
    # accessibility, for macOS versions that block simulated keystrokes.
    if system.is_locked():
        _unlock_applescript_ui(password)
        return _wait_unlock()
    return True
