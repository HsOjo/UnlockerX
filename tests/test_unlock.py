"""Tests for unlock helpers."""

from __future__ import annotations

import Quartz

from app.platform import unlock as unlock_mod
from app.platform.unlock import _escape_applescript_string, _KEYCODE_MAP


def test_escape_applescript_string_escapes_quotes_and_backslashes():
    assert _escape_applescript_string('a"b\\c') == 'a\\"b\\\\c'


def test_escape_applescript_string_escapes_control_chars_including_tab():
    assert _escape_applescript_string('a\tb\nc') == 'a\\tb\\nc'


def test_keycode_map_covers_letters_digits_and_common_symbols():
    assert _KEYCODE_MAP['a'] == (0x00, 0)
    assert _KEYCODE_MAP['A'] == (0x00, Quartz.kCGEventFlagMaskShift)
    assert _KEYCODE_MAP['1'] == (0x12, 0)
    assert _KEYCODE_MAP['!'] == (0x12, Quartz.kCGEventFlagMaskShift)
    assert _KEYCODE_MAP[' '] == (0x31, 0)
    assert _KEYCODE_MAP['/'] == (0x2c, 0)
    assert _KEYCODE_MAP['?'] == (0x2c, Quartz.kCGEventFlagMaskShift)


def test_type_string_keycodes_posts_lowercase_letters(monkeypatch):
    posted = []

    def fake_create(source, keycode, down):
        return ['event', source, keycode, down]

    def fake_set_flags(ev, flags):
        ev.append(flags)

    def fake_post(tap, ev):
        posted.append((tap, list(ev)))

    monkeypatch.setattr(Quartz, 'CGEventCreateKeyboardEvent', fake_create)
    monkeypatch.setattr(Quartz, 'CGEventSetFlags', fake_set_flags)
    monkeypatch.setattr(Quartz, 'CGEventPost', fake_post)
    monkeypatch.setattr(unlock_mod.time, 'sleep', lambda x: None)

    unlock_mod._type_string_keycodes('ab')

    assert len(posted) == 4  # a down/up, b down/up
    for tap, ev in posted:
        assert tap == Quartz.kCGHIDEventTap
        assert ev[1] == unlock_mod._HID_SOURCE
    assert posted[0][1][2:] == [0x00, True]
    assert posted[1][1][2:] == [0x00, False]
    assert posted[2][1][2:] == [0x0b, True]
    assert posted[3][1][2:] == [0x0b, False]


def test_type_string_keycodes_posts_shift_for_uppercase(monkeypatch):
    posted = []

    def fake_create(source, keycode, down):
        return ['event', source, keycode, down]

    def fake_set_flags(ev, flags):
        ev.append(flags)

    def fake_post(tap, ev):
        posted.append((tap, list(ev)))

    monkeypatch.setattr(Quartz, 'CGEventCreateKeyboardEvent', fake_create)
    monkeypatch.setattr(Quartz, 'CGEventSetFlags', fake_set_flags)
    monkeypatch.setattr(Quartz, 'CGEventPost', fake_post)
    monkeypatch.setattr(unlock_mod.time, 'sleep', lambda x: None)

    unlock_mod._type_string_keycodes('A')

    # Shift down, A down, A up, Shift up
    assert len(posted) == 4
    assert posted[0][1][2:] == [56, True]
    assert posted[1][1][2:] == [0x00, True, Quartz.kCGEventFlagMaskShift]
    assert posted[2][1][2:] == [0x00, False, Quartz.kCGEventFlagMaskShift]
    assert posted[3][1][2:] == [56, False]


def test_hid_source_is_created_lazily(monkeypatch):
    original = unlock_mod._HID_SOURCE
    try:
        unlock_mod._HID_SOURCE = None
        created = []

        def fake_create(state):
            created.append(state)
            return 'fake-source'

        monkeypatch.setattr(Quartz, 'CGEventSourceCreate', fake_create)

        assert unlock_mod._hid_source() == 'fake-source'
        assert unlock_mod._hid_source() == 'fake-source'
        assert len(created) == 1
    finally:
        unlock_mod._HID_SOURCE = original


def test_unlock_cgevent_posts_sequence(monkeypatch):
    posted = []

    def fake_create(source, keycode, down):
        return ['event', source, keycode, down]

    def fake_mouse_create(source, mouse_type, pos, button):
        return ['mouse', source, mouse_type, pos, button]

    def fake_set_flags(ev, flags):
        ev.append(flags)

    def fake_post(tap, ev):
        posted.append((tap, list(ev) if isinstance(ev, list) else ev))

    monkeypatch.setattr(Quartz, 'CGEventCreateKeyboardEvent', fake_create)
    monkeypatch.setattr(Quartz, 'CGEventCreateMouseEvent', fake_mouse_create)
    monkeypatch.setattr(Quartz, 'CGEventSetFlags', fake_set_flags)
    monkeypatch.setattr(Quartz, 'CGEventPost', fake_post)
    monkeypatch.setattr(unlock_mod.time, 'sleep', lambda x: None)

    unlock_mod._unlock_cgevent('ab')

    # recorded events: Backspace down/up, a down/up, b down/up, Return down/up
    assert len(posted) == 8
    assert posted[0][1][2:] == [51, True]
    assert posted[1][1][2:] == [51, False]
    assert posted[2][1][2:] == [0x00, True]
    assert posted[3][1][2:] == [0x00, False]
    assert posted[4][1][2:] == [0x0b, True]
    assert posted[5][1][2:] == [0x0b, False]
    assert posted[6][1][2:] == [36, True]
    assert posted[7][1][2:] == [36, False]
