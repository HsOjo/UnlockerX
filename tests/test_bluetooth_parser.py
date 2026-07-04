from __future__ import annotations

from unittest.mock import patch

from app.platform import bluetooth


def test_normalize_strips_separators_and_lowers():
    assert bluetooth._normalize('A4:C6:F0:D8:E1:EF') == 'a4c6f0d8e1ef'
    assert bluetooth._normalize('a4-c6-f0-d8-e1-ef') == 'a4c6f0d8e1ef'


def test_is_powered_on_parses_attrib_on():
    sample = {
        'SPBluetoothDataType': [
            {'controller_properties': {'controller_state': 'attrib_on'}},
        ],
    }
    with patch('app.platform.bluetooth._run_system_profiler', return_value=sample):
        assert bluetooth.is_powered_on() is True


def test_is_powered_on_returns_false_when_off():
    sample = {
        'SPBluetoothDataType': [
            {'controller_properties': {'controller_state': 'attrib_off'}},
        ],
    }
    with patch('app.platform.bluetooth._run_system_profiler', return_value=sample):
        assert bluetooth.is_powered_on() is False


def test_profiler_cache_parses_connected_devices():
    sample = {
        'SPBluetoothDataType': [
            {
                'device_connected': [
                    {'My Device': {'device_address': 'A4:C6:F0:D8:E1:EF', 'device_rssi': -55}},
                ],
                'device_not_connected': [
                    {'Other': {'device_address': '00:11:22:33:44:55'}},
                ],
            },
        ],
    }
    with patch('app.platform.bluetooth._run_system_profiler', return_value=sample):
        devices = bluetooth._system_profiler_devices()
    assert len(devices) == 2
    connected = next(d for d in devices if d.address == 'A4:C6:F0:D8:E1:EF')
    assert connected.connected is True
    assert connected.rssi == -55
    disconnected = next(d for d in devices if d.address == '00:11:22:33:44:55')
    assert disconnected.connected is False
    assert disconnected.rssi is None
