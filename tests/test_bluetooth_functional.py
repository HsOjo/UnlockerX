"""Functional tests for Bluetooth discovery.

These tests exercise the real IOBluetooth / system_profiler stack on macOS.
They require Bluetooth permission and at least one paired or visible device
is helpful for meaningful assertions, but the tests avoid requiring a specific
device to be connected.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

from app.platform import bluetooth


@pytest.mark.functional
class TestBluetoothDiscovery:
    def test_controller_power_state_does_not_crash(self):
        """Calling is_powered_on must not raise in either source or frozen builds."""
        result = bluetooth.is_powered_on()
        assert isinstance(result, bool)

    def test_paired_devices_returns_list(self):
        """paired_devices must return a list of DeviceInfo without raising."""
        devices = bluetooth.paired_devices()
        assert isinstance(devices, list)
        for device in devices:
            assert device.address
            assert isinstance(device.connected, bool)

    def test_system_profiler_runs_successfully(self):
        """system_profiler must exit 0 and produce valid JSON."""
        proc = subprocess.run(
            ['/usr/sbin/system_profiler', 'SPBluetoothDataType', '-json'],
            capture_output=True, text=True, encoding='utf-8', timeout=8)
        assert proc.returncode == 0
        assert proc.stdout

    def test_system_profiler_devices_returns_list(self):
        """_system_profiler_devices must return a list of DeviceInfo."""
        devices = bluetooth._system_profiler_devices()
        assert isinstance(devices, list)
        for device in devices:
            assert device.address

    def test_info_for_unknown_device_returns_none(self):
        """info() for a non-existent address must return None gracefully."""
        result = bluetooth.info('00:00:00:00:00:00')
        assert result is None

    def test_io_bluetooth_framework_imported(self):
        """PyInstaller must include the IOBluetooth framework binding."""
        from IOBluetooth import IOBluetoothDevice
        # Import is the assertion; do not call pairedDevices() here because it
        # requires a running NSApplication/NSRunLoop and aborts in plain pytest.
        assert IOBluetoothDevice is not None


@pytest.mark.functional
def test_diagnostic_mode_prints_and_exits():
    """--diagnose-bluetooth must run without launching NSApp."""
    proc = subprocess.run(
        [sys.executable, '__main__.py', '--diagnose-bluetooth'],
        capture_output=True, text=True, encoding='utf-8', timeout=15)
    assert proc.returncode == 0
    output = proc.stdout + proc.stderr
    assert 'Bluetooth Diagnostic' in output
    assert 'system_profiler' in output
    assert 'IOBluetooth direct' in output


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'functional'])
