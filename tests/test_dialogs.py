"""Tests for dialog branching without showing real UI."""

from __future__ import annotations

import pytest

from app.core.i18n import load_language
from app.core.ports import DeviceInfo
from tests.fakes import FakePlatform
from app.ui import dialogs


class TestSelectLanguage:
    def test_selects_current_code(self, monkeypatch):
        from app.core.i18n import LANGUAGES, load_language
        load_language()
        selected = []

        def fake_select(title, description, items, default_index=0):
            assert items == [lang.l_this for lang in LANGUAGES.values()]
            assert default_index == list(LANGUAGES.keys()).index('cn')
            return default_index

        monkeypatch.setattr(dialogs, 'select_from_list', fake_select)

        d = dialogs.Dialogs(load_language('en'), None)  # type: ignore[arg-type]
        d.select_language(selected.append, current_code='cn')
        assert selected == ['cn']

    def test_defaults_to_first_when_code_unknown(self, monkeypatch):
        from app.core.i18n import LANGUAGES, load_language
        load_language()

        def fake_select(title, description, items, default_index=0):
            assert default_index == 0
            return 0

        monkeypatch.setattr(dialogs, 'select_from_list', fake_select)

        d = dialogs.Dialogs(load_language('en'), None)  # type: ignore[arg-type]
        d.select_language(lambda code: None, current_code='xx')


class TestBindBluetoothDevice:
    def test_shows_devices_even_when_power_state_reported_off(self, monkeypatch):
        """If paired_devices returns entries, the list should be shown even when
        bluetooth_powered_on reports False (defense against IOBluetooth power
        state returning 0 in frozen builds while system_profiler still lists devices).
        """
        platform = FakePlatform()
        platform.bluetooth_powered_on = lambda: False
        platform.paired = [
            DeviceInfo(name='AirPods', address='A1:B2:C3', connected=False, rssi=None),
            DeviceInfo(name='Mouse', address='D4:E5:F6', connected=False, rssi=None),
        ]
        selected = []

        def fake_select(title, description, items):
            assert len(items) == 2
            assert items[0] == 'AirPods'
            return 0

        monkeypatch.setattr(dialogs, 'select_from_list', fake_select)
        monkeypatch.setattr(dialogs, 'show_alert', lambda *args, **kwargs: None)

        d = dialogs.Dialogs(load_language('en'), None)  # type: ignore[arg-type]
        d.bind_bluetooth_device(platform, lambda addr, name: selected.append((addr, name)))

        assert selected == [('A1:B2:C3', 'AirPods')]

    def test_opens_settings_when_no_devices_and_power_off(self, monkeypatch):
        platform = FakePlatform()
        platform.bluetooth_powered_on = lambda: False
        platform.paired = []

        alerts = []
        settings_opened = []

        monkeypatch.setattr(dialogs, 'show_alert', lambda *args: alerts.append(args))
        monkeypatch.setattr(dialogs, 'select_from_list', lambda *args, **kwargs: None)
        platform.open_bluetooth_settings = lambda: settings_opened.append(True)

        d = dialogs.Dialogs(load_language('en'), None)  # type: ignore[arg-type]
        d.bind_bluetooth_device(platform, lambda addr, name: None)

        assert len(alerts) == 1
        assert len(settings_opened) == 1
