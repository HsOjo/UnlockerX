from __future__ import annotations

import json
import subprocess
import threading
import time
from typing import Optional

from AppKit import NSApplication
from IOBluetooth import IOBluetoothDevice, IOBluetoothHostController

from app.core.ports import DeviceInfo

# IOBluetoothDevice.RSSI() returns this sentinel when the value is unavailable.
_RSSI_UNAVAILABLE = 127

# How long a system_profiler snapshot is considered fresh for info() lookups.
_PROFILER_CACHE_TTL = 2.0


def _normalize(address: str) -> str:
    return address.replace(':', '').replace('-', '').lower()


def _cocoa_app_running() -> bool:
    """Return True only when the process has a running NSApplication.

    IOBluetooth Objective-C APIs abort the process when called without a
    running NSApplication/NSRunLoop (e.g. during pytest or diagnostics).
    """
    try:
        return bool(NSApplication.sharedApplication().isRunning())
    except Exception:
        return False


def _to_info(device) -> DeviceInfo:
    name = device.name() or ''
    address = device.addressString() or ''
    connected = bool(device.isConnected())
    rssi: Optional[int] = None
    if connected:
        value = device.RSSI()
        if value is not None and value != _RSSI_UNAVAILABLE:
            rssi = int(value)
    return DeviceInfo(name=name, address=address, connected=connected, rssi=rssi)


def _run_system_profiler() -> Optional[dict]:
    try:
        proc = subprocess.run(
            ['/usr/sbin/system_profiler', 'SPBluetoothDataType', '-json'],
            capture_output=True, text=True, encoding='utf-8', timeout=8)
    except (subprocess.TimeoutExpired, OSError):
        return None

    if proc.returncode != 0 or not proc.stdout:
        return None

    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def _controller_powered_on() -> bool:
    """Return True when the Bluetooth controller reports itself as powered on.

    Uses system_profiler instead of IOBluetoothHostController because the
    Objective-C API can abort the process when called without a running
    NSApplication/NSRunLoop (e.g. during diagnostics or from a worker thread).
    """
    data = _run_system_profiler()
    if data is None:
        return False

    entries = data.get('SPBluetoothDataType') or []
    for entry in entries:
        state = entry.get('controller_properties', {}).get('controller_state', '')
        if state == 'attrib_on':
            return True
    return False


class _ProfilerCache:
    """Simple TTL cache for system_profiler Bluetooth snapshots.

    Callers must hold ``_lock`` when mutating or reading cache state. In the
    current architecture all callers are on the main thread, but the lock makes
    the invariant explicit and safe if that ever changes.
    """

    def __init__(self, ttl: float):
        self.ttl = ttl
        self._lock = threading.Lock()
        self._time: float = 0.0
        self._devices: list[DeviceInfo] = []
        self._by_address: dict[str, DeviceInfo] = {}

    def refresh(self) -> list[DeviceInfo]:
        data = _run_system_profiler()
        with self._lock:
            if data is None:
                return self._devices

            entries = data.get('SPBluetoothDataType') or []
            if not entries:
                self._devices = []
                self._by_address = {}
                self._time = time.time()
                return self._devices

            result = []
            seen = set()
            for entry in entries:
                for connected in (True, False):
                    key = 'device_connected' if connected else 'device_not_connected'
                    devices = entry.get(key) or []
                    for item in devices:
                        if not isinstance(item, dict):
                            continue
                        for name, props in item.items():
                            if not isinstance(props, dict):
                                continue
                            address = props.get('device_address', '')
                            if not address:
                                continue
                            norm = _normalize(address)
                            if norm in seen:
                                continue
                            seen.add(norm)
                            rssi_raw = props.get('device_rssi')
                            rssi = int(rssi_raw) if isinstance(rssi_raw, (int, str)) and str(rssi_raw).lstrip('-').isdigit() else None
                            result.append(DeviceInfo(
                                name=name, address=address,
                                connected=connected, rssi=rssi))

            self._devices = result
            self._by_address = {_normalize(d.address): d for d in result}
            self._time = time.time()
            return result

    def devices(self) -> list[DeviceInfo]:
        with self._lock:
            stale = time.time() - self._time > self.ttl
            cached = self._devices
        if stale:
            return self.refresh()
        return cached

    def get(self, address: str) -> Optional[DeviceInfo]:
        with self._lock:
            stale = time.time() - self._time > self.ttl
            if not stale:
                return self._by_address.get(_normalize(address))
        self.refresh()
        with self._lock:
            return self._by_address.get(_normalize(address))


_profiler_cache = _ProfilerCache(_PROFILER_CACHE_TTL)


def _system_profiler_devices() -> list[DeviceInfo]:
    """Enumerate Bluetooth devices via system_profiler.

    This is much more reliable than IOBluetooth's pairedDevices() inside a
    frozen PyInstaller app, because system_profiler reads the same system cache
    that System Settings uses and does not depend on the IOBluetooth runloop.
    """
    return _profiler_cache.refresh()


def _all_known_devices(retry: int = 3) -> list:
    """Return paired + recent + favorite devices, deduplicated by address."""
    if not _cocoa_app_running():
        return []
    for attempt in range(retry):
        sources = [
            IOBluetoothDevice.pairedDevices() or [],
            IOBluetoothDevice.recentDevices_(100) or [],
            IOBluetoothDevice.favoriteDevices() or [],
        ]
        seen = set()
        result = []
        for source in sources:
            for device in source:
                addr = _normalize(device.addressString() or '')
                if addr and addr not in seen:
                    seen.add(addr)
                    result.append(device)
        if result:
            return result
        if attempt < retry - 1:
            time.sleep(0.3)
    return []


def _find_io_bluetooth(address: str):
    if not _cocoa_app_running():
        return None
    target = _normalize(address)
    # Prefer direct lookup by address; this works even when pairedDevices() is empty.
    device = IOBluetoothDevice.deviceWithAddressString_(address)
    if device is not None:
        return device
    for device in _all_known_devices():
        if _normalize(device.addressString() or '') == target:
            return device
    return None


def is_powered_on() -> bool:
    return _controller_powered_on()


def paired_devices() -> list[DeviceInfo]:
    """Return bonded/known Bluetooth devices, using system_profiler as primary source."""
    return _system_profiler_devices()


def info(address: str) -> Optional[DeviceInfo]:
    """Return current DeviceInfo for the bound address.

    Uses the system_profiler cache as the primary source because it gives
    reliable connection state + RSSI without requiring IOBluetooth runloop
    synchronization. Falls back to IOBluetooth direct lookup if the device is
    not in the system_profiler snapshot.
    """
    cached = _profiler_cache.get(address)
    if cached is not None:
        return cached

    device = _find_io_bluetooth(address)
    if device is not None:
        return _to_info(device)
    return None


def connect(address: str) -> bool:
    device = _find_io_bluetooth(address)
    if device is None:
        return False
    if device.isConnected():
        return True
    # Synchronous connection request; returns kIOReturnSuccess (0) on success.
    return device.openConnection() == 0
